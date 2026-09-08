#!/usr/bin/env python3
"""九命奇冤 导读页核验：引文逐字比对库本 + 排版红线 + 数字声明"""
import re, sys, unicodedata

L1 = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/九命奇冤.txt'
L2 = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/警富新书.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/jiuming-qiyuan.html'

lib1 = open(L1, encoding='utf-8').read()
lib2 = open(L2, encoding='utf-8').read()
page = open(HTML, encoding='utf-8').read()

def norm(s):
    s = re.sub(r'\s+', '', s)
    return ''.join(ch for ch in s if unicodedata.category(ch)[0] not in ('P', 'S', 'Z'))

l1n, l2n = norm(lib1), norm(lib2)

fails = 0
def ok(msg): print(f'[OK]   {msg}')
def bad(msg): print(f'[FAIL] {msg}'); globals()['fails'] += 1

# 1) blockquote 引文：与两份库本任一逐字比对
quotes = []
for m in re.finditer(r'<blockquote class="bq">(.*?)</blockquote>', page, re.S):
    body = re.sub(r'<span class="src">.*?</span>', '', m.group(1), flags=re.S)
    body = re.sub(r'<span class="who">.*?</span>', '', body, flags=re.S)
    quotes.append(re.sub(r'<[^>]+>', '', body).strip())
print(f'blockquote 引文 {len(quotes)} 段')
for q in quotes:
    qn = norm(q)
    if not qn: bad(f'空引文 {q[:20]}'); continue
    in1, in2 = qn in l1n, qn in l2n
    if in1 or in2:
        ok(f'{"新本" if in1 else ""}{"底本" if in2 else ""} {q[:26]}')
    else:
        bad(f'两本皆无 {q[:30]}')

# 2) 行内织入片段（prose 中未加引号或加「」的原文字样）
inline = [
    '借历史上的公案，加以新的内容，来攻击当日黑暗地狱中的贪官污吏',
    '似乎是受了外国小说的影响，这是本书的一个特色',
    '恶听堪舆之言，勒某拆居相让，长伊风水。某念父置子不弃，相拒成仇，屡被势逼',
    '阴阳地理', '看风水看的灵', '诨号', '钻穿石',
    '见了酒不要命的', '弹压', '灌他一个烂醉', '等大爷亲来验明再杀',
    '烧够了两个多时辰', '鞭敲金镫响，人唱凯旋歌',
    '张凤掼在地下', '好一位义士',
    '实系被烟闷死，别无伤痕', '生妻叶氏，已经有身五月',
    '炭灰烧红', '淬在醋里',
    '二百银子', '茶资', '须得要抄了他的底子来', '教他口供', '终日在街头赌博',
    '虎豪叠噬抄杀七尸八命事', '财神摆布巧织瞒详八命沉冤号天究救事',
    '捏凶叠噬坑杀八命七尸台宪受贿沉冤干证非刑受夹号天超雪死生有赖事',
    '屠证沉冤坑生灭死千金易捏九命难伸鬼泣人悲泣叩超生雪死事',
    '恶以雄财贿县', '恶以雄财大贿刑证沉冤', '逼蚁具词存案', '行牌吊审', '所供如故',
    '夹棍', '照壁', '刑法可以乱行，我口不可以乱说',
    '落地舌', '射日矢', '包天胆', '擎天木', '跛脚夫', '四蹄儿', '双角目', '钻穿石',
    '死后加刑', '东来', '登朝抱告', '欲知三人后世端详，请看',
    '警富后传', '托生惠州府，瞽目为奴', '宗孔哑口丐食',
]
for f in inline:
    fn = norm(f)
    if fn in l1n: ok(f'行内·新本 {f[:24]}')
    elif fn in l2n: ok(f'行内·底本 {f[:24]}')
    else: bad(f'行内两本皆无 {f[:30]}')

