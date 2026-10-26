#!/usr/bin/env python3
"""Anki vocab decks from a JSON word list (source of truth: data/<lang>_words.json).
  python tools/build_deck.py build   <project> [--lang hebrew]      [--contact]  # fast: JSON + <project>/media/<lang>/ + fonts/ + tools/template/ -> 4 set decks + _all (no video access)
  python tools/build_deck.py extract <project> [--lang hebrew]      # only for entries whose image/audio file is missing: cut from entry's video
  python tools/build_deck.py init    <project> [--lang hebrew]      # one-time: config/*.json+.csv -> data/<lang>_words.json
JSON: {"lang","root","dir","prefix","font","sets":[{freq,freq_tag}],"words":[{id,word,english,occurrences,rank,due,
 pos,pos_label,freq,freq_tag,image,audio,src:{video,crop,pad,frame_t,audio_start,audio_end}}]} sorted by occurrences desc.
Deck: <root>::<freq>::<pos_label>; GUID guid_for(lang,id); model/deck IDs from stable names."""
import csv, glob, hashlib, json, os, subprocess, sys, time, genanki
from PIL import Image
TOOLS = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(TOOLS)
PROJ = next((a for a in sys.argv[2:] if not a.startswith("-") and os.path.isdir(os.path.join(REPO, a))), "biblehebrew")
os.chdir(os.path.join(REPO, PROJ))  # all data/, media/<lang>/, out/, config/, input/ paths are relative to the project dir

def stable_id(s): return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16) | 1 << 30
T = os.path.join(TOOLS, "template")
def _t(n): return open(os.path.join(T, n), encoding="utf-8").read()
FRONT, BACK, CSS = _t("front.html"), _t("back.html"), _t("style.css")  # CSS: __DIR__ -> rtl/ltr
FONTS = os.path.join(REPO, "fonts")

_models = {}
def model_for(lang, direction):
    if lang not in _models:
        _models[lang] = genanki.Model(stable_id("model:" + lang), f"Vocab ({lang})",
          fields=[{"name": n} for n in ["Word", "Audio", "Image", "English", "Occurrences", "Rank"]],
          templates=[{"name": "Word → Meaning",
            "qfmt": FRONT, "afmt": BACK}], css=CSS.replace("__DIR__", direction))
    return _models[lang]

def arg(name, default):
    a = sys.argv; return a[a.index(name) + 1] if name in a else default
def jpath(lang): return f"data/{lang}_words.json"
def load(lang): return json.load(open(jpath(lang), encoding="utf-8"))
def save(d):
    d["words"].sort(key=lambda w: w["due"])
    with open(jpath(d["lang"]), "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=1)

def init(lang):
    words, meta, seq = [], {}, 0
    for p in sorted(glob.glob("config/*.json")):
        c = json.load(open(p, encoding="utf-8"))
        if c["lang"] != lang: continue
        meta = {k: c[k] for k in ("lang", "root", "dir")}
        for r in csv.DictReader(open(c["cards"], encoding="utf-8")):
            words.append({"id": r["id"], "word": r["word"], "english": r["english"], "occurrences": int(r["number"]),
                "pos": r.get("pos") or c["pos"], "pos_label": c["pos_label"], "freq": c["freq"],
                "freq_tag": r.get("freq") or c.get("freq_tag", c["freq"]),
                "image": f"{r['id']}.jpg", "audio": f"{r['id']}.mp3", "_seq": seq,
                "src": {"video": c["video"], "crop": c["crop"], "pad": c.get("pad", 0.15), "frame_t": r["frame_t"],
                        "audio_start": r["audio_start"], "audio_end": r["audio_end"]}}); seq += 1
    for i, w in enumerate(sorted(words, key=lambda w: (-w["occurrences"], w["_seq"]))):
        w["due"] = i + 1; w["rank"] = 1 + sum(1 for x in words if x["occurrences"] > w["occurrences"]); del w["_seq"]
    sets = list(dict.fromkeys((w["freq"], w["freq_tag"].split("::")[0]) for w in words))
    meta.update(prefix=meta["root"].lower(), font="_EzraSIL.ttf" if lang == "hebrew" else None,
                sets=[{"freq": f, "freq_tag": t} for f, t in sets], words=words)
    save(meta); print("wrote", jpath(lang), len(words), "words")

def rerank(d):
    ws = d["words"]
    for w in ws: w["rank"] = 1 + sum(1 for x in ws if x["occurrences"] > w["occurrences"])
    for i, w in enumerate(sorted(ws, key=lambda w: (-w["occurrences"], w["due"]))): w["due"] = i + 1

def extract(lang):
    d = load(lang); media = f"media/{lang}"; os.makedirs(media, exist_ok=True); n = 0
    for w in d["words"]:
        s = w.get("src", {}); img, aud = f"{media}/{w['image']}", f"{media}/{w['audio']}"
        if not os.path.exists(img):
            x, y, cw, ch = s["crop"]; n += 1
            subprocess.run(["ffmpeg","-v","error","-y","-ss",str(s["frame_t"]),"-i",s["video"],"-frames:v","1",
                "-vf",f"crop={cw}:{ch}:{x}:{y}","-q:v","3",img], check=True)
        if not os.path.exists(aud):
            st = max(0, float(s["audio_start"]) - s["pad"]); du = float(s["audio_end"]) + s["pad"] - st; n += 1
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{st:.2f}","-t",f"{du:.2f}","-i",s["video"],"-vn",
                "-af","afade=t=in:d=0.05","-ac","1","-b:a","96k",aud], check=True)
        missing = [k for k in ("word", "english") if not w.get(k)]
        if missing: print("WARN", w["id"], "missing text:", missing, "(fill in JSON from video", s.get("video"), s.get("frame_t"), ")")
    rerank(d); save(d); print("extracted", n, "missing files")

