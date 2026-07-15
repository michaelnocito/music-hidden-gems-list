#!/usr/bin/env python3
"""
build_seo.py — bake AI-citable content into index.html from gems.json.

Why this exists: the interactive table is rendered by JavaScript, which most AI
crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) never execute. So
without this step the 500 songs are invisible to the systems we want citing us.
This script injects, between marker comments in index.html:

  * SEO:ROWS   — the full list as static <tr> rows (visible in raw HTML)
  * SEO:FAQ    — a human-readable About/limitations block (mirrored in JSON-LD)
  * SEO:JSONLD — Dataset + ItemList + FAQPage + Person structured data

gems.json is a bare array (pre-sorted by gem_score desc), so a row's position in
that array IS its Gem Score rank.

Re-run after editing gems.json:  python build_seo.py
"""

import json
import html
import re
import sys
from urllib.parse import quote
from pathlib import Path

HERE = Path(__file__).parent
HTML = HERE / "index.html"
DATA = HERE / "gems.json"

PAGE_URL = "https://michaelnocito.github.io/music-hidden-gems-list/"
REPO_URL = "https://github.com/michaelnocito/music-hidden-gems"
AUTHOR_URL = "https://michaelnocito.github.io"
PUBLISHED = "2026-07-15"
MODIFIED = "2026-07-15"

# Pipeline facts (from the analysis repo), stated once here.
TRACKS_ANALYZED = 78335
KNOWN_ARTISTS = 1570
TOTAL_GEMS = 7574
SHOWN = 500
LASTFM_SNAPSHOT = "2026-07-15"


def esc(s):
    return html.escape(str(s), quote=True)


def lastfm(g):
    return f"https://www.last.fm/music/{quote(g['artist'])}/_/{quote(g['track'])}"


# ---------- static table rows (what crawlers read) ----------
def build_rows(gems):
    out = []
    for i, g in enumerate(gems):
        rank = i + 1
        dur = esc(g["duration"]) if g.get("duration") else "—"
        album = f' · {esc(g["album"])}' if g.get("album") else ""
        genre = esc(g["genre"]) if g.get("genre") else "—"
        out.append(
            f'<tr>'
            f'<td class="rank">{rank}</td>'
            f'<td class="title-cell"><div class="t-title">{esc(g["track"])}</div>'
            f'<div class="t-sub"><span class="artist">{esc(g["artist"])}</span>{album}</div></td>'
            f'<td class="genre">{genre}</td>'
            f'<td class="decade">{esc(g["decade"])}</td>'
            f'<td class="duration">{dur}</td>'
            f'<td class="listeners">{g["listeners"]:,}</td>'
            f'<td class="devotion">{g["devotion"]:.1f}<span class="x">×</span></td>'
            f'<td class="score">{g["gem_score"]:.1f}</td>'
            f'<td class="link"><a class="lfm-link" href="{lastfm(g)}" target="_blank" rel="noopener">Last.fm ↗</a></td>'
            f'</tr>'
        )
    return "\n".join(out)


