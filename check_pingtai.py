# -*- coding: utf-8 -*-
"""check_pingtai.py  引文核对 + 白话反扫 + 红线检查"""
import re,sys
from html.parser import HTMLParser

PAGE='/home/robertsong/workspace/claude/daizhige-daodu/pingtai-jilue.html'
SRC='/home/robertsong/workspace/claude/daizhige-simplified/史藏/纪事本末/平台纪略.txt'

src=open(SRC,encoding='utf-8').read()
html=open(PAGE,encoding='utf-8').read()
def norm(s): return re.sub(r'[\W_]+','',s,flags=re.UNICODE)
nsrc=norm(src)

VOID={'br','img','meta','link','input','hr','path','circle','rect','line','ellipse','stop','use','polyline','polygon'}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]      # (tag, cls)
        self.qtext=[]      # 引文容器文本
        self.cur_q=None
        self.protxt=[]     # (block_idx, text) 白话
        self.skip=0        # script/style 深度
        self.puafound=[]
    def handle_starttag(self,tag,attrs):
        if tag in VOID: return
        d=dict(attrs); cls=d.get('cls') or d.get('class') or ''
        if tag in('script','style'): self.skip+=1; return
        if re.search(r'\b(q|qv|sealq)\b',cls):
            self.cur_q={'cls':cls,'buf':[]}
        self.stack.append((tag,cls))
    def handle_startendtag(self,tag,attrs):
        pass
    def handle_endtag(self,tag):
        if tag in VOID: return
        if tag in('script','style'):
            self.skip=max(0,self.skip-1); return
        if self.cur_q and self.stack and re.search(r'\b(q|qv|sealq)\b',self.stack[-1][1]):
            self.qtext.append((self.cur_q['cls'],''.join(self.cur_q['buf'])))
            self.cur_q=None
        if self.stack and self.stack[-1][0]==tag:
            self.stack.pop()
        elif self.stack:
            # 容错:找最近的同名
            for i in range(len(self.stack)-1,-1,-1):
                if self.stack[i][0]==tag:
                    del self.stack[i:]
                    break
    def handle_data(self,data):
        if self.skip: return
        if self.cur_q is not None:
            self.cur_q['buf'].append(data)
        else:
            # 判断当前是否处于块级白话环境
            cls=' '.join(c for _,c in self.stack)
            if re.search(r'\bsrc\b',cls): return   # 出处注豁免
            self.protxt.append((len(self.protxt),data))

p=P();p.feed(html)

# ---- 1. 正扫:引文逐条比对 ----
quotes=[norm(t) for _,t in p.qtext if norm(t)]
miss=[]
for q in quotes:
    if q not in nsrc: miss.append(q[:60])
print(f"[1] 引文容器 {len(quotes)} 条, 未命中 {len(miss)}")
for m in miss: print("   MISS:",m)

# ---- 2. 反扫:白话 6 字窗 ----
# 块级切分:每个 data 片段单独 norm,再取所有6字窗
hits=[]
for idx,t in p.protxt:
    n=norm(t)
    if len(n)<6: continue
    for i in range(len(n)-5):
        w=n[i:i+6]
        if w in nsrc:
            hits.append((idx,t[:30],w))
print(f"[2] 白话 6 字窗反扫: {len(hits)} 撞")
for h in hits[:40]: print("   HIT:",h[1],'>>>',h[2])

# ---- 3. 红线:长划线/半字线/PUA/多 · ----
red=[]
for pat,name in [(r'—','长划线—'),(r'–','en dash'),(r'−','minus'),(r'[-]','PUA'),(r'[\U00020000-\U0003FFFF]','扩展区')]:
    if re.search(pat,html): red.append(name)
# · 每块最多1(按 data 片段近似渲染行)
dots=[]
for idx,t in p.protxt:
    if t.count('·')>1: dots.append((idx,t[:40]))
print(f"[3] 红线: {red}, 多·片段 {len(dots)}")
for d in dots: print("   DOT:",d)

# ---- 4. 必备要素 ----
need=['殆知阁古代文献简体库','daizhige-daodu','时代局限提醒','引文经脚本','第 349 篇']
absent=[n for n in need if n not in html]
print(f"[4] 页脚要素缺失: {absent if absent else '无'}")

ok= not miss and not hits and not red and not dots and not absent
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
