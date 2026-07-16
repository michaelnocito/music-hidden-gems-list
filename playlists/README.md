# Hidden Gems — Apple Music playlists

Five 100-song playlists split from `gems.json`, ordered by era then
Gem Score. Import each CSV into Apple Music with a playlist transfer
tool (they read the Title/Artist/Album columns):

1. Go to **soundiiz.com** (or **tunemymusic.com**) and connect Apple Music.
2. Choose import from **file / text list**, upload one CSV.
3. Name the playlist, confirm the matches, save. Repeat per file.

| File | Era | Song breakdown |
| --- | --- | --- |
| `01-music-hidden-gems-1950s-1990s.csv` | 1950s-1990s | 1950s: 9, 1960s: 18, 1970s: 25, 1980s: 37, 1990s: 11 |
| `02-music-hidden-gems-1990s-2000s.csv` | 1990s-2000s | 1990s: 39, 2000s: 61 |
| `03-music-hidden-gems-2000s-2010s.csv` | 2000s-2010s | 2000s: 62, 2010s: 38 |
| `04-music-hidden-gems-2010s.csv` | 2010s | 2010s: 100 |
| `05-music-hidden-gems-2010s-2020s.csv` | 2010s-2020s | 2010s: 41, 2020s: 59 |

Regenerate with `python build_playlists.py`.