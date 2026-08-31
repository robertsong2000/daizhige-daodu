# -*- coding: utf-8 -*-
"""鸡肋编导读核验：全部 .q 双侧逐字 + 「」反扫 + 红线 + 机数。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'jile-bian.html'
LIB = '../daizhige-simplified/子藏/笔记/鸡肋编.txt'

html = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()

# ---------- norm：只留 CJK 双区间 ----------
def norm(s):
    return ''.join(c for c in s
                   if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0003ffff')

LIBN = norm(lib)
if not LIBN:
    print('FAIL: 库本 norm 为空'); sys.exit(1)

# ---------- QCollector：栈配平，VOID 不入栈 ----------
VOID = {'br', 'img', 'meta', 'link', 'input', 'hr', 'source'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.qdepth = None; self.buf = []; self.blocks = []
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        if self.qdepth is not None:
            self.qdepth.append(tag)
        elif tag == 'q':
            self.qdepth = []; self.buf = []
        self.stack.append(tag)
        if tag == 'q' and self.qdepth is None:
            self.qdepth = []; self.buf = []
        # 处理嵌套 q：外层 q 已开，内层 q 忽略独立收集
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.qdepth is not None and tag == 'q':
            self.blocks.append(''.join(self.buf))
            self.qdepth = None; self.buf = []
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            if self.stack: self.stack.pop()
    def handle_data(self, data):
        if self.qdepth is not None:
            self.buf.append(data)

# 简化：直接用 qdepth 标记法
class QCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.qdepth = 0
        self.buf = []
        self.blocks = []
    def _isq(self, attrs):
        for k, v in attrs:
            if k == 'class' and v and 'q' in v.split():
                return True
        return False
    def handle_starttag(self, tag, attrs):
        isq = (not self.qdepth) and self._isq(attrs) and tag in ('span', 'div', 'p', 'blockquote', 'em', 'b')
        if tag not in VOID:
            self.stack.append(tag)
        if isq:
            self.qdepth = len(self.stack)  # 含自身
            self.buf = []
    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if self.qdepth and len(self.stack) < self.qdepth:
            self.blocks.append(''.join(self.buf))
            self.qdepth = 0
            self.buf = []
    def handle_data(self, data):
        if self.qdepth:
            self.buf.append(data)

qc = QCollector()
qc.feed(html)
blocks = [b for b in qc.blocks if norm(b)]
print(f'收集 .q 块：{len(qc.blocks)}（有效 {len(blocks)}）')
if len(qc.blocks) < 45:
    print('FAIL: .q 块数量异常'); sys.exit(1)

fails = []
for i, b in enumerate(blocks):
    n = norm(b)
    if n not in LIBN:
        fails.append((i, b[:60]))
if fails:
    print(f'FAIL: {len(fails)} 块引文不在库本')
    for i, b in fails:
        print('  ', i, b)
    sys.exit(1)
print(f'PASS: {len(blocks)} 块 .q 全部逐字命中库本')

# ---------- 「」反扫：剥 style/script ----------
body = re.sub(r'<style.*?</style>', '', html, flags=re.S)
body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
text = re.sub(r'<[^>]+>', '', body)
quotes = re.findall(r'「([^」]*)」', text)
bad = []
for q in quotes:
    n = norm(q)
    if n and n not in LIBN:
        bad.append(q)
if bad:
    print('FAIL: 「」反扫不通过')
    for q in bad: print('  ', q)
    sys.exit(1)
print(f'PASS: 「」反扫 {len(quotes)} 处全部在库本')

# ---------- 红线 ----------
if '—' in html.replace('&mdash;', ''):
    print('FAIL: 含长划线 —'); sys.exit(1)
if '–' in html:
    print('FAIL: 含 –'); sys.exit(1)
for ln, line in enumerate(text.splitlines(), 1):
    if line.count('·') > 1:
        print(f'FAIL: 行{ln} 有 {line.count("·")} 个 ·'); sys.exit(1)
for a, b in (('「', '」'), ('（', '）'), ('《', '》')):
    if text.count(a) != text.count(b):
        print(f'FAIL: {a}{b} 不配对 {text.count(a)}/{text.count(b)}'); sys.exit(1)
print('PASS: 红线（—/–/每行·≤1/引号配对）')

# ---------- 机数 ----------
import unicodedata
errs = []
def chk(name, got, want):
    if got != want:
        errs.append(f'{name}: 页面 {want} ≠ 实测 {got}')

n_total = len(lib)
n_nows = len(re.sub(r'\s', '', lib))
n_han = sum(1 for c in lib if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0003ffff')
chk('全帙字数', n_total, 65751)
chk('去空白', n_nows, 64193)
chk('汉字', n_han, 52359)

lines = lib.splitlines()
marks = [i for i, l in enumerate(lines) if '●卷' in l]
chk('卷标数', len(marks), 3)
counts = []
bounds = marks + [len(lines)]
for k in range(3):
    seg = lines[bounds[k]+1:bounds[k+1]]
    counts.append(sum(1 for l in seg if l.strip()))
chk('三卷条数', tuple(counts), (95, 95, 117))
chk('上中下条数和', sum(counts), 307)

pua = [c for c in lib if 0xE000 <= ord(c) <= 0xF8FF]
chk('PUA 总数', len(pua), 204)
chk('PUA 种数', len(set(pua)), 92)

for w, want in [('鸡肋', 5), ('两脚羊', 1), ('不羡羊', 1), ('和骨烂', 1), ('饶把火', 1),
                ('事魔食菜', 1), ('羊角', 1), ('进冰船', 1), ('握发殿', 1), ('恶发殿', 1),
                ('悦生随钞', 1), ('清源庄季裕', 1)]:
    got = len(re.findall(re.escape(w), lib))
    if got != want:
        errs.append(f'词频 {w}: 页面写 {want} ≠ 实测 {got}')

# 关键句唯一性（短引文需带上下文保证唯一）
for w, want in [('人肉之价，贱于犬豕', 1), ('全躯暴以为腊', 1), ('呜呼痛哉', 1),
                ('欲得官，杀人放火受招安', 1), ('有持至行在犹食者', 1),
                ('遂去其冠', 1), ('有胞衣', 1), ('置一羊角其中', 1),
                ('时至元己卯仲春月', 1), ('季裕手集', 1), ('龙潜木', 1),
                ('看参政乡人', 1), ('女和尚', 1), ('打爷贼', 1), ('乌龟头', 1),
                ('这汉毒也', 1), ('估人呼为保仪', 1), ('秋壑点定', 1),
                ('南渡衣冠欠王导', 1), ('北狩应悲易水寒', 1), ('我乃秋收冬藏', 1),
                ('赶着行在卖酒醋', 1), ('欲以谷代俸钱', 1), ('总木价六万五千余贯', 1),
                ('谓之进冰船', 1), ('谓钱王怒即升此殿也', 1), ('视牛骨为愈矣', 1)]:
    got = len(re.findall(re.escape(norm(w)), LIBN))
    if got != want:
        errs.append(f'句频 {w}: 期望 {want} ≠ 实测 {got}')

# 页面数字与实测一致
for s in ['65,751', '64,193', '52,359', '九十五条', '一百一十七条', '三百零七']:
    if s not in html:
        errs.append(f'页面缺少数字串 {s}')

# hero 三签
for w in ['两脚羊', '进冰船', '事魔食菜']:
    if f'<span class="q">{w}</span>' not in html:
        errs.append(f'hero 签缺 {w}')

# 英文残留（成文手滑词）
for w in ['the ', 'and ', 'TODO', 'FIXME', 'ponytail', 'question', 'instrument', 'designer']:
    if w in text:
        errs.append(f'英文残留 {w!r}')

if errs:
    print('FAIL: 机数断言')
    for e in errs: print('  ', e)
    sys.exit(1)
print('PASS: 机数断言（三口径/三卷条数/PUA/词频/句频唯一性）')
print('ALL PASS')
