#!/usr/bin/env python3
"""甘泽谣导读页核验：引文正向对库 + 页面反扫 + 排版红线 + 结构断言。
用法: python3 verify_ganzeyaou.py [mulu_html_path]  (mulu 参数在取号更新后传入做联检)
"""
import re, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(BASE, '..', 'daizhige-simplified', '子藏', '笔记', '甘泽谣.txt')
PAGE = os.path.join(BASE, 'ganzeyaou.html')

def hz(s):
    return re.sub(r'[^一-鿿]', '', s)

lib = open(LIB, encoding='utf-8').read()
lib_n = hz(lib)
other = re.findall(r'[^一-鿿\s]', lib)
page = open(PAGE, encoding='utf-8').read()

fails = []
def check(cond, msg):
    if cond:
        print('PASS', msg)
    else:
        fails.append(msg)
        print('FAIL', msg)

# ---- 库本机数 ----
lib_nospace = re.sub(r'\s', '', lib)
check(len(lib_nospace) == 8739, f'库本去空白字数(含标点) {len(lib_nospace)} == 8739')
print('INFO 库内非汉字非空白字符数:', len(other), ('样例:'+repr(other[:10])) if other else '')

# ---- 正向：所有 <q> 逐字对库 ----
quotes = re.findall(r'<q[^>]*>(.*?)</q>', page, re.S)
qn = [(i, hz(re.sub(r'<[^>]+>', '', q))) for i, q in enumerate(quotes)]
qn = [(i, t) for i, t in qn if t]
pos = []
for i, t in qn:
    p = lib_n.find(t)
    check(p >= 0, f'引文{i:02d} 库本命中 [{t[:22]}...]({len(t)}字)')
    pos.append(p)
mono = all(a <= b for a, b in zip(pos, pos[1:]))
check(mono, '引文库内位置单调（篇序不乱）')
print(f'INFO 正向引文 {len(qn)} 条')

# ---- 反向：剥引文/引号/申报区后 6 字窗不得撞库 ----
body = page[page.index('<body'):]
body = re.sub(r'<q[^>]*>.*?</q>', '▒', body, flags=re.S)          # 引文遮罩
body = re.sub(r'「[^」]*」', '▒', body)                              # 页内小引号（校记等）
body = re.sub(r'『[^』]*』', '▒', body)
jiaoji = re.search(r'<div class="jiaoji">.*?</div>\s*</main>', body, re.S)
if jiaoji:
    body = body.replace(jiaoji.group(0), '▒校记申报区豁免▒')
plain = re.sub(r'</?(?:p|div|section|h[1-6]|li|details|summary|blockquote|footer|nav|ul|button|td|tr|br)[^>]*>', '\n', body)
plain = re.sub(r'<[^>]+>', '', plain)
plain = plain.replace('&amp;', '&')
lines = [re.sub(r'\s', '', l) for l in plain.split('\n')]
BAD = []
nw = 0
for li, line in enumerate(lines):
    for i in range(len(line) - 5):
        w = line[i:i+6]
        nw += 1
        if hz(w) == w and w in lib_n:
            BAD.append((li, w))
check(not BAD, f'反扫 6 字窗零撞库（渲染行 {len(lines)}，扫描窗 {nw}）')
if BAD:
    print('INFO 反扫撞点:', BAD[:20])

# ---- 排版红线 ----
check('—' not in page, '无长划线 —')
check('–' not in page, '无短划线 –')
vis = re.sub(r'<[^>]+>', '\n', body)
lines = [l for l in vis.split('\n')]
dot_bad = [l for l in lines if l.count('·') > 1]
check(not dot_bad, '渲染每行 · ≤ 1')
print('INFO · 总数:', sum(l.count('·') for l in lines))

# ---- 零外部依赖 + 标签配平 ----
check('<script src' not in page and '@import' not in page and '<link' not in page, '无外部资源')
check('src="' not in page.replace('svg', '').replace('SRC', '') or '<img' not in page, '无外链图片')
for t in ['div', 'span', 'p', 'q', 'section', 'details', 'summary', 'svg', 'g', 'button', 'main', 'footer']:
    o = len(re.findall(f'<{t}[ >]', page))
    c = len(re.findall(f'</{t}>', page))
    check(o == c, f'标签配平 <{t}> {o}=={c}')

# ---- 页脚四件 ----
for key in ['文本来源', '库外申报', '上一篇同系列', '读法提醒', 'daizhigev20', '二百八十六']:
    check(key in page, f'页脚含「{key}」')

# ---- 结构 ----
for pid in [f'p{i}' for i in range(1, 10)]:
    check(f'id="{pid}"' in page, f'锚点 {pid} 存在')
names = ['魏先生', '素娥', '陶岘', '懒残', '聂隐娘', '韦驺', '圆观', '红线', '许云封']
for n in names:
    check(f'<h2>{n}</h2>' in page, f'篇题 {n}')

# ---- mulu 联检（可选，取号更新后传入）----
if len(sys.argv) > 1:
    mulu = open(sys.argv[1], encoding='utf-8').read()
    nos = [int(n) for n in re.findall(r'class="no mono">([0-9]+)<', mulu)]
    check(sorted(nos) == list(range(1, len(nos) + 1)), f'mulu 编号 1..{len(nos)} 连续')
    check(max(nos) in nos and f'href="ganzeyaou.html"' in mulu, 'mulu 含甘泽谣条目')
    m = re.search(r'<a class="entry" href="ganzeyaou\.html">\s*<span class="no mono">(\d+)</span>', mulu)
    check(m and int(m.group(1)) == max(nos), f'甘泽谣条目编号 {m.group(1) if m else "?"} == 最大号 {max(nos)}')
    anchors = re.findall(r'(二百八十[0-9一二三四五六七八九十]*)篇', mulu)
    exp = ['二百八十三', '二百八十二', '二百八十一', '二百八十'][0]
    want = {283: '二百八十三', 284: '二百八十四', 285: '二百八十五', 286: '二百八十六', 287: '二百八十七'}.get(len(nos), '?')
    check(all(a == want for a in anchors), f'mulu kicker/footer 计数均为 {want}（实测 {set(anchors)}）')

print('=' * 30)
print('FAILS:', len(fails))
sys.exit(1 if fails else 0)
