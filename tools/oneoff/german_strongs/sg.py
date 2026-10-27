import json,re,unicodedata as U
js=open("tools/oneoff/german_strongs/sources/strongs-greek-dictionary.js",encoding="utf-8").read()
G=json.loads(js[js.index("{",js.index("strongsGreekDictionary")):js.rindex("}")+1])
def nfc(s): return U.normalize("NFC",s)
def strip(s): return "".join(c for c in U.normalize("NFD",s) if not U.combining(c)).lower().replace("ς","σ")
ex,un={},{}
for k,v in G.items():
    l=nfc(v["lemma"]); ex.setdefault(l,[]).append(k); un.setdefault(strip(l),[]).append(k)
d=json.load(open("biblegreek/data/greek_words.json"))
res={}
for w in d["words"]:
    lem=nfc(w["word"].split(",")[0].split(" (")[0].strip())
    c=ex.get(lem) or un.get(strip(lem)) or []
    res[w["id"]]=(lem,c)
one=sum(len(c)==1 for _,c in res.values()); print("single",one,"multi",sum(len(c)>1 for _,c in res.values()),"none",sum(len(c)==0 for _,c in res.values()))
json.dump({k:[l,c] for k,(l,c) in res.items()},open("tools/oneoff/german_strongs/sg_res.json","w"),ensure_ascii=False)
for k,(l,c) in res.items():
    if len(c)!=1: print(k,l,[(x,G[x]["lemma"],G[x].get("kjv_def","")[:50]) for x in c])
