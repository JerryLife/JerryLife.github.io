---
layout: page
permalink: /service/
title: Service
description: Professional services in academic communities
nav: true
nav_order: 5
---

<style>
.service-page {
  margin-top: 1.25rem;
}
.service-section {
  margin-top: 2rem;
}
.service-section:first-child {
  margin-top: 0;
}
.service-section h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.85rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--global-divider-color);
}
.service-list {
  border-bottom: 1px solid var(--global-divider-color);
}
.service-row {
  display: grid;
  grid-template-columns: 4.5rem minmax(0, 1fr);
  column-gap: 1.25rem;
  padding: 0.85rem 0;
  border-top: 1px solid var(--global-divider-color);
}
.service-year {
  color: var(--global-theme-color);
  font-weight: 600;
  line-height: 1.7;
}
.service-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}
.service-item {
  display: inline-flex;
  align-items: baseline;
  gap: 0.35rem;
  border: 1px solid var(--global-divider-color);
  border-radius: 0.45rem;
  padding: 0.25rem 0.55rem;
  line-height: 1.35;
}
.service-role {
  color: var(--global-text-color-light);
  font-size: 0.9rem;
}
@media (max-width: 576px) {
  .service-row {
    grid-template-columns: 1fr;
    row-gap: 0.45rem;
  }
  .service-year {
    line-height: 1.3;
  }
}
</style>

<div class="service-page">
  {% for section in site.data.service %}
    <section class="service-section">
      <h3>{{ section.title }}</h3>
      <div class="service-list">
        {% for group in section.years %}
          <div class="service-row">
            <div class="service-year">{{ group.year }}</div>
            <div class="service-items">
              {% for item in group.items %}
                <span class="service-item">
                  <strong>{{ item.name }}</strong>
                  {% if item.role %}
                    <span class="service-role">{{ item.role }}</span>
                  {% endif %}
                </span>
              {% endfor %}
            </div>
          </div>
        {% endfor %}
      </div>
    </section>
  {% endfor %}
</div>