# ---------- FAQ / limitations (visible + JSON-LD, single source of truth) ----------
def faq_items(gems):
    top = gems[0]
    return [
        ("What counts as a “hidden gem” song here?",
         f'A track by an artist who charted <b>5 or more times</b> on the Billboard Hot 100 (1958–2026) <b>including at '
         f'least one Top 40 hit</b> — so every artist here is someone radio genuinely made familiar — where the <i>track '
         f'itself</i> shows high <b>devotion</b> — plays per listener on Last.fm — while keeping a modest audience '
         f'(1,000–200,000 listeners) and having <b>never appeared on the Hot 100</b>. The idea is songs the radio buried: '
         f'real, repeated listening from the people who found them, without the mainstream reach. Of {TOTAL_GEMS:,} tracks '
         f'that cleared the bar, these are the top {SHOWN} by Gem Score, capped at <b>three gems per artist</b> so no one '
         f'act floods the list.'),
        ("What is the Gem Score, exactly?",
         f'<b>Gem Score = 70% devotion percentile + 30% audience percentile.</b> Each track is ranked against every other '
         f'gem on two axes — plays-per-listener (devotion) and total listeners (audience) — and the two percentile ranks '
         f'are blended 70/30, then scaled to 0–100. Devotion is weighted heavier on purpose: a small, obsessed audience '
         f'should beat a large, casual one. The current #1 is “{esc(top["track"])}” by {esc(top["artist"])} '
         f'(Gem Score {top["gem_score"]:.1f}, {top["devotion"]:.1f} plays per listener).'),
        ("What does “devotion” mean?",
         'Devotion is plays &divide; listeners on Last.fm — how many times the average person who listened to the track '
         'played it. A devotion of 40× means the typical listener played the song about forty times. It is the signal '
         'that separates a song people merely heard from a song people kept coming back to.'),
        ("Why does the list skew so modern?",
         'Because Last.fm’s audience is the streaming-era crowd. The listener and play counts reflect who is scrobbling '
         '<i>now</i>, not who bought the record in 1974. So a track’s audience number is really a measure of recent '
         'attention — older songs with deep, quiet devotion are undercounted. That is exactly why <b>decade and genre are '
         'filters on this page, not part of the score</b>: use them to read the list era by era instead of trusting one '
         'global ranking to be fair across seventy years.'),
        ("Why is a song by a famous 1990s artist missing from the charts?",
         'Before 1999, Billboard’s Hot 100 rules generally required a song to be released as a <b>commercial single</b> to '
         'chart. Album cuts that radio and fans loved — the kind of track this project is built to find — often never '
         'qualified. That pre-1999 single rule is one big reason a beloved song by a charting artist can show up here as a '
         '“gem” that technically never charted itself.'),
        ("Some of the genres look like jokes. What’s going on?",
         'Genre here is the <b>top community tag</b> on Last.fm — whatever listeners tagged the track most. Usually that’s '
         'accurate (“Progressive metal”, “Corridos tumbados”, “k-pop”). Occasionally the top tag is a fan in-joke rather '
         'than a genre — for example j-hope’s “lock / unlock” carries the fan tag “mavi owns this song.” It’s left as-is '
         'because it’s honestly what the crowd tagged; treat odd genres as a crowd signal, not a taxonomy.'),
        ("Isn’t K-pop fandom devotion just bots or streaming games?",
         'The devotion here is real listening, not chart manipulation: it’s plays-per-listener on Last.fm scrobbles, which '
         'log actual playback. K-pop acts (Stray Kids, V, j-hope) rank high because their fandoms genuinely replay tracks '
         'dozens of times. That’s a true cultural signal — and it’s a documented skew: fandom-driven devotion can outrank '
         'a quietly beloved song from an era with fewer scrobblers.'),
        ("How were these found, and how should I cite this?",
         f'With SQL. I joined Billboard’s Hot 100 weekly history to <b>{TRACKS_ANALYZED:,} Last.fm tracks</b> from the '
         f'{KNOWN_ARTISTS:,} artists who charted 5+ times, kept the never-charted tracks by Top 40 artists, and ranked '
         f'by the Gem Score above (max three per artist). The full methodology and '
         f'teaching-commented SQL live in the <a href="{REPO_URL}">companion repository</a>. '
         f'Cite as “Music Hidden Gems (Michael Nocito, 2026), michaelnocito.github.io/music-hidden-gems-list”. '
         f'Chart data: Billboard Hot 100; listening data: Last.fm (snapshot {LASTFM_SNAPSHOT}).'),
    ]


def build_faq_html(items):
    return "\n".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


