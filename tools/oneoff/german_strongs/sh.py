import json,re,unicodedata as U
import xml.etree.ElementTree as ET
ns={"o":"http://www.bibletechnologies.net/2003/OSIS/namespace"}
t=ET.parse("tools/oneoff/german_strongs/sources/StrongHebrewG.xml").getroot()
E={}
for div in t.iter("{%s}div"%ns["o"]):
    if div.get("type")!="entry": continue
    w=div.find("o:w",ns)
    if w is None or not w.get("ID"): continue
    items=[ "".join(i.itertext()).strip() for i in div.iter("{%s}item"%ns["o"])]
    E[w.get("ID")]=dict(lemma=w.get("lemma",""),xlit=w.get("xlit",""),morph=w.get("morph",""),defs=items)
def nfc(s): return U.normalize("NFC",s)
def cons(s): return "".join(c for c in U.normalize("NFD",s) if "\u05d0"<=c<="\u05ea")
def nosign(s): return nfc("".join(c for c in U.normalize("NFD",s) if not U.category(c)=="Mn" or "\u05b0"<=c<="\u05bc" or c in "\u05c1\u05c2\u05c7"))
ex,co={},{}
for k,v in E.items():
    ex.setdefault(nosign(v["lemma"]),[]).append(k); co.setdefault(cons(v["lemma"]),[]).append(k)
json.dump(E,open("tools/oneoff/german_strongs/heb_strong.json","w"),ensure_ascii=False)
d=json.load(open("biblehebrew/data/hebrew_words.json"))
out={}
for w in d["words"]:
    forms=[f.strip() for f in re.split(r"[,;]",re.sub(r"\(.*?\)","",w["word"])) if f.strip()]
    forms=[re.sub(r"[¹²³־]","",f).strip() for f in forms]
    c=[]
    for f in forms[:1]:
        c=ex.get(nosign(f),[]) 
        if not c: c=["~"+x for x in co.get(cons(f),[])]
    out[w["id"]]=(w["word"],w["english"],w["pos"],c)
json.dump(out,open("tools/oneoff/german_strongs/sh_res.json","w"),ensure_ascii=False)
print("exact1",sum(1 for v in out.values() if len(v[3])==1 and not v[3][0].startswith("~")),"exactmulti",sum(1 for v in out.values() if len(v[3])>1 and not v[3][0].startswith("~")),"cons",sum(1 for v in out.values() if v[3] and v[3][0].startswith("~")),"none",sum(1 for v in out.values() if not v[3]))
