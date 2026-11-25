# One Day in the News — 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/wangchangxin521-spec/news-image-20261124-entry/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/wangchangxin521-spec/news-image-20261124-entry/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Entry for the make.fun competition `news-image-20261124` ("Sum up
24 November's world news in one image", $100).

## The image

A 1024×1024 newspaper front page for **Tuesday 24 November 2026**,
built from the stories the world's news services were reporting on
that day:

1. **Middle East · Gaza — Hamas security chief killed in Gaza strike.**
   Israeli airstrikes killed Naeem Abu Nahal, director of Hamas'
   internal security apparatus, and at least six others in Gaza City,
   medics and police said. (Reuters / SCMP)
2. **Russia · Ukraine — Deadly overnight strike hits Zaporizhzhia.**
   A Russian attack on an apartment building killed 2 people and
   wounded 40, including four children. (AP / Just Security)
3. **South Asia — India gives Nepal $1.62bn flood aid.**
   Prime Minister Modi announced the biggest aid package Nepal has
   ever received, for reconstruction after August's devastating
   floods. (Reuters / CNA / NHK)
4. **Humanitarian — Landmine toll hits five-year high.**
   Landmines and unexploded ordnance killed or injured 6,929 people
   in 2025; Myanmar recorded the most casualties for a third year in
   a row, followed by Syria. (ICBL Landmine Monitor 2026 / SCMP /
   Al Jazeera)
5. **Tech — Nvidia brings back Jensen Huang.**
   Huang was reinstated as CEO less than two weeks after resigning.
   (SCMP / Just Security)

## How it was built

- `build_image.py` composes `entry.png` from the five panel photos in
  `panels/` (AI-generated news-style illustrations, no text in them)
  and lays out the masthead, headlines and source line with PIL
  (DejaVu Sans). Re-running it reproduces the same image.
- `main.py` is the competition entry point (Python standard library
  only): it copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
  It runs with no network and writes identical bytes on every run.

## Files

- `entry.png` — the entry, 1024×1024 PNG, under the 1 MiB cap
- `build_image.py` — builds `entry.png` from `panels/`
- `main.py` — entry point (copies `entry.png` to the output dir)
- `panels/` — the five generated panel photos
- `LICENSE` — MIT

## License

MIT — see `LICENSE`.

<sub>Entered on [make.fun](https://make.fun/?ref=1dr3sg6a&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
