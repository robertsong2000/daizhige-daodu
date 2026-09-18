#!/usr/bin/env python3
# 核验 huqian-jing.html：引文比对 + 白话反扫(含script) + 排版规则
# 归一口径：空白与标点剥离；库本（一作X）夹注双侧剔除；库本 <..> 缺字标记双侧剔除
import re, sys
from html.parser import HTMLParser

HTML='/home/robertsong/workspace/claude/daizhige-daodu/huqian-jing.html'
LIB='/home/robertsong/workspace/claude/daizhige-simplified/子藏/兵家/虎钤经.txt'
NORM=re.compile('[\s，。、；：？！「」『』（）〔〕·.,;:?!〈〉《》"\'“”‘’\-—–…＿＿．]+')
VAR=re.compile('（一作[^）]*）')
MARK=re.compile('<[^>]{1,6}>')

def raw_norm(s): return NORM.sub('', VAR.sub('', MARK.sub('', s)))

lib=raw_norm(open(LIB,encoding='utf-8').read())

EXEMPT_CLS={'qn','src','vseal','seal','vq'}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks=[]; self.prose=[]; self.stack=[]
        self.skip=0; self._buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); cls=set((a.get('class') or '').split())
        if tag in ('script','style'):
            self.skip+=1; self.stack.append((tag,False,False,False)); return
        if self.skip:
            self.stack.append((tag,False,False,False)); return
        is_q=('q' in cls) or ('qi' in cls)
        is_ex=bool(cls & EXEMPT_CLS) or ('data-t' in a)
        was_q=self.q_open(); was_ex=self.ex_open()
        if is_q and not was_q:
            self.stack.append((tag,True,is_ex or was_ex,True)); self._buf=[]; return
        self.stack.append((tag,was_q,is_ex or was_ex,False))
    def q_open(self): return any(f for _,f,_,_ in self.stack)
    def ex_open(self): return any(e for _,_,e,_ in self.stack)
    def handle_endtag(self,tag):
        if tag in ('script','style'):
            self.skip=max(0,self.skip-1)
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                opened_q=self.stack[i][3]
                del self.stack[i:]
                if opened_q and not self.q_open():
                    t=raw_norm(''.join(self._buf))
                    if t: self.blocks.append(t)
                break
    def handle_data(self,d):
        if self.skip: return
        SEP='\x01'
        if self.q_open():
            if not self.ex_open(): self._buf.append(d)
        elif self.ex_open():
            pass
        else:
            self.prose.append(SEP+d+SEP)

raw=open(HTML,encoding='utf-8').read()
p=P(); p.feed(raw)

errs=[]
for i,ln in enumerate(raw.split('\n'),1):
    if '—' in ln or '–' in ln: errs.append(f'L{i} 长划线')
    if ln.count('·')>1: errs.append(f'L{i} · 超标({ln.count("·")})')

miss=[b for b in p.blocks if b not in lib]

pn=raw_norm(''.join(p.prose))
def scan(text):
    hits=[]; W=6
    for i in range(len(text)-W+1):
        w=text[i:i+W]
        if w in lib: hits.append(w)
    seen=set(); u=[]
    for h in hits:
        if h not in seen: seen.add(h); u.append(h)
    return u
hits=scan(pn)
sfrag=[]
sm=re.findall(r'<script[^>]*>(.*?)</script>', raw, re.S)
for s in sm:
    for f in re.split(r'["\'`]', s):
        if f.strip(): sfrag.append('\x01'+raw_norm(f)+'\x01')
shits=scan(raw_norm('\x01'.join(sfrag)))

print(f'引文块: {len(p.blocks)}  未命中: {len(miss)}')
for b in miss[:25]: print('  MISS:',b[:80])
print(f'白话反扫六字窗: DOM {len(hits)} 撞 / JS {len(shits)} 撞')
for h in hits[:30]:
    i=pn.find(h); print('  DOM HIT:',h,'|',pn[max(0,i-14):i+20])
for h in shits[:20]:
    print('  JS HIT:',h)
print('排版:', errs if errs else 'OK')
sys.exit(1 if (miss or hits or shits or errs) else 0)
