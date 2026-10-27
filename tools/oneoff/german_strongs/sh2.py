import json,re
E=json.load(open("tools/oneoff/german_strongs/heb_strong.json")); R=json.load(open("tools/oneoff/german_strongs/sh_res.json"))
stop=set("to the a an of be in on one who what which and or as is are".split())
def score(eng,pos,k):
    e=E[k]; txt=(" ".join(e["defs"])).lower(); m=e["morph"]
    ws=[x for x in re.findall(r"[a-z]+",eng.lower()) if x not in stop and len(x)>2]
    s=sum(2 for x in ws if x[:5] in txt)
    if pos=="verb" and m.startswith("v"): s+=3
    if pos=="noun" and m.startswith("n") and "pr" not in m: s+=2
    if pos=="name" and "n-pr" in m: s+=4
    if pos=="adj" and m.startswith("a"): s+=2
    if pos=="other" and not m.startswith(("v","n-")): s+=1
    if pos!="name" and "n-pr" in m: s-=3
    return s
res={}
for i,(word,eng,pos,c) in R.items():
    c=[x.lstrip("~") for x in c]
    if not c: res[i]=None; continue
    sc=sorted(((score(eng,pos,k),int(k[1:]),k) for k in c),reverse=True)
    res[i]=[(s,k) for s,_,k in sc]
json.dump(res,open("tools/oneoff/german_strongs/sh_scored.json","w"))
for i,(word,eng,pos,c) in R.items():
    r=res[i]
    if r is None or len(r)>1 or c[0].startswith("~") or r[0][0]<2:
        top=" ; ".join(f"{k}[{s}] {E[k]['lemma']} {E[k]['morph']}: {(E[k]['defs'] or [''])[0][:40]}" for s,k in (r or [])[:4])
        print(f"{i} | {word} | {eng} | {pos} || {top}")
