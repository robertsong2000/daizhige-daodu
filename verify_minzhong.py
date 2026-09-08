#!/usr/bin/env python3
# 核验 minzhong-haicuo-shu.html：引文双侧比对 + 反扫 + 排版规则 + 结构断言 + JS 数据联检
import re, sys, unicodedata

PAGE = 'minzhong-haicuo-shu.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/闽中海错疏.txt'

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[^\w]', '', s)

raw = open(PAGE, encoding='utf-8').read()
lib_raw = open(LIB, encoding='utf-8').read()
fails = []

lib_flat = re.sub(r'\s', '', lib_raw)
n_flat = len(lib_flat)
L = norm(lib_raw)

# ---- 引文提取：正文 <q>/「」 + script 内 <q>/「'' ----
quotes = []
doc = re.sub(r'<script\b.*?</script>', '', raw, flags=re.S)
doc = re.sub(r'<style\b.*?</style>', '', doc, flags=re.S)
for m in re.finditer(r'<q[^>]*>(.*?)</q>', doc, flags=re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1))
    quotes.append(('body<q>' + str(len(quotes)+1), inner))
doc_nq = re.sub(r'<q[^>]*>.*?</q>', '', doc, flags=re.S)
text = re.sub(r'<[^>]+>', '\n', doc_nq)
for m in re.finditer(r'「([^」]+)」', text):
    quotes.append(('body「」' + str(len(quotes)+1), m.group(1)))
for m in re.finditer(r'『([^』]+)』', text):
    quotes.append(('body『』' + str(len(quotes)+1), m.group(1)))
scripts = ''.join(re.findall(r'<script\b.*?</script>', raw, flags=re.S))
s_txt = re.sub(r'<[^>]+>', '\n', scripts)
for m in re.finditer(r'「([^」]+)」', s_txt):
    quotes.append(('js「」' + str(len(quotes)+1), m.group(1)))

nq = sum(1 for _, q in quotes if len(norm(q)) >= 2)
print(f'引文总数: {len(quotes)}（norm≥2 计 {nq}）')
uniq = {norm(q) for _, q in quotes if len(norm(q)) >= 2}
print(f'去重后: {len(uniq)}')
for tag, q in quotes:
    n = norm(q)
    if len(n) < 2:
        continue
    if n not in L:
        fails.append(f'引文核验失败 [{tag}]: {q[:70]}')

# ---- 残文反扫 >=6 字组撞库（script 已剥除，<q>「」已剥）----
residual = re.sub(r'「[^」]*」', '', text)
residual = re.sub(r'『[^』]*』', '', residual)
for ln in residual.split('\n'):
    n = norm(ln)
    for i in range(len(n) - 5):
        g = n[i:i+6]
        if g in L:
            fails.append(f'反扫撞库: {g}  行: {ln.strip()[:60]}')
            break

# ---- 排版规则 ----
if '—' in raw or '–' in raw:
    fails.append('出现长划线 —/–')
for i, ln in enumerate(raw.split('\n'), 1):
    if ln.count('·') > 1:
        fails.append(f'第{i}行 · 超限: {ln.strip()[:60]}')
low = raw.lower()
for pat, msg in [('<link', '外部 <link'), ('@import', '@import'), ('url(', 'css url('),
                 ('<img', '<img'), ('<script src', '外链 script'), ('http://', 'http://')]:
    if pat in low:
        fails.append(f'外部依赖: {msg}')
if low.count('https://') != 1 or 'github.com/robertsong2000/daizhigev20' not in low:
    fails.append('https 引用数异常（应为仅页脚仓库链接 1 处）')
for a, b, msg in [('<div', '</div>', 'div'), ('<q', '</q>', 'q'), ('<section', '</section>', 'section'),
                  ('<footer', '</footer>', 'footer'), ('<button', '</button>', 'button')]:
    if raw.count(a) != raw.count(b):
        fails.append(f'标签不配平: {msg} {raw.count(a)}/{raw.count(b)}')
for token in ['殆知阁古代文献', '逐字核验', '历史眼光', 'href="mulu.html"']:
    if token not in raw:
        fails.append(f'页脚缺: {token}')

# ---- 库本统计 ----
print(f'库本: 去空白 {n_flat} 字')
if n_flat != 11558:
    fails.append(f'库本去空白字数变动: {n_flat}')

# ---- 结构断言 ----
if raw.count('class="kcard"') != 5:
    fails.append(f'翻板数异常: {raw.count("class=\"kcard\"")} != 5')
mitems = re.findall(r"\{ t: '([^']+)'", scripts)
print(f'谱册条目: {len(mitems)}')
if len(mitems) != 46:
    fails.append(f'谱册条目数异常: {len(mitems)} != 46')
if len(set(mitems)) != len(mitems):
    fails.append('谱册条目名重复')
mq = re.findall(r'id="(q-an-[a-z0-9]+)"', raw)
refs = set(re.findall(r"an: '([a-z0-9,-]+)'", scripts))
need = set()
for r in refs:
    need.update(r.split(','))
missing = need - set(mq)
if missing:
    fails.append(f'an 引用缺 qbank 条目: {missing}')
unused = set(mq) - need
if unused:
    print(f'未引用 qbank 条目: {sorted(unused)}')

# ---- JS 内不得出现 <q 字面量 ----
if '<q' in scripts or '</q' in scripts:
    fails.append('script 内出现 <q 字面量')

if fails:
    print('\n== 失败 ==')
    for f in fails:
        print('✗', f)
    sys.exit(1)
print('\n全部通过 ✓')
