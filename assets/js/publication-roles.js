(() => {
  const list = document.querySelector('.all-publications');
  if (!list) return;

  const filter = list.querySelector('.publication-role-filter');
  const buttons = [...filter.querySelectorAll('button')];
  const collections = [...list.querySelectorAll('.publication-collection')];
  const status = list.querySelector('.publication-filter-status');
  const labels = { all: 'All roles', first: 'First / co-first author', corresponding: 'Corresponding author', other: 'Other author roles' };

  const matches = (entry, role) => {
    const first = entry.classList.contains('first-author');
    const corresponding = entry.classList.contains('corresponding-author');
    return role === 'all' || (role === 'first' && first) || (role === 'corresponding' && corresponding) || (role === 'other' && !first && !corresponding);
  };

  const applyRole = (role) => {
    const counts = collections.map(collection => {
      let count = 0;
      collection.querySelectorAll('ol.bibliography > li').forEach(item => {
        const entry = item.querySelector('.publication-entry');
        const visible = entry && matches(entry, role);
        item.hidden = !visible;
        if (visible) count += 1;
      });
      collection.querySelectorAll('ol.bibliography').forEach(group => {
        const visible = [...group.children].some(item => !item.hidden);
        group.hidden = !visible;
        const heading = group.previousElementSibling;
        if (heading && heading.matches('.bibliography')) heading.hidden = !visible;
      });
      collection.querySelector('.publication-empty').hidden = count !== 0;
      return count;
    });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.publicationRole === role)));
    status.textContent = `${labels[role]} · ${counts[0]} peer-reviewed publication${counts[0] === 1 ? '' : 's'} · ${counts[1]} preprint${counts[1] === 1 ? '' : 's'}`;
  };

  buttons.forEach(button => button.addEventListener('click', () => applyRole(button.dataset.publicationRole)));
  filter.hidden = false;
  applyRole('all');

  document.querySelectorAll('.publication-bib-toggle').forEach(button => {
    button.addEventListener('click', () => {
      const bib = document.getElementById(button.getAttribute('aria-controls'));
      const expanded = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(expanded));
      bib.hidden = !expanded;
    });
  });
})();