# 3) 数字与事实声明
n1 = len(re.sub(r'\s', '', lib1)); n2 = len(re.sub(r'\s', '', lib2))
ok(f'新本去空白 {n1}') if n1 == 64305 else bad(f'新本字数 {n1} != 64305')
ok(f'底本去空白 {n2}') if n2 == 75216 else bad(f'底本字数 {n2} != 75216')
for v in ['64305', '75216']:
    if v in page: ok(f'页面声明 {v}')
    else: bad(f'页面未声明 {v}')
chs = len(re.findall(r'第[一二三四五六七八九十]{1,3}回　', lib1))
if chs == 19: ok('新本正文回数 19')
else: bad(f'新本正文回数 {chs} != 19')
if '三十六回' in lib1 and '三十六回' in page: ok('识语三十六回声明一致')
else: bad('三十六回声明缺失')
c2 = len(re.findall(r'第[一二三四五六七八九十百]{1,4}回', lib2))
if c2 >= 40: ok(f'底本回数 {c2}')
else: bad(f'底本回数异常 {c2}')
# 置信
cat = open('/home/robertsong/workspace/claude/catalog.csv', encoding='utf-8').read()
if '九命奇冤,吴趼人,清,晚清谴责小说,确定' in cat: ok('书目置信 确定')
else: bad('书目置信行不匹配')
# 讹字声明
rare = [ch for ch in set(lib1) if ord(ch) > 0xFFFF]
cnt = sum(lib1.count(ch) for ch in rare)
if rare and cnt == 10 and f'U+{ord(rare[0]):05X}' in page: ok(f'生僻字 U+{ord(rare[0]):05X} 十见已声明')
else: bad(f'生僻字核对 {[(f"U+{ord(c):05X}", lib1.count(c)) for c in rare]}')
for pair in [('锅于戊申年', '祸讹作锅'), ('抢雪菊', '去讹作雪'), ('两退', '腿讹作退'),
             ('粱天来', '梁粱互见'), ('抚慰天未', '天未互见')]:
    src = l2n if pair[0] in l2n else l1n
    (ok if norm(pair[0]) in (l2n if pair[0] in l2n else l1n) else bad)(f'{pair[1]} ({pair[0]})')
if '张风' in lib1: ok('凤风互见（新本）')
else: bad('新本未见张风')
# 目录止于十九
ml = re.findall(r'第[一二三四五六七八九十]{1,3}回 [^\n]{4,}', lib1[:lib1.find('第一回　乱哄哄')])
if ml and len(ml) == 19: ok('库本目录恰列十九回')
else: bad(f'目录条数 {len(ml)}')
if '第十九回' in page and '第十九回' in lib1: ok('断点第十九回双方一致')
else: bad('第十九回声明缺失')

# 4) 排版红线
for ch, name in [('—', '长划线—'), ('–', '短划线–'), ('─', '制表线─'), ('│', '竖线│')]:
    if ch in page: bad(f'出现 {name}')
    else: ok(f'无{name}')
for i, line in enumerate(page.split('\n'), 1):
    c = line.count('·')
    if c > 1: bad(f'源码第{i}行有{c}个·')
for i, line in enumerate(page.split('\n'), 1):
    if '<blockquote' in line and line.count('<blockquote') > 1: bad(f'第{i}行多blockquote')
# 引号配平（正文文本节点）
body_txt = re.sub(r'<script.*?</script>', '', page, flags=re.S)
body_txt = re.sub(r'<[^>]+>', '', body_txt)
if body_txt.count('「') != body_txt.count('」'): bad(f'「」不配平 {body_txt.count("「")}/{body_txt.count("」")}')
else: ok('「」配平')

# 5) 特殊字符扫描
for i, ch in enumerate(page):
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF or 0xF900 <= o <= 0xFAFF or o > 0xFFFF:
        bad(f'页面含特殊字符 U+{o:05X} @ {page[max(0,i-20):i+8]!r}')

print()
print('全部通过' if fails == 0 else f'{fails} 项失败')
sys.exit(1 if fails else 0)
