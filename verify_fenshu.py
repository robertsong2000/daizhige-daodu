#!/usr/bin/env python3
# verify_fenshu.py: fenshu.html vs 库本 焚书.txt
import re, pathlib, sys

ROOT = pathlib.Path(__file__).parent
SRC = pathlib.Path('/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/焚书.txt')
lib = SRC.read_text(encoding='utf-8')
lib_n = re.sub(r'\s', '', lib)
PUNCT = re.compile(r'[，。、；：？！「」『』《》（）…·　\s,.:;!?()"\'\'"”’]')
lib_np = PUNCT.sub('', lib)

html = (ROOT / 'fenshu.html').read_text(encoding='utf-8')

fail = []
loose = []

def norm(s):
    return re.sub(r'\s', '', s)

def norm_p(s):
    return PUNCT.sub('', s)

def check(text, tag):
    t = norm(text)
    if not t:
        return
    if t in lib_n:
        return 'strict'
    if norm_p(text) and norm_p(text) in lib_np:
        loose.append((tag, t[:24]))
        return 'loose'
    fail.append(f'{tag} not verbatim in lib: {t[:34]}')
    return None

# 1. collect quote blocks from page
def strip_inner(text):
    text = re.sub(r'<span class="attr">.*?</span>', '', text, flags=re.S)
    return re.sub(r'<[^>]+>', '', text)

quotes = []
for m in re.finditer(r'<(\w+)([^>]*class="[^"]*\bq\b[^"]*"[^>]*)>(.*?)</\1>', html, re.S):
    quotes.append(('q-block', strip_inner(m.group(3))))
for sel in [r'<div class="ke-reveal"[^>]*>(.*?)</div>',
            r'<span class="lian-item">(.*?)</span>',
            r'<span class="say">(.*?)</span>',
            r'<span class="gap">(.*?)</span>',
            r'<div class="yeju"[^>]*>(.*?)</div>',
            r'<div class="zhi-retort"[^>]*>(.*?)</div>',
            r'<p class="big-q"[^>]*>(.*?)</p>',
            r'<span class="bd"><b>(.*?)</b></span>']:
    for m in re.finditer(sel, html, re.S):
        quotes.append(('block', re.sub(r'<[^>]+>', '', m.group(1))))
# 2. 「…」 spans in rendered text
body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
for m in re.finditer(r'「(.*?)」', body, re.S):
    quotes.append(('corner', m.group(1)))
# 3. zqs array in script
script = re.search(r'<script>(.*?)</script>', html, re.S).group(1)
zblock = re.search(r'var zqs = \[(.*?)\];', script, re.S).group(1)
zqs = re.findall(r"'([^']+)'", zblock)

tags = {}
for i, (tag, q) in enumerate(quotes):
    tags.setdefault(norm(q), tag)
    check(q, f'{tag}#{i}')
for i, q in enumerate(zqs):
    check(q, f'zqs#{i}')

# dedupe within q-blocks only (corner/block categories may overlap by design)
qblocks = [norm(q) for t, q in quotes if t == 'q-block']
if len(set(qblocks)) != len(qblocks):
    fail.append('duplicate q-blocks on page')

# 4. red lines
for ch, name in [('—', 'em-dash'), ('–', 'en-dash')]:
    if ch in html:
        fail.append(f'{name} present')
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fail.append(f'line {i} has more than one interpunct')
# 5. footer trio + numbering + char claim
for w in ['文本来源', '引文核验', '时代局限', '之一百九十三', '十五万九千四百四十九']:
    if w not in html:
        fail.append(f'page missing {w}')
lib_clean = re.sub(r'\s', '', lib)
if len(lib_clean) != 159449:
    fail.append(f'lib chars {len(lib_clean)} != 159449')
# 6. half-width punctuation in rendered text (URL / script filename whitelisted)
body_w = body.replace('github.com/robertsong2000/daizhigev20', '').replace('verify_fenshu.py', '')
if re.search(r'[,.:;?!]', body_w):
    fail.append('half-width punctuation in rendered text')

if fail:
    print('\nFAIL:')
    for f in fail:
        print(' -', f)
    sys.exit(1)
print(f'  quotes checked: {len(quotes)} blocks + {len(zqs)} zqs, all verbatim')
print(f'  loose tier (punct-only drift): {len(loose)}')
for t, s in loose:
    print('   ~', t, s)
print('  red lines: no long dash, interpunct cap, footer trio, halfwidth punct')
print(f'  lib chars: {len(lib_clean)}')
print('verify_fenshu: ALL PASS')
