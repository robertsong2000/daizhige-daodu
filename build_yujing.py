#!/usr/bin/env python3
"""玉镜新谭导读页 build：库本切片注入 + PUA 检查 + 白话反扫 + 标点规则"""
import re, sys, io

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/玉镜新谭.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/yujing-xintan.tpl.html'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/yujing-xintan.html'

src = open(SRC, encoding='utf-8').read()
src = re.sub(r'^\s+', '', src)  # keep raw for slicing; norm handles the rest
raw = open(SRC, encoding='utf-8').read()

QUOTES = [
 ('Q1',  '市井一亡赖耳', '性多狡诈'),
 ('Q2',  '日务樗蒲为计', '一掷百万'),
 ('Q3',  '思为阉寺', '遂以此净身者'),
 ('Q4',  '昼潜僻巷乞食', '夜投破寺假息'),
 ('Q5',  '我此方司土之神也', '唯此小鬼求赦之'),
 ('Q6',  '言无后福', '安能动鬼神耶'),
 ('Q7',  '唯嘱汝以尊名', '可保令终也'),
 ('Q8',  '今日残生是公所赐也', '唯神是殛'),
 ('Q9',  '身在京华', '一家书者'),
 ('Q10', '凡智慧者化为愚蒙', '未有若此大神通也'),
 ('Q11', '止知有厂臣', '此乾坤倒置时也'),
 ('Q12', '皆崇焕之力', '颂其功焉'),
 ('Q13', '忠贤何人，而敢建祠太学之侧乎', '之俎豆'),
 ('Q14', '魏忠贤生祠，不论在京在外', '不准存留别改'),
 ('Q15', '此杀身之道也', '扇头诗乎'),
 ('Q16', '录用章奏', '不敢窜易一字'),
 ('Q17', '囚首雉经', '而不可得'),
 ('Q18', '凡一切奏章', '而云厂臣者'),
 ('Q19', '天无二日，匪类之称上公', '更为语不择音'),
 ('Q20', '长安中，无贵无贱呼为', '性命矣'),
 ('Q21', '询知恶党之私呼魏忠贤也', '其语何语耶'),
 ('Q22', '从此巩固皇图', '处处周到'),
 ('Q23', '凡诸衙门官吏', '二千里安置'),
 ('Q24', '行至阜丘', '悬于梁上'),
 ('Q25', '越三月，定爰书', '寸磔于市'),
]

def sliceq(a, b):
    i = raw.find(a)
    assert i >= 0, f'start anchor missing: {a}'
    j = raw.find(b, i)
    assert j >= 0, f'end anchor missing: {b}'
    return raw[i:j + len(b)]

def norm(s):
    s = re.sub(r'[\s　]+', '', s)
    s = re.sub(r'[，。！？：；、「」『』（）·…．,.\'"\-—–《》〈〉？！;:]', '', s)
    table = str.maketrans({'艹': '草', '瘖': '喑', '繇': '由', '筭': '算', '僣': '僭'})
    return s.translate(table)

quotes = {}
for qid, a, b in QUOTES:
    s = sliceq(a, b)
    pua = [c for c in s if 0xE000 <= ord(c) <= 0xF8FF]
    assert not pua, f'{qid} contains PUA {pua!r}'
    quotes[qid] = norm(s)
    print(f'{qid}: {len(s)} chars | {s[:40]}')

html = open(TPL, encoding='utf-8').read()

# inject quotes
for qid, _, _ in QUOTES:
    tok = f'__{qid}__'
    assert tok in html, f'token {tok} not in tpl'
    html = html.replace(tok, f'<q>{sliceq(*QUOTES[[q for q,_,_ in QUOTES].index(qid)][1:])}</q>')

assert '__Q' not in html, 'unreplaced token remains'

# ---- check 1: PUA anywhere ----
pua_all = [(hex(ord(c)), i) for i, c in enumerate(html) if 0xE000 <= ord(c) <= 0xF8FF]
assert not pua_all, f'PUA in output: {pua_all[:5]}'

# ---- check 2: no long dashes ----
for ch in ('—', '–'):
    assert ch not in html, f'long dash {ch!r} found'

# ---- check 3: vernacular reverse scan (6-char window) ----
# strip script blocks, then remove q/qv tagged content
body = re.sub(r'<script>.*?</script>', '', html, flags=re.S)
body = re.sub(r'<q\b[^>]*>.*?</q>', '', body, flags=re.S)
body = re.sub(r'<span class="qv"[^>]*>.*?</span>', '', body, flags=re.S)
# drop tags but keep element boundaries as line breaks (no cross-element splicing)
text = re.sub(r'<[^>]+>', '\n', body)
book_norm = norm(raw)
hits = []
for ln in text.split('\n'):
    nt = norm(ln)
    for i in range(len(nt) - 5):
        w = nt[i:i + 6]
        if w in book_norm:
            hits.append((ln.strip()[:30], w))
            break
    if len(hits) > 10:
        break
assert not hits, f'reverse-scan collisions: {[h[1] + " @" + h[0] for h in hits]}'

# ---- check 4: at most one · per rendered line ----
bad_dot = []
for ln in re.sub(r'<[^>]+>', '', re.sub(r'<script>.*?</script>', '', html, flags=re.S)).split('\n'):
    if ln.count('·') > 1:
        bad_dot.append(ln.strip()[:50])
assert not bad_dot, f'multi-dot lines: {bad_dot}'

open(OUT, 'w', encoding='utf-8').write(html)
nq = len(QUOTES)
print(f'OK -> {OUT} | {nq} quotes verified, reverse-scan clean, no PUA, no long dash, dot rule pass')
