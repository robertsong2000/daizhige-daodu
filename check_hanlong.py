#!/usr/bin/env python3
import re, sys, html

LIB='/home/robertsong/workspace/claude/daizhige-simplified/易藏/术数/撼龙经.txt'
PAGE='/home/robertsong/workspace/claude/daizhige-daodu/hanlong-jing.html'

# 异体归一映射（两边都过）
NORM={'纒':'缠','様':'样','覔':'觅','騐':'验','靣':'面','縁':'缘','兠':'兜','皃':'貌',
      '祻':'祸','鬭':'斗','髙':'高','隠':'隐','揷':'插','掲':'揭','枱':'台','屛':'屏',
      '廽':'回','住':'驻','防':'护','唌':'涎'}
PUNCT=re.compile(r'[\s，。、；：？！「」『』（）【】〈〉《》·•．,.:;?!"\'「」…—–※\*]')

def norm(t):
    for k,v in NORM.items(): t=t.replace(k,v)
    return PUNCT.sub('',t)

lib=norm(open(LIB,encoding='utf-8').read())
page=open(PAGE,encoding='utf-8').read()

fails=0
# ---------- 1. 引文核验：.q / .qv 块 ----------
# 先剥 script
page_nos=re.sub(r'<script[\s\S]*?</script>','',page)
# 抓 .q 块（div/p class 含 q）与 .qv span；块边界切分
qblocks=[]
for m in re.finditer(r'<(div|p|span)[^>]*class="([^"]*\bq\b[^"]*|\bqv\b[^"]*)"[^>]*>([\s\S]*?)</\1>', page_nos):
    tag,cls,inner=m.group(1),m.group(2),m.group(3)
    # 剥出处注与内层标签
    inner=re.sub(r'<span class="src">[\s\S]*?</span>','',inner)
    txt=re.sub(r'<[^>]+>','',inner)
    txt=html.unescape(txt)
    if not txt.strip(): continue
    qblocks.append((cls,txt))
print(f'引文块数: {len(qblocks)}')
for i,(cls,txt) in enumerate(qblocks):
    n=norm(txt)
    c=lib.count(n)
    ok=c>=1
    if not ok:
        fails+=1
        print(f'  FAIL[{i}] ({cls}) {txt[:50]}')
print(f'引文核验: {"PASS" if fails==0 else str(fails)+" FAIL"}')

# ---------- 2. 白话反扫：剥引文后 6 字窗 ----------
body=re.sub(r'<script[\s\S]*?</script>','',page)
# 剥 q/qv 块内容
body=re.sub(r'<(div|p|span)[^>]*class="[^"]*\b(q|qv)\b[^"]*"[^>]*>[\s\S]*?</\1>','',body)
body=re.sub(r'<script[\s\S]*?</script>','',body)
txt=re.sub(r'<[^>]+>',' ',body)
txt=html.unescape(txt)
ntxt=norm(txt)
WIN=6
miss=0
libset=set(lib[i:i+WIN] for i in range(len(lib)-WIN+1))
# 白话逐窗扫描
hits=[]
for i in range(len(ntxt)-WIN+1):
    w=ntxt[i:i+WIN]
    if w in libset:
        hits.append(w)
# 去重
hits=sorted(set(hits))
print(f'白话反扫 6 字窗命中: {len(hits)}')
for h in hits[:30]:
    print('  HIT:',h)
    fails+=1

# ---------- 3. JS 内白话（script 内容，引文走 #qb 已核） ----------
scripts=re.findall(r'<script[\s\S]*?</script>',page)
js=re.sub(r'<[^>]+>',' ',' '.join(scripts))
js=re.sub(r'/\*[\s\S]*?\*/','',js)
njs=norm(js)
jhits=set(w for i in range(len(njs)-WIN+1) if (w:=njs[i:i+WIN]) in libset)
# JS 中允许出现引文库内容（已核），过滤：命中窗若完全在引文串内则豁免
qall=norm(''.join(t for _,t in qblocks))
real=[w for w in jhits if w not in qall]
print(f'JS 反扫命中: {len(jhits)}（豁免引文库内 {len(jhits)-len(real)}）')
for h in real[:20]:
    print('  JSHIT:',h)
    fails+=1

# ---------- 4. 红线 ----------
if '—' in page or '–' in page:
    print('红线: 长划线存在'); fails+=1
for ln,line in enumerate(page.split('\n'),1):
    if line.count('·')>1:
        print(f'红线: 行{ln} · 超标'); fails+=1
if '第〇〇篇' not in page:
    print('提示: 缺篇号占位')
print('TOTAL:', 'PASS' if fails==0 else f'{fails} PROBLEMS')
sys.exit(0 if fails==0 else 1)
