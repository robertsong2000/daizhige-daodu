#!/usr/bin/env python3
"""核验 datang-chuangye-qijuzhu.html：引文逐字对库 + 平文本片段双查 + 机数复核 + 排版红线。"""
import re, sys, unicodedata

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/datang-chuangye-qijuzhu.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/编年/大唐创业起居注.txt'

errors = []
def check(cond, msg):
    if not cond:
        errors.append(msg)

def strip_punct(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        cat = unicodedata.category(ch)
        if cat.startswith('P') or cat.startswith('S'):
            continue
        if 0xE000 <= ord(ch) <= 0xF8FF or ord(ch) >= 0x20000 and unicodedata.category(ch) == 'Co':
            continue
        out.append(ch)
    return ''.join(out)

lib_raw = open(LIB, encoding='utf-8').read()
lib_flat = re.sub(r'\s', '', lib_raw)
lib_norm = strip_punct(lib_raw)

html = open(PAGE, encoding='utf-8').read()

# ---------- 1. 收集 .q span（标签平衡扫描） ----------
q_spans = []
for m in re.finditer(r'<(\w+)([^>]*\bclass="[^"]*\bq\b[^"]*"[^>]*)>', html):
    tag = m.group(1)
    depth = 1
    pos = m.end()
    pat = re.compile(r'<(/?)%s\b[^>]*?(/?)>' % tag)
    while depth > 0:
        t = pat.search(html, pos)
        if not t:
            errors.append('未闭合的 .q 标签 at %d' % m.start())
            depth = 0
            break
        if t.group(2) == '/':
            continue
        if t.group(1) == '/':
            depth -= 1
        else:
            depth += 1
        pos = t.end()
    inner = html[m.end():pos]
    inner = re.sub(r'<[^>]+>', '', inner)
    q_spans.append((m.start(), inner))
check(len(q_spans) == 37, '页内 .q 数量应为 37，实得 %d' % len(q_spans))

# 每个引文在库内（去标点）恰好在位
Q_EXPECT_ONCE = {
    '起义旗至发引凡四十八日', '起自太原至京城凡一百二十六日', '起摄政至即真日凡一百八十三日',
}
for _, q in q_spans:
    nq = strip_punct(q)
    check(len(nq) > 0, '空 .q')
    check(nq in lib_norm, '引文不在库内: %s' % q[:22])
for _, q in q_spans:
    nq = strip_punct(q)
    if nq in Q_EXPECT_ONCE:
        check(lib_norm.count(nq) == 1, '卷面引文应唯一: %s' % q[:16])

# 页内 .q 不得重复
norms = [strip_punct(q) for _, q in q_spans]
check(len(norms) == len(set(norms)), '页内 .q 有重复')

# ---------- 2. 平文本引用片段：页内出现 且 库内存在 ----------
PLAIN = [
    '此后余年，实为天假', '信使行人，无能自达', '私窃喜甚',
    '伪若避之', '谬谓之曰', '欷歔不得已', '帝不得已而行', '帝若不得已而従之',
    '尝卒与突厥相遇', '骁锐者为别队', '十三岁，岁在丁亥',
    '何従而至天既为孤遣来', '岂谓系之二日（甲子是十五日丙寅是十七日）',
    '马二千疋', '帝素怀济世之略，有经纶天下之心。',
]
page_text = re.sub(r'<[^>]+>', '', html)
page_norm = strip_punct(page_text)
for p in PLAIN:
    np_ = strip_punct(p)
    check(np_ in page_norm, '平文本片段未在页内: %s' % p[:18])
    check(np_ in lib_norm, '平文本片段不在库内: %s' % p[:18])

# ---------- 3. 机数复核 ----------
c = lib_flat
check(len(c) == 25605, '全帙去空白含标点应为 25605，实得 %d' % len(c))
for w, n in [('突厥', 45), ('大郎', 17), ('二郎', 17), ('伪', 2), ('谬', 5), ('不得已', 3), ('従', 64)]:
    check(c.count(w) == n, '「%s」应为 %d 见，实得 %d' % (w, n, c.count(w)))
check('25,605' in page_text, '页内缺 25,605 计数')
check('伪<small>2 见' in html, 'chip 伪 2 见')
check('谬<small>5 见' in html, 'chip 谬 5 见')
check('不得已<small>3 见' in html, 'chip 不得已 3 见')
check('全书 64 见' in page_text, '校记従 64 见')

# 三卷日数与比例条
check(48 + 126 + 183 == 357, '三卷日数合计应为 357')
check('三百五十七' in page_text, '页内缺三百五十七日')
for cls, days in [('seg1', 48), ('seg2', 126), ('seg3', 183)]:
    m = re.search(r'\.%s \{ width: ([\d.]+)%%' % cls, html)
    check(bool(m), '缺 %s 宽度' % cls)
    if m:
        expect = days / 357 * 100
        got = float(m.group(1))
        check(abs(got - expect) < 0.01, '%s 宽度 %s 应为 %.2f' % (cls, got, expect))

# ---------- 4. 排版红线 ----------
check('—' not in html, '禁长划线 —')
check('–' not in html, '禁短划线 –')
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        errors.append('第 %d 行 · 超过 1 个' % i)
check(page_text.count('之七十三') >= 2, 'kicker 与 title 应含之七十三')

# ---------- 结果 ----------
if errors:
    print('FAIL (%d)' % len(errors))
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('PASS: %d 条 .q 引文 + %d 条平文本片段 + 机数 + 红线 全部通过' % (len(q_spans), len(PLAIN)))
