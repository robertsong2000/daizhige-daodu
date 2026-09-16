#!/usr/bin/env python3
# build chan-shu.html: slice quotes from library with unique-anchor assertions, inject into template
import re, sys, unicodedata

REPO = '/home/robertsong/workspace/claude/daizhige-daodu'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/谗书.txt'
TPL = REPO + '/chan-shu.tpl.html'
OUT = REPO + '/chan-shu.html'

raw = open(LIB, encoding='utf-8').read()
# strip editorial bracket notes and defect boxes
lib = re.sub(r'\[[^\]]*\]', '', raw)
lib = lib.replace('□', '')

def norm(s):
    return ''.join(c for c in s if unicodedata.category(c)[0] in 'LN')

NL = norm(lib)

def slice_q(start, end=None):
    i = lib.count(start)
    assert i == 1, f'anchor not unique ({i}): {start[:20]}'
    a = lib.index(start)
    if end is None:
        return start
    assert lib.count(end) == 1, f'end anchor not unique: {end[:20]}'
    b = lib.index(end, a) + len(end)
    seg = lib[a:b]
    assert '［' not in seg and '[' not in seg, f'bracket leaked into quote: {seg[:40]}'
    return seg

QUOTES = {
  'epigraph': slice_q('物之小兮迎网而毙', '腹之馁兮。吁！'),
  'spider':   slice_q('秋虫，蜘蛛也。致身网罗间', '实腹亦网罗间。'),
  'c1': slice_q('以所试不如人', '用公道落去。'),
  'c2': slice_q('然文章之兴不为举场也', '不为举场也，明矣。'),
  'c3': slice_q('君子有其位', '诫将来也。'),
  'c4': slice_q('所以不废谗书也', '不亦宜乎！'),
  't1': slice_q('其畜养者', '故谓之天鸡。'),
  't2': slice_q('非毛羽彩错', '道之坏也有是夫！'),
  'h1': slice_q('视玉帛而取之者', '则曰救彼涂炭。'),
  'h2a': slice_q('而西刘则曰', '居宜如是。'),
  'h2b': slice_q('楚籍则曰', '可取而代。'),
  'h3': slice_q('意彼未必无退逊之心', '然后生其谋耳。'),
  'h4': slice_q('是以峻宇逸游', '鲜也。'),
  'y1': slice_q('吾秉箕箒', '何尝不言通达。'),
  'y2': slice_q('以匡国致君为己任', '以安民济物为心期'),
  'y3': slice_q('以吾观之', '又安可食其食？'),
  'y4': slice_q('乃闭气而死。'),
  's1': slice_q('由是万岁之声', '东山万岁之声也。'),
  's2': slice_q('以一山之呼', '况千口万口者乎？'),
  's3': slice_q('是以东封之呼', '英主之不幸。'),
  'x1': slice_q('然食人之食', '理也。况妾乎。'),
  'x2': slice_q('谋及媍人者必亡', '惜其不用。'),
  'x3': slice_q('余前过大行时', '固拾于编简。'),
  'r1': slice_q('是位胜其道', '天下不得不理也。'),
  'r2': slice_q('是位不胜其道', '天下不得不乱也。'),
  'r3': slice_q('穷仲尼于乱也', '故庙之于后。'),
  'p1': slice_q('有其位则执大柄以定是非'),
  'p2': slice_q('无其位则着私而疏善恶'),
}
for k, v in QUOTES.items():
    n = norm(v)
    assert len(n) >= 5, f'quote too short: {k}'
    assert n in NL, f'quote not in library: {k} :: {n[:30]}'
print('quotes sliced:', len(QUOTES))

# volume structure -> pu wall columns
lines = [l.strip().strip('　') for l in raw.split('\n')]
titles = []   # (vol_idx, title, is_missing)
vol = -1
for l in lines:
    s = l.strip().replace('　', '')
    if not s:
        continue
    m = re.match(r'^谗书卷第([一二三四五])$', s)
    if m:
        vol = '一二三四五'.index(m.group(1))
        continue
    if vol < 0:
        continue
    if len(s) > 16 or re.search(r'[，。！？：；「」（)]', s.split('[')[0]):
        continue
    mm = re.match(r'^([^（\[]+?)(\[原阙[^\]]*\])?$', s)
    if not mm or not mm.group(1):
        continue
    titles.append((vol, mm.group(1), bool(mm.group(2))))
counts = [0] * 5
for v, t, miss in titles:
    counts[v] += 1
assert [c for c in counts] == [12, 12, 11, 12, 13], counts
assert len(titles) == 60, len(titles)
print('volumes:', counts, 'total', len(titles))

cols = []
for v in range(5):
    items = []
    for vv, t, miss in titles:
        if vv != v:
            continue
        items.append(('<i>■</i>' if miss else '') + t)
    qh = f'<div class="qh">卷{["一","二","三","四","五"][v]} · {counts[v]}篇</div>'
    qv = '<div class="qv">' + ''.join(f'<span class="pt">{it}</span>' for it in items) + '</div>'
    pn = '<div class="pn">■ 有目无文</div>' if any(m for _, _, m in titles if _ == v) else ''
    cols.append(f'<div class="pcol">{qh}{qv}{pn}</div>')
# per-title containment + volume order check (titles are not contiguous in lib: bodies intervene)
pos = -1
for v, t, miss in titles:
    nt = norm(t)
    assert nt in NL, f'title not in lib: {t}'
    i = NL.find(nt, pos + 1)
    assert i > pos, f'title out of order: {t}'
    pos = i
print('pu titles: 60 individually verified, order monotonic')

tpl = open(TPL, encoding='utf-8').read()
for k, v in QUOTES.items():
    tpl = tpl.replace(f'⟦Q:{k}⟧', v)
assert '⟦Q:' not in tpl, 'unfilled quote placeholder'
tpl = tpl.replace('⟦PU⟧', '\n      '.join(cols))
# spacing audit of counts in copy
assert '篇目六十' in tpl and len(titles) == 60
assert tpl.count('夹注六十四处') == 1 and raw.count('枚庵校本') == 64
open(OUT, 'w', encoding='utf-8').write(tpl)
print('written', OUT, len(tpl), 'bytes')