def contact(imgs, path, cols=4):
    ims = [Image.open(p) for p in imgs]; tw, th = ims[0].width // 3, ims[0].height // 3
    sheet = Image.new("RGB", (cols * tw, ((len(ims) + cols - 1) // cols) * th), "white")
    for i, im in enumerate(ims): sheet.paste(im.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    sheet.save(path)

def package(d, words, out, sheet=True):
    lang = d["lang"]; media = f"media/{lang}"; m = model_for(lang, d.get("dir", "ltr")); decks = {}
    files = [os.path.join(FONTS, d["font"])] if d.get("font") else []
    for w in sorted(words, key=lambda w: w["due"]):
        name = f"{d['root']}::{w['freq']}::{w['pos_label']}"
        deck = decks.setdefault(name, genanki.Deck(stable_id("deck:" + name), name))
        for f in (w["image"], w["audio"]):
            if not os.path.exists(f"{media}/{f}"): sys.exit(f"missing {media}/{f} - run: build_deck.py extract")
        deck.add_note(genanki.Note(model=m, guid=genanki.guid_for(lang, w["id"]), due=w["due"],
            tags=[f"pos::{w['pos']}", f"freq::{w['freq_tag']}", f"lang::{lang}"],
            fields=[w["word"], f"[sound:{w['audio']}]", f'<img src="{w["image"]}">', w["english"], str(w["occurrences"]), str(w["rank"])]))
        files += [f"{media}/{w['image']}", f"{media}/{w['audio']}"]
    genanki.Package(list(decks.values()), media_files=files).write_to_file(out)
    if sheet: contact([f"{media}/{w['image']}" for w in words], out.replace(".apkg", "_contact.png"))
    print(f"wrote {out}: {len(words)} notes, {len(decks)} decks")

def build(lang, sheet):
    d = load(lang); os.makedirs("out", exist_ok=True); p = d["prefix"]
    for s in d["sets"]:
        package(d, [w for w in d["words"] if w["freq"] == s["freq"]], f"out/{p}_{s['freq_tag']}.apkg", sheet)
    package(d, d["words"], f"out/{p}_all.apkg", sheet)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"; lang = arg("--lang", None) or os.path.basename(glob.glob("data/*_words.json")[0]).split("_words")[0]; t = time.time()
    {"init": init, "extract": extract, "build": lambda l: build(l, "--contact" in sys.argv)}[cmd](lang)
    print(f"done in {time.time() - t:.1f}s")
