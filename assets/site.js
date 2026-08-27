(() => {
  const menus = Array.from(document.querySelectorAll('.nav-menu'));
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

  const setOpen = (menu, open) => {
    menu.classList.toggle('is-open', open);
    const toggle = menu.querySelector('.nav-toggle');
    if (toggle) {
      toggle.setAttribute('aria-expanded', String(open));
      toggle.textContent = open ? '−' : '+';
    }
  };

  const closeAll = except => menus.forEach(menu => {
    if (menu !== except) setOpen(menu, false);
  });

  menus.forEach(menu => {
    const toggle = menu.querySelector('.nav-toggle');
    if (toggle) {
      toggle.addEventListener('click', () => {
        const opening = !menu.classList.contains('is-open');
        closeAll(menu);
        setOpen(menu, opening);
      });
    }

    menu.addEventListener('mouseenter', () => {
      if (finePointer.matches) {
        closeAll(menu);
        setOpen(menu, true);
      }
    });
    menu.addEventListener('mouseleave', () => {
      if (finePointer.matches) setOpen(menu, false);
    });
    menu.addEventListener('focusin', () => {
      closeAll(menu);
      setOpen(menu, true);
    });
    menu.addEventListener('focusout', () => requestAnimationFrame(() => {
      if (!menu.contains(document.activeElement)) setOpen(menu, false);
    }));
  });

  document.addEventListener('click', event => {
    if (!event.target.closest('.nav-menu')) closeAll();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      const openMenu = document.querySelector('.nav-menu.is-open');
      if (openMenu) {
        setOpen(openMenu, false);
        const toggle = openMenu.querySelector('.nav-toggle');
        if (toggle && toggle.offsetParent !== null) toggle.focus();
      }
    }
  });
})();
