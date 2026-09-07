#!/usr/bin/env python3
# 核验 xiangxing-gongan.html 全部引文与案签标题，与库内文件逐字比对（去标点+NFKC 归一）
import re, unicodedata, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/职官/鼎镌国朝名公神断详刑公案.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/xiangxing-gongan.html'

PUNC = re.compile(r'[\s，。：；、「」『』‘’“”！？（）《》〈〉…·\-—–,.\'\"!?()【】〔〕\[\]]+')

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return PUNC.sub('', s)

src = norm(open(SRC, encoding='utf-8').read())
html = open(HTML, encoding='utf-8').read()

fails = []
n = 0

# 1) 全部 class="qq" 引文（跳过 data-plain 的署名，它们也在库本中，一并核验即可）
for m in re.finditer(r'<span class="qq"[^>]*>(.*?)</span>', html, re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1))
    n += 1
    if norm(inner) not in src:
        fails.append(('QQ', inner[:60]))

# 2) 全部案签与精读标题 class="vt"
vt_titles = []
for m in re.finditer(r'<span class="qn vt">(.*?)</span>', html, re.S):
    vt_titles.append(re.sub(r'<[^>]+>', '', m.group(1)))
for m in re.finditer(r'<h3 class="vt">(.*?)</h3>', html, re.S):
    vt_titles.append(re.sub(r'<[^>]+>', '', m.group(1)))
seen = set()
for t in vt_titles:
    if t in seen: continue
    seen.add(t)
    n += 1
    if norm(t) not in src:
        fails.append(('VT', t))

# 3) 类名（data-cat + 「类」）与官衔（.qk）
cats = set(re.findall(r'data-cat="([^"]+)"', html))
for c in sorted(cats):
    n += 1
    if norm(c + '类') not in src:
        fails.append(('CAT', c))
ranks = set(re.findall(r'<span class="qk">([^<]+)</span>', html))
for r in sorted(ranks):
    n += 1
    if norm(r) not in src:
        fails.append(('RANK', r))

# 4) 署名（data-plain qq 已在 step1 核验，这里单独报数）
print(f'核验总数: {n} 处（引文 {sum(1 for _ in re.finditer(r"<span class=\"qq\"", html))} + 标题 {len(seen)} + 类名 {len(cats)} + 官衔 {len(ranks)}）')
if fails:
    print('FAILED:')
    for k, s in fails:
        print(' ', k, s)
    sys.exit(1)
print('ALL PASS: 引文与标题均与库内文件去标点 NFKC 归一后逐字比对一致')
