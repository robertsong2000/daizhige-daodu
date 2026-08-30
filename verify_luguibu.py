#!/usr/bin/env python3
# 录鬼簿导读页核验：页面全部 .q 逐字对库 + 62 剧目/44 名牌顺序全等 + 分区人数复算 + 红线
import re, sys

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/lugui-bu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/诗藏/剧曲/录鬼簿.txt'

t = open(LIB, encoding='utf-8').read()
h = open(HTML, encoding='utf-8').read()
fails, checks = [], 0

def ck(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)

CJK = r'[一-鿿□]'
def norm(s):
    return ''.join(ch for ch in s if re.match(CJK, ch))

# ---------- 1. 页面全部 .q 逐字对库 ----------
qs = re.findall(r'<span class="q"[^>]*>(.*?)</span>', h, re.S)
ck(len(qs) >= 55, f'.q 数量异常: {len(qs)}')
for i, q in enumerate(qs, 1):
    qn = norm(q)
    ck(len(qn) >= 2, f'引文{i} 过短: {q[:20]}')
    ck(qn in norm(t), f'引文{i} 不在库内: {q[:40]}')

# ---------- 2. 关汉卿 62 剧目：库本顺序与页面 chips 全等 ----------
a = t.find('关汉卿【大都人', 1862)
b = t.find('白仁甫【', a)
lib_drama = []
for ln in t[a:b].split('\n'):
    s = ln.strip('　').strip()
    if not s or s.startswith(('关汉卿', '珠玑语唾')):
        continue
    name = s.split('【')[0]
    if norm(name):
        lib_drama.append(name)
ck(len(lib_drama) == 62, f'库本关汉卿剧目 {len(lib_drama)} != 62')
page_chips = re.findall(r'<span class="chip[^"]*">\s*(?:<a[^>]*>)?\s*<span class="q">([^<]+)</span>', h)
ck(len(page_chips) == 62, f'页面 chips {len(page_chips)} != 62')
ck(page_chips == lib_drama, f'chips 与库本顺序/内容不一致: {[ (p,l) for p,l in zip(page_chips, lib_drama) if norm(p)!=norm(l) ][:3]}')

# ---------- 3. 名公 44 名牌顺序全等 ----------
a = t.find('○前辈名公乐章传于世者')
b = t.find('○前辈才人有所编传奇行于世者五十六人')
lib_gong = []
for ln in t[a:b].split('\n'):
    if not ln.startswith('　　'):
        continue
    s = ln.strip('　').strip()
    if not s or s.startswith(('右', '○')):
        continue
    lib_gong.append(s.split('【')[0])
ck(len(lib_gong) == 44, f'库本名公 {len(lib_gong)} != 44')
page_nm = [x.strip() for x in
           re.findall(r'<span class="nm[^"]*">([^<]*)(?:<span class="tag">[^<]*</span>)?</span>', h)]
ck(len(page_nm) == 44, f'页面名牌 {len(page_nm)} != 44')
ck([norm(x) for x in page_nm] == [norm(x) for x in lib_gong], '名牌与库本不一致')

# ---------- 4. 分区人数机器复算 ----------
def blocks(a, b):
    return [p for p in re.split(r'\n\s*\n', t[a:b]) if p.strip()]

def persons(a, b):
    n = 0
    for p in blocks(a, b):
        lines = [l for l in p.split('\n') if l.strip()]
        first = lines[0]
        if not first.startswith('　　'):
            continue
        s = first.strip('　')
        if re.match(r'^[^【】\n]{1,14}【', s):
            n += 1
        elif len(lines) == 1 and len(s) <= 6 and not re.search(r'[，。、』》』：]', s) \
                and not s.startswith(('右', '已上', '增补')):
            n += 1
    return n

def seg(x, y):
    return t.find(x), t.find(y)

aa, bb = seg('○前辈才人有所编传奇行于世者五十六人', '●录鬼簿卷下')
ck(persons(aa, bb) == 56, f"才人 {persons(aa,bb)} != 56")
aa, bb = seg('○方今才人相知者，为之作传，以〔凌波仙〕曲吊之', '○已死才人不相知者')
ck(persons(aa, bb) == 18, f"相知 {persons(aa,bb)} != 18")
aa, bb = seg('○已死才人不相知者', '○方今知名才人')
ck(persons(aa, bb) == 9, f"已死不相知 {persons(aa,bb)} != 9")
aa, bb = seg('○方今知名才人', '○方今才人闻名而不相知者')
ck(persons(aa, bb) == 19, f"知名才人 {persons(aa,bb)} != 19")
aa, bb = seg('○方今才人闻名而不相知者', '●录鬼簿续编')
ck(persons(aa, bb) == 4, f"闻名不相知 {persons(aa,bb)} != 4")
aa, bb = seg('●录鬼簿续编', '●目录')
bb = t.find('●目录', aa)
xb = persons(aa, bb)
ck(xb == 87, f"续编 {xb} != 87")
ck(44 + 56 + 18 + 9 + 19 + 4 == 150, '合计 != 150')

# ---------- 5. 页面数字与库本口径 ----------
ck('50,362' in h and len(t) == 50362, f"全帙字数不符: {len(t)}")
ck('43,115' in h and len(re.sub(r'\s', '', t)) == 43115, f"去空白字数不符: {len(re.sub(chr(92)+'s','',t))}")
for frag in ['太保刘公秉忠', '金元曲家一百五十二人', '四百五十二种',
             '王思顺等三十三人', '一十八人', '八十九人', '百五十一人', '五十六人']:
    ck(frag in t, f'库本缺片段: {frag}')
    ck(frag in h, f'页面缺片段: {frag}')

# ---------- 6. 红线 ----------
ck('—' not in h, '页面出现长划线 —')
ck('–' not in h, '页面出现 en dash –')
for i, ln in enumerate(h.split('\n'), 1):
    ck(ln.count('·') <= 1, f'第{i}行 · 超限: {ln.strip()[:40]}')
ck('�' not in h, '页面出现 U+FFFD')
ck(not any('' <= c <= '' for c in h), '页面出现 PUA 缺字')
ck('<title>录鬼簿 · 殆知阁导读之八十三</title>' in h, 'title 序号不符')

# ---------- 7. 页脚与来源 ----------
for frag in ['殆知阁简体库', 'daizhigev20', '逐字核验', '古今之别']:
    ck(frag in h, f'页脚缺: {frag}')

print(f'共 {checks} 项检查，{len(qs)} 条 .q，{len(page_chips)} chips，{len(page_nm)} 名牌')
if fails:
    print('FAIL:')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('ALL PASS')
