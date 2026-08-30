#!/usr/bin/env python3
# verify_yinshan.py 〈饮膳正要〉导读页核验
import re, sys

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yinshan-zhengyao.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/饮膳正要.txt'

html = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()
lines = lib.split('\n')
lib_n = norm_ne = None
def _strip_ws(s): return re.sub(r'\s', '', s)

def norm(s):
    out = []
    for ch in s:
        if '一' <= ch <= '鿿':
            out.append(ch)
        elif ch.isascii() and ch.isalnum():
            out.append(ch)
    return ''.join(out)

lib_n = norm(lib)          # 归一（去空白去标点）后的库本，页面 .q 同口径比对

fails, checks = [], 0
def ok(cond, msg):
    global checks
    checks += 1
    if not cond: fails.append(msg)

# ---------- 1. 引文扫描（标签配平，闭合标签须完整吃掉） ----------
def collect_spans(html, cls_token):
    spans = []
    for m in re.finditer(r'<(\w+)([^>]*)>', html):
        cm = re.search(r'class="([^"]*)"', m.group(2))
        if not cm or cls_token not in cm.group(1).split():
            continue
        tag = m.group(1)
        i = m.end()
        depth = 1
        pat = re.compile(r'<(/?)' + tag + r'(?=[\s>])')
        while depth > 0:
            n = pat.search(html, i)
            if not n:
                break
            if n.group(1):                       # 闭合标签
                depth -= 1
                i = html.find('>', n.end()) + 1  # 必须越过本闭合标签的 '>'
            else:
                depth += 1
                i = n.end()
        seg = re.sub(r'<[^>]+>', '', html[m.end():i])
        spans.append(seg)
    return spans

qs = collect_spans(html, 'q')
zu = collect_spans(html, 'zui')
ok(len(qs) >= 60, f'.q 引文数量异常: {len(qs)}')
ok(len(zu) == 20, f'.zui 醉墙数量应为 20: {len(zu)}')

for i, q in enumerate(qs, 1):
    n = norm(q)
    if not n:
        fails.append(f'.q #{i} 空引文'); continue
    c = lib_n.count(n)
    if c != 1:
        fails.append(f'.q #{i} 库内出现 {c} 次: {q[:30]}')
for i, z in enumerate(zu, 1):
    if lib_n.count(norm(z)) != 1:
        fails.append(f'.zui #{i} 库内不唯一: {z[:26]}')
print(f'[1] .q {len(qs)} 段 + .zui {len(zu)} 段逐字核验完成')

# ---------- 2. 断口与转引 ----------
ok(lib_n.count(norm('虾不可与')) >= 1, '断口「虾不可与」库内不存在')
ok('class="cut"' in html, '缺断口标记 .cut')
ok('转引' in html and 'qk' in html, '转引标记缺失')

# ---------- 3. 排版红线 ----------
ok('—' not in html, '出现长划线 —')
ok('–' not in html, '出现长划线 –')
for ln_no, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'第 {ln_no} 行 · 超过 1 个')
print('[2] 排版红线检查完成')

# ---------- 4. 机算统计 ----------
def cnt_header(pat):
    return sum(1 for l in lines if l.strip().startswith(pat))

sec_names = ['聚珍异馔','诸般汤煎','诸水','神仙服食','食疗诸病',
             '米谷品','兽品','禽品','鱼品','果品','菜品','料物性味']
secs = {n: cnt_header({'聚珍异馔':'卷第一聚珍异馔','诸般汤煎':'卷第二诸般汤煎',
        '诸水':'卷第二诸水','神仙服食':'卷第二神仙服食','食疗诸病':'卷第二食疗诸病',
        '米谷品':'卷第三米谷品','兽品':'卷第三兽品','禽品':'卷第三禽品',
        '鱼品':'卷第三鱼品','果品':'卷第三果品','菜品':'卷第三菜品',
        '料物性味':'卷第三料物性味'}[n]) for n in sec_names}
total = sum(secs.values())
nospace = len(re.sub(r'\s', '', lib))
juzhen_seg = lib.split('卷第一聚珍异馔', 1)[1].split('卷第二诸般汤煎', 1)[0]
vol3 = ['米谷品','兽品','禽品','鱼品','果品','菜品','料物性味']
vol3_total = sum(secs[k] for k in vol3)

def html_has(s): return s in html

ok(html_has(f'>{nospace:,}'), '库本字数页面缺失')
ok(html_has(f'>{total}<'), f'条目总数 {total} 页面缺失')
ok(html_has(f'>{secs["聚珍异馔"]}<'), '聚珍方数页面缺失')
for k in vol3:
    ok(html_has(f'>{secs[k]}<'), f'{k} 条数 {secs[k]} 页面缺失')
ok(html_has(f'>{vol3_total}') or html_has('二百二十七'), f'卷三合计 {vol3_total} 页面缺失')
ok(html_has(f'>{juzhen_seg.count("一脚子")}<'), '一脚子见次页面缺失')
ok(html_has(f'>{juzhen_seg.count("草果")}<'), '草果见次页面缺失')
ok(html_has(f'>{juzhen_seg.count("回回豆子")}<'), '回回豆子见次页面缺失')
ok(html_has(f'>{lib.count("回回")}'), '回回见次页面缺失')
ok(html_has(f'>{lib.count("无毒")}<'), '无毒见次页面缺失')
ok(html_has('二十条') and len(zu) == 20, '醉墙二十条口径不合')

# 禁单句数：按内容行（跳过节首引言行）以句号切分，含末尾残句
def section_sents(header_line, intro_line):
    idx = next(i for i, l in enumerate(lines) if l.strip() == header_line)
    out = []
    seen_intro = False
    for k in range(idx + 1, len(lines)):
        s = lines[k].strip()
        if not s: continue
        if s.startswith('卷第'): break
        if not seen_intro:
            assert s.startswith(intro_line[:6]), f'{header_line} 引言行形态不符: {s[:20]}'
            seen_intro = True
            continue
        out.append(s)
    return [x for x in ''.join(out).split('。') if x.strip()]

lh = section_sents('食物利害', '盖食物有利害者')
fan = section_sents('食物相反', '盖食不欲杂')
ok(len(lh) == 51 and html_has('五十一'), f'食物利害 {len(lh)} 节 与页面 51 不合')
ok(len(fan) == 55 and html_has('五十五'), f'食物相反 {len(fan)} 句 与页面 55 不合')
ok(html.count('class="dish"') == 95, '菜牌应为 95 枚')
print('[3] 机算统计核对完成：条目', total, '全帙', nospace, '卷三', vol3_total)

# ---------- 5. 页面结构 ----------
ok('殆知阁导读之七十二' in html, 'title 篇号缺失')
ok('殆知阁导读 · 七十二' in html, 'kicker 篇号缺失')
ok('daizhige-daodu' in html and 'daizhigev20' in html, '页脚链接缺失')
ok('verify_yinshan.py' in html, '页脚核验说明缺失')
ok(html.count('文本来源') == 1 and html.count('引文核验') == 1, '页脚要素缺失')
ok('忽思慧' in html and '天历三年' in html, '核心要素缺失')

# ---------- 汇总 ----------
print()
if fails:
    print('FAIL', len(fails), '项：')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print(f'ALL PASS  {checks} 项断言全过  (.q {len(qs)} 段 + .zui {len(zu)} 段)')
