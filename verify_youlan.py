# 碣石调幽兰 导读页核验：引文逐字对库 + 反扫 + 排版规则 + 库本机数
import re, sys, unicodedata

LIB = 'daizhige-simplified/艺藏/音乐/碣石调幽兰.txt'
PAGE = 'daizhige-daodu/jieshi-diao-youlan.html'

raw = open(LIB, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()
errs, warns = [], []

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        cat = unicodedata.category(ch)
        if cat.startswith('P'):   # 去标点；保留｜(Sm)等符号
            continue
        out.append(ch)
    return ''.join(out)

nlib = norm(raw)

# ---- 库本机数 ----
flat = re.sub(r'\s', '', raw)
if len(flat) != 5224: errs.append(f'库本去空白 {len(flat)} != 5224')
if raw.count('拍之') != 4: errs.append('拍之 != 4')
lines = [l.strip() for l in raw.split('\n')]
i0, i1 = lines.index('幽兰 第五'), lines.index('碣石调幽兰第五 此弄宜缓消息弹之')
if sum(l.count('一句') for l in lines[i0:i1] if not l.startswith('拍之')) != 45:
    errs.append('谱内一句 != 45')
tunes_lib = []
for l in lines[lines.index('碣石调幽兰第五 此弄宜缓消息弹之') + 1:]:
    if l.startswith('注') or l.startswith('（注'):
        break
    tunes_lib += [x for x in re.split(r'\s{2,}|　+| +', l) if x]
if len(tunes_lib) != 59: errs.append(f'曲目 {len(tunes_lib)} != 59')

# ---- 排版规则 ----
if '—' in html or '–' in html: errs.append('出现长划线')
for i, l in enumerate(html.split('\n'), 1):
    if l.count('·') > 1: errs.append(f'行{i} · 超1')
for pat, name in [('<script src', '外部脚本'), ('<link', '外部link'), ('@import', '外部import'),
                  ('url(http', '外部资源'), ('<img', '外链图片'), ('src="http', '外链src')]:
    if pat in html: errs.append('外部依赖: ' + name)
for kw in ['文本来源', '核验声明', '库本讹字申报', '使用提醒', 'mulu.html', 'github.com/robertsong2000/daizhigev20']:
    if kw not in html: errs.append('页脚缺: ' + kw)

# ---- 摘除程序直出区（谱卷/曲目墙），单独核 ----
score_blocks = re.findall(r'<section class="pai">.*?</section>', html, re.S)
if len(score_blocks) != 4: errs.append(f'谱段 {len(score_blocks)} != 4')
sec_counts = []
sents_all = []
for blk in score_blocks:
    sents = re.findall(r'<div class="sent">(.*?)</div>', blk, re.S)
    sec_counts.append(len(sents))
    for s in sents:
        s = re.sub(r'<span class="sn mono">\d+</span>', '', s)
        t = norm(re.sub(r'<[^>]+>', '', s))
        sents_all.append(t)
if sec_counts != [14, 17, 8, 6]: errs.append(f'各拍句数 {sec_counts} != [14,17,8,6]')
if len(sents_all) != 45: errs.append(f'谱句 {len(sents_all)} != 45')
for k, t in enumerate(sents_all, 1):
    if t not in nlib: errs.append(f'谱句{k}不在库本: {t[:20]}')

rest = re.sub(r'<section class="pai">.*?</section>', '', html, flags=re.S)
wall = re.search(r'<div class="wall" data-lib="tunes">(.*?)</div>', rest, re.S)
tn = re.findall(r'<span class="tn[^"]*">([^<]+)</span>', wall.group(1))
if len(tn) != 59: errs.append(f'页面曲目 {len(tn)} != 59')
for t in tn:
    if norm(t) not in nlib: errs.append('曲目不在库本: ' + t)
rest = rest.replace(wall.group(0), '')

# ---- 引文核验：「」与『』 ----
quotes = re.findall(r'「([^」]+)」', rest) + re.findall(r'『([^』]+)』', rest)
nq = 0
for q in quotes:
    t = norm(q)
    if len(t) < 2: continue
    nq += 1
    if t not in nlib: errs.append('引文不在库本: ' + q[:40])

# ---- 申报的展示型原文（无引号直排）----
DECLARED = [
    norm('丘公字明，会稽人也。梁末隐于九疑山，妙绝楚调，于幽兰一曲尤特精绝。以其声微而志远，而不堪授人。以陈祯明三年，授宜都王叔明。随开皇十年，于丹阳县卒，年九十七。无子传之，其声遂简耳。'),
    '以其声微而志远而不堪授人',
    '丘公云自齐撮以下有若仙声',
    '此弄宜缓消息弹之',
]
rest_norm0 = norm(re.sub(r'<[^>]+>', '', rest))
for d in DECLARED:
    if d not in nlib: errs.append('申报原文不在库本: ' + d[:24])

# ---- 反扫：去引文/申报后，不得与库本成句（≥6字）相撞 ----
nrest = rest_norm0
for d in DECLARED:
    if d not in nrest:
        errs.append('申报原文未在页面出现: ' + d[:16])
        continue
    nrest = nrest.replace(d, '�')
for q in sorted({norm(q) for q in quotes if len(norm(q)) >= 2}, key=len, reverse=True):
    nrest = nrest.replace(q, '�')
big = {nlib[i:i+6] for i in range(len(nlib) - 5)}
hits = []
i = 0
while i < len(nrest) - 5:
    g = nrest[i:i+6]
    if '�' in g:
        i += 1; continue
    if g in big:
        hits.append((i, g)); i += 6
    else:
        i += 1
for i, g in hits:
    errs.append(f'反扫撞库 @{i}: {g}')

# ---- mulu 联检（若已收录）----
try:
    mulu = open('daizhige-daodu/mulu.html', encoding='utf-8').read()
    nums = sorted(int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', mulu))
    if nums and nums != list(range(1, len(nums) + 1)):
        errs.append('mulu 编号不连续')
    if mulu.count('href="jieshi-diao-youlan.html"') != 1:
        errs.append('mulu 中幽兰条目重复或缺失')
except FileNotFoundError:
    warns.append('mulu 未检')

print(f'引文 {nq} 条 | 谱句 45 | 曲目 59 | 申报 {len(DECLARED)} 条 | 反扫撞库 {len(hits)}')
for w in warns: print('WARN:', w)
if errs:
    print('FAIL', len(errs))
    for e in errs[:30]: print(' -', e)
    sys.exit(1)
print('ALL PASS')
