---
layout: page
permalink: /teaching/
title: Teaching
description: Teaching experience and mentorship
nav: true
nav_order: 6
---

<style>
.teaching-page {
  margin-top: 1.25rem;
}
.teaching-section {
  margin-top: 2rem;
}
.teaching-section:first-child {
  margin-top: 0;
}
.teaching-section h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.85rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--global-divider-color);
}
.teaching-intro {
  color: var(--global-text-color-light);
  margin: -0.25rem 0 0.9rem;
}
.teaching-list {
  border-bottom: 1px solid var(--global-divider-color);
}
.teaching-row {
  display: grid;
  grid-template-columns: 8rem minmax(0, 1fr);
  column-gap: 1.25rem;
  padding: 0.95rem 0;
  border-top: 1px solid var(--global-divider-color);
}
.teaching-when {
  color: var(--global-theme-color);
  font-weight: 600;
  line-height: 1.45;
}
.teaching-title {
  font-size: 1.05rem;
  line-height: 1.35;
  margin: 0;
}
.teaching-title a {
  color: var(--global-text-color);
}
.teaching-title a:hover {
  color: var(--global-theme-color);
}
.teaching-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.35rem;
}
.teaching-tag {
  display: inline-flex;
  align-items: baseline;
  border: 1px solid var(--global-divider-color);
  border-radius: 0.45rem;
  color: var(--global-text-color-light);
  font-size: 0.9rem;
  line-height: 1.35;
  padding: 0.2rem 0.5rem;
}
.teaching-code {
  color: var(--global-theme-color);
  font-weight: 600;
}
.teaching-notes {
  color: var(--global-text-color-light);
  margin: 0.45rem 0 0;
  padding-left: 1rem;
}
.teaching-notes li {
  margin: 0.15rem 0;
}
@media (max-width: 576px) {
  .teaching-row {
    grid-template-columns: 1fr;
    row-gap: 0.45rem;
  }
}
</style>

<div class="teaching-page">
  <section class="teaching-section">
    <h3>Teaching Assistant</h3>
    <div class="teaching-list">
      {% for item in site.data.teaching.teaching_assistant %}
        <article class="teaching-row">
          <div class="teaching-when">{{ item.term }}</div>
          <div>
            <h4 class="teaching-title">{{ item.course }}</h4>
            <div class="teaching-meta">
              <span class="teaching-tag teaching-code">{{ item.code }}</span>
            </div>
          </div>
        </article>
      {% endfor %}
    </div>
  </section>

  <section class="teaching-section">
    <h3>Mentorship</h3>
    <p class="teaching-intro">It is my honor to work with many talented students and colleagues.</p>
    <div class="teaching-list">
      {% for person in site.data.teaching.mentorship %}
        <article class="teaching-row">
          <div class="teaching-when">{{ person.period }}</div>
          <div>
            <h4 class="teaching-title">
              {% if person.url %}
                <a href="{{ person.url }}" target="_blank" rel="noopener noreferrer">{{ person.name }}</a>
              {% else %}
                {{ person.name }}
              {% endif %}
            </h4>
            <div class="teaching-meta">
              <span class="teaching-tag">{{ person.role }}</span>
              <span class="teaching-tag">{{ person.institution }}</span>
            </div>
            {% if person.notes %}
              <ul class="teaching-notes">
                {% for note in person.notes %}
                  <li>{{ note }}</li>
                {% endfor %}
              </ul>
            {% endif %}
          </div>
        </article>
      {% endfor %}
    </div>
  </section>
</div>
