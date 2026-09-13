---
layout: page
permalink: /publications/
title: Publications
description: Selected work and a complete publication record.
nav: true
nav_order: 1
---

<div class="publications faculty-publications">
  <section class="selected-publications" aria-labelledby="selected-publications-title">
    <div class="publication-section-heading">
      <h2 id="selected-publications-title">Selected Publications</h2>
      <a href="#all-publications">View full list <span aria-hidden="true">↓</span></a>
    </div>
    {% bibliography --file selected.bib --template bib_selected --group_by none %}
  </section>

  <section id="all-publications" class="all-publications" aria-labelledby="all-publications-title">
    <h2 id="all-publications-title">All Publications</h2>
    <div class="publication-role-filter" role="group" aria-label="Filter publications by author role" hidden>
      <span class="publication-filter-label">Role</span>
      <button type="button" data-publication-role="all" aria-pressed="true">All</button>
      <button type="button" data-publication-role="first" aria-pressed="false">First / Co-first</button>
      <button type="button" data-publication-role="corresponding" aria-pressed="false">Corresponding</button>
      <button type="button" data-publication-role="other" aria-pressed="false">Other</button>
    </div>
    <p class="publication-author-note">* Equal contribution &nbsp; · &nbsp; † Corresponding author</p>
    <p class="publication-filter-status" aria-live="polite" aria-atomic="true"></p>

    <section id="publication-list" class="publication-collection" aria-labelledby="peer-reviewed-title">
      <h3 id="peer-reviewed-title" class="publication-collection-title">Peer-reviewed Publications</h3>
      {% bibliography --file publications.bib %}
      <p class="publication-empty" hidden>No peer-reviewed publications match this role.</p>
    </section>

    <section id="preprints" class="publication-collection" aria-labelledby="preprints-title">
      <h3 id="preprints-title" class="publication-collection-title">Preprints &amp; Ongoing Work</h3>
      {% bibliography --file preprints.bib %}
      <p class="publication-empty" hidden>No preprints match this role.</p>
    </section>
  </section>
</div>

<script src="{{ '/assets/js/publication-roles.js' | relative_url }}" defer></script>
