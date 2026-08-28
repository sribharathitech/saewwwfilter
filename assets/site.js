(() => {
  document.documentElement.classList.add('content-protected');

  const notice = document.createElement('div');
  notice.className = 'content-protection-notice';
  notice.setAttribute('role', 'status');
  notice.setAttribute('aria-live', 'polite');
  notice.textContent = 'This website content is protected by Sri Bharathi. Reproduction requires written permission.';
  document.body.appendChild(notice);
  let noticeTimer;

  const showProtectionNotice = () => {
    notice.classList.add('is-visible');
    window.clearTimeout(noticeTimer);
    noticeTimer = window.setTimeout(() => notice.classList.remove('is-visible'), 2600);
  };

  const isEditable = target => target instanceof Element && Boolean(target.closest('input, textarea, select, [contenteditable="true"]'));
  const isProtected = target => target instanceof Element && Boolean(target.closest('main, .site-footer'));
  const hasProtectedSelection = () => {
    const selection = window.getSelection();
    const anchor = selection && selection.anchorNode;
    const element = anchor instanceof Element ? anchor : anchor && anchor.parentElement;
    return Boolean(element && element.closest('main, .site-footer'));
  };

  document.querySelectorAll('img').forEach(image => {
    image.draggable = false;
  });

  document.addEventListener('contextmenu', event => {
    if (isProtected(event.target)) {
      event.preventDefault();
      showProtectionNotice();
    }
  });

  document.addEventListener('copy', event => {
    if ((isProtected(event.target) || hasProtectedSelection()) && !isEditable(event.target)) {
      event.preventDefault();
      showProtectionNotice();
    }
  });

  document.addEventListener('cut', event => {
    if (isProtected(event.target) && !isEditable(event.target)) event.preventDefault();
  });

  document.addEventListener('dragstart', event => {
    if (event.target instanceof HTMLImageElement) {
      event.preventDefault();
      showProtectionNotice();
    }
  });

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
    const command = event.ctrlKey || event.metaKey;
    const protectedShortcut = command && ['a', 'c', 'p', 's', 'u', 'x'].includes(event.key.toLowerCase());
    const developerShortcut = event.key === 'F12' || (command && event.shiftKey && ['c', 'i', 'j', 'k'].includes(event.key.toLowerCase())) || (command && event.altKey && event.key.toLowerCase() === 'i');
    if ((protectedShortcut || developerShortcut) && !isEditable(event.target)) {
      event.preventDefault();
      showProtectionNotice();
      return;
    }
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
