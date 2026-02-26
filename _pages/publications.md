---
layout: page
permalink: /publications/
title: Publications
description: Publications and Preprints.
nav: true
nav_order: 3
---

<!-- _pages/publications.md -->

<style>
.pub-stats {
  font-size: 1.1em;
  margin-bottom: 0.75rem;
  color: var(--global-text-color-light);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0;
  align-items: center;
}
.pub-stats .stat-item {
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}
.pub-stats .divider {
  margin: 0 0.5rem;
}
.pub-stats .filter-btn {
  cursor: pointer;
  padding: 0.2em 0.6em;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}
.pub-stats .filter-btn:hover {
  opacity: 0.8;
}
.pub-stats .filter-btn.active {
  border-color: var(--global-theme-color);
}
.pub-stats .first-author-label {
  background-color: var(--global-first-author-bg-color);
}
.pub-stats .corresponding-author-label {
  background-color: var(--global-corresponding-author-bg-color);
}

/* Venue filter row */
.venue-stats {
  font-size: 1em;
  margin-bottom: 1.5rem;
  color: var(--global-text-color-light);
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}
.venue-stats .venue-btn {
  cursor: pointer;
  padding: 0.15em 0.5em;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  font-size: 0.9em;
  color: white;
}
.venue-stats .venue-btn:hover {
  opacity: 0.8;
}
.venue-stats .venue-btn.active {
  border-color: var(--global-theme-color);
}
.publications ol.bibliography > li > .row.is-hidden-by-filter {
  display: none;
}

/* Fix alignment: ensure all rows have consistent padding/margin */
.publications ol.bibliography li .row {
  padding: 0.75rem;
  margin-left: -0.75rem;
  margin-right: -0.75rem;
}
</style>

<div id="pub-stats-container" class="pub-stats">
  <!-- Dynamic content will be inserted here -->
  <span class="stat-item">Loading stats...</span>
</div>

<div id="venue-stats-container" class="venue-stats">
  <!-- Dynamic venue buttons will be inserted here -->
</div>

<script>
document.addEventListener("DOMContentLoaded", function() {
  generatePubStats();
});

const venueColorMap = {
{% for venue in site.data.venues %}
  "{{ venue[0] | slugify }}": "{{ venue[1].color | default: '' }}"{% unless forloop.last %},{% endunless %}
{% endfor %}
};

const activeFilter = {
  type: null,
  value: null,
};

function getVenueButtonStyle(code) {
  const backgroundColor = venueColorMap[code] || "var(--global-theme-color)";
  return `background-color: ${backgroundColor}; color: white;`;
}

function generatePubStats() {
  const allRows = document.querySelectorAll('.publications ol.bibliography li .row');
  let firstAuthorCount = 0;
  let corrAuthorCount = 0;
  const venueCounts = {}; // { 'kdd': { count: 0, name: 'KDD' } }

  allRows.forEach(row => {
    // Count authors
    if (row.classList.contains('first-author')) {
      firstAuthorCount++;
    }
    if (row.classList.contains('corresponding-author')) {
      corrAuthorCount++;
    }

    // Identify venue
    // The bib.liquid adds class "venue-xxxx"
    let venueCode = null;
    let venueName = null;
    
    // Find basic venue class from the row classes
    row.classList.forEach(cls => {
      if (cls.startsWith('venue-')) {
        venueCode = cls.replace('venue-', '');
      }
    });

    // If we found a venue code (e.g. 'kdd'), let's get the display name
    if (venueCode) {
      // Try to get the name from the <abbr> tag
      const abbrEl = row.querySelector('.abbr abbr');
      if (abbrEl) {
        // "KDD 2026" -> "KDD"
        venueName = abbrEl.textContent.trim().split(' ')[0];
      } else {
        venueName = venueCode.toUpperCase();
      }

      if (!venueCounts[venueCode]) {
        venueCounts[venueCode] = { count: 0, name: venueName };
      }
      venueCounts[venueCode].count++;
    }
  });

  // 1. Render Author Stats
  const authorHtml = `
    <span class="stat-item">
      <span class="filter-btn first-author-label" id="filter-first-author" onclick="toggleFilter('first-author')">*First Author</span>: ${firstAuthorCount}
    </span>
    <span class="divider">|</span>
    <span class="stat-item">
      <span class="filter-btn corresponding-author-label" id="filter-corresponding-author" onclick="toggleFilter('corresponding-author')">†Corresponding Author</span>: ${corrAuthorCount}
    </span>
  `;
  document.getElementById('pub-stats-container').innerHTML = authorHtml;

  // 2. Render Venue Stats (Sorted by count DESC)
  const sortedVenues = Object.keys(venueCounts).sort((a, b) => {
    return venueCounts[b].count - venueCounts[a].count;
  });

  let venuesHtml = '';
  sortedVenues.forEach(code => {
    const data = venueCounts[code];
    venuesHtml += `
      <span
        class="venue-btn"
        id="filter-venue-${code}"
        style="${getVenueButtonStyle(code)}"
        onclick="toggleFilter('venue', '${code}')"
      >
        ${data.name}: ${data.count}
      </span>
    `;
  });
  document.getElementById('venue-stats-container').innerHTML = venuesHtml;
  updateFilterUI();
  applyFilters();
}

function toggleFilter(filterType, value = null) {
  const isSameFilter = activeFilter.type === filterType && activeFilter.value === value;

  if (isSameFilter) {
    activeFilter.type = null;
    activeFilter.value = null;
  } else {
    activeFilter.type = filterType;
    activeFilter.value = value;
  }

  updateFilterUI();
  applyFilters();
}

function updateFilterUI() {
  const allFilterButtons = document.querySelectorAll(
    '#pub-stats-container .filter-btn, #venue-stats-container .venue-btn'
  );
  allFilterButtons.forEach(btn => btn.classList.remove('active'));

  if (activeFilter.type === 'first-author' || activeFilter.type === 'corresponding-author') {
    const authorBtn = document.getElementById('filter-' + activeFilter.type);
    if (authorBtn) {
      authorBtn.classList.add('active');
    }
    return;
  }

  if (activeFilter.type === 'venue' && activeFilter.value) {
    const venueBtn = document.getElementById('filter-venue-' + activeFilter.value);
    if (venueBtn) {
      venueBtn.classList.add('active');
    }
  }
}

function applyFilters() {
  const allRows = document.querySelectorAll('.publications ol.bibliography li .row');

  allRows.forEach(row => {
    let visible = true;

    if (activeFilter.type === 'first-author') {
      visible = row.classList.contains('first-author');
    } else if (activeFilter.type === 'corresponding-author') {
      visible = row.classList.contains('corresponding-author');
    } else if (activeFilter.type === 'venue' && activeFilter.value) {
      visible = row.classList.contains('venue-' + activeFilter.value);
    }

    row.classList.toggle('is-hidden-by-filter', !visible);
  });
}
</script>

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

{% bibliography %}

</div>
