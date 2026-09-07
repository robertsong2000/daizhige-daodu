# -*- coding: utf-8 -*-
# 引文核验：天妃显圣录（子藏/笔记/天妃显圣录.txt）
# 规则：页面内所有 .q / .qt 引文与库内文件去标点、去空白、异体字归一后逐字比对
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/天妃显圣录.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/tianfei-xiansheng-lu.html'

import re, sys

VAR = {'歳':'岁','厯':'历','歴':'历','逺':'远','髙':'高','葢':'盖','寛':'宽',
       '踈':'疏','疎':'疏','宻':'密','郤':'却','穽':'阱','毬':'球','黒':'黑',
       '隂':'阴','徳':'德','疉':'叠','乗':'乘','縁':'缘','隠':'隐','遯':'遁',
       '説':'说','毎':'每','胷':'胸','聨':'联'}

def norm(s):
    s = ''.join(VAR.get(c, c) for c in s)
    return ''.join(c for c in s if '一' <= c <= '鿿')

src = open(SRC, encoding='utf-8').read()
clean = ''.join(c for c in src if not c.isspace())
nsrc = norm(src)

html = open(HTML, encoding='utf-8').read()

# 抓取所有引文节点：先剔除出处小签与装饰节点，再剥标签
body = html
body = re.sub(r'<span class="src">.*?</span>', '', body, flags=re.S)
quotes = []
quotes += re.findall(r'<span class="q">(.*?)</span>', body, flags=re.S)
quotes += re.findall(r'<blockquote class="qt">(.*?)</blockquote>', body, flags=re.S)

fails = 0
if not quotes:
    print('FAIL 未抓到任何引文节点'); fails += 1
for i, q in enumerate(quotes, 1):
    text = re.sub(r'<[^>]+>', '', q)
    nq = norm(text)
    if not nq:
        print('FAIL 空引文 #%d：%s' % (i, text[:40])); fails += 1; continue
    if nq not in nsrc:
        print('FAIL #%d 未命中：%s' % (i, text[:60])); fails += 1

# 事实核对（库内实测）
main = src.split('●天妃诞降本传')[1].split('附录')[0]
facts = [
    ('去空白字数 36036', len(clean) == 36036),
    ('正录自诞降本传以下55段', main.count('●') + 1 == 55),
    ('附录51章', len(re.findall(r'●第[一二三四五六七八九十百零]+章', src)) == 51),
    ('正录及序无天后', '天后' not in src.split('附录')[0]),
    ('褒封二十四命题', '历朝显圣褒封共二十四命' in clean),
    ('僧照乘刊布题记', '住持僧照乘发心刊布' in clean),
    ('郑和今经七次', '今经七次' in clean),
    ('三序作者', all(x in clean for x in ['尧俞', '黄起有', '麟焻'])),
    ('师泉井记在录', '师泉井记' in clean and '耿恭拜井' in clean),
    ('二十四命年注括号25处', src.split('●历朝显圣褒封共二十四命')[1].split('●历朝褒封致祭诏诰')[0].count('（') == 25),
]
for name, ok in facts:
    if not ok:
        print('FAIL 事实：%s' % name); fails += 1

# 页面排版红线
if '—' in html or '–' in html:
    print('FAIL 页面含长划线'); fails += 1
for ln, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        print('FAIL 行%d 含%d个·：%s' % (ln, line.count('·'), line.strip()[:60])); fails += 1
if any(0xE000 <= ord(c) <= 0xF8FF for c in html):
    print('FAIL 页面含私用区字符'); fails += 1
for bad in ['<script src', '<link ', '<img ', '@import', 'http://', 'https://cdn']:
    if bad in html.replace('https://github.com/robertsong2000/daizhige-daodu', ''):
        print('FAIL 页面含外部依赖：%s' % bad); fails += 1
if html.count('<section') != html.count('</section>') or html.count('<div') != html.count('</div>') \
   or html.count('<details') != html.count('</details>') or html.count('<blockquote') != html.count('</blockquote>'):
    print('FAIL 标签不配对 section:%d/%d div:%d/%d details:%d/%d bq:%d/%d' % (
        html.count('<section'), html.count('</section>'), html.count('<div'), html.count('</div>'),
        html.count('<details'), html.count('</details>'), html.count('<blockquote'), html.count('</blockquote>')))
    fails += 1
if html.count('class="rung"') + html.count('class="rung none"') != 24:
    print('FAIL 褒封梯不是24级'); fails += 1
if 'verify_tianfei.py' not in html:
    print('FAIL 页脚未注核验方式'); fails += 1

print('引文 %d 条（.q + .qt 全抓全查），事实 %d 项，排版 6 规则' % (len(quotes), len(facts)))
print('ALL PASS' if fails == 0 else 'FAILED: %d' % fails)
sys.exit(0 if fails == 0 else 1)
