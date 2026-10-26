# ankisets

## biblehebrew
Anki decks (Biblical Hebrew vocab) built from app videos.
Data: `data/hebrew_words.json` (source of truth, 756 words, sorted by occurrences desc; id, word, english, occurrences, rank, pos, freq, image, audio, src). Media cached in `media/hebrew/` (incl. Ezra SIL font).
Build (≈1 s, no videos): `python build_deck.py build [--lang hebrew] [--contact]` -> `out/biblehebrew_{250plus,120plus,70plus,50plus,all}.apkg`.
New words: add entries to the JSON, then `python build_deck.py extract` cuts only missing images/audio from the videos (needs ffmpeg; videos not included). `init` regenerates the JSON from legacy `config/` CSVs (one-time).
Decks: BibleHebrew::<freq>::<POS>, tags pos::, freq::, lang::.
