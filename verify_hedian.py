#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""何典 导读页核验：引文逐字（去标点+归一）+ 「」反扫 + 排版红线 + 机数断言"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/hedian.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/何典.txt'

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8', errors='replace').read()
FAIL = []

VAR = {}  # 异体字归一表，库本有异体时在此登记

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        ch = VAR.get(ch, ch)
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

lib_n = norm(lib)
print(f"库本归一后字符数: {len(lib_n)}")
if len(lib_n) < 40000:
    FAIL.append(f"库本字符数异常: {len(lib_n)}")

# ---------- 1. 收集 .q 引文 ----------
VOID = {'br', 'img', 'meta', 'link', 'hr', 'input', 'source', 'wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__()
        self.qs = []
        self.qdepth = 0
        self.buf = []
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        cls = (a.get('class') or '').split()
        if 'q' in cls:
            self.qdepth += 1
            self.buf.append([])
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        cls = None
        if self.qdepth > 0:
            text = ''.join(self.buf.pop()) if self.buf else ''
            self.qs.append(text)
            self.qdepth -= 1
    def handle_data(self, data):
        if self.qdepth > 0 and self.buf:
            self.buf[-1].append(data)

qc = QC()
qc.feed(page)
print(f".q 引文块: {len(qc.qs)}")
if len(qc.qs) < 35:
    FAIL.append(f"引文块过少: {len(qc.qs)}")

bad = 0
for i, t in enumerate(qc.qs):
    n = norm(t)
    if not n:
        continue
    if n not in lib_n:
        bad += 1
        print(f"  FAIL q{i}: {t[:42]}...")
        # 邻近诊断
        probe = n[:8]
        j = lib_n.find(probe)
        if j >= 0:
            print(f"       库本同处: ...{lib_n[max(0,j-4):j+30]}...")
        else:
            print(f"       库本无此前缀: {probe}")
if bad == 0:
    print("  ok 全部引文逐字命中库本")
else:
    FAIL.append(f"{bad} 条引文未命中")

# ---------- 2. 「」反扫：页面一切「」内文字都必须在库本 ----------
for m in re.finditer(r'「([^「」]+)」', page):
    n = norm(m.group(1))
    if n and n not in lib_n:
        FAIL.append(f"「」反扫未命中: 「{m.group(1)}」")

# ---------- 3. 回目十牌逐条（上下联分列，各自成 .q）----------
hm = [
    ('五脏庙活鬼求儿', '三家村死人出世'),
    ('造鬼庙为酬梦里缘', '做新戏惹出飞来祸'),
    ('摇小船阳沟里失风', '出老材死路上远转'),
    ('假烧香赔钱养汉', '左嫁人坐产招夫'),
    ('刘莽贼使尽老婆钱', '形容管领回开口货'),
    ('活死人讨饭遇仙人', '臭花娘烧香逢色鬼'),
    ('骚师姑痴心帮色鬼', '活死人结发聘花娘'),
    ('鬼谷先生白日升天', '畔房小姐黑夜打鬼'),
    ('贪城隍激反大头鬼', '怯总兵偏听长舌妇'),
    ('阎罗王君臣际会', '活死人夫妇团圆'),
]
onpage = [norm(x) for x in qc.qs]
for k, (a, b) in enumerate(hm, 1):
    for half in (a, b):
        nh = norm(half)
        if nh not in lib_n:
            FAIL.append(f"第{k}回半联未命中库本: {half}")
        if not any(nh == s or nh in s for s in onpage):
            FAIL.append(f"第{k}回半联缺页: {half}")

# ---------- 4. 排版红线 ----------
if '—' in page or '–' in page:
    FAIL.append("出现长划线")
for ln, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        FAIL.append(f"第{ln}行 · 超限")
txt = re.sub(r'<style>.*?</style>', '', page, flags=re.S)
body_text = re.sub(r'<[^>]+>', '', txt)
print(f"渲染文本 · 总数: {body_text.count('·')}")
if body_text.count('·') > 1:
    FAIL.append("正文 · 超限")

# ---------- 5. 机数断言 ----------
if page.count('class="node') != 6:
    FAIL.append("时间链节点应为 6")
if page.count('class="pai"') != 10:
    FAIL.append("路引牌应为 10")
if page.count('class="gq"') != 10:
    FAIL.append("鬼籍应为 10 条")
if page.count('class="ye"') != 4:
    FAIL.append("书叶选抄应为 4 片")
if '一百四十三' not in page:
    FAIL.append("页脚编号缺一百四十三")
if '<script' in page:
    FAIL.append("不允许脚本")

print()
if FAIL:
    print(f"共 {len(FAIL)} 项 FAIL：")
    for f in FAIL:
        print("  -", f)
    sys.exit(1)
print("全部通过：引文逐字命中，反扫命中，排版红线通过，机数断言通过。")
