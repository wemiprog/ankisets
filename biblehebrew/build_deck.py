#!/usr/bin/env python3
"""Data-driven Anki deck builder.
  Single:   python build_deck.py config/<video>.json            -> cfg["output"]
  Combined: python build_deck.py --all [config_dir] [-o out.apkg] -> every *.json in one .apkg
Config keys: root (e.g. BibleHebrew/BibleGreek), lang, dir (rtl/ltr), pos (tag), pos_label (deck, e.g. Noun),
 freq (label, e.g. 250+), freq_tag (tag-safe, e.g. 250plus), video, output, crop[x,y,w,h], pad, cards (CSV).
Deck: <root>::<freq>::<pos_label>. Deck IDs derive from the deck name (stable).
CSV: id,word,english,number,frame_t,audio_start,audio_end (optional pos,freq override tags)."""
import csv, glob, hashlib, json, os, subprocess, sys, genanki
from PIL import Image
BASE = os.path.dirname(os.path.abspath(__file__)); os.chdir(BASE)

def stable_id(s): return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16) | 1 << 30


HOM = '<script>document.querySelectorAll(".word,.en").forEach(function(e){if(!e.dataset.h){e.dataset.h=1;e.innerHTML=e.innerHTML.replace(/([\u00b9\u00b2\u00b3])/g,"<span class=hom>$1</span>")}})</script>'
FRONT = '<div class="box wordbox"><div class="word">{{Word}}</div><div class="play">{{Audio}}</div></div>' + HOM
BACK = ('<div class="box wordbox"><div class="word">{{Word}}</div><div class="play">{{Audio}}</div></div>'
        '<div id="answer"></div><div class="pic">{{Image}}</div>'
        '<div class="box enbox"><div class="en">{{English}}</div></div>'
        '{{#Occurrences}}<div class="occ">Occurrences: <b>{{Occurrences}}</b></div>{{/Occurrences}}' + HOM)
CSS = """.card{font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;text-align:center;background:#fff;color:#1d1d1f;margin:0;padding:14px}
.box{position:relative;max-width:560px;margin:8px auto 14px;background:#e6e6e8;border-radius:18px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.wordbox{padding:26px 64px;min-height:56px;display:flex;align-items:center;justify-content:center}
.word{font-size:2.2em;line-height:1.35;direction:__DIR__;font-family:'SBL Hebrew','Ezra SIL','Taamey Frank CLM','Times New Roman',serif}
.hom{font-family:-apple-system,sans-serif;font-size:.5em;font-weight:700;color:#c62828;vertical-align:super;unicode-bidi:isolate;margin:0 3px}
.play{position:absolute;top:10px;right:10px}
.play .replay-button,.play .soundLink,.play a{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.18);text-decoration:none;margin:0}
.play .replay-button svg,.play .soundLink svg,.play img{width:22px;height:22px}
.play .replay-button svg circle{fill:transparent;stroke:none}
.play .replay-button svg path{fill:#555;stroke:none}
.pic img{max-width:100%;max-height:45vh;border-radius:10px}
.enbox{padding:16px 20px}
.en{font-size:1.25em;line-height:1.4}
.occ{font-size:.85em;color:#2e7d32;margin-top:4px}
.occ b{font-weight:700}
.nightMode .card,.night_mode .card,.card.nightMode,.card.night_mode{background:#1e1e1e;color:#eee}
.nightMode .box,.night_mode .box{background:#333336;box-shadow:none}
.nightMode .play a,.night_mode .play a,.nightMode .play .replay-button,.night_mode .play .replay-button{background:#4a4a4e}
.nightMode .play .replay-button svg path,.night_mode .play .replay-button svg path{fill:#ddd}
.nightMode .occ,.night_mode .occ{color:#81c784}
.nightMode .hom,.night_mode .hom{color:#ef6c6c}
@media (max-width:480px){.wordbox{padding:22px 54px}.word{font-size:1.9em}.en{font-size:1.1em}}"""

