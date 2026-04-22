(function () {
  let deferredPrompt = null;

  function toggleOfflineIndicator() {
    const indicator = document.getElementById("offline-indicator");
    if (!indicator) return;
    indicator.classList.toggle("d-none", navigator.onLine);
  }

  function setupInstallPrompt() {
    const banner = document.getElementById("install-banner");
    const installButton = document.getElementById("install-button");
    const dismissButton = document.getElementById("install-dismiss");

    if (!banner || !installButton || !dismissButton) return;

    window.addEventListener("beforeinstallprompt", (event) => {
      event.preventDefault();
      deferredPrompt = event;
      banner.classList.remove("d-none");
    });

    installButton.addEventListener("click", async function () {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      banner.classList.add("d-none");
    });

    dismissButton.addEventListener("click", function () {
      banner.classList.add("d-none");
    });

    window.addEventListener("appinstalled", function () {
      banner.classList.add("d-none");
    });
  }

  async function registerServiceWorker() {
    if (!("serviceWorker" in navigator)) return;
    try {
      await navigator.serviceWorker.register("/service-worker.js");
    } catch (error) {
      console.error("No se pudo registrar el service worker", error);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    toggleOfflineIndicator();
    setupInstallPrompt();
    registerServiceWorker();
  });

  window.addEventListener("online", toggleOfflineIndicator);
  window.addEventListener("offline", toggleOfflineIndicator);
})();
