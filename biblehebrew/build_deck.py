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

_models = {}
def model_for(lang, direction):
    if lang not in _models:
        _models[lang] = genanki.Model(stable_id("model:" + lang), f"Vocab ({lang})",
          fields=[{"name": n} for n in ["Word", "Audio", "Image", "English", "Occurrences"]],
          templates=[{"name": "Word → Meaning",
            "qfmt": '<div class="word">{{Word}}</div>{{Audio}}<script>document.querySelectorAll(".word").forEach(function(e){e.innerHTML=e.innerHTML.replace(/([\u00b9\u00b2\u00b3])/g,"<span class=hom>$1</span>")})</script>',
            "afmt": '<div class="word">{{Word}}</div><hr id=answer><div>{{Image}}</div><div class="en">{{English}}</div>'}],
          css=f""".card{{font-family:sans-serif;text-align:center;background:#fff;color:#000}}
.word{{font-size:64px;direction:{direction};font-family:'SBL Hebrew','SBL Greek','Ezra SIL','Times New Roman',serif;margin:20px}}

.hom{{font-family:sans-serif;font-size:40px;font-weight:bold;color:#c00;vertical-align:super;unicode-bidi:isolate;margin:0 4px}}
.en{{font-size:26px;margin-top:12px}} img{{max-width:100%;max-height:60vh}}""")
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
