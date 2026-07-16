#!/usr/bin/env python3
"""
build_playlists.py — split gems.json into 5 playlists of 100, grouped by era.

The 500 gems are ordered by Artist Era (chronological) then Gem Score
(best first), then chunked into five 100-song playlists. Because the eras
are lopsided (the 2010s alone is 179 songs) a couple of playlists straddle
two adjacent eras, but each is exactly 100 songs and the blocks stay in
chronological order.

Each file is the minimal Title/Artist/Album CSV that playlist importers
(Soundiiz, TuneMyMusic, Playlisty) accept for Apple Music / Spotify.

Re-run after gems.json changes:  python build_playlists.py
"""

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "playlists"
OUT.mkdir(exist_ok=True)

ERA_ORDER = ["1950s", "1960s", "1970s", "1980s",
             "1990s", "2000s", "2010s", "2020s"]
rank = {d: i for i, d in enumerate(ERA_ORDER)}

gems = json.loads((HERE / "gems.json").read_text(encoding="utf-8"))

# Chronological by era, best Gem Score first within each era.
pool = sorted(gems, key=lambda g: (rank.get(g["decade"], 99), -g["gem_score"]))

index_rows = []
for i in range(5):
    chunk = pool[i * 100:(i + 1) * 100]
    counts = Counter(x["decade"] for x in chunk)
    spans = [d for d in ERA_ORDER if d in counts]
    label = spans[0] if len(spans) == 1 else f"{spans[0]}-{spans[-1]}"
    fname = f"{i + 1:02d}-music-hidden-gems-{label}.csv"

    with open(OUT / fname, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Title", "Artist", "Album"])
        for g in chunk:
            w.writerow([g["track"], g["artist"], g["album"]])

    breakdown = ", ".join(f"{d}: {counts[d]}" for d in spans)
    index_rows.append((fname, label, breakdown))
    print(f"wrote {fname}  ({len(chunk)} songs | {breakdown})")

# A small index so the folder explains itself.
lines = [
    "# Hidden Gems — Apple Music playlists",
    "",
    "Five 100-song playlists split from `gems.json`, ordered by era then",
    "Gem Score. Import each CSV into Apple Music with a playlist transfer",
    "tool (they read the Title/Artist/Album columns):",
    "",
    "1. Go to **soundiiz.com** (or **tunemymusic.com**) and connect Apple Music.",
    "2. Choose import from **file / text list**, upload one CSV.",
    "3. Name the playlist, confirm the matches, save. Repeat per file.",
    "",
    "| File | Era | Song breakdown |",
    "| --- | --- | --- |",
]
for fname, label, breakdown in index_rows:
    lines.append(f"| `{fname}` | {label} | {breakdown} |")
lines.append("")
lines.append("Regenerate with `python build_playlists.py`.")
(OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
print(f"wrote playlists/README.md")
