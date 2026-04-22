(function () {
  const DB_NAME = "artesano-market-db";
  const DB_VERSION = 1;
  const STORE_NAME = "cart_items";
  const LOCAL_DIRTY_KEY = "artesano-cart-dirty";

  function openDb() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = function (event) {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: "producto_id" });
        }
      };

      request.onsuccess = function () {
        resolve(request.result);
      };

      request.onerror = function () {
        reject(request.error);
      };
    });
  }

  async function withStore(mode, callback) {
    const db = await openDb();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE_NAME, mode);
      const store = transaction.objectStore(STORE_NAME);
      const result = callback(store, resolve, reject);

      transaction.onerror = function () {
        reject(transaction.error);
      };

      transaction.oncomplete = function () {
        db.close();
        if (result !== undefined) {
          resolve(result);
        }
      };
    });
  }

  const store = {
    cart: {
      selectors: {
        badge: "#navbar-cart-count",
      },

      urls: {
        state: "/carro/estado/",
        sync: "/carro/sincronizar/",
      },

      get isAuthenticated() {
        return document.body.dataset.authenticated === "true";
      },

      updateBadge(count) {
        const badge = document.querySelector(this.selectors.badge);
        if (!badge) return;

        const parsedCount = Number(count) || 0;
        badge.textContent = parsedCount;
        badge.style.display = parsedCount > 0 ? "inline" : "none";
      },

      markDirty() {
        window.localStorage.setItem(LOCAL_DIRTY_KEY, "true");
      },

      clearDirty() {
        window.localStorage.removeItem(LOCAL_DIRTY_KEY);
      },

      isDirty() {
        return window.localStorage.getItem(LOCAL_DIRTY_KEY) === "true";
      },

      getCsrfToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
      },

      normalizeItem(raw) {
        const cantidad = Math.max(1, Number(raw.cantidad) || 1);
        const precioUnitario = Number(raw.precio_unitario || raw.precio || 0);
        const subtotal = Number((precioUnitario * cantidad).toFixed(2));

        return {
          producto_id: Number(raw.producto_id),
          nombre: raw.nombre,
          precio_unitario: precioUnitario.toFixed(2),
          precio: subtotal.toFixed(2),
          subtotal: subtotal.toFixed(2),
          cantidad,
          imagen: raw.imagen || "",
          stock: Number(raw.stock || 999),
        };
      },

      async getLocalItems() {
        const items = await withStore("readonly", (objectStore, resolve) => {
          const request = objectStore.getAll();
          request.onsuccess = function () {
            resolve(request.result || []);
          };
        });
        return items.map((item) => this.normalizeItem(item));
      },

      async replaceLocalItems(items) {
        await withStore("readwrite", (objectStore) => {
          objectStore.clear();
          items.forEach((item) => objectStore.put(this.normalizeItem(item)));
        });
        this.updateBadge(this.countItems(items));
      },

      async saveLocalItem(item) {
        const normalized = this.normalizeItem(item);
        await withStore("readwrite", (objectStore) => {
          objectStore.put(normalized);
        });
      },

      async deleteLocalItem(productoId) {
        await withStore("readwrite", (objectStore) => {
          objectStore.delete(Number(productoId));
        });
      },

      countItems(items) {
        return items.reduce((total, item) => total + (Number(item.cantidad) || 0), 0);
      },

      totalItems(items) {
        return items.reduce((total, item) => total + Number(item.subtotal || item.precio || 0), 0).toFixed(2);
      },

      async request(url, options = {}) {
        const response = await fetch(url, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
          ...options,
        });

        let data = {};
        try {
          data = await response.json();
        } catch (error) {
          data = {};
        }

        if (!response.ok || data.ok === false) {
          const message = data.message || data.error || "No fue posible completar la acción.";
          throw new Error(message);
        }

        if (Array.isArray(data.items)) {
          await this.replaceLocalItems(data.items);
          this.clearDirty();
        } else if (typeof data.count !== "undefined") {
          this.updateBadge(data.count);
        }

        return data;
      },

      async fetchServerState() {
        if (!this.isAuthenticated || !navigator.onLine) return null;

        try {
          const data = await this.request(this.urls.state);
          return data;
        } catch (error) {
          return null;
        }
      },

      setButtonState(button, html, disabled) {
        if (!button) return;
        button.innerHTML = html;
        button.disabled = disabled;
      },

      showFeedback(target, message, type) {
        if (!target) return;
        target.classList.remove("d-none", "alert-success", "alert-danger", "alert-warning");
        target.classList.add(type === "error" ? "alert-danger" : "alert-success");
        target.style.backgroundColor = type === "error" ? "var(--color-terracotta)" : "var(--color-olive-light)";
        target.style.color = "white";
        target.innerHTML = message;
      },

      readProductData(button) {
        return {
          producto_id: Number(button.dataset.id),
          nombre: button.dataset.productName || "Producto artesanal",
          precio_unitario: Number(button.dataset.productPrice || 0).toFixed(2),
          cantidad: 1,
          imagen: button.dataset.productImage || "",
          stock: Number(button.dataset.productStock || 999),
        };
      },

      async addOfflineProduct(button) {
        const product = this.readProductData(button);
        const items = await this.getLocalItems();
        const existing = items.find((item) => item.producto_id === product.producto_id);

        if (existing) {
          const nextQuantity = Math.min(existing.cantidad + 1, existing.stock);
          existing.cantidad = nextQuantity;
          await this.saveLocalItem(existing);
        } else {
          await this.saveLocalItem(product);
        }

        const localItems = await this.getLocalItems();
        this.updateBadge(this.countItems(localItems));
        this.markDirty();
        return {
          ok: true,
          offline: true,
          items: localItems,
          count: this.countItems(localItems),
          total: this.totalItems(localItems),
          message: "Producto agregado al carrito offline.",
        };
      },

      async restarOfflineProduct(productoId) {
        const items = await this.getLocalItems();
        const item = items.find((entry) => entry.producto_id === Number(productoId));
        if (!item) return null;

        if (item.cantidad <= 1) {
          await this.deleteLocalItem(productoId);
        } else {
          item.cantidad -= 1;
          await this.saveLocalItem(item);
        }

        const updatedItems = await this.getLocalItems();
        this.updateBadge(this.countItems(updatedItems));
        this.markDirty();
        return {
          ok: true,
          items: updatedItems,
          count: this.countItems(updatedItems),
          total: this.totalItems(updatedItems),
        };
      },

      async removeOfflineProduct(productoId) {
        await this.deleteLocalItem(productoId);
        const updatedItems = await this.getLocalItems();
        this.updateBadge(this.countItems(updatedItems));
        this.markDirty();
        return {
          ok: true,
          items: updatedItems,
          count: this.countItems(updatedItems),
          total: this.totalItems(updatedItems),
        };
      },

      async clearOfflineCart() {
        await this.replaceLocalItems([]);
        this.markDirty();
        return { ok: true, items: [], count: 0, total: "0.00" };
      },

      async syncWithServer() {
        if (!this.isAuthenticated || !navigator.onLine) return null;

        const items = await this.getLocalItems();
        if (!items.length && !this.isDirty()) {
          return this.fetchServerState();
        }

        try {
          const response = await fetch(this.urls.sync, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Requested-With": "XMLHttpRequest",
              "X-CSRFToken": this.getCsrfToken(),
            },
            body: JSON.stringify({
              items: items.map((item) => ({
                producto_id: item.producto_id,
                cantidad: item.cantidad,
              })),
            }),
          });
          const data = await response.json();
          if (!response.ok || data.ok === false) {
            throw new Error(data.message || "No fue posible sincronizar el carrito.");
          }
          await this.replaceLocalItems(data.items || []);
          this.clearDirty();
          return data;
        } catch (error) {
          this.markDirty();
          return null;
        }
      },

      async initialize() {
        const localItems = await this.getLocalItems();
        if (localItems.length) {
          this.updateBadge(this.countItems(localItems));
        }

        if (this.isAuthenticated && navigator.onLine) {
          if (localItems.length || this.isDirty()) {
            await this.syncWithServer();
          } else if (Number(document.querySelector(this.selectors.badge)?.textContent || 0) > 0) {
            await this.fetchServerState();
          }
        }
      },

      bindAddButtons(root = document) {
        root.querySelectorAll("[data-add-to-cart]").forEach((button) => {
          if (button.dataset.cartBound === "true") return;
          button.dataset.cartBound = "true";

          button.addEventListener("click", async (event) => {
            event.preventDefault();

            const url = button.dataset.cartUrl || `/carro/agregar/${button.dataset.id}/`;
            const loadingText = button.dataset.loadingText || '<i class="fas fa-spinner fa-spin mr-1"></i>';
            const successText = button.dataset.successText || '<i class="fas fa-check mr-1"></i> ¡Agregado!';
            const defaultText = button.dataset.defaultText || button.innerHTML;
            const feedbackTarget = button.dataset.feedbackTarget
              ? document.querySelector(button.dataset.feedbackTarget)
              : null;

            button.dataset.defaultText = defaultText;
            this.setButtonState(button, loadingText, true);

            try {
              const data = navigator.onLine
                ? await this.request(url)
                : await this.addOfflineProduct(button);

              this.setButtonState(button, successText, true);

              if (feedbackTarget) {
                this.showFeedback(
                  feedbackTarget,
                  data.offline
                    ? '<i class="fas fa-cloud-download-alt mr-2"></i> Producto guardado offline. Se sincronizará al reconectar.'
                    : '<i class="fas fa-check-circle mr-2"></i> Producto agregado al carrito.',
                  "success",
                );
              }

              window.setTimeout(() => {
                this.setButtonState(button, defaultText, false);
              }, 1500);
            } catch (error) {
              this.setButtonState(button, defaultText, false);
              if (feedbackTarget) {
                this.showFeedback(
                  feedbackTarget,
                  `<i class="fas fa-exclamation-triangle mr-2"></i> ${error.message}`,
                  "error",
                );
              }
            }
          });
        });
      },
    },
  };

  window.ArtesanoStore = store;

  document.addEventListener("DOMContentLoaded", function () {
    store.cart.initialize();
    store.cart.bindAddButtons();
    window.addEventListener("online", function () {
      store.cart.syncWithServer();
    });
  });
})();
