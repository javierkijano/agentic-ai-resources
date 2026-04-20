const cardToggles = document.querySelectorAll("[data-card-toggle]");
const bucketToggles = document.querySelectorAll("[data-bucket-toggle]");

function closeAllBucketMenus(exceptMenu = null) {
  document.querySelectorAll("[data-bucket-menu]").forEach((menu) => {
    if (menu !== exceptMenu) {
      menu.hidden = true;
    }
  });
  bucketToggles.forEach((button) => {
    const card = button.closest(".task-card");
    const menu = card?.querySelector("[data-bucket-menu]");
    if (menu !== exceptMenu) {
      button.setAttribute("aria-expanded", "false");
    }
  });
}

cardToggles.forEach((button) => {
  button.addEventListener("click", () => {
    const detailsId = button.getAttribute("aria-controls");
    const details = detailsId ? document.getElementById(detailsId) : null;
    if (!details) return;

    const shouldOpen = details.hidden;
    details.hidden = !shouldOpen;
    button.setAttribute("aria-expanded", String(shouldOpen));
    button.textContent = shouldOpen ? "Ocultar detalle" : "Ver detalle";
  });
});

bucketToggles.forEach((button) => {
  const card = button.closest(".task-card");
  const menu = card?.querySelector("[data-bucket-menu]");
  if (!menu) return;

  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const willOpen = menu.hidden;
    closeAllBucketMenus(willOpen ? menu : null);
    menu.hidden = !willOpen;
    button.setAttribute("aria-expanded", String(willOpen));
  });

  menu.querySelectorAll("[data-bucket-choice]").forEach((choiceButton) => {
    choiceButton.addEventListener("click", (event) => {
      event.stopPropagation();
      button.textContent = `Cuándo lo haré · ${choiceButton.textContent.trim()}`;
      menu.hidden = true;
      button.setAttribute("aria-expanded", "false");
    });
  });
});

document.addEventListener("click", () => {
  closeAllBucketMenus();
});
