import json, re, sys

LIB = '../daizhige-simplified/史藏/志存记录/朝野佥载.txt'
PAGE = 'chaoye-qinzai.html'

norm = lambda s: re.sub(r'\s+', '', s)
lib = norm(open(LIB, encoding='utf-8').read())
raw = open(PAGE, encoding='utf-8').read()
text = re.sub(r'<[^>]+>', '', re.sub(r'<script[\s\S]*?</script>', '', raw))
pt = norm(text)
fails = []

# 1 引文双侧核验
qs = json.load(open('quotes_chaoye.json', encoding='utf-8'))
for k, v in qs.items():
    nv = norm(v)
    if nv not in lib:
        fails.append(f'[库本缺] {k}')
    if nv not in pt:
        fails.append(f'[页面缺] {k}')
print(f'引文 {len(qs)} 条 双侧核验 {"通过" if not fails else "失败"}')

# 2 标签短语（卡片/签内短引）
TAGS = ['仙人献果', '玉女登梯', '犊子悬车', '驴驹拔橛',
        '赤黧豹', '白额豹', '黑豹', '布施',
        '满路悲号，声动山谷', '落栈着石，百无一存',
        '张公吃酒李公醉', '观法师即是菩萨行人也']
for t in TAGS:
    if norm(t) not in lib:
        fails.append(f'[标签库本缺] {t}')
    if norm(t) not in pt:
        fails.append(f'[标签页面缺] {t}')
print(f'标签短语 {len(TAGS)} 条 双侧核验')

# 3 排版红线
if re.search(r'[—–]', raw):
    fails.append('[禁长划线] 页面含 — 或 –')
chunks = [c for c in re.split(r'<[^>]+>|\n', raw) if '·' in c]
for c in chunks:
    if c.count('·') > 1:
        fails.append(f'[·限用] 一行多·: {c.strip()[:40]}')
print(f'红线检查：长划线 / ·（{len(chunks)} 行含·，均不超1） / PUA')
pua = [c for c in set(raw) if 0xE000 <= ord(c) <= 0xF8FF]
if pua:
    fails.append(f'[零PUA] {pua}')
print('红线检查：长划线 / · / PUA')

# 4 零外部依赖
if re.search(r'<link|<script[^>]+src|@import|url\(', raw):
    fails.append('[外部依赖] 发现外链资源')
print('零外部依赖检查')

# 5 字数自述 / 篇号 / 页脚
need = ['58660', '第二百零六篇', '殆知阁古代文献简体库',
        'github.com/robertsong2000/daizhigev20',
        '脚本核验通过', '不代表编者立场', '<title>朝野佥载 · 殆知阁导读</title>']
for t in need:
    if t not in raw:
        fails.append(f'[缺要素] {t}')
print('要素检查：字数自述 / 篇号 / 页脚三件套 / title')

if fails:
    print('\nFAIL')
    for f in fails:
        print(' ', f)
    sys.exit(1)
print('\nALL PASS')
