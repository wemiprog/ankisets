# ankisets

Layout: `tools/build_deck.py` (shared builder), `tools/template/` (front/back HTML + CSS, `__DIR__` = rtl/ltr), `fonts/` (bundled into decks), one folder per project (`biblehebrew/`, later `biblegreek/`) with `data/<lang>_words.json`, `media/<lang>/`, `out/`, legacy `config/`, `input/` (source videos, git-ignored).
Setup: `python -m venv .venv && .venv/bin/pip install -r requirements.txt` (extract also needs ffmpeg).

## biblehebrew
Anki decks (Biblical Hebrew vocab) built from app videos.
Data: `biblehebrew/data/hebrew_words.json` (source of truth, 756 words, sorted by occurrences desc; id, word, english, occurrences, rank, pos, freq, image, audio, src). Media cached in `biblehebrew/media/hebrew/`; font `fonts/_EzraSIL.ttf`.
Build (≈1 s, no videos): `python tools/build_deck.py build biblehebrew [--contact]` -> `biblehebrew/out/biblehebrew_{250plus,120plus,70plus,50plus,all}.apkg`.
New words: add entries to the JSON, then `python tools/build_deck.py extract biblehebrew` cuts only missing images/audio from `biblehebrew/input/` videos. `init biblehebrew` regenerates the JSON from legacy `config/` CSVs.
Decks: BibleHebrew::<freq>::<POS>, tags pos::, freq::, lang::.
