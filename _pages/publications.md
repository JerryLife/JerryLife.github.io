---
layout: page
permalink: /publications/
content_key: publications
---

<div class="publications faculty-publications">
  <section class="selected-publications" aria-labelledby="selected-publications-title">
    <div class="publication-section-heading">
      <h2 id="selected-publications-title">{{ page.copy.selected_heading | escape }}</h2>
      <a href="#all-publications">{{ page.copy.full_list_label | escape }} <span aria-hidden="true">↓</span></a>
    </div>
    {% bibliography --file selected.bib --template bib_selected --group_by none %}
  </section>

  <section id="all-publications" class="all-publications" aria-labelledby="all-publications-title">
    <h2 id="all-publications-title">{{ page.copy.all_heading | escape }}</h2>
    <div class="publication-role-filter" role="group" aria-label="Filter publications by author role" hidden>
      <span class="publication-filter-label">{{ page.copy.role_label | escape }}</span>
      <button type="button" data-publication-role="all" aria-pressed="true">{{ page.copy.all_role_label | escape }}</button>
      <button type="button" data-publication-role="first" aria-pressed="false">{{ page.copy.first_role_label | escape }}</button>
      <button type="button" data-publication-role="corresponding" aria-pressed="false">{{ page.copy.corresponding_role_label | escape }}</button>
      <button type="button" data-publication-role="other" aria-pressed="false">{{ page.copy.other_role_label | escape }}</button>
    </div>
    <p class="publication-author-note">{{ page.copy.author_note | escape }}</p>
    <p class="publication-filter-status" aria-live="polite" aria-atomic="true" data-reviewed-singular="{{ page.copy.reviewed_singular | escape }}" data-reviewed-plural="{{ page.copy.reviewed_plural | escape }}" data-preprint-singular="{{ page.copy.preprint_singular | escape }}" data-preprint-plural="{{ page.copy.preprint_plural | escape }}"></p>

    <section id="publication-list" class="publication-collection" aria-labelledby="peer-reviewed-title">
      <h3 id="peer-reviewed-title" class="publication-collection-title">{{ page.copy.reviewed_heading | escape }}</h3>
      {% bibliography --file publications.bib %}
      <p class="publication-empty" hidden>{{ page.copy.reviewed_empty | escape }}</p>
    </section>

    <section id="preprints" class="publication-collection" aria-labelledby="preprints-title">
      <h3 id="preprints-title" class="publication-collection-title">{{ page.copy.preprints_heading | escape }}</h3>
      {% bibliography --file preprints.bib %}
      <p class="publication-empty" hidden>{{ page.copy.preprints_empty | escape }}</p>
    </section>

  </section>
</div>

<script src="{{ '/assets/js/publication-roles.js' | relative_url }}" defer></script>
