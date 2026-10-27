from PIL import Image; import numpy as np, glob
for f in sorted(glob.glob('/workspace/ankisets/biblegreek/out/preview_*.png')):
    a=np.asarray(Image.open(f).convert('RGB')).astype(int)
    grey=(abs(a[:,:,0]-230)<=3)&(abs(a[:,:,2]-232)<=3)
    rows=np.where(grey[:,30])[0]
    boxes=[];st=rows[0];pv=rows[0]
    for r in rows[1:]:
        if r!=pv+1: boxes.append((st,pv)); st=r
        pv=r
    boxes.append((st,pv)); boxes=[b for b in boxes if b[1]-b[0]>40]
    out=[]
    for y0,y1 in boxes:
        cols=np.where(grey[(y0+y1)//2])[0]; x0,x1=cols.min(),cols.max()
        sub=a[y0:y1+1,x0:x1+1].sum(2)
        # word/english ink: dark pixels (<300) not in play button zone (right 64px)
        txt=np.where(sub[:, :-64]<300)
        iy0,iy1=txt[0].min()+y0,txt[0].max()+y0; ix0,ix1=txt[1].min()+x0,txt[1].max()+x0
        s=f"box {x1-x0+1}x{y1-y0+1}: text ink dx={((ix0+ix1)/2-(x0+x1)/2):+.1f} dy={((iy0+iy1)/2-(y0+y1)/2):+.1f}"
        # play button: white circle in right zone
        wz=(a[y0:y1+1,x1-64:x1+1].min(2)>=250)
        if wz.sum()>200:
            py=np.where(wz)[0]; s+=f"; button dy={((py.min()+py.max())/2+y0-(y0+y1)/2):+.1f}"
        out.append(s)
    print(f.split('/')[-1], out)
