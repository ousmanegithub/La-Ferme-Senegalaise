/*
 * La Ferme Sénégalaise: site-wide interactions.
 * Deliberately dependency-free (no jQuery/React) for a fast, SEO-friendly
 * server-rendered site: this file only progressively enhances markup that
 * already works without JS.
 */
(function () {
  "use strict";

  // --- Header: shadow once the page scrolls, + mobile nav toggle ---------
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  const mobileNav = document.querySelector(".mobile-nav");

  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  if (toggle && mobileNav) {
    toggle.addEventListener("click", () => {
      const isOpen = mobileNav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
      document.body.style.overflow = isOpen ? "hidden" : "";
    });

    mobileNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileNav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      });
    });
  }

  // --- Mobile submenu expand/collapse -------------------------------------
  document.querySelectorAll("[data-submenu-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const submenu = btn.nextElementSibling;
      const isOpen = submenu.style.display === "block";
      submenu.style.display = isOpen ? "none" : "block";
      btn.setAttribute("aria-expanded", String(!isOpen));
    });
  });

  // --- Gallery: category filter -------------------------------------------
  const filterButtons = document.querySelectorAll("[data-gallery-filter]");
  const galleryItems = document.querySelectorAll("[data-gallery-category]");
  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterButtons.forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");
      const filter = btn.getAttribute("data-gallery-filter");
      galleryItems.forEach((item) => {
        const match = filter === "all" || item.getAttribute("data-gallery-category") === filter;
        item.style.display = match ? "" : "none";
      });
    });
  });

  // --- Gallery: simple lightbox -------------------------------------------
  const lightbox = document.querySelector("[data-lightbox]");
  if (lightbox) {
    const lightboxMedia = lightbox.querySelector("[data-lightbox-media]");
    const closeLightbox = () => {
      lightbox.classList.remove("is-open");
      lightboxMedia.innerHTML = "";
      document.body.style.overflow = "";
    };
    document.querySelectorAll("[data-lightbox-trigger]").forEach((trigger) => {
      trigger.addEventListener("click", (e) => {
        e.preventDefault();
        const fullImage = trigger.getAttribute("data-full");
        const embedUrl = trigger.getAttribute("data-embed");
        lightboxMedia.innerHTML = embedUrl
          ? `<iframe src="${embedUrl}" allow="autoplay; fullscreen" allowfullscreen frameborder="0"></iframe>`
          : `<img src="${fullImage}" alt="">`;
        lightbox.classList.add("is-open");
        document.body.style.overflow = "hidden";
      });
    });
    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox || e.target.closest(".lightbox__close")) closeLightbox();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeLightbox();
    });
  }

  // --- Basic client-side required-field feedback (server still validates) -
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      let valid = true;
      form.querySelectorAll("[required]").forEach((field) => {
        if (!field.value.trim()) {
          valid = false;
          field.setAttribute("aria-invalid", "true");
        } else {
          field.removeAttribute("aria-invalid");
        }
      });
      if (!valid) e.preventDefault();
    });
  });
})();
