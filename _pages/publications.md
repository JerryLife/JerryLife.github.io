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
  margin-bottom: 1.5rem;
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
/* Hide non-matching papers when filter is active */
.publications.filter-first-author ol.bibliography > li > .row:not(.first-author) {
  display: none;
}
.publications.filter-corresponding-author ol.bibliography > li > .row:not(.corresponding-author) {
  display: none;
}
</style>

<div class="pub-stats">
  <span class="stat-item">
    <span class="filter-btn first-author-label" id="filter-first-author" onclick="toggleFilter('first-author')">*First Author</span>: 10
  </span>
  <span class="divider">|</span>
  <span class="stat-item">
    <span class="filter-btn corresponding-author-label" id="filter-corresponding-author" onclick="toggleFilter('corresponding-author')">†Corresponding Author</span>: 2
  </span>
</div>

<script>
function toggleFilter(filterType) {
  const pubContainer = document.querySelector('.publications');
  const btn = document.getElementById('filter-' + filterType);
  const otherFilterType = filterType === 'first-author' ? 'corresponding-author' : 'first-author';
  const otherBtn = document.getElementById('filter-' + otherFilterType);
  
  // Check if this filter is already active
  const isActive = pubContainer.classList.contains('filter-' + filterType);
  
  // Remove all filters
  pubContainer.classList.remove('filter-first-author', 'filter-corresponding-author');
  btn.classList.remove('active');
  otherBtn.classList.remove('active');
  
  // If wasn't active, apply this filter
  if (!isActive) {
    pubContainer.classList.add('filter-' + filterType);
    btn.classList.add('active');
  }
}
</script>

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

{% bibliography %}

</div>