_models = {}
def model_for(lang, direction):
    if lang not in _models:
        _models[lang] = genanki.Model(stable_id("model:" + lang), f"Vocab ({lang})",
          fields=[{"name": n} for n in ["Word", "Audio", "Image", "English", "Occurrences"]],
          templates=[{"name": "Word → Meaning",
            "qfmt": FRONT, "afmt": BACK}], css=CSS.replace("__DIR__", direction))
    return _models[lang]

def build(cfg_path):
    cfg = json.load(open(cfg_path, encoding="utf-8")); lang = cfg["lang"]
    name = f"{cfg['root']}::{cfg['freq']}::{cfg['pos_label']}"
    deck = genanki.Deck(stable_id("deck:" + name), name)
    media = f"media/{lang}"; os.makedirs(media, exist_ok=True)
    x, y, w, h = cfg["crop"]; pad = cfg.get("pad", 0.15); m = model_for(lang, cfg.get("dir", "ltr"))
    files, imgs = [], []
    for r in csv.DictReader(open(cfg["cards"], encoding="utf-8")):
        img = f"{media}/{r['id']}.jpg"; aud = f"{media}/{r['id']}.mp3"
        subprocess.run(["ffmpeg","-v","error","-y","-ss",r["frame_t"],"-i",cfg["video"],"-frames:v","1",
            "-vf",f"crop={w}:{h}:{x}:{y}","-q:v","3",img], check=True)
        s = max(0, float(r["audio_start"]) - pad); d = float(r["audio_end"]) + pad - s
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{s:.2f}","-t",f"{d:.2f}","-i",cfg["video"],"-vn",
            "-af","afade=t=in:d=0.05","-ac","1","-b:a","96k",aud], check=True)
        tags = [f"pos::{r.get('pos') or cfg['pos']}", f"freq::{r.get('freq') or cfg.get('freq_tag', cfg['freq'])}", f"lang::{lang}"]
        deck.add_note(genanki.Note(model=m, guid=genanki.guid_for(lang, r["id"]), tags=tags,
            fields=[r["word"], f"[sound:{os.path.basename(aud)}]", f'<img src="{os.path.basename(img)}">', r["english"], r["number"]]))
        files += [img, aud]; imgs.append(img)
    return cfg, deck, files, imgs

def contact(imgs, path, cols=4):
    ims = [Image.open(p) for p in imgs]; tw, th = ims[0].width // 3, ims[0].height // 3
    sheet = Image.new("RGB", (cols * tw, ((len(ims) + cols - 1) // cols) * th), "white")
    for i, im in enumerate(ims): sheet.paste(im.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    sheet.save(path)

if __name__ == "__main__":
    os.makedirs("out", exist_ok=True); a = sys.argv[1:]
    if a and a[0] == "--all":
        out = a[a.index("-o") + 1] if "-o" in a else "out/biblehebrew_all.apkg"
        cdir = a[1] if len(a) > 1 and not a[1].startswith("-") else "config"
        decks, files, imgs = [], [], []
        fq = a[a.index("--freq") + 1] if "--freq" in a else None
        for p in sorted(glob.glob(f"{cdir}/*.json")):
            if fq and json.load(open(p))["freq"] != fq: continue
            _, d, f, i = build(p); files += f; imgs += i; print(p, "->", d.name, len(d.notes))
            same = [x for x in decks if x.deck_id == d.deck_id]
            if same: same[0].notes += d.notes
            else: decks.append(d)
        genanki.Package(decks, media_files=files).write_to_file(out); contact(imgs, out.replace(".apkg", "_contact.png"))
        print("wrote", out, len(decks), "decks")
    else:
        cfg, d, f, i = build(a[0])
        genanki.Package(d, media_files=f).write_to_file(cfg["output"]); contact(i, cfg["output"].replace(".apkg", "_contact.png"))
        print("wrote", cfg["output"], d.name, len(d.notes))
