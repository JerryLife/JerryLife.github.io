---
layout: page
permalink: /teaching/
title: Teaching
description: Courses and learning resources.
nav: false
published: false
nav_order: 3
---

{% assign course_sections = site.data.content.teaching.sections | where: 'kind', 'instructor' %}
{% assign course_count = 0 %}
{% for section in course_sections %}
  {% assign course_count = course_count | plus: section.entries.size %}
{% endfor %}

<div class="faculty-teaching">
  <section aria-labelledby="courses-heading">
    <h2 id="courses-heading">Courses</h2>
    {% if course_count > 0 %}
      {% for section in course_sections %}
        {% if section.entries.size > 0 %}
          {% if course_sections.size > 1 %}<h3>{{ section.title | escape }}</h3>{% endif %}
          <div class="faculty-course-list">
            {% for course in section.entries %}
              <article class="faculty-course">
                <p class="faculty-course-period">{{ course.term | escape }}</p>
                <div>
                  <h3>{% if course.code != blank %}<span class="faculty-course-code">{{ course.code | escape }}</span> — {% endif %}{{ course.course | escape }}</h3>
                  {% if course.institution != blank %}<p class="faculty-course-institution">{{ course.institution | escape }}</p>{% endif %}
                  {% if course.notes.size > 0 %}
                    <ul class="faculty-course-notes">
                      {% for note in course.notes %}<li>{{ note | markdownify }}</li>{% endfor %}
                    </ul>
                  {% endif %}
                  {% if course.url and course.url != '' %}<a class="faculty-text-link" href="{{ course.url | escape }}">Course website <span aria-hidden="true">↗</span></a>{% endif %}
                </div>
              </article>
            {% endfor %}
          </div>
        {% endif %}
      {% endfor %}
    {% else %}
      <div class="faculty-teaching-note">
        <p>Course information and learning resources will be posted here when teaching assignments are confirmed.</p>
        <p>For research interests, prospective student inquiries, and my mentoring experience, please visit <a href="{{ '/supervision/' | relative_url }}">Supervision <span aria-hidden="true">→</span></a>.</p>
      </div>
    {% endif %}
  </section>
</div>
