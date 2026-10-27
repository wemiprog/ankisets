# ankisets

Layout: `tools/build_deck.py` (shared builder), `tools/template/` (front/back HTML + CSS, `__DIR__` = rtl/ltr), `fonts/` (bundled into decks), one folder per project (`biblehebrew/`, `biblegreek/`) with `data/<lang>_words.json`, `media/<lang>/`, `out/`, legacy `config/`, `input/` (source videos, git-ignored).
Setup: `python -m venv .venv && .venv/bin/pip install -r requirements.txt` (extract also needs ffmpeg).

## biblehebrew
Anki decks (Biblical Hebrew vocab) built from app videos.
Data: `biblehebrew/data/hebrew_words.json` (source of truth, 756 words, sorted by occurrences desc; id, word, english, occurrences, rank, pos, freq, image, audio, src). Media cached in `biblehebrew/media/hebrew/`; font `fonts/_EzraSIL.ttf`.
Build (a few s, no videos): `python tools/build_deck.py build biblehebrew [--contact]` -> `biblehebrew/biblehebrew_{250plus,120plus,70plus,50plus,all}.{EN,DE,EN.wDE}.apkg`.
New words: add entries to the JSON, then `python tools/build_deck.py extract biblehebrew` cuts only missing images/audio from `biblehebrew/input/` videos. `init biblehebrew` regenerates the JSON from legacy `config/` CSVs.
Decks: BibleHebrew::<freq>::<POS>, tags pos::, freq::, lang::.

## biblegreek
Same layout and builder: `biblegreek/data/greek_words.json` (1023 words), media in `biblegreek/media/greek/`, font `fonts/_GentiumPlus.ttf`.
Build: `python tools/build_deck.py build biblegreek` -> `biblegreek/biblegreek_{50plus,20plus,13plus,10plus,all}.{EN,DE,EN.wDE}.apkg`.

## Variants and deck preset
- `.EN` English answer; `.DE` German answer + English small (decks `Bibel-Hebräisch` / `Bibel-Griechisch`, German subdeck names); `.EN.wDE` English answer + German small.
- German glosses (`german`) and Strong's numbers (`strongs`) are stored in the JSON; the build only reads them (one-off tools: `tools/oneoff/german_strongs/`).
- Every package carries its own deck preset (`tools/template/deck_preset.json`, named after the top deck): new cards in ascending position (= frequency order across all subdecks), order gathered, 5 new cards/day, learning/relearning steps 10m, desired retention 0.90, no FSRS parameters; everything else Anki default.

## Import / Import-Hinweis
**EN:** In Anki (desktop 23.10+, AnkiMobile 23.10+, AnkiDroid 2.17+) import the `.apkg` and **tick “Import any deck presets”** (it is off by default); leave “Import any learning progress” off. FSRS cannot be switched on by a deck file: **enable FSRS once** under Deck Options → FSRS (it applies to the whole collection). After a few hundred reviews, press **Optimize** in the FSRS section.

**DE:** In Anki (Desktop 23.10+, AnkiMobile 23.10+, AnkiDroid 2.17+) die `.apkg` importieren und **„Import any deck presets“ / „Stapel-Voreinstellungen importieren“ ankreuzen** (standardmässig aus); „Lernfortschritt importieren“ aus lassen. FSRS lässt sich nicht über die Datei einschalten: **FSRS einmalig aktivieren** unter Stapeloptionen → FSRS (gilt für die ganze Sammlung). Nach einigen hundert Wiederholungen im FSRS-Abschnitt auf **Optimieren** drücken.
