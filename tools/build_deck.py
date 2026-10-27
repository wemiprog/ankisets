#!/usr/bin/env python3
"""Anki vocab decks from a JSON word list (source of truth: data/<lang>_words.json).
  python tools/build_deck.py build   <project> [--lang hebrew]      [--contact]  # fast: JSON + <project>/media/<lang>/ + fonts/ + tools/template/ -> per set + _all, each in 3 variants EN/DE/EN.wDE (no video access)
  python tools/build_deck.py extract <project> [--lang hebrew]      # only for entries whose image/audio file is missing: cut from entry's video
  python tools/build_deck.py init    <project> [--lang hebrew]      # one-time: config/*.json+.csv -> data/<lang>_words.json
JSON: {"lang","root","dir","prefix","font","sets":[{freq,freq_tag}],"words":[{id,word,english,occurrences,rank,due,
 pos,pos_label,freq,freq_tag,image,audio,german,strongs,src:{video,crop,pad,frame_t,audio_start,audio_end}}]} sorted by occurrences desc.
Deck: <root>::<freq>::<pos_label> (singular English: Noun, Verb, Adjective, Other, Proper Name; also shown on the back as POS, then Strong's); GUID guid_for(lang,id) (EN) / guid_for(lang,id,variant);
Packages: <prefix>_<set>.<variant>.apkg + <prefix>_all.<variant>.apkg, variants EN, DE, EN.wDE (separate note types); model/deck IDs from stable names."""
import csv, glob, unicodedata, hashlib, json, os, subprocess, sys, time, genanki
from PIL import Image
TOOLS = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(TOOLS)
PROJ = next((a for a in sys.argv[2:] if not a.startswith("-") and os.path.isdir(os.path.join(REPO, a))), "biblehebrew")
os.chdir(os.path.join(REPO, PROJ))  # all data/, media/<lang>/, out/, config/, input/ paths are relative to the project dir

def stable_id(s): return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16) | 1 << 30
T = os.path.join(TOOLS, "template")
def _t(n): return open(os.path.join(T, n), encoding="utf-8").read()
FRONT, BACK, CSS = _t("front.html"), _t("back.html"), _t("style.css")  # CSS: __DIR__ -> rtl/ltr
FONTS = os.path.join(REPO, "fonts")

WORDFONT = {  # lang -> (@font-face rule, .word font-family list)
    "hebrew": ('@font-face{font-family:EzraSIL;src:url("_EzraSIL.ttf")}', "'EzraSIL','Ezra SIL','SBL Hebrew','Times New Roman',serif"),
    "greek": ('@font-face{font-family:GentiumPlus;src:url("_GentiumPlus.ttf")}', "'GentiumPlus','Gentium Plus','Times New Roman',serif")}
# Greek: word 2.0em, shrunk per card by character count (Size field -> class), JS refines (never below 1.4em); English 1.4em
EXTRA_CSS = {"greek": "\n.word{font-size:2em}.word.len-l{font-size:1.8em}.word.len-xl{font-size:1.5em}.word.len-xxl{font-size:1.4em}.en{font-size:1.4em}"
    "@media (max-width:480px){.word{font-size:2em}.word.len-l{font-size:1.8em}.word.len-xl{font-size:1.5em}.word.len-xxl{font-size:1.4em}.en{font-size:1.4em}.enbox{padding:22px 24px}}"}
FIT_JS = ('<script>(function(){var e=document.querySelector(".word");if(!e)return;function f(){var base=parseFloat(getComputedStyle(e.parentNode).fontSize),i=0;'
          'while(i++<12&&e.getBoundingClientRect().height>parseFloat(getComputedStyle(e).lineHeight)*1.4){var px=parseFloat(getComputedStyle(e).fontSize)*0.95;if(px<base*1.4)px=base*1.4;e.style.fontSize=px+"px";if(px<=base*1.4)break}}'
          'if(document.fonts&&document.fonts.ready)document.fonts.ready.then(f);else f()})()</script>')  # shrink only if still wrapping; floor 1.4em
def size_class(word):  # NFC chars; thresholds measured at 390px with Gentium Plus
    n = len(unicodedata.normalize("NFC", word))
    return "" if n <= 17 else "len-l" if n <= 19 else "len-xl" if n <= 22 else "len-xxl"
def tmpl(t, lang):
    return t if lang != "greek" else t.replace('<div class="word">', '<div class="word {{Size}}">', 1).replace('<div class="play">{{Audio}}</div></div>', '<div class="play">{{Audio}}</div></div>' + FIT_JS, 1)
