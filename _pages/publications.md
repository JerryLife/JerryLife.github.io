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
}
.venue-stats .venue-btn:hover {
  opacity: 0.8;
}
.venue-stats .venue-btn.active {
  border-color: var(--global-theme-color);
}
/* Venue colors - distinct from first/corresponding author colors */
.venue-stats .venue-kdd { background-color: #7c3aed; color: white; }
.venue-stats .venue-emnlp { background-color: #0891b2; color: white; }
.venue-stats .venue-acl { background-color: #059669; color: white; }
.venue-stats .venue-neurips { background-color: #dc2626; color: white; }
.venue-stats .venue-iclr { background-color: #ea580c; color: white; }
.venue-stats .venue-sigmod { background-color: #2563eb; color: white; }
.venue-stats .venue-mlsys { background-color: #9333ea; color: white; }
.venue-stats .venue-aaai { background-color: #0284c7; color: white; }
.venue-stats .venue-arxiv { background-color: #6b7280; color: white; }
.venue-stats .venue-tbd { background-color: #4f46e5; color: white; }
.venue-stats .venue-tist { background-color: #0d9488; color: white; }
.venue-stats .venue-tkde { background-color: #be185d; color: white; }

/* Hide non-matching papers when filter is active */
.publications.filter-first-author ol.bibliography > li > .row:not(.first-author) {
  display: none;
}
.publications.filter-corresponding-author ol.bibliography > li > .row:not(.corresponding-author) {
  display: none;
}
/* Venue filter hiding rules */
.publications.filter-venue-kdd ol.bibliography > li > .row:not(.venue-kdd) { display: none; }
.publications.filter-venue-emnlp ol.bibliography > li > .row:not(.venue-emnlp) { display: none; }
.publications.filter-venue-acl ol.bibliography > li > .row:not(.venue-acl) { display: none; }
.publications.filter-venue-neurips ol.bibliography > li > .row:not(.venue-neurips) { display: none; }
.publications.filter-venue-iclr ol.bibliography > li > .row:not(.venue-iclr) { display: none; }
.publications.filter-venue-sigmod ol.bibliography > li > .row:not(.venue-sigmod) { display: none; }
.publications.filter-venue-mlsys ol.bibliography > li > .row:not(.venue-mlsys) { display: none; }
.publications.filter-venue-aaai ol.bibliography > li > .row:not(.venue-aaai) { display: none; }
.publications.filter-venue-arxiv ol.bibliography > li > .row:not(.venue-arxiv) { display: none; }
.publications.filter-venue-tbd ol.bibliography > li > .row:not(.venue-tbd) { display: none; }
.publications.filter-venue-tist ol.bibliography > li > .row:not(.venue-tist) { display: none; }
.publications.filter-venue-tkde ol.bibliography > li > .row:not(.venue-tkde) { display: none; }
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

const venueFilters = ['kdd', 'emnlp', 'acl', 'neurips', 'iclr', 'sigmod', 'mlsys', 'aaai', 'arxiv', 'tbd', 'tist', 'tkde'];

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
      <span class="venue-btn venue-${code}" id="filter-venue-${code}" onclick="toggleVenueFilter('${code}')">
        ${data.name}: ${data.count}
      </span>
    `;
    
    // Ensure we track this venue for filtering clear logic if it wasn't in our hardcoded list
    if (!venueFilters.includes(code)) {
      venueFilters.push(code);
    }
  });
  document.getElementById('venue-stats-container').innerHTML = venuesHtml;
}

function toggleFilter(filterType) {
  const pubContainer = document.querySelector('.publications');
  const btn = document.getElementById('filter-' + filterType);
  
  // If button doesn't exist (yet), return
  if (!btn) return;

  const otherFilterType = filterType === 'first-author' ? 'corresponding-author' : 'first-author';
  const otherBtn = document.getElementById('filter-' + otherFilterType);
  
  // Check if this filter is already active
  const isActive = pubContainer.classList.contains('filter-' + filterType);
  
  // Remove all filters (author and venue)
  pubContainer.classList.remove('filter-first-author', 'filter-corresponding-author');
  venueFilters.forEach(v => pubContainer.classList.remove('filter-venue-' + v));
  
  // Update UI states
  if (btn) btn.classList.remove('active');
  if (otherBtn) otherBtn.classList.remove('active');
  venueFilters.forEach(v => {
    const vBtn = document.getElementById('filter-venue-' + v);
    if (vBtn) vBtn.classList.remove('active');
  });
  
  // If wasn't active, apply this filter
  if (!isActive) {
    pubContainer.classList.add('filter-' + filterType);
    if (btn) btn.classList.add('active');
  }
}

function toggleVenueFilter(venue) {
  const pubContainer = document.querySelector('.publications');
  const btn = document.getElementById('filter-venue-' + venue);
  
  // Check if this filter is already active
  const isActive = pubContainer.classList.contains('filter-venue-' + venue);
  
  // Remove all filters (author and venue)
  pubContainer.classList.remove('filter-first-author', 'filter-corresponding-author');
  venueFilters.forEach(v => pubContainer.classList.remove('filter-venue-' + v));
  
  // Remove active class from all buttons
  const authBtn1 = document.getElementById('filter-first-author');
  const authBtn2 = document.getElementById('filter-corresponding-author');
  if (authBtn1) authBtn1.classList.remove('active');
  if (authBtn2) authBtn2.classList.remove('active');
  
  venueFilters.forEach(v => {
    const vBtn = document.getElementById('filter-venue-' + v);
    if (vBtn) vBtn.classList.remove('active');
  });
  
  // If wasn't active, apply this filter
  if (!isActive) {
    pubContainer.classList.add('filter-venue-' + venue);
    if (btn) btn.classList.add('active');
  }
}
</script>

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

{% bibliography %}

</div>
