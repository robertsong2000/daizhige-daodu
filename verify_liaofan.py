#!/usr/bin/env python3
"""核验 liaofan-sixun.html：引文逐字对库 + 排版红线 + 机数断言。
库本：daizhige-simplified/儒藏/修身治家/了凡四训.txt
"""
import re, sys
from html.parser import HTMLParser

PAGE = 'liaofan-sixun.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/儒藏/修身治家/了凡四训.txt'

def norm(t):
    out = []
    for ch in t:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF or 0xF900 <= o <= 0xFAFF:
            out.append(ch)
    return ''.join(out)

class QCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, is_q)
        self.q_depth = 0
        self.buf = []
        self.quotes = []         # finished .q texts
        self.raw_all = []
    VOID = {'br','img','meta','link','hr','input','area','base','col','embed','source','track','wbr'}
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class') or ''
        is_q = 'q' in cls.split()
        self.stack.append((tag, is_q))
        if is_q:
            self.q_depth += 1
            if self.q_depth == 1:
                self.buf = []
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                closing = self.stack[i:]
                del self.stack[i:]
                for _, was_q in closing:
                    if was_q:
                        self.q_depth -= 1
                        if self.q_depth == 0 and self.buf:
                            self.quotes.append(''.join(self.buf))
                            self.buf = []
                return
    def handle_data(self, data):
        self.raw_all.append(data)
        if self.q_depth > 0:
            self.buf.append(data)

def main():
    html = open(PAGE, encoding='utf-8').read()
    lib = open(LIB, encoding='utf-8').read()
    lib_n = norm(lib)
    errs, warns = [], []

    # ---- 排版红线 ----
    if '—' in html: errs.append('出现长划线 —')
    if '–' in html: errs.append('出现短划线 –')
    for i, ln in enumerate(html.split('\n'), 1):
        if ln.count('·') > 1:
            errs.append(f'第{i}行 · 超过1个')
        if ln.count('・') > 1:
            errs.append(f'第{i}行 ・ 超过1个')
    for ch in html:
        if 0xE000 <= ord(ch) <= 0xF8FF:
            errs.append(f'出现 PUA 私有区字符 U+{ord(ch):04X}')
            break

    # ---- 引文逐字对库 ----
    p = QCollector()
    p.feed(html)
    quotes = [q.strip() for q in p.quotes]
    for i, q in enumerate(quotes, 1):
        qn = norm(q)
        if not qn:
            errs.append(f'引文{i} 归一后为空')
            continue
        if qn not in lib_n:
            errs.append(f'引文{i} 未命中库本: {q[:40]}…')

    # ---- 机数断言（口径：页面展示的统计，脚本独立重算）----
    rings = len(re.findall(r'class="ring', html))
    doubles = len(re.findall(r'ring double', html))
    cells = len(re.findall(r'<div class="cell">', html))
    if rings != 14: errs.append(f'历日朱圈 {rings} != 14')
    if doubles != 1: errs.append(f'双圈 {doubles} != 1')
    if cells != 31: errs.append(f'历日格 {cells} != 31')
    six = len(re.findall(r'<span class="q">余好洁', html))
    if len(re.findall(r'<div class="chips">.*?</div>', html, re.S)) != 1:
        warns.append('chips 区块数异常')
    chips_q = 0
    m = re.search(r'<div class="chips">(.*?)</div>', html, re.S)
    if m: chips_q = len(re.findall(r'<span class="q">', m.group(1)))
    if chips_q != 6: errs.append(f'无子之相 chips {chips_q} != 6')
    m = re.search(r'<div class="ten">(.*?)</div>', html, re.S)
    ten_q = len(re.findall(r'<span class="q">', m.group(1))) if m else 0
    if ten_q != 10: errs.append(f'十纲 chips {ten_q} != 10')
    m = re.search(r'<div class="six-chips">(.*?)</div>', html, re.S)
    sixq = len(re.findall(r'<span class="q">', m.group(1))) if m else 0
    if sixq != 6: errs.append(f'六想 chips {sixq} != 6')
    tcards = len(re.findall(r'<div class="tcard">', html))
    if tcards != 3: errs.append(f'三心卡 {tcards} != 3')
    hexs = len(re.findall(r'<div class="hex">\s*(.*?)</div>', html, re.S))
    hx = re.search(r'<div class="hex">(.*?)</div>', html, re.S)
    yao = len(re.findall(r'<i', hx.group(1))) if hx else 0
    yang = len(re.findall(r'<i class="y"', hx.group(1))) if hx else 0
    if yao != 6: errs.append(f'谦卦爻 {yao} != 6')
    if yang != 1: errs.append(f'谦卦阳爻 {yang} != 1')
    tabs = len(re.findall(r'<span class="tab', html))
    if tabs != 4: errs.append(f'四训 tabs {tabs} != 4')
    lrows = len(re.findall(r'<div class="lrow">', html))
    if lrows != 4: errs.append(f'愿账行(含表头) {lrows} != 4')
    stamps = len(re.findall(r'<div class="stamp[ "]', html))
    if stamps != 3: errs.append(f'命纸验印 {stamps} != 3')
    piseal = len(re.findall(r'class="pi-seal"', html))
    if piseal != 2: errs.append(f'批单卡验印 {piseal} != 2')
    mzq = len(re.findall(r'<div class="mz-item"><span class="q">', html))
    if mzq != 3: errs.append(f'命纸批条 {mzq} != 3')

    # ---- 批单数字对库 ----
    for frag in ['县考童生，当十四名', '府考七十一名', '提学考第九名', '九十一石五斗', '二分三厘七毫', '一分四厘六毫']:
        if norm(frag) not in lib_n:
            errs.append(f'批单/账数 {frag} 未见于库本')

    # ---- 页面身份 ----
    if '第九十四篇' not in html: errs.append('页面缺 第九十三篇 标识')
    if '殆知阁导读之九十四' not in html: errs.append('title 序号未同步')
    if 'github.com/robertsong2000/daizhigev20' not in html: errs.append('页脚缺库链接')

    total = len(quotes)
    print(f'.q 引文总数: {total}')
    print(f'命中: {total - len([e for e in errs if "未命中库本" in e or "归一后为空" in e])}')
    for w in warns: print('WARN:', w)
    if errs:
        print('\n== FAIL ==')
        for e in errs: print(' -', e)
        sys.exit(1)
    print('== ALL PASS ==')

if __name__ == '__main__':
    main()
