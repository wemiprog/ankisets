# usage (from repo root): python tools/oneoff/german_strongs/render3.py <project> <lang> <word id> <EN|DE|EN.wDE>  -> <project>/out/preview_<id>_back_<variant>.png
import sys,subprocess,os,re
proj,lang,wid,variant=sys.argv[1:5]
sys.argv=['x','build',proj]; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')); import build_deck as b
d=b.load(lang); w=[x for x in d["words"] if x["id"]==wid][0]
m=b.model_for(lang,d.get("dir","ltr"),variant); css=m.css; BK=m.templates[0]["afmt"]
play='<a class="replay-button" href="#"><svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="29"/><path d="M56.502,32.301l-37.502,20.101l0.329,-40.804l37.173,20.703Z"/></svg></a>'
med=os.path.abspath(f"media/{lang}"); font=os.path.join(b.FONTS,d["font"])
css=css.replace(f'url("{d["font"]}")',f'url("file://{font}")')
F={"Word":w["word"],"Audio":play,"Image":f'<img src="file://{med}/{w["image"]}">',"English":w["english"],"Occurrences":str(w["occurrences"]),"Rank":str(w["rank"]),"POS":b.POS_DE[w["pos_label"]] if variant=="DE" else w["pos_label"],"Size":b.size_class(w["word"]),"Strongs":w.get("strongs",""),"German":b.german_html(w,lang) if variant!="EN" else w.get("german","")}
h=BK
while "{{#" in h: h=re.sub(r"\{\{#(\w+)\}\}((?:(?!\{\{#).)*?)\{\{/\1\}\}",lambda m:m.group(2) if F.get(m.group(1)) else "",h,flags=re.S)
h=re.sub(r"\{\{(\w+)\}\}",lambda m:F[m.group(1)],h)
f=f"/tmp/prev_{wid}_{variant}.html"; open(f,"w").write(f"<html><head><meta charset=utf-8><style>{css}</style><style>html{{width:390px}}</style></head><body class=card>{h}</body></html>")
out=os.path.abspath(f"out/preview_{wid}_back_{variant}.png")
subprocess.run(["google-chrome","--headless","--no-sandbox","--disable-gpu","--hide-scrollbars","--allow-file-access-from-files","--window-size=390,844","--virtual-time-budget=2000",f"--screenshot={out}","file://"+f],capture_output=True); print(out)
