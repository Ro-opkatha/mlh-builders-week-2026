const menuToggle = document.querySelector(".menu-toggle");
const navigationMenu = document.querySelector(".navigation-menu");
const navigationLinks = document.querySelectorAll(".navigation-link");
const sections = document.querySelectorAll("main section[id]");

function setMenuOpen(isOpen) {
  menuToggle.setAttribute("aria-expanded", String(isOpen));
  menuToggle.setAttribute(
    "aria-label",
    isOpen ? "Close navigation menu" : "Open navigation menu",
  );
  navigationMenu.classList.toggle("is-open", isOpen);
  document.body.classList.toggle("menu-open", isOpen);
}

menuToggle.addEventListener("click", () => {
  const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
  setMenuOpen(!isOpen);
});

navigationLinks.forEach((link) => {
  link.addEventListener("click", () => setMenuOpen(false));
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menuToggle.getAttribute("aria-expanded") === "true") {
    setMenuOpen(false);
    menuToggle.focus();
  }
});

document.addEventListener("click", (event) => {
  if (
    menuToggle.getAttribute("aria-expanded") === "true" &&
    !navigationMenu.contains(event.target) &&
    !menuToggle.contains(event.target)
  ) {
    setMenuOpen(false);
  }
});

if ("IntersectionObserver" in window) {
  const sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        navigationLinks.forEach((link) => {
          const isActive = link.getAttribute("href") === `#${entry.target.id}`;
          link.classList.toggle("is-active", isActive);

          if (isActive) {
            link.setAttribute("aria-current", "location");
          } else {
            link.removeAttribute("aria-current");
          }
        });
      });
    },
    {
      rootMargin: "-30% 0px -60% 0px",
    },
  );

  sections.forEach((section) => sectionObserver.observe(section));
}