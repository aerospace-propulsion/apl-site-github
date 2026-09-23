---
crumb: Research
title: Projects
permalink: /research/projects/
---

## Current Projects

<ul class="project-list">
{% for p in site.data.projects.current %}
  <li><span class="pname">{{ p.name }}</span><span class="pmeta">{{ p.sponsor }}, {{ p.period }}</span></li>
{% endfor %}
</ul>

## Past Projects

<ul class="project-list">
{% for p in site.data.projects.past %}
  <li><span class="pname">{{ p.name }}</span><span class="pmeta">{{ p.sponsor }}, {{ p.period }}</span></li>
{% endfor %}
</ul>
