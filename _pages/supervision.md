---
layout: page
permalink: /group/
content_key: supervision
---
{% assign supervision = site.data.content.supervision %}
{% assign mentoring = site.data.content.mentoring %}
{% assign contact_email = site.data.content.profile.basics.email %}

<div class="faculty-supervision">
  <section class="faculty-supervision-intro" aria-labelledby="openings-heading">
    <h2 id="openings-heading">{{ page.copy.openings_heading | escape }}</h2>
    <div class="faculty-lead">{{ supervision.openings_summary | markdownify }}</div>
    <a class="faculty-text-link" href="#inquiry-heading">
      {{- page.copy.inquiry_heading | escape }}
      <span aria-hidden="true">→</span></a
    >
  </section>

  <section class="faculty-supervision-section" aria-labelledby="principles-heading">
    <h2 id="principles-heading">{{ page.copy.principles_heading | escape }}</h2>
    <ul class="faculty-supervision-principles">
      {% for principle in supervision.principles %}
        <li>{{ principle | escape }}</li>
      {% endfor %}
    </ul>
  </section>

  <section class="faculty-supervision-section" aria-labelledby="qualities-heading">
    <h2 id="qualities-heading">{{ page.copy.qualities_heading | escape }}</h2>
    {% if supervision.requirements.size > 0 %}
      <div class="faculty-requirements">
        <h3>{{ page.copy.requirements_heading | escape }}</h3>
        <ul>
          {% for requirement in supervision.requirements %}
            <li>{{ requirement | markdownify }}</li>
          {% endfor %}
        </ul>
      </div>
    {% endif %}
    <dl class="faculty-mentoring-values">
      {% for criterion in supervision.criteria %}
        <div>
          <dt>{{ criterion.title | escape }}</dt>
          <dd>{{ criterion.description | escape }}</dd>
        </div>
      {% endfor %}
    </dl>
  </section>

  <section class="faculty-supervision-section faculty-inquiry" aria-labelledby="inquiry-heading">
    <div class="faculty-inquiry-title">
      <h2 id="inquiry-heading">{{ page.copy.inquiry_heading | escape }}</h2>
      <a class="faculty-contact-email" href="mailto:{{ contact_email | escape }}?subject={{ supervision.contact.subject | url_encode }}">
        {{- contact_email | escape -}}
      </a>
    </div>
    <div class="faculty-inquiry-details">
      <div class="faculty-application-materials">{{ supervision.contact.introduction | markdownify }}</div>
      <p>{{ page.copy.questions_intro | escape }}</p>
      <ol>
        {% for question in supervision.contact.questions %}
          <li>{{ question | escape }}</li>
        {% endfor %}
      </ol>
    </div>
  </section>

  {% if mentoring.entries.size > 0 %}
    <section class="faculty-supervision-section" aria-labelledby="mentoring-heading">
      <div class="faculty-section-heading">
        <h2 id="mentoring-heading">{{ page.copy.mentoring_heading | escape }}</h2>
      </div>
      <p class="faculty-mentoring-intro">{{ supervision.mentoring_intro | escape }}</p>
      <ul class="faculty-mentee-list">
        {% for mentee in mentoring.entries %}
          <li class="faculty-mentee">
            <div class="faculty-mentee-period">{{ mentee.period | replace: ' - ', '–' | escape }}</div>
            <div class="faculty-mentee-details">
              <h3>
                {% if mentee.url != blank -%}
                  <a href="{{ mentee.url | escape }}">
                    {{- mentee.name | escape }}
                    <span aria-hidden="true">↗</span></a
                  >
                {%- else -%}
                  {{- mentee.name | escape -}}
                {%- endif %}
              </h3>
              <p class="faculty-mentee-meta">
                {{
                  mentee.role
                  | replace: 'Master Student', "Master's student"
                  | replace: 'Undergraduate Student', 'Undergraduate student'
                  | replace: 'Visiting Ph.D. Student', 'Visiting Ph.D. student'
                  | escape
                }}
                <span aria-hidden="true">·</span> {{ mentee.institution | replace: 'Zhe Jiang University', 'Zhejiang University' | escape }}
              </p>
              {% if mentee.topic != blank %}
                <p class="faculty-mentee-topic">{{ mentee.topic | escape }}</p>
              {% endif %}
              {% if mentee.outcome != blank %}
                <p class="faculty-mentee-outcome">
                  <span>{{ page.copy.outcome_label | escape }}</span> {{ mentee.outcome | escape }}
                </p>
              {% elsif mentee.notes.size > 0 %}
                {% for note in mentee.notes %}
                  <div class="faculty-mentee-outcome">{{ note | markdownify }}</div>
                {% endfor %}
              {% endif %}
            </div>
          </li>
        {% endfor %}
      </ul>
    </section>
  {% endif %}
</div>
