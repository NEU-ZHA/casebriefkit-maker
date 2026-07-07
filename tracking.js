(function () {
  function trackEvent(name, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, params || {});
    }
  }

  window.caseBriefKitTrack = trackEvent;

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-track-event]");
    if (!target) return;
    const eventName = target.getAttribute("data-track-event");
    if (!eventName) return;
    trackEvent(eventName, {
      link_text: target.textContent.trim().slice(0, 80),
      link_url: target.href || "",
      page_path: window.location.pathname,
      format: target.getAttribute("data-format") || "",
    });
  });
})();
