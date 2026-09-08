# -*- coding: utf-8 -*-
"""蟹略 引文核验: 页面 data-v 块 + 动态内容 EXTRA 全部与库内文件 CJK 序列比对"""
import re, sys
from html.parser import HTMLParser

HTML = 'xielue.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/蟹略.txt'

def cjk(s):
    return ''.join(ch for ch in s if '㐀' <= ch <= '鿿' or '豈' <= ch <= '﫿')

flat = cjk(open(SRC, encoding='utf-8').read())

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []   # [tag, is_dv, skip_src]
        self.out = []
    def handle_starttag(self, tag, attrs):
        dv = any(k == 'data-v' for k, _ in attrs)
        cls = dict(attrs).get('class', '')
        self.stack.append([tag, dv, 'src' in cls.split(), []])
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                node = self.stack[i]
                if node[1]:
                    self.out.append(''.join(node[3]))
                del self.stack[i:]
                for anc in self.stack:
                    anc[3].append(' ')
                break
    def handle_data(self, d):
        if any(e[2] for e in self.stack):
            return
        for anc in self.stack:
            if anc[1]:
                anc[3].append(d)

p = P()
p.feed(open(HTML, encoding='utf-8').read())

# 渲染后 DOM 抓取优先 (shot_xielue.mjs 产出), 静态解析兜底
import json, os
if os.path.exists('/tmp/xielue_dv.json'):
    p.out = json.load(open('/tmp/xielue_dv.json'))
    print('使用渲染 DOM 抓取:', len(p.out), '条')
else:
    print('使用静态解析:', len(p.out), '条')

EXTRA = [
    # 解剖图动态内容 (PARTS)
    '礼记曰：蚕则绩而蟹有匡。', '匡实黄金重，螯肥白玉香。',
    '岭表录异曰：蟹壳内有黄赤膏。', '满腹红膏肥似髓，贮盘青壳大于杯。',
    '广韵曰：厣，蟹腹下厣，即脐也。', '想见霜脐当大嚼，梦回雪厣摩围山。',
    '大戴礼曰：二螯八足。', '螯犹兵也，小虫而倾两端自卫，故使傍行。',
    '博物志曰：蟹目相向者，毒尤甚。', '怒目横行与虎争，寒沙奔火祸胎成。',
    '本草经曰：蟹足节屈曲，行则旁横。', '横行葭苇中，不自贵其身。',
    # 正文 em 半引述
    '匡大如笠', '蟹因霜重金膏溢', '能与豹鬬', '斫雪双螯洗手供', '蟹馔牢丸美',
    '读尔雅不熟', '西湖蟹称天下第一', '蟹大而美', '不言肥而言癯',
    '投蟹漆中化水饮之长生', '虾荒蟹乱', '淞江蟹舍主人欢',
    '但见横行疑是躁，不知公子实无肠。',
]

fails = 0
seen = set()
for t in [cjk(x) for x in p.out] + [cjk(x) for x in EXTRA]:
    if not t or t in seen:
        continue
    seen.add(t)
    if t not in flat:
        fails += 1
        print('MISS:', t[:64])

uniq = len(seen)
print(f'核验 {uniq} 处, 失败 {fails}')
if fails:
    sys.exit(1)

# 排版规则
html = open(HTML, encoding='utf-8').read()
for i, line in enumerate(html.split('\n'), 1):
    if '—' in line or '–' in line:
        print(f'L{i} 长划线'); fails += 1
    if line.count('·') > 1:
        print(f'L{i} · 超标: {line.strip()[:50]}'); fails += 1
if re.search(r'(src|href)="http', html):
    print('外部依赖'); fails += 1
if fails:
    sys.exit(1)
print('排版规则通过: 无长划线, 每行·≤1, 无外部依赖')
