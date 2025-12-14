---
layout: page
permalink: /publications/
title: Publications
description: Publications and Preprints. (*Equal contribution; †Corresponding author)
nav: true
nav_order: 3
---

<!-- _pages/publications.md -->

<style>
.pub-stats {
  font-size: 0.9em;
  margin-bottom: 1.5rem;
  color: var(--global-text-color-light);
}
.pub-stats .first-author-label {
  background-color: var(--global-first-author-bg-color);
  padding: 0.15em 0.5em;
  border-radius: 0.25rem;
}
.pub-stats .corresponding-author-label {
  background-color: var(--global-corresponding-author-bg-color);
  padding: 0.15em 0.5em;
  border-radius: 0.25rem;
}
</style>

<div class="pub-stats">
  <span class="first-author-label">First Author</span>: 10 &nbsp;|&nbsp;
  <span class="corresponding-author-label">Corresponding Author</span>: 2
</div>

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<div class="publications">

{% bibliography %}

</div>
