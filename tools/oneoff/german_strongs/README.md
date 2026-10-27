# One-off: German glosses + Strong's numbers (not part of the build)

These files document how the `german` and `strongs` fields in
`biblehebrew/data/hebrew_words.json` and `biblegreek/data/greek_words.json` were produced.
The fields are stored permanently in those JSONs; `tools/build_deck.py build` only reads them.
Nothing here runs during a build. Run from the repo root if you ever need to redo a step.

| File | Purpose |
|---|---|
| `glosses/de_he_<set>.txt`, `glosses/de_gr_<set>.txt` | Hand-written German glosses, `index|gloss`, index = position within the set (JSON order) |
| `applyde.py <project> <lang> <set_tag>` | Writes one gloss file into the JSON `german` field |
| `sh.py`, `sh2.py` | Hebrew: lemma matching against Strong's (exact pointed lemma, then consonants), scoring of candidates by English/POS |
| `sh_manual.txt` | Hebrew: manually resolved Strong's numbers (ambiguous/unmatched lemmas) |
| `sg.py`, `sg_manual.json` | Greek: lemma matching against Strong's; manual resolutions |
| `strong_he.json`, `strong_gr.json` | Final id -> Strong's maps that were written into the JSON `strongs` field |
| `render3.py <project> <lang> <id> <EN\|DE\|EN.wDE>` | Renders a back-side preview PNG into `<project>/out/` |
| `sources/StrongHebrewG.xml` | Open Scriptures Strong's Hebrew (OSIS, Public Domain), github.com/openscriptures/strongs @ 0acd2f2 |
| `sources/strongs-greek-dictionary.js` | Open Scriptures Strong's Greek (JSON, © Open Scriptures, CC-BY-SA; dictionary text Public Domain), same repo |

Reference lexica: Gesenius (Hebrew, public-domain editions), Strong's (Open Scriptures);
Greek cross-check against the German Strong's by Kautz (copyrighted, kept locally only in
`biblegreek/data/sources/`, git-ignored, not committed).

Strong's: Hebrew 748/756 matched. No Strong's entry exists for the prefixes/particles
וְ, הַ (2 cards), לְ, בְּ, כְּ, הֲ and כַּאֲשֶׁר (= כְּ + H834); their `strongs` field is „Präfix“
(כַּאֲשֶׁר: „Präfix + H834“), as decided by Michi. Greek 1023/1023 matched.
