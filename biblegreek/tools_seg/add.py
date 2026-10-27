import json,sys
def add(tag,video,prefix,start,pos,poslabel,freq,D,skip_first=0):
    S=json.load(open("/tmp/g/segs.json"))[tag][skip_first:skip_first+len(D)]
    assert len(S)==len(D)
    d=json.load(open("data/greek_words.json")); have={w["word"].split(" (")[0] for w in d["words"]}
    print("dups:",[g for g,_,_ in D if g.split(" (")[0] in have])
    ft=freq.replace("+","plus")
    for k,((g,e,n),s) in enumerate(zip(D,S)):
        i=f"{prefix}-{k+start:02d}"
        d["words"].append(dict(id=i,word=g,english=e,occurrences=n,rank=0,due=99999+k,pos=pos,pos_label=poslabel,freq=freq,freq_tag=ft,image=i+".jpg",audio=i+".mp3",
          src=dict(video=video,crop=[60,810,1086,870],pad=0.15,frame_t=s["frame_t"]+0.2,audio_start=s["audio_start"],audio_end=s["audio_end"])))
    json.dump(d,open("data/greek_words.json","w"),ensure_ascii=False,indent=1)
    print(len(d["words"]), sum(w["freq"]==freq for w in d["words"]), sum(w["freq"]==freq and w["pos"]==pos for w in d["words"]))
