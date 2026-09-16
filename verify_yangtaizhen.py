#!/usr/bin/env python3
# 核验 yangtaizhen-waizhuan.html：引文逐字比对 + 白话六字窗反扫 + 排版红线
import re, sys
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yangtaizhen-waizhuan.html"
SRC  = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/杨太真外传.txt"

VARMAP = str.maketrans({"呉":"吴","髙":"高","褔":"福","戶":"户","囘":"回"})
def norm(s):
    s = s.translate(VARMAP)
    return "".join(ch for ch in s if ch.isalnum())

src = open(SRC, encoding="utf-8").read()
nsrc = norm(src)

class Walk(HTMLParser):
    BLOCK = {"p","div","h1","h2","h3","h4","h5","h6","blockquote","li","section",
             "footer","nav","body","html","td","th","tr","table","aside","main","header"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes=[]; self.runs=[]
        self.buf=[]; self.bufline=0
        self.in_q=0; self.skip=0
        self.stack=[]
        self.void={"meta","link","br","hr","img","input","area","base","col",
                   "embed","source","track","wbr"}
    def is_q(self, attrs):
        for k,v in attrs:
            if k=="class" and v:
                return "q" in v.split()
        return False
    def handle_starttag(self, tag, attrs):
        if tag in ("script","style","title"): self.skip+=1
        isq = (tag=="q") or self.is_q(attrs)
        if tag not in self.void and tag not in ("script","style"):
            self.stack.append(isq)
        if isq:
            self.flush(); self.in_q+=1
        elif tag in self.BLOCK:
            self.flush()
    def handle_endtag(self, tag):
        if tag in ("script","style","title"): self.skip=max(0,self.skip-1)
        if tag in self.void: return
        wasq = self.stack.pop() if self.stack else False
        if wasq:
            self.flush(); self.in_q-=1
        elif tag in self.BLOCK:
            self.flush()
    def handle_startendtag(self, tag, attrs):
        if tag=="q" or self.is_q(attrs):
            self.flush()
    def handle_data(self, d):
        if self.skip: return
        self.buf.append(d)
        if not self.bufline: self.bufline=self.getpos()[0]
    def flush(self):
        if not self.buf: return
        text="".join(self.buf); ln=self.bufline
        if self.in_q>0: self.quotes.append((text,ln))
        elif text.strip(): self.runs.append((text,ln))
        self.buf=[]; self.bufline=0

html=open(PAGE, encoding="utf-8").read()

errs=[]
if "—" in html: errs.append("出现长划线 —")
if "–" in html: errs.append("出现短划线 –")

w=Walk(); w.feed(html); w.flush()

qfails=[]; short=[]
for t,ln in w.quotes:
    n=norm(t)
    if len(n)<3: short.append((t.strip()[:30],ln)); continue
    if n not in nsrc: qfails.append((t.strip()[:60],ln))

hits=[]
for t,ln in w.runs:
    n=norm(t)
    for i in range(len(n)-5):
        win=n[i:i+6]
        if win in nsrc: hits.append((win,t.strip()[:40],ln))

print(f"引文总数: {len(w.quotes)}  通过: {len(w.quotes)-len(qfails)-len(short)}")
for t,ln in qfails: print(f"  [Q未中] L{ln}: {t}")
for t,ln in short:  print(f"  [Q过短] L{ln}: {t}")
print(f"反扫撞窗: {len(hits)}")
for win,t,ln in hits: print(f"  [反扫] L{ln} 窗[{win}] 于: {t}")

for t,ln in w.runs:
    if t.count("·")>1: print(f"  [·超标] L{ln}: {t.strip()[:60]}")

sys.exit(1 if (qfails or hits or errs) else 0)
