import json,subprocess,sys,numpy as np
from PIL import Image,ImageDraw
S=json.load(open("/tmp/g/segs.json"))
for t in sys.argv[1:]:
    v=f"input/10plus_{t}.mp4"; rows=[]
    f=np.load(f"/tmp/g/{t}.npy").astype(int)
    for k,w in enumerate(S[t]):
        def fr(ts):
            return Image.frombytes("RGB",(1206,2622),subprocess.run(["ffmpeg","-v","error","-ss",str(ts),"-i",v,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout)
        a=fr(w["frame_t"]+0.2)
        i=int(w["w_end"]*5)+1
        while i<len(f) and not (205<f[i][136:156,15:30].mean()<225 and f[i][136:156,15:30].std()<1.5 and f[i][50:66,15:30].std()>=1.5): i+=1
        b=fr(min(i,len(f)-1)/5+0.3)
        im=Image.new("RGB",(2200,190),"white")
        im.paste(a.crop((90,420,1110,760)).resize((450,150)),(0,20)); im.paste(a.crop((77,845,385,985)).resize((220,100)),(1030,20))
        im.paste(a.crop((950,218,1165,320)),(1260,20)); im.paste(b.crop((90,1300,1110,1680)).resize((450,168)),(1290,10))
        ImageDraw.Draw(im).text((5,2),f"{t} #{k+1}",fill="red"); rows.append(im)
    for p in range(0,len(rows),10):
        sh=Image.new("RGB",(2200,190*len(rows[p:p+10])),"white")
        for j,r in enumerate(rows[p:p+10]): sh.paste(r,(0,190*j))
        sh.resize((1650,int(sh.height*0.75))).save(f"/tmp/g/s2_{t}_{p//10}.jpg",quality=85)
