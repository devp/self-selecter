# self-selecter

A web app for music lovers to curate their own musical catalog with a quirky,
visual, and fun interface.

## Setup

1. Serve static web pages from `src/`. e.g. `cd src; python -m http.server`

## The Plan...

- 2025-06-08: In `bootstrap-data`, create some ad-hoc generated CLI scripts with
  the idea and manually modifying and curating music with tags. (The YouTube
  corpus is lacking in useful tags, ultimately.) Though this isn't the ideal UI,
  I want to set up a fruitful interaction between curated tags and using the
  tags to self-select music.

- next: add support for Bandcamp, and standalone URLs (which will lack metadata,
  e.g. WBGO radio)

# About

## Goals

- Create a fast, simple interface for music discovery and curation
- Enable self-hosting and complete data control
- Provide platform independence from music streaming services
- Deliver a delightful, visual-first user experience

## Tech Stack

- HTML/CSS
- HTMX
- Static file web server

## Inspirations

This project draws inspiration from classic music discovery platforms:

- [Songza](https://en.wikipedia.org/wiki/Songza) - For its mood-based music
  selection
- [Muxtape](https://en.wikipedia.org/wiki/Muxtape) - For its minimalist playlist
  interface
- [8tracks](https://en.wikipedia.org/wiki/8tracks.com) - For its
  community-driven curation

The technical architecture is influenced by:

- [the self-hosting community](https://github.com/awesome-selfhosted/awesome-selfhosted)
- [Static site generators](https://en.wikipedia.org/wiki/Static_site_generator)
- [HTMX](https://htmx.org/)

The name is a little bit of a pun, and mostly a reference to my favorite ska
band: [The Selecter](https://en.wikipedia.org/wiki/The_Selecter).
