# Music Hidden Gems — the list site

Browsable front-end for the 500 top hidden gem songs found in the
[music-hidden-gems](https://github.com/michaelnocito/music-hidden-gems)
SQL analysis. Companion to
[steam-hidden-gems-list](https://github.com/michaelnocito/steam-hidden-gems-list)
and
[streaming-hidden-gems-list](https://github.com/michaelnocito/streaming-hidden-gems-list),
same format and design.

**Live:** https://michaelnocito.github.io/music-hidden-gems-list/

## What it is

- `index.html` — the whole site (no framework, no build server). A sortable,
  filterable table of the top 500 gems.
- `gems.json` — the data, exported straight from the analysis database
  (Billboard Hot 100 joined to Last.fm, snapshot 2026-07-14). A bare array,
  pre-sorted by Gem Score descending.
- `build_seo.py` — bakes the 500 rows, an About/limitations FAQ, and
  `schema.org` JSON-LD into `index.html` as static HTML so AI crawlers (which
  don't run the JavaScript table) can read and cite the list. Re-run after
  editing `gems.json`: `python build_seo.py`.

## What a gem is

A track by an artist who charted **5+ times** on the Billboard Hot 100
(1958–2026), where the track itself shows high **devotion** — plays per
listener on Last.fm — while keeping a modest audience. Songs the radio buried.

**Gem Score = 70% devotion percentile + 30% audience percentile**, scaled to
0–100. Devotion is weighted heavier on purpose: a small, obsessed audience
beats a large, casual one.

## Known limits (stated on the page)

- The list skews modern because Last.fm's audience is the streaming-era crowd —
  so **decade and genre are filters, not part of the score.**
- Genre is the top community tag; occasionally that tag is a fan in-joke, not a
  genre.
- The pre-1999 Billboard commercial-single rule is why some beloved songs by
  charting artists never charted themselves.
- K-pop fandom devotion is real (scrobbled) listening, and a documented skew.

## How the list was made

The methodology, the teaching-commented SQL, the artist-name entity resolution,
and the text-join match-rate story live in the analysis repo:
https://github.com/michaelnocito/music-hidden-gems
