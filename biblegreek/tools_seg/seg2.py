import numpy as np, sys, json
out={}
for t in sys.argv[1:]:
    f=np.load(f"/tmp/g/{t}.npy").astype(int); rms=np.load(f"/tmp/g/{t}_rms.npy"); F=5
    W=[(205<fr[50:66,15:30].mean()<225 and fr[50:66,15:30].std()<1.5) for fr in f]
    runs=[];i=0
    while i<len(W):
        j=i
        while j+1<len(W) and W[j+1]==W[i]: j+=1
        if W[i] and j-i>=1: runs.append((i,j))
        i=j+1
    words=[]
    for a,b in runs:
        box=f[a+1][46:72,8:90]
        if any((abs(box-w["_b"])>50).sum()<15 for w in words): continue
        i0,i1=int(a/F*20),int(min(b/F+1,a/F+3)*20); seg=rms[i0:i1]; on=np.where(seg>max(300,seg.max()*0.08))[0]
        au=(round((i0+on[0])*0.05,2),round((i0+on[-1]+1)*0.05,2)) if len(on) else (a/F,a/F+1)
        words.append(dict(frame_t=round(a/F+0.3,2),w_end=b/F,audio_start=au[0],audio_end=au[1],_b=box))
    for w in words: del w["_b"]
    out[t]=words; print(t,len(words))
json.dump(out,open("/tmp/g/segs.json","w"),indent=0)
