import sys; sys.argv=['x','build','biblegreek']; import build_deck as b, subprocess, re
d=b.load("greek"); ids=["gr-n10p-01","gr-v10p-03","gr-a10p-17","gr-n10p-49"]; ws=[w for w in d["words"] if w["id"] in ids]
b.package(d, ws, "out/biblegreek_trial.apkg", sheet=False)
m=b.model_for("greek","ltr"); css=m.css; FR,BK=m.templates[0]["qfmt"],m.templates[0]["afmt"]; tmp="/tmp/g/prev"
play='<a class="replay-button" href="#"><svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="29"/><path d="M56.502,32.301l-37.502,20.101l0.329,-40.804l37.173,20.703Z"/></svg></a>'
js='<script>document.fonts.ready.then(()=>{document.body.setAttribute("data-h",[...document.querySelectorAll(".box")].map(e=>e.getBoundingClientRect().height).join(","))})</script>'
for w in ws:
    for side,t in (("front",FR),("back",BK)):
        h=t.replace("{{Word}}",w["word"]).replace("{{Audio}}",play).replace("{{Image}}",f'<img src="{w["image"]}">').replace("{{English}}",w["english"]).replace("{{Occurrences}}",str(w["occurrences"])).replace("{{Rank}}",str(w["rank"])).replace("{{Size}}",b.size_class(w["word"]))
        for tag in ("#Occurrences","/Occurrences","#Rank","/Rank"): h=h.replace("{{"+tag+"}}","")
        f=f"{tmp}/{w['id']}_{side}.html"
        open(f,"w").write(f"<html><head><meta charset=utf-8><style>{css}</style><style>html{{width:390px}}</style></head><body class=card>{h}{js}</body></html>")
        subprocess.run(["google-chrome","--headless","--no-sandbox","--disable-gpu","--hide-scrollbars","--window-size=390,844","--virtual-time-budget=2000",f"--screenshot=/workspace/ankisets/biblegreek/out/preview_{w['id']}_{side}.png","file://"+f],capture_output=True)
        if side=="back":
            o=subprocess.run(["google-chrome","--headless","--no-sandbox","--disable-gpu","--window-size=390,844","--virtual-time-budget=2000","--dump-dom","file://"+f],capture_output=True,text=True).stdout
            print(w["word"], b.size_class(w["word"]), re.search(r'data-h="([^"]*)"',o).group(1))
