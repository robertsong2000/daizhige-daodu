#!/usr/bin/env python3
"""核验 xuanhe-yishi.html：「」引文逐字对库 + 6字反扫 + 排版红线 + 机数 + mulu 联检(传参 mulu 时)。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'xuanhe-yishi.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/大宋宣和遗事.txt'

raw = open(LIB, encoding='utf-8', errors='ignore').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

LIB_N = norm(raw)

class QCollect(HTMLParser):
    """收集 body 全部文本节点（逐节点，不跨标签拼接）。"""
    def __init__(self):
        super().__init__()
        self.nodes = []
    def handle_data(self, data):
        if data.strip():
            self.nodes.append(data)

html = open(PAGE, encoding='utf-8').read()
body = html[html.index('<body'):]
qc = QCollect()
qc.feed(body)
nodes = qc.nodes
qtext = ''.join(nodes)

fails = []

# ---------- 1. 全部「」引文逐字对库 ----------
spans = re.findall(r'「([^」]*)」', qtext)
bad_quotes = []
for s in spans:
    sn = norm(s)
    if len(sn) == 0:
        continue
    if sn not in LIB_N:
        bad_quotes.append(s[:42])

# 申报清单：页面中不带「」的库本成句（开卷诗逐行、书名、榜内名号），逐条对库
DECLARED = [
    '暂时罢鼓膝间琴', '闲把遗编阅古今', '常叹贤君务勤俭', '深悲庸主事荒淫',
    '说破兴亡多少事', '高山流水有知音',
    '大宋宣和遗事',
    '智多星吴加亮', '玉麒麟卢进义', '青面兽杨志', '混江龙李海', '九纹龙史进',
    '入云龙公孙胜', '浪里百跳张顺', '霹雳火秦明', '活阎罗阮小七', '立地太岁阮小五',
    '短命二郎阮进', '大刀关必胜', '豹子头林冲', '黑旋风李逵', '小旋风柴进',
    '金枪手徐宁', '扑天雕李应', '赤发鬼刘唐', '一撞直董平', '插翅虎雷横',
    '美髯公朱同', '神行太保戴宗', '赛关索王雄', '病尉迟孙立', '小李广花荣',
    '没羽箭张青', '没遮拦穆横', '浪子燕青', '花和尚鲁智深', '行者武松',
    '铁鞭呼延绰', '急先锋索超', '拼命二郎石秀', '火船工张岑', '摸着云杜千',
    '铁天王晁盖',
]
for s in DECLARED:
    if norm(s) not in LIB_N:
        bad_quotes.append('[申报清单] ' + s[:42])

# ---------- 2. 反扫：每个文本节点剥引文后，不得残留 ≥6 字库本连续段 ----------
def max_lib_run(sn):
    best, n = 0, len(sn)
    for i in range(n):
        for j in range(n, i, -1):
            if j - i > best and sn[i:j] in LIB_N:
                best = j - i
                break
    return best

rescan = []
for nd in nodes:
    t = norm(nd)
    for s in re.findall(r'「([^」]*)」', nd):
        t = t.replace(norm(s), '', 1)
    for d in DECLARED:
        t = t.replace(norm(d), '')
    if len(t) >= 6 and max_lib_run(t) >= 6:
        rescan.append(nd[:40])

# ---------- 3. 排版红线 ----------
if '—' in html or '–' in html:
    fails.append('出现长划线')
for line in html.split('\n'):
    if line.count('·') > 1:
        fails.append('单行 · 超限: ' + line.strip()[:40])
for nd in nodes:
    if nd.count('·') > 1:
        fails.append('单节点 · 超限: ' + nd.strip()[:40])
for pat, why in [('<script src', '外部脚本'), ('<link', '外部样式'), ('@import', '外部导入'), ('src="http', '外部资源')]:
    if pat in html:
        fails.append('外部依赖: ' + why)

# ---------- 4. 机数 ----------
n_total = len(re.sub(r'\s', '', raw))
if n_total != 66401:
    fails.append(f'库本去空白 {n_total} != 66401')
bounds = [31, 18765, 35657, 52521, len(raw)]
for name, exp, a, b in [('元集', 18560, 31, 18765), ('亨集', 16738, 18765, 35657),
                        ('利集', 16723, 35657, 52521), ('贞集', 14361, 52521, len(raw))]:
    got = len(re.sub(r'\s', '', raw[a:b]))
    if got != exp:
        fails.append(f'{name} 去空白 {got} != {exp}')
chips = re.findall(r'<div class="nm">', body)
if len(chips) != 36:
    fails.append(f'三十六人榜 {len(chips)} 卡 != 36')
stamps = re.findall(r'<div class="hstamp">(.)</div>', body)
if stamps != ['入', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']:
    fails.append('回戳序异常: ' + ''.join(stamps))
m = re.search(r'殆知阁导读 · 第(\d+)篇', html)
e = re.search(r'殆知阁导读 第(\d+)篇至此读毕', html)
if not m or not e or m.group(1) != e.group(1):
    fails.append('眉线与收梢篇号不一致')
else:
    print(f'篇号: 第{m.group(1)}篇')
if '酣Ａ' in qtext:
    fails.append('缺字占位符Ａ混入引文区')

# ---------- 结果 ----------
if bad_quotes:
    fails.append(f'{len(bad_quotes)} 条引文/申报未过库:')
    fails += ['  MISS ' + s for s in bad_quotes]
if rescan:
    fails.append(f'{len(rescan)} 处未申报库本成句:')
    fails += ['  RESCAN ' + s for s in rescan]
if fails:
    print('FAIL')
    for f in fails:
        print(f)
    sys.exit(1)
print(f'PASS: {len(spans)} 条「」引文逐字对库全过, {len(DECLARED)} 条申报对库全过, 反扫无残留, 红线干净, 机数全中')

# ---------- 5. mulu 联检 ----------
if len(sys.argv) > 1:
    mulu = open(sys.argv[1], encoding='utf-8').read()
    m2 = re.findall(r'<span class="no mono">(\d+)</span>', mulu)
    nums = [int(x) for x in m2]
    if sorted(nums) != list(range(1, len(nums) + 1)):
        fails2 = ['mulu 编号有缺号或重号']
    else:
        fails2 = []
        if max(nums) != int(m.group(1)):
            fails2.append(f"mulu 最大编号 {max(nums)} 与页内篇号 {m.group(1)} 不一致")
        if 'xuanhe-yishi.html' not in mulu:
            fails2.append('mulu 未链接本页')
        if '大宋宣和遗事' not in mulu:
            fails2.append('mulu 无本条书名')
        fm = re.search(r'([一二三四五六七八九十百零]+)篇导读', mulu)
        def cn2int(s):
            d = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
            if '百' in s:
                b, rest = s.split('百', 1)
                v = d.get(b, 1) * 100
                if '十' in rest:
                    t, o = rest.split('十', 1)
                    v += (d.get(t, 1) if t else 1) * 10 + d.get(o, 0)
                else:
                    v += d.get(rest, 0)
            elif '十' in s:
                t, o = s.split('十', 1)
                v = (d.get(t, 1) if t else 1) * 10 + d.get(o, 0)
            else:
                v = d.get(s, 0)
            return v
        if fm and cn2int(fm.group(1)) != nums[-1]:
            fails2.append(f"mulu 页脚计数 {fm.group(1)} != {nums[-1]}")
    if fails2:
        print('MULU FAIL')
        for f in fails2:
            print(f)
        sys.exit(1)
    print(f'MULU PASS: 编号 1..{max(nums)} 无缺无重, 条目/链接/页脚计数一致')
