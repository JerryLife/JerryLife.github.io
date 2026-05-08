---
layout: page
permalink: /talk/
title: Talk
description: Invited talks, keynotes, and seminars.
nav: true
nav_order: 4
---

<style>
.talk-list {
  margin-top: 1.25rem;
}
.talk-item {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr);
  column-gap: 1.25rem;
  padding: 1.25rem 0;
  border-top: 1px solid var(--global-divider-color);
}
.talk-item:last-child {
  border-bottom: 1px solid var(--global-divider-color);
}
.talk-date {
  align-self: start;
  border: 1px solid var(--global-divider-color);
  border-radius: 0.5rem;
  padding: 0.45rem 0.35rem;
  text-align: center;
  line-height: 1.1;
}
.talk-date .month {
  display: block;
  color: var(--global-theme-color);
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
}
.talk-date .day {
  display: block;
  color: var(--global-text-color);
  font-size: 1.45rem;
  font-weight: 600;
  margin-top: 0.1rem;
}
.talk-date .year {
  display: block;
  color: var(--global-text-color-light);
  font-size: 0.78rem;
  margin-top: 0.1rem;
}
.talk-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.45rem;
  color: var(--global-text-color-light);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}
.talk-type {
  color: var(--global-theme-color);
  font-weight: 600;
}
.talk-title {
  font-size: 1.1rem;
  line-height: 1.35;
  margin: 0;
}
.talk-title a {
  color: var(--global-text-color);
}
.talk-title a:hover {
  color: var(--global-theme-color);
}
.talk-venue {
  color: var(--global-text-color-light);
  margin: 0.35rem 0 0;
}
.talk-host {
  margin-left: 0;
}
@media (max-width: 576px) {
  .talk-item {
    grid-template-columns: 1fr;
    row-gap: 0.65rem;
  }
  .talk-date {
    display: inline-flex;
    gap: 0.35rem;
    align-items: baseline;
    justify-content: flex-start;
    width: fit-content;
    padding: 0.35rem 0.55rem;
  }
  .talk-date .month,
  .talk-date .day,
  .talk-date .year {
    display: inline;
    margin: 0;
    font-size: 0.9rem;
  }
  .talk-host {
    display: block;
    margin-left: 0;
    margin-top: 0.15rem;
  }
}
</style>

<div class="talk-list">
  {% assign talks = site.data.talk | sort: "date" | reverse %}
  {% for talk in talks %}
    <article class="talk-item">
      <time class="talk-date" datetime="{{ talk.date | date: '%Y-%m-%d' }}">
        <span class="month">{{ talk.date | date: "%b" }}</span>
        <span class="day">{{ talk.date | date: "%d" }}</span>
        <span class="year">{{ talk.date | date: "%Y" }}</span>
      </time>
      <div class="talk-content">
        <div class="talk-meta">
          <span class="talk-type">{{ talk.type }}</span>
          <span>{{ talk.venue }}</span>
        </div>
        <h3 class="talk-title">
          {% if talk.url %}
            <a href="{{ talk.url }}" target="_blank" rel="noopener noreferrer">{{ talk.title }}</a>
          {% else %}
            {{ talk.title }}
          {% endif %}
        </h3>
        {% if talk.note %}
          <p class="talk-venue"><span class="talk-host">{{ talk.note }}</span></p>
        {% endif %}
      </div>
    </article>
  {% endfor %}
</div>
