#!/usr/bin/env python3
# 核验 dianzaiji.html：q 引文逐字比对 + 白话反扫六字窗 + 版式红线
import re, sys
from html.parser import HTMLParser

SRC='/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/滇载记.txt'
HTML='dianzaiji.html'

FOLD={}  # 本库讹字照录（四君于/浮淡怪说等），不做归一映射

def norm(s):
    out=[]
    for ch in s:
        o=ord(ch)
        if (0x3400<=o<=0x9fff) or (0xf900<=o<=0xfaff) or ch.isdigit():
            out.append(ch)
    return ''.join(out)

src=norm(open(SRC,encoding='utf-8').read())

VOID={'br','img','meta','link','input','hr','source','wbr'}

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.quotes=[]; self.prose=[]; self.title=[]
        self._cur=None
    def handle_starttag(self,tag,attrs):
        if tag in VOID: return
        self.stack.append(tag)
        if tag=='q': self._cur=[]
        if tag=='title': self._cur=[]
    def handle_endtag(self,tag):
        if tag in VOID: return
        if tag in self.stack:
            while self.stack:
                x=self.stack.pop()
                if x==tag: break
        if tag=='q' and self._cur is not None:
            self.quotes.append(''.join(self._cur)); self._cur=None
        if tag=='title' and self._cur is not None:
            self.title.append(''.join(self._cur)); self._cur=None
    def handle_data(self,data):
        if self._cur is not None:
            self._cur.append(data); return
        if any(x in ('script','style') for x in self.stack): return
        if any(x in ('q','qv') for x in self.stack): return
        self.prose.append(data)

html=open(HTML,encoding='utf-8').read()
p=P(); p.feed(html)

fails=[]
nq=0
for i,q in enumerate(p.quotes):
    n=norm(q)
    if len(n)<2: continue
    nq+=1
    if n not in src:
        fails.append((i,q[:60]))

prose_raw=''.join(p.prose)
prose_norm=norm(prose_raw)+norm(''.join(p.title))
hits=[]
W=6
for i in range(len(prose_norm)-W+1):
    w=prose_norm[i:i+W]
    if w in src:
        hits.append(w)

def context_for(w):
    for j in range(len(prose_raw)-5):
        if norm(prose_raw[j:j+len(w)+8]).startswith(w):
            return prose_raw[max(0,j-18):j+len(w)+14]
    return w

dash=[html[max(0,m.start()-20):m.start()+20] for m in re.finditer('[—–]',html)]
midots=[(ln+1,l) for ln,l in enumerate(html.split('\n')) if l.count('·')>1]

print(f'引文申报 {nq} 处')
if fails:
    print('引文比对失败：')
    for i,q in fails: print(f'  [{i}] {q}')
else:
    print('引文比对：全部通过（去标点+归一后逐字在库本）')
if hits:
    print(f'白话反扫六字窗：{len(hits)} 撞')
    seen=set()
    for w in hits:
        if w in seen: continue
        seen.add(w)
        print(f'  {w} | 页面语境: {context_for(w)}')
else:
    print('白话反扫六字窗：零撞')
if dash:
    print(f'长划线：{len(dash)} 处'); [print('  ',d) for d in dash]
else:
    print('长划线：0')
if midots:
    print('行内·超1：'); [print(f'  L{n}: {l.strip()[:70]}') for n,l in midots]
else:
    print('行内·上限：通过')

ok = not fails and not hits and not dash and not midots
print('RESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
