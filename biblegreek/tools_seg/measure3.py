# per-word: final font-size em, wraps?, and centering offsets (line box) for word and en
import sys,json,html,subprocess,re; sys.argv=['x','build','biblegreek']; import build_deck as b
d=b.load("greek"); m=b.model_for("greek","ltr"); css=m.css
front=m.templates[0]["qfmt"]
play='<a class="replay-button" href="#"><svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="29"/><path d="M56.502,32.301l-37.502,20.101l0.329,-40.804l37.173,20.703Z"/></svg></a>'
res={}
cards="".join(f'<iframe></iframe>' for _ in [])
# render each card's front in its own section: reuse template per word but FIT_JS uses querySelector -> run per-card via sections
items=[]
for w in d["words"]:
    h=front.replace("{{Word}}",html.escape(w["word"])).replace("{{Audio}}",play).replace("{{Size}}",b.size_class(w["word"])).replace('document.querySelector(".word")','document.currentScript.parentNode.querySelector(".word")')
    items.append(f'<section>{h}</section>')
js='''<script>setTimeout(()=>{document.fonts.ready.then(()=>{let r=[];document.querySelectorAll("section").forEach(s=>{let e=s.querySelector(".word"),bx=s.querySelector(".box"),p=s.querySelector(".play a");let base=parseFloat(getComputedStyle(bx).fontSize),lh=parseFloat(getComputedStyle(e).lineHeight),R=e.getBoundingClientRect(),B=bx.getBoundingClientRect(),P=p.getBoundingClientRect();
r.push([e.textContent,+(parseFloat(getComputedStyle(e).fontSize)/base).toFixed(2),R.height>lh*1.4,+((R.left+R.right)/2-(B.left+B.right)/2).toFixed(1),+((R.top+R.bottom)/2-(B.top+B.bottom)/2).toFixed(1),+((P.top+P.bottom)/2-(B.top+B.bottom)/2).toFixed(1)])});document.body.setAttribute("data-r",JSON.stringify(r))})},500)</script>'''
open("/tmp/g/prev/m3.html","w").write(f"<html><head><meta charset=utf-8><style>{css}</style><style>html{{width:390px}}</style></head><body class=card>{''.join(items)}{js}</body></html>")
out=subprocess.run(["google-chrome","--headless","--no-sandbox","--disable-gpu","--window-size=390,800","--virtual-time-budget=6000","--dump-dom","file:///tmp/g/prev/m3.html"],capture_output=True,text=True).stdout
r=json.loads(html.unescape(re.search(r'data-r="([^"]*)"',out).group(1)))
from collections import Counter
print("sizes:",Counter(x[1] for x in r)); print("wraps:",[x[0] for x in r if x[2]])
print("max |dx| word:",max(abs(x[3]) for x in r),"max |dy| word:",max(abs(x[4]) for x in r),"max |dy| play:",max(abs(x[5]) for x in r))
for x in r:
    if x[1]<2: print(x)