_models = {}
VARIANTS = ("EN", "DE", "EN.wDE")  # back answer area: EN = English only (approved design); DE = German main + English small; EN.wDE = English main + German small
def back_for(variant):
    if variant == "EN": return BACK
    main, sub = ("German", "English") if variant == "DE" else ("English", "German")
    b = BACK.replace('<div class="box enbox"><div class="en">{{English}}</div></div>',
        f'<div class="box enbox two"><div class="en">{{{{{main}}}}}</div>{{{{#{sub}}}}}<div class="sub">{{{{{sub}}}}}</div>{{{{/{sub}}}}}</div>', 1)
    return b.replace('querySelectorAll(".word,.en")', 'querySelectorAll(".word,.en,.sub")', 1)
SUB_CSS = ("\n.enbox.two{flex-direction:column}.sub{font-size:.95em;line-height:1.3;color:#6e6e73;margin-top:8px}"
           ".nightMode .sub,.night_mode .sub{color:#a1a1a6}")
def model_for(lang, direction, variant="EN"):
    face, fam = WORDFONT[lang]; key = (lang, variant)
    if key not in _models:  # EN keeps the original model ID; DE / EN.wDE are separate note types so all three can coexist
        mid = stable_id("model:" + lang) if variant == "EN" else stable_id(f"model:{lang}:{variant}")
        _models[key] = genanki.Model(mid, f"Vocab ({lang}) {variant}",
          fields=[{"name": n} for n in ["Word", "Audio", "Image", "English", "Occurrences", "Rank"] + (["Size"] if lang == "greek" else []) + ["POS", "Strongs", "German"]],
          templates=[{"name": "Word → Meaning",
            "qfmt": tmpl(FRONT, lang), "afmt": tmpl(back_for(variant), lang)}], css=CSS.replace("__DIR__", direction).replace("__FONTFACE__", face).replace("__WORDFONT__", fam) + EXTRA_CSS.get(lang, "") + ("" if variant == "EN" else SUB_CSS))
    return _models[key]

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
    meta.update(prefix=meta["root"].lower(), font={"hebrew": "_EzraSIL.ttf", "greek": "_GentiumPlus.ttf"}.get(lang),
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

def package(d, words, out, sheet=True, variant="EN"):
    lang = d["lang"]; media = f"media/{lang}"; m = model_for(lang, d.get("dir", "ltr"), variant); decks = {}
    files = [os.path.join(FONTS, d["font"])] if d.get("font") else []
    for w in sorted(words, key=lambda w: w["due"]):
        name = f"{d['root']}::{w['freq']}::{w['pos_label']}"
        deck = decks.setdefault(name, genanki.Deck(stable_id("deck:" + name), name))
        for f in (w["image"], w["audio"]):
            if not os.path.exists(f"{media}/{f}"): sys.exit(f"missing {media}/{f} - run: build_deck.py extract")
        if variant != "EN" and not w.get("german"): sys.exit(f"{w['id']}: no german gloss in JSON")
        deck.add_note(genanki.Note(model=m, guid=genanki.guid_for(lang, w["id"]) if variant == "EN" else genanki.guid_for(lang, w["id"], variant), due=w["due"],
            tags=[f"pos::{w['pos']}", f"freq::{w['freq_tag']}", f"lang::{lang}"],
            fields=[w["word"], f"[sound:{w['audio']}]", f'<img src="{w["image"]}">', w["english"], str(w["occurrences"]), str(w["rank"])] + ([size_class(w["word"])] if lang == "greek" else []) + [w["pos_label"], w.get("strongs", ""), w.get("german", "")]))
        files += [f"{media}/{w['image']}", f"{media}/{w['audio']}"]
    genanki.Package(list(decks.values()), media_files=files).write_to_file(out)
    if sheet and variant == "EN": contact([f"{media}/{w['image']}" for w in words], "out/" + os.path.basename(out).replace(".apkg", "_contact.png"))
    print(f"wrote {out}: {len(words)} notes, {len(decks)} decks")

def build(lang, sheet):  # reads only the JSON fields (german, strongs are stored there; no lookups at build time)
    d = load(lang); os.makedirs("out", exist_ok=True); p = d["prefix"]
    for v in VARIANTS:
        for s in d["sets"]:
            package(d, [w for w in d["words"] if w["freq"] == s["freq"]], f"{p}_{s['freq_tag']}.{v}.apkg", sheet, v)
        package(d, d["words"], f"{p}_all.{v}.apkg", sheet, v)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"; lang = arg("--lang", None) or os.path.basename(glob.glob("data/*_words.json")[0]).split("_words")[0]; t = time.time()
    {"init": init, "extract": extract, "build": lambda l: build(l, "--contact" in sys.argv)}[cmd](lang)
    print(f"done in {time.time() - t:.1f}s")
