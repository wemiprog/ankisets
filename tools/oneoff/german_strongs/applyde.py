import json,sys
proj,lang,tag=sys.argv[1:4]
p=f"{proj}/data/{lang}_words.json"; d=json.load(open(p))
freq=[s["freq"] for s in d["sets"] if s["freq_tag"]==tag][0]
ws=[w for w in d["words"] if w["freq"]==freq]
L=[l.split("|",1) for l in open(f"tools/oneoff/german_strongs/glosses/de_{lang[:2]}_{tag}.txt").read().strip().split("\n")]
assert len(L)==len(ws),(len(L),len(ws))
for i,(k,g) in enumerate(L):
    assert int(k)==i,(k,i); assert g.strip(); ws[i]["german"]=g.strip()
json.dump(d,open(p,"w"),ensure_ascii=False,indent=1); print(tag,len(ws),"filled; total",sum(1 for w in d["words"] if w.get("german")))
