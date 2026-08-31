#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_lienvzhuan.py — 列女传导读页核验
1) 全部 .q 逐字对库（去标点去空白归一后子串比对，双侧）
2) 「」反扫：页面所有「」引文必须落在 .q 内
3) 红线：无 — –；渲染行 · ≤1；标签配平；文本节点无英文字母
4) 机数：库本三口径、七卷一百零四传、颂曰/君子曰计数、点名册逐名同序、
   七传序位、缺字段两侧、卷位断言、页内实测行数字
"""
import re, sys, json, html as htmlmod
from html.parser import HTMLParser

LIB = 'daizhige-simplified/史藏/传记/列女传.txt'
PAGE = 'daizhige-daodu/lienv-zhuan.html'
FAIL = []

def err(m):
    FAIL.append(m); print('FAIL:', m)

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch.isspace(): continue
        # 全角/半角标点与符号剔除：只留 CJK 双区间 + 拉丁数字用于小口径
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF or ch.isdigit():
            out.append(ch)
    return ''.join(out)

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
libN = norm(lib)

# ---------- 1. .q 收集器（栈配平，VOID 不入栈） ----------
VOID = {'meta','link','br','hr','img','input','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.qdepth=0; self.cur=[]; self.blocks=[]; self.pos=0
        self.dropped=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); cls=(a.get('class') or '').split()
        if self.qdepth>0 and 'lost' in cls: self.dropped=True
        if 'q' in cls and self.qdepth==0:
            self.qdepth=len(self.stack)+1; self.cur=[]; self.pos=self.getpos()
        if tag not in VOID: self.stack.append(tag)
    def handle_endtag(self,tag):
        if tag in VOID: return
        if self.stack and tag in self.stack:
            while self.stack:
                t=self.stack.pop()
                if t==tag: break
        if self.qdepth and len(self.stack)<self.qdepth:
            self.qdepth=0; self.blocks.append((''.join(self.cur), self.pos)); self.dropped=False
    def handle_data(self,d):
        if self.qdepth and not self.dropped: self.cur.append(d)

qc=QC(); qc.feed(page)
qblocks=[t for t,_ in qc.blocks]
print(f'.q blocks collected: {len(qblocks)}')

QUOTES_EXPECT = 24
if len(qblocks) < QUOTES_EXPECT: err(f'.q 数 {len(qblocks)} < 预期 {QUOTES_EXPECT}')

for i,(t,pos) in enumerate(qc.blocks):
    line=pos[0]
    n=norm(t)
    if not n: err(f'第{i}块 .q（行{line}）收集为空')
    elif n not in libN: err(f'.q 引文不在库内（行{line}）：{t[:40]}…')

# ---------- 2. 「」反扫（剥 style/script 后扫文本） ----------
body=re.sub(r'<style.*?</style>','',page,flags=re.S)
body=re.sub(r'<script.*?</script>','',body,flags=re.S)
txts=re.sub(r'<[^>]+>','',body)
plain=htmlmod.unescape(txts.replace('',''))
BARE={'君子曰'}  # 无
for m in re.finditer(r'「([^」]*)」', plain):
    seg=m.group(1)
    n=norm(seg)
    joined=norm(''.join(qblocks))
    ok=(n and (any(n in norm(qb) for qb in qblocks) or n in joined))
    if not ok: err('「」引文未落在 .q 内：'+seg[:30])

# ---------- 3. 红线 ----------
rendered=[]
for i,l in enumerate(body.split('\n'),1):
    s=re.sub(r'<[^>]+>','',l)
    s=htmlmod.unescape(s).strip()
    if s: rendered.append((i,s))
for i,s in rendered:
    if '—' in s or '–' in s: err(f'行{i} 含长划线')
    if s.count('·')>1: err(f'行{i} · 超一枚：{s[:50]}')
    if re.search(r'[A-Za-z]', s) and 'github' not in s and 'SF Mono' not in s and 'daizhigev20' not in s:
        err(f'行{i} 文本含英文字母：{s[:60]}')
# 标签配平
opens=len(re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(/?)>', page))
# 粗平衡：逐类计数（void 除外）
for tag in ['div','span','section','article','header','footer','main','p','h2','h3','a','style','script','b','small','i','em']:
    o=len(re.findall(r'<'+tag+r'\b',page)); c=len(re.findall(r'</'+tag+r'>',page))
    if o!=c: err(f'标签 {tag} 不配平 {o}/{c}')

# ---------- 4. 机数 ----------
n_total=len(lib); n_nobuf=len(re.sub(r'\s','',lib))
n_han=sum(1 for c in lib if 0x3400<=ord(c)<=0x9FFF or 0x20000<=ord(c)<=0x3FFFF)
if (n_total,n_nobuf,n_han)!=(50153,48543,38809): err(f'库本口径变化 {n_total}/{n_nobuf}/{n_han}')

juans=[];cur=None
for l in lib.split('\n'):
    s=l.strip()
    m=re.match(r'^●卷([一二三四五六七])[　\s]*(\S*传)?',s)
    if m:
        name=m.group(2)
        if not name:
            idx=lib.split('\n').index(l)
            for k in range(idx+1,min(idx+4,len(lib.split('\n')))):
                m2=re.match(r'^([一-鿿]{2,4}传)$',lib.split('\n')[k].strip())
                if m2: name=m2.group(1); break
        cur={'no':m.group(1),'name':name,'bios':[]}; juans.append(cur)
    elif cur is not None and s.startswith('△'):
        cur['bios'].append(s[1:].strip())
cnt=[len(j['bios']) for j in juans]
if cnt!=[14,15,15,15,15,15,15]: err(f'卷内传数 {cnt}')
if sum(cnt)!=104: err('传数非104')
if lib.count('颂曰')!=104: err('颂曰非104')
if lib.count('君子曰')!=16: err('君子曰非16')

# 点名册 JS 数据
m=re.search(r'const JUANS = (\[.*?\]);', page, re.S)
if not m: err('未找到 JUANS 数据')
else:
    js=json.loads(m.group(1))
    if len(js)!=7: err('JS 卷数非7')
    disp=lambda n: n.replace('\ue4b8','□').replace('{新女}','□').replace('\ue4aa','□').replace('\ue46d','□')
    for a_,b_ in zip(js,juans):
        if a_['no']!=b_['no'] or a_['name']!=b_['name']: err(f"卷{b_['no']} 卷头不符")
        if a_['bios']!=[disp(x) for x in b_['bios']]:
            err(f"卷{b_['no']} 点名册与库本不同序")
    if sum(len(a_['bios']) for a_ in js)!=104: err('JS 传数非104')

# 七传序位
POS={'邹孟轲母':('一',11),'楚庄樊姬':('二',5),'楚武邓曼':('三',2),'鲁漆室女':('三',13),'赵将括母':('三',15),'齐太仓女':('六',15),'周幽褒姒':('七',3)}
for name,(jn,idx) in POS.items():
    j=[x for x in juans if x['no']==jn][0]
    if name not in j['bios']: err(f'{name} 不在卷{jn}')
    elif j['bios'].index(name)+1!=idx: err(f'{name} 序位非第{idx}传（实为{j["bios"].index(name)+1}）')
    CNMAP={2:'二',3:'三',5:'五',11:'十一',13:'十三',15:'十五'}
    if f'第{CNMAP[idx]}传' not in page: err(f'页面缺序位文案 第{CNMAP[idx]}传')

# 缺字段两侧 + 库本原位
if '卒于木之下' not in lib: err('库本缺字段锚点不符')
sides=['王遂行，卒于','木之下。']
for s in sides:
    if norm(s) not in libN: err('缺字段侧不在库内：'+s)
if len(re.findall(r'<span class="lost">□□</span>',page))!=1: err('缺位虚框非一处')

# 页内实测行数字
for frag in ['50,153','48,543','38,809','一百零四']:
    if frag not in page: err('页内缺实测数：'+frag)
if '一百零四传点名册' not in page: err('缺点名册标题')
if '之一百二十五' not in page: err('页内缺编号 124')
if '<title>列女传 · 殆知阁导读之一百二十五</title>' not in page: err('title 不符')

# coda 收梢引文
if norm('受赂亡赵，身死灭国。') not in libN: err('coda 引文不在库内')

# hero ghost 名牌均为库内传名
allnames=set()
for j in juans:
    for b in j['bios']:
        for x in [b] : allnames.add(x)
allnames2=set()
for j in juans:
    for b in j['bios']:
        allnames2.add(b.replace('\ue4b8','□').replace('{新女}','□').replace('\ue4aa','□').replace('\ue46d','□'))
allnames=allnames2
ghost_ok=True
for m in re.finditer(r'<div class="ghost">([^<]*)</div>',page):
    for tok in m.group(1).split('　'):
        if tok and tok not in allnames: err('ghost 名不在库内：'+tok); ghost_ok=False

# 英文残留兜底（渲染文本已在上面查过，这里查 JS/属性外的可疑串）
for bad in ['Frage','TODO','lorem']:
    if bad in page: err('可疑残留：'+bad)

print()
print('='*46)
if FAIL:
    print(f'FAILED: {len(FAIL)} 项'); sys.exit(1)
print('ALL PASS — 列女传导读页核验全过')
print(f'.q={len(qblocks)} 传=104 颂=104 君子曰=16 库本={n_total}/{n_nobuf}/{n_han}')
