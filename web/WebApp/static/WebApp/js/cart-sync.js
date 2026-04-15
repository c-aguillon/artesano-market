(function () {
  const config = window.ARTESANO_CONFIG || {};
  const cartUrls = config.cartUrls || {};
  const user = config.user || {};

  function getCsrfToken() {
    const value = `; ${document.cookie}`;
    const parts = value.split("; csrftoken=");
    return parts.length === 2 ? parts.pop().split(";").shift() : "";
  }

  function openDb() {
    return new Promise((resolve, reject) => {
      if (!("indexedDB" in window)) {
        resolve(null);
        return;
      }

      const request = indexedDB.open("artesano-market", 1);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains("cartSnapshots")) {
          db.createObjectStore("cartSnapshots", { keyPath: "key" });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function saveSnapshot(snapshot) {
    if (!user.key) return;
    const db = await openDb();
    if (!db) return;
    await new Promise((resolve, reject) => {
      const tx = db.transaction("cartSnapshots", "readwrite");
      tx.objectStore("cartSnapshots").put({ key: user.key, snapshot, updatedAt: new Date().toISOString() });
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
  }

  async function readSnapshot() {
    if (!user.key) return null;
    const db = await openDb();
    if (!db) return null;
    return new Promise((resolve, reject) => {
      const tx = db.transaction("cartSnapshots", "readonly");
      const request = tx.objectStore("cartSnapshots").get(user.key);
      request.onsuccess = () => resolve(request.result ? request.result.snapshot : null);
      request.onerror = () => reject(request.error);
    });
  }

  async function clearSnapshot() {
    if (!user.key) return;
    const db = await openDb();
    if (!db) return;
    await new Promise((resolve, reject) => {
      const tx = db.transaction("cartSnapshots", "readwrite");
      tx.objectStore("cartSnapshots").delete(user.key);
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "La solicitud fallo.");
    }
    return data;
  }

  function updateNavbarCount(count) {
    const badge = document.getElementById("navbar-cart-count");
    if (!badge) return;
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline" : "none";
  }

  function renderCartTable(data) {
    const tbody = document.getElementById("carro-tbody");
    const footer = document.getElementById("carro-footer");
    const total = document.getElementById("total-label");
    if (!tbody || !footer || !total) return;

    if (!data.items.length) {
      tbody.innerHTML = `
        <tr id="fila-vacia">
          <td colspan="4" class="text-center py-5">
            <i class="fas fa-shopping-basket fa-4x mb-3 text-muted opacity-25"></i>
            <h4 class="text-muted">Tu carrito esta vacio</h4>
            <a href="/catalogo/" class="btn btn-nav-cta mt-3">Ir a la tienda</a>
          </td>
        </tr>`;
      footer.style.display = "none";
      return;
    }

    tbody.innerHTML = data.items.map((item) => `
      <tr data-id="${item.producto_id}">
        <td class="py-3">
          <div class="d-flex align-items-center">
            ${item.imagen ? `<img src="${item.imagen}" alt="${item.nombre}" class="rounded mr-3 shadow-sm" style="width:60px;height:60px;object-fit:cover;">` : ""}
            <span class="font-weight-bold text-dark">${item.nombre}</span>
          </div>
        </td>
        <td class="text-center py-3">
          <div class="btn-group btn-group-sm border rounded-pill overflow-hidden">
            <button class="btn btn-light border-0 px-3 btn-restar" data-id="${item.producto_id}">
              <i class="fas fa-minus small"></i>
            </button>
            <span class="px-3 py-1 bg-white font-weight-bold">${item.cantidad}</span>
            <button class="btn btn-light border-0 px-3 btn-agregar" data-id="${item.producto_id}">
              <i class="fas fa-plus small"></i>
            </button>
          </div>
        </td>
        <td class="text-right py-3">
          <span class="font-weight-bold text-dark">$${item.subtotal}</span>
        </td>
        <td class="text-right py-3">
          <button class="btn btn-link text-danger p-0 btn-eliminar" data-id="${item.producto_id}">
            <i class="fas fa-trash-alt"></i>
          </button>
        </td>
      </tr>
    `).join("");

    total.textContent = "$" + data.total;
    footer.style.display = "block";
  }

  function renderWidget(data) {
    const tbody = document.getElementById("widget-tbody");
    const footer = document.getElementById("widget-footer");
    const total = document.getElementById("widget-total");
    if (!tbody || !footer || !total) return;

    if (!data.items.length) {
      tbody.innerHTML = `
        <tr id="widget-vacio">
          <td colspan="3" class="text-center py-5 text-muted">
            <i class="fas fa-shopping-basket fa-3x mb-3 d-block opacity-25" style="color:#ddd;"></i>
            <p class="mb-0" style="font-style:italic;">Tu carrito esta vacio</p>
          </td>
        </tr>`;
      footer.style.display = "none";
      return;
    }

    tbody.innerHTML = data.items.map((item) => `
      <tr class="border-bottom" style="border-color:rgba(0,0,0,0.05)!important;" data-id="${item.producto_id}">
        <td class="pl-3 py-3 align-middle" style="width:50px;">
          ${item.imagen
            ? `<img src="${item.imagen}" alt="${item.nombre}" class="rounded shadow-sm" style="width:40px;height:40px;object-fit:cover;">`
            : `<div class="rounded bg-light d-flex align-items-center justify-content-center" style="width:40px;height:40px;">
                 <i class="fas fa-image text-muted" style="font-size:0.8rem;"></i>
               </div>`}
        </td>
        <td class="py-3 align-middle">
          <div class="font-weight-bold text-dark mb-0" style="line-height:1.2;">${item.nombre}</div>
          <div class="text-muted small">x${item.cantidad} - $${item.subtotal}</div>
        </td>
        <td class="pr-3 py-3 align-middle text-right" style="width:100px;">
          <div class="btn-group btn-group-sm">
            <button class="btn btn-outline-secondary border-0 px-2 btn-restar-w" data-id="${item.producto_id}">
              <i class="fas fa-minus" style="font-size:0.7rem;"></i>
            </button>
            <button class="btn btn-outline-secondary border-0 px-2 btn-agregar-w" data-id="${item.producto_id}">
              <i class="fas fa-plus" style="font-size:0.7rem;"></i>
            </button>
            <button class="btn btn-outline-danger border-0 px-2 btn-eliminar-w" data-id="${item.producto_id}">
              <i class="fas fa-trash-alt" style="font-size:0.7rem;"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join("");

    total.textContent = "$" + data.total;
    footer.style.display = "block";
  }

  function dispatchCartUpdated(data) {
    updateNavbarCount(data.count || 0);
    renderCartTable(data);
    renderWidget(data);
  }

  async function persistAndRender(data) {
    if (!data.items.length) {
      await clearSnapshot();
    } else {
      await saveSnapshot(data);
    }
    dispatchCartUpdated(data);
    return data;
  }

  function buildItemUrl(base, id) {
    return `${base}${id}/`;
  }

  async function updateCart(url, options) {
    const data = await fetchJson(url, options);
    return persistAndRender(data);
  }

  async function syncCartState() {
    if (!user.isAuthenticated || !cartUrls.estado) return;
    try {
      const serverData = await fetchJson(cartUrls.estado, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      const localData = await readSnapshot();

      if (serverData.items.length) {
        await saveSnapshot(serverData);
        dispatchCartUpdated(serverData);
        return;
      }

      if (localData && localData.items && localData.items.length && cartUrls.sincronizar) {
        const restored = await fetchJson(cartUrls.sincronizar, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify({ items: localData.items })
        });
        await saveSnapshot(restored);
        dispatchCartUpdated(restored);
        return;
      }

      dispatchCartUpdated(serverData);
    } catch (error) {
      console.error("No se pudo sincronizar el carrito:", error);
    }
  }

  function setButtonLoading(button, mode) {
    const originalHtml = button.innerHTML;
    const originalOpacity = button.style.opacity;
    button.disabled = true;
    button.innerHTML = mode === "inline" ? '<i class="fas fa-spinner fa-spin mr-1"></i>' : '<i class="fas fa-spinner fa-spin mr-2"></i> Agregando...';

    return function restore(success) {
      if (success && mode === "inline") {
        button.innerHTML = '<i class="fas fa-check mr-1"></i> ¡Agregado!';
        button.style.opacity = "0.7";
        setTimeout(() => {
          button.innerHTML = originalHtml;
          button.style.opacity = originalOpacity;
          button.disabled = false;
        }, 1500);
        return;
      }
      button.innerHTML = originalHtml;
      button.style.opacity = originalOpacity;
      button.disabled = false;
    };
  }

  function showAlert(targetId, isError, message) {
    if (!targetId) return;
    const alert = document.getElementById(targetId);
    if (!alert) return;
    alert.classList.remove("d-none", "alert-success", "alert-danger");
    alert.classList.add(isError ? "alert-danger" : "alert-success");
    alert.style.backgroundColor = isError ? "" : "var(--color-olive-light)";
    alert.style.color = isError ? "" : "white";
    alert.innerHTML = message;
  }

  async function handleAddButton(button) {
    const mode = button.dataset.feedbackMode === "inline" ? "inline" : "detail";
    const restore = setButtonLoading(button, mode);
    try {
      await updateCart(buildItemUrl(cartUrls.agregarBase, button.dataset.id), { headers: { "X-Requested-With": "XMLHttpRequest" } });
      if (button.dataset.feedbackTarget) {
        showAlert(button.dataset.feedbackTarget, false, '<i class="fas fa-check-circle mr-2"></i> ¡Producto agregado al carrito!');
      }
      restore(true);
    } catch (error) {
      if (button.dataset.feedbackTarget) {
        showAlert(button.dataset.feedbackTarget, true, "Error al agregar. Intenta de nuevo.");
      }
      restore(false);
    }
  }

  document.addEventListener("click", async (event) => {
    const addButton = event.target.closest("#btn-agregar-detalle, .btn-agregar-home");
    if (addButton && user.isAuthenticated) {
      event.preventDefault();
      await handleAddButton(addButton);
      return;
    }

    const addCart = event.target.closest(".btn-agregar, .btn-agregar-w");
    if (addCart) {
      event.preventDefault();
      await updateCart(buildItemUrl(cartUrls.agregarBase, addCart.dataset.id), { headers: { "X-Requested-With": "XMLHttpRequest" } });
      return;
    }

    const subtractCart = event.target.closest(".btn-restar, .btn-restar-w");
    if (subtractCart) {
      event.preventDefault();
      await updateCart(buildItemUrl(cartUrls.restarBase, subtractCart.dataset.id), { headers: { "X-Requested-With": "XMLHttpRequest" } });
      return;
    }

    const deleteCart = event.target.closest(".btn-eliminar, .btn-eliminar-w");
    if (deleteCart) {
      event.preventDefault();
      await updateCart(buildItemUrl(cartUrls.eliminarBase, deleteCart.dataset.id), { headers: { "X-Requested-With": "XMLHttpRequest" } });
      return;
    }

    const clearButton = event.target.closest("#btn-limpiar, #widget-btn-limpiar");
    if (clearButton) {
      event.preventDefault();
      await updateCart(cartUrls.limpiar, { headers: { "X-Requested-With": "XMLHttpRequest" } });
    }
  });

  syncCartState();
})();
