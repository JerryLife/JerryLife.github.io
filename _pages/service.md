---
layout: page
permalink: /service/
title: Service
description: Professional services in academic communities
nav: true
nav_order: 4
---

{% assign service_sections = site.data.generated.content.service.groups %}

<div class="service-page">
  {% if service_sections and service_sections.size > 0 %}
    {% for section in service_sections %}
      {% assign repeated_role = '' %}
      {% if section.kind == 'conference-reviewers' or section.kind == 'journal-reviewers' %}
        {% assign repeated_role = 'Reviewer' %}
      {% elsif section.kind == 'tutorial' %}
        {% assign repeated_role = 'Tutorial Speaker' %}
      {% endif %}
      <section class="service-section" aria-labelledby="service-{{ section.kind }}">
        <h2 id="service-{{ section.kind }}">{{ section.title | escape }}</h2>
        <dl class="service-list">
          {% for group in section.years %}
            <div class="service-row">
              <dt class="service-year">{{ group.year | escape }}</dt>
              <dd>
                <ul class="service-items" role="list">
                  {% for item in group.items %}
                    <li class="service-item">
                      {% if item.url and item.url != '' %}
                        <a class="service-name" href="{{ item.url | escape }}" target="_blank" rel="noopener noreferrer">{{ item.name | escape }}</a>
                      {% else %}
                        <span class="service-name">{{ item.name | escape }}</span>
                      {% endif %}
                      {% if item.role != blank and item.role != repeated_role %}
                        <span class="service-role">— {{ item.role | escape }}</span>
                      {% endif %}
                    </li>
                  {% endfor %}
                </ul>
              </dd>
            </div>
          {% endfor %}
        </dl>
      </section>
    {% endfor %}
  {% endif %}
</div>
