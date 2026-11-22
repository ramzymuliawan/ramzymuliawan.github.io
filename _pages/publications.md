---
layout: page
permalink: /publications/
title: Publications
nav: true
nav_order: 1
---

<!-- _pages/publications.md -->

<nav class="cv-contents" aria-label="Publication types">
  <ul class="list-inline">
    <li class="list-inline-item"><a href="#journal-articles">Journal articles</a></li>
    <li class="list-inline-item"><a href="#book-chapters">Book chapters</a></li>
    <li class="list-inline-item"><a href="#research-reports">Research reports</a></li>
    <li class="list-inline-item"><a href="#theses">Theses</a></li>
  </ul>
</nav>

<div class="publications">

<h2 id="journal-articles" class="mt-4">Journal articles</h2>

{% bibliography --query @article %}

<h2 id="book-chapters" class="mt-4">Book chapters</h2>

{% bibliography --query @incollection %}

<h2 id="research-reports" class="mt-4">Research reports</h2>

{% bibliography --query @techreport %}

<h2 id="theses" class="mt-4">Theses</h2>

{% bibliography --query @mastersthesis %}

</div>
