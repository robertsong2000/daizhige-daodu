#!/usr/bin/env python3
"""取经诗话 导读页核验：引文逐字比对库本 + 17段题机校 + 反扫 + 排版红线 + mulu连续性"""
import re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/诗藏/诗话/大唐三藏取经诗话.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/qujing-shihua.html'
MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'

lib = open(LIB, encoding='utf-8').read()
page = open(HTML, encoding='utf-8').read()

def norm(s):
    s = re.sub(r'\s+', '', s)
    return ''.join(ch for ch in s if unicodedata.category(ch)[0] not in ('P', 'S', 'Z'))

lib_n = norm(lib)
fails = 0
nq = 0

def check(label, text):
    global fails, nq
    qn = norm(text)
    if not qn:
        print(f'[FAIL] 空引文 {label}'); fails += 1; return
    nq += 1
    if qn in lib_n:
        print(f'[OK]   {label}')
    else:
        print(f'[FAIL] 库本无此句: {label} -> {qn[:40]}'); fails += 1

# 1. <q> 元素（剥内层标签，含夹注 span）
for m in re.finditer(r'<q class="q">(.*?)</q>', page, re.S):
    body = re.sub(r'<[^>]+>', '', m.group(1))
    check(body.strip()[:24], body)
    for ch in body:
        o = ord(ch)
        if 0xE000 <= o <= 0xF8FF or 0xF900 <= o <= 0xFAFF or o > 0xFFFF:
            print(f'       注意 特殊字符 U+{o:04X} {ch!r}'); fails += 1

# 2. 「」行内引文（全源扫描，含 JS 字符串；剥标签后核验）
for m in re.finditer(r'「([^」]*)」', page):
    t = re.sub(r'<[^>]+>', '', m.group(1))
    if norm(t):
        check('「' + t[:20] + '」', t)

# 3. poem 块（剥标签后应整段在库本）
for m in re.finditer(r'<div class="poem">(.*?)</div>', page, re.S):
    body = re.sub(r'<[^>]+>', '', m.group(1))
    # 上下两联各自核验（br 分隔的两联在库本相邻）
    parts = [p for p in re.split(r'<br\s*/?>', m.group(1)) if norm(p)]
    for p in parts:
        check('poem联 ' + norm(p)[:14], re.sub(r'<[^>]+>', '', p))

# 4. 17 段题机校（ST 数组 t 值须为库本目录行）
titles = re.findall(r'\{v:"[上中下]",no:"[^"]*",t:"([^"]+)"', page)
if len(titles) != 17:
    print(f'[FAIL] ST 段数 {len(titles)} != 17'); fails += 1
else:
    print(f'[INFO] ST 段数 17')
for t in titles:
    if norm(t) in lib_n:
        print(f'[OK]   段题 {t}')
    else:
        print(f'[FAIL] 段题不在库本: {t}'); fails += 1
lost = len(re.findall(r'lost:1', page))
print(f'[INFO] 亡题段数 {lost}（应为2）')
if lost != 2:
    fails += 1

# 5. 反扫：剔除已核验区域后，正文任意 6 字连串不得撞库（书名自身除外）
scrub = re.sub(r'<q class="q">.*?</q>', '\n', page, flags=re.S)
scrub = re.sub(r'「[^」]*」', '\n', scrub)
scrub = re.sub(r'<div class="poem">.*?</div>', '\n', scrub, flags=re.S)
scrub = re.sub(r'no:"[^"]*",t:"[^"]*"', '\n', scrub)
# 归属标签与出处条（段题或自撰短语，段题已由第4节机校覆盖）
scrub = re.sub(r'<span class="bq-src">.*?</span>', '\n', scrub, flags=re.S)
scrub = re.sub(r'<div class="ltag">.*?</div>', '\n', scrub, flags=re.S)
scrub = re.sub(r'<span class="who">.*?</span>', '\n', scrub, flags=re.S)
scrub = re.sub(r'<span class="lost">.*?</span>', '\n', scrub, flags=re.S)
# JS 吐猴计数词组：逐条为已核验大引文的子串
scrub = re.sub(r'var cyc=\[[^\]]*\]', '\n', scrub)
plain = re.sub(r'<[^>]+>', '', scrub)
hits = set()
SPLIT = r'[\s，。；：！？、,.;:!?\n\r()\[\]{}"\'《》〈〉（）：·]'
for clause in re.split(SPLIT, plain):
    if '大唐三藏取经诗话' in clause:
        clause = clause.replace('大唐三藏取经诗话', '')
    for i in range(len(clause) - 5):
        w = clause[i:i+6]
        if norm(w) and norm(w) in lib_n:
            hits.add(w)
if hits:
    fails += 1
    print(f'[FAIL] 反扫撞库 {len(hits)} 处（未标记的库本原话）:')
    for h in sorted(hits):
        print(f'       -> {h}')
else:
    print('[OK]   反扫 6 字窗零撞库')

# 6. 排版红线
for bad, name in [('—', '长划线—'), ('–', '短划线–'), ('─', '制表线─'), ('│', '竖线│')]:
    if bad in page:
        print(f'[FAIL] 出现 {name}'); fails += 1
for i, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        print(f'[FAIL] 第{i}行有{line.count("·")}个·'); fails += 1

# 7. 结构配平与页脚三件套
for tag in ('div', 'q', 'section', 'blockquote'):
    o = len(re.findall(f'<{tag}[ >]', page)); c = page.count(f'</{tag}>')
    if o != c:
        print(f'[FAIL] <{tag}> 不配平 开{o}闭{c}'); fails += 1
for kw in ('文本来源', '库外申报', '时代局限提醒', 'daizhigev20'):
    if kw not in page:
        print(f'[FAIL] 页脚缺 {kw}'); fails += 1
ext = re.findall(r'https?://[^"\'< )]+', page)
if len(ext) != 1 or 'daizhigev20' not in ext[0]:
    print(f'[FAIL] 外链异常: {ext}'); fails += 1
else:
    print(f'[OK]   外链仅页脚仓库 1 处')

print(f'[INFO] 共核验引文/段题 {nq} 条（含段题与「」行内）')

# 8. mulu 联动（页面已入 mulu 时才查）
if 'qujing-shihua.html' in open(MULU, encoding='utf-8').read():
    m = open(MULU, encoding='utf-8').read()
    nos = sorted(int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', m))
    if nos == list(range(1, len(nos) + 1)):
        print(f'[OK]   mulu 编号 1..{nos[-1]} 连续')
    else:
        print(f'[FAIL] mulu 编号断号: max={nos[-1]} 条数={len(nos)}'); fails += 1
    kc = re.search(r'殆知阁古代文献 · ([一二三四五六七八九十百零\d]+)篇导读合订', m)
    fc = re.search(r'([一二三四五六七八九十百零\d]+)篇导读', m)
    print(f'[INFO] kicker={kc.group(1) if kc else "?"} footer={fc.group(1) if fc else "?"}')
else:
    print('[INFO] mulu 尚未收录本页，跳过联动检查')

print('RESULT:', 'PASS' if fails == 0 else f'FAIL({fails})')
sys.exit(0 if fails == 0 else 1)
