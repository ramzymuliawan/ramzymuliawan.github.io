---
layout: page
permalink: /publications/
title: Publications
description: My book chapter, research report, journal articles, and thesis, grouped by digital rights and other work.
nav: true
nav_order: 1
---

<!-- _pages/publications.md -->

<div class="publications">

<h2 class="mt-4">Digital rights</h2>

{% bibliography --query @*[category=digital-rights] %}

<h2 class="mt-4">Other work</h2>

{% bibliography --query @*[category=other] %}

</div>
