---
layout: page
permalink: /publications/
title: Publications
description: My journal articles, book chapter, research report, and thesis, newest first.
nav: true
nav_order: 1
---

<!-- _pages/publications.md -->

<div class="publications">

<h2 class="mt-4">Journal articles</h2>

{% bibliography --query @article %}

<h2 class="mt-4">Book chapters</h2>

{% bibliography --query @incollection %}

<h2 class="mt-4">Research reports</h2>

{% bibliography --query @techreport %}

<h2 class="mt-4">Theses</h2>

{% bibliography --query @mastersthesis %}

</div>
