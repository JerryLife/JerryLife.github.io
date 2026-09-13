(() => {
  document.querySelectorAll('.faculty-main a[href], .faculty-footer-inner a[href]').forEach(link => {
    const text = link.textContent.trim();
    if (!text || link.querySelector('img, svg, .faculty-link-arrow') || /[↗→↙←]/u.test(text)) return;
    const href = link.getAttribute('href').trim();
    if (!href || href.startsWith('#') || link.classList.contains('anchorjs-link')) return;
    const target = new URL(href, window.location.href);
    const arrow = document.createElement('span');
    arrow.className = 'faculty-link-arrow';
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '\u00a0' + (target.origin !== window.location.origin || /\.pdf$/i.test(target.pathname) ? '↗' : '→');
    link.append(arrow);
  });
})();
