#!/usr/bin/env python3
# 园冶 页面核验：引文逐字 + 排版规则 + 篇目计数 + 缺篇声明
import re, sys

PAGE = 'yuanye.html'
SRC = '../daizhige-simplified/艺藏/工艺/园冶.txt'

def norm(t):
    return re.sub(r'[\s，。：；、「」『』？！（）《》〈〉\.\,\:\;\"\'\?\!\-—–·◎（）()〔〕]+', '', t)

page = open(PAGE, encoding='utf-8').read()
src = open(SRC, encoding='utf-8').read()
nsrc = norm(src)

fails = []

# 1. 抽取页面所有 .q 元素，逐个要求：页面文本含之 + 库内文件含之
qs = re.findall(r'class="q"[^>]*>(.*?)</(?:blockquote|span|p|div|td)>', page, re.S)
quotes = []
for raw in qs:
    txt = re.sub(r'<[^>]+>', '', raw)
    for frag in re.split(r'(?:</p>)|(?:\n)', txt):
        frag = frag.strip()
        if frag:
            quotes.append(frag)
seen = set()
for q in quotes:
    nq = norm(q)
    if not nq or nq in seen:
        continue
    seen.add(nq)
    if nq not in nsrc:
        fails.append(f'引文不在库内: {q[:40]}')

print(f'核验引文片段 {len(seen)} 条')

# 2. 关键断言性陈述的库内证据
must_in_src = ['或问日', '巧于因界', '全叼人力', '远借，邻界', '存式百状', '其状可骇，万无一失', '园牧', '崇祯辛未', '崇祯甲戌']
for m in must_in_src:
    if m not in src:
        fails.append(f'库内缺证据串: {m}')

# 3. 缺篇与库外声明：园说/八字名句/阮大铖 均不在库内文本
for absent in ['园说', '虽由人作', '宛自天开', '阮大铖', '冶叙']:
    if absent in src:
        fails.append(f'声明缺席者却出现在库内: {absent}')
for absent in ['虽由人作', '宛自天开']:
    if absent in page:
        fails.append(f'页面不得引用库外名句: {absent}')

# 4. 排版：禁长划线；渲染行 · ≤1
for ch, name in [('—', '——'), ('–', '–'), ('‒', '―'), ('―', '―')]:
    if ch in page:
        fails.append(f'禁用字符 {name} 出现')
text_only = re.sub(r'<style>.*?</style>', '', page, flags=re.S)
text_only = re.sub(r'<[^>]+>', '\n', text_only)
for i, line in enumerate(text_only.split('\n')):
    if line.count('·') > 1:
        fails.append(f'渲染行多·: {line.strip()[:40]}')

# 5. 无外部依赖
if re.search(r'(src|href)\s*=\s*"https?:', page):
    fails.append('存在外部资源链接')

# 6. 篇目计数：与库内文件重算比对
def slice_between(a, b=None):
    i = src.find(a)
    j = src.find(b) if b else len(src)
    return src[i:j] if i >= 0 else ''

xiangdi = slice_between('一、相地', '二、立基')
liji = slice_between('二、立基', '三、屋宇')
wuyu = slice_between('三、屋宇', '◎屋宇图式')
langan = slice_between('卷二', '卷三')
duoshan = slice_between('四、掇山', '五、选石')
xuanshi = slice_between('五、选石', '六、借景')

def count_sub(line_re, blob):
    return len(re.findall(line_re, blob, re.M))

counts = {
    '相地六类': (count_sub(r'（[一二三四五六]）、', xiangdi), 6),
    '立基七处': (count_sub(r'（[一二三四五六七]）、', liji), 7),
    '屋宇二十二目': (count_sub(r'（[一二三四五六七八九十]+）、', wuyu), 22),
    '掇山十七法': (count_sub(r'（[一二三四五六七八九十]+）、', duoshan), 17),
    '选石十六品': (count_sub(r'（[一二三四五六七八九十]+）、', xuanshi), 16),
    '栏杆八式存名': (count_sub(r'^[^\n]*式[：。]', langan), 8),
}
for name, (got, want) in counts.items():
    if got != want:
        fails.append(f'计数 {name}: 页面称 {want}，库内实得 {got}')
print('篇目计数:', {k: v[0] for k, v in counts.items()})

if fails:
    print('\nFAIL')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('PASS: 引文逐字、排版规则、计数、缺篇声明全部通过')