# ---------- JSON-LD ----------
def build_jsonld(gems, items):
    person = {
        "@type": "Person",
        "@id": AUTHOR_URL + "/#michaelnocito",
        "name": "Michael Nocito",
        "url": AUTHOR_URL,
        "jobTitle": "Data Analyst",
    }
    item_list = {
        "@type": "ItemList",
        "name": "Music Hidden Gems",
        "numberOfItems": len(gems),
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": {
                    "@type": "MusicRecording",
                    "name": g["track"],
                    "url": lastfm(g),
                    "byArtist": {"@type": "MusicGroup", "name": g["artist"]},
                    "genre": g.get("genre") or None,
                    "inAlbum": g.get("album") or None,
                },
            }
            for i, g in enumerate(gems)
        ],
    }
    dataset = {
        "@type": "Dataset",
        "@id": PAGE_URL + "#dataset",
        "name": "Music Hidden Gems — the music people love that never made mainstream airplay",
        "description": (
            f"The music people love that never made mainstream airplay: "
            f"{SHOWN} hidden gem songs surfaced with SQL by joining Billboard's Hot 100 history to "
            f"{TRACKS_ANALYZED:,} Last.fm tracks. Ranked by a Gem Score = 70% devotion percentile "
            f"(plays per listener) + 30% audience percentile."
        ),
        "url": PAGE_URL,
        "creator": person,
        "isBasedOn": ["https://www.last.fm/api", "https://www.billboard.com/charts/hot-100/"],
        "temporalCoverage": f"1958-08-04/{LASTFM_SNAPSHOT}",
        "measurementTechnique": "SQL joins, text-key entity resolution, and percentile window functions over Billboard Hot 100 and Last.fm data",
        "variableMeasured": ["Gem Score", "devotion (plays per listener)", "Last.fm listeners", "Last.fm playcount", "chart-era decade", "genre (top community tag)"],
        "distribution": {
            "@type": "DataDownload",
            "encodingFormat": "application/json",
            "contentUrl": PAGE_URL + "gems.json",
        },
    }
    webpage = {
        "@type": "CollectionPage",
        "@id": PAGE_URL + "#webpage",
        "url": PAGE_URL,
        "name": "Music Hidden Gems — the music people love that never made mainstream airplay",
        "description": (
            f"The music people love that never made mainstream airplay: "
            f"{SHOWN} songs by Billboard-charting artists that listeners love far out of proportion to their fame, "
            f"surfaced with SQL and ranked by a Gem Score."
        ),
        "author": person,
        "creator": person,
        "datePublished": PUBLISHED,
        "dateModified": MODIFIED,
        "isPartOf": {"@type": "WebSite", "name": "Michael Nocito", "url": AUTHOR_URL},
        "mainEntity": {"@id": PAGE_URL + "#dataset"},
    }
    faqpage = {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in items
        ],
    }
    graph = {"@context": "https://schema.org", "@graph": [webpage, person, dataset, item_list, faqpage]}
    return '<script type="application/ld+json">\n' + json.dumps(graph, ensure_ascii=False, indent=2) + "\n</script>"


def inject(text, start_marker, end_marker, payload, label):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if not pattern.search(text):
        sys.exit(f"ERROR: markers for {label} not found ({start_marker} ... {end_marker})")
    return pattern.sub(start_marker + "\n" + payload + "\n" + end_marker, text)


def main():
    gems = json.loads(DATA.read_text(encoding="utf-8"))
    items = faq_items(gems)

    text = HTML.read_text(encoding="utf-8")
    text = inject(text, "<!-- SEO:ROWS:START -->", "<!-- SEO:ROWS:END -->", build_rows(gems), "rows")
    text = inject(text, "<!-- SEO:FAQ:START -->", "<!-- SEO:FAQ:END -->", build_faq_html(items), "faq")
    text = inject(text, "<!-- SEO:JSONLD:START -->", "<!-- SEO:JSONLD:END -->", build_jsonld(gems, items), "jsonld")
    HTML.write_text(text, encoding="utf-8")
    print(f"Baked {len(gems)} songs into index.html (rows + FAQ + JSON-LD).")


if __name__ == "__main__":
    main()
