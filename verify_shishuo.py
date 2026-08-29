#!/usr/bin/env python3
# 核验 shishuo-xinyu.html：引文逐字比对库内文件 + 门墙计数机器复核 + 排版红线
import re, sys

PAGE = 'shishuo-xinyu.html'
SRC_MAIN = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/世说新语.txt'
SRC_SONG = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/正史/宋书.txt'

# 关键引文清单（规范化后必须出现在页面 .q 中，且命中库内文件）
KEY_MAIN = [
 '未若栁絮因风起', '小时了了，大未必佳', '想君小时，必当了了', '木犹如此，人何以堪',
 '既有凌霄之姿，何肻为人作耳目近玩', '子非吾友也', '吾靳固不与，广陵散于今绝矣',
 '太学生三千人上书请以为师，不许', '唯有一郎在东床上坦腹卧，如不闻', '因嫁女与焉',
 '古人贵朝闻夕死，况君前途尚可', '处遂改励，终为忠臣孝子', '乡里皆谓已死，更相庆',
 '吾本乗兴而行，兴尽而返，何必见戴', '我以天地为栋宇，屋室为防衣，诸君何为入吾防中',
 '前有大梅林，饶子，甘酸可以解渇', '士卒闻之，口皆出水，乘此得及前源',
 '以屐齿蹍之，又不得', '世说之名肇于刘向', '不知何人改为新语',
 '所记分三十八门', '惟頼是注以传', '同为考证家所引据', '义庆本小说家言',
 '祚亡于清谈', '世言江左善清谭，今阅新语，信乎其言之也', '胡儿谢朗小字也',
 '管宁华歆共园中锄菜', '白雪纷纷何所似', '撒盐空中差可拟', '公大笑乐',
 '韪大踧踖', '攀枝执条', '然流泪', '养令翮成，置使飞去', '正此好',
 '郗公云', '嵇中散临刑东市，神气不变，索琴弹之，奏广陵散', '刘伶恒纵酒放逹',
 '啮破即吐之', '魏武行役，失汲道，军皆渇', '蛟或浮或没', '且人患志之不立',
]
KEY_SONG = [
 '为性简素，寡嗜欲，爱好文义，文词虽不多，然足为宗室之表',
 '少善骑乘，及长以世路艰难，不复跨马', '招聚文学之士，近远必至',
 '太尉袁淑，文冠当时', '鲍照等并为辞章之美引为佐史国臣',
]

def norm(s):
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

fails = []
html = open(PAGE, encoding='utf-8').read()
raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.S)
src_main = open(SRC_MAIN, encoding='utf-8').read()
src_song = open(SRC_SONG, encoding='utf-8').read()
nsrc_main, nsrc_song = norm(src_main), norm(src_song)

# 1. 页面所有 .q 引文块，按标点切段逐段比对
spans = re.findall(r'<span class="q">(.*?)</span>', raw, flags=re.S)
qtexts = [re.sub(r'<[^>]+>', '', t) for t in spans]
print(f'页面 .q 引文块 {len(qtexts)} 块')
tiny = 0
for i, qt in enumerate(qtexts):
    for seg in re.findall(r'[一-鿿]+', qt):
        if len(seg) < 2:
            tiny += 1
            continue
        if seg in nsrc_main or seg in nsrc_song:
            continue
        fails.append(f'引文块 #{i+1} 片段不在库内: {seg[:40]}')
print(f'其中长度为 1 的碎片 {tiny} 个（跳过比对）')

for q in KEY_MAIN:
    if norm(q) not in ''.join(norm(x) for x in qtexts):
        fails.append(f'关键引文未在页面 .q 中出现: {q[:24]}')
    elif norm(q) not in nsrc_main:
        fails.append(f'关键引文在主库文件中不存在: {q[:24]}')
for q in KEY_SONG:
    if norm(q) not in nsrc_song:
        fails.append(f'宋书关键引文在宋书中不存在: {q[:24]}')

# 2. 门墙计数机器复核
HEAD = re.compile(r'^\s*([一-鿿]{1,4})第[一二三四五六七八九十百]+[【】上下]*\s*$')
lines = src_main.split('\n')
heads = [(i, m.group(1)) for i, l in enumerate(lines) if (m := HEAD.match(l))]
heads.append((len(lines), 'EOF'))
skip = {'梁　刘孝标　注', '宋　刘义庆　撰'}
cnt = {}
for k in range(len(heads)-1):
    s, e = heads[k][0], heads[k+1][0]
    name = heads[k][1]
    n = 0
    for l in lines[s+1:e]:
        st = l.strip()
        if not l.startswith('　　') or not st: continue
        if '钦定四库全书' in st or '世说新语卷' in st or st in skip: continue
        if st.startswith('总纂官') or st.startswith('总　校'): continue
        n += 1
    cnt[name] = cnt.get(name, 0) + n
total = sum(cnt.values())
nmenn = len(heads) - 1
print(f'机器复核：{nmenn} 扇门（赏誉上下合并），共 {total} 段')

walls = re.findall(r'style="--h:(\d+)"[^>]*data-n="(\d+)" data-name="([^"]+)"', raw)
if len(walls) != 36:
    fails.append(f'门墙应为 36 格，实际 {len(walls)}')
mx = max(cnt.values())
for h, n, name in walls:
    n = int(n)
    if cnt.get(name) != n:
        fails.append(f'门墙 {name} 页面 {n} 段，机算 {cnt.get(name)}')
    if int(h) != round(n / mx * 100):
        fails.append(f'门墙 {name} 高度 {h}% 与段数不成比例（应为 {round(n/mx*100)}）')
dcounts = re.findall(r'data-n="(\d+)" data-name="([^"]+)">.*?<span class="dcount">(\d+)段', raw)
for n, name, dn in dcounts:
    if n != dn:
        fails.append(f'门墙 {name} data-n={n} 与 dcount={dn} 不一致')
for s in ['968', '1614', '三十六门', '卷二十五', '四十六']:
    if s not in html:
        fails.append(f'页面缺少数字/标识: {s}')
if src_main.count('【') != 1614:
    fails.append(f"库本注块数机算 {src_main.count('【')}，页面写 1614")

# 3. 校记表用字须确凿见于库本
for ch in '栁隂乗肻渇甞逹壻隟爼叚頼防髙攷':
    if ch in '髙攷':
        if ch not in src_main and ch not in src_song:
            fails.append(f'校记用字不在库内: {ch}')
    elif ch not in src_main:
        fails.append(f'校记用字不在主库文件: {ch}')

# 4. 排版红线
for ch, name in [('—', 'EM DASH'), ('–', 'EN DASH'), ('‒', 'FIGURE DASH'), ('⸺', 'TWO-EM DASH'), ('⸻', 'THREE-EM DASH')]:
    if ch in html:
        fails.append(f'发现禁用字符 {name}')
plain = re.sub(r'<[^>]+>', '', raw)
for ln in plain.splitlines():
    if ln.count('·') > 1:
        fails.append(f'一行内出现 {ln.count("·")} 个 ·: {ln.strip()[:50]}')
for ch in html:
    if 0xE000 <= ord(ch) <= 0xF8FF:
        fails.append('页面含私有区字符（应以 .lost 虚框示缺字）')
        break
for pat, why in [('href="http', '外链 href'), ("href='http", '外链 href'), ('src="http', '外链 src'),
                 ('<link', '外部 link'), ('@import', '外部 import'), ('url(http', '外部资源')]:
    if pat in html:
        fails.append(f'发现外部依赖: {why}')

if len(norm(html)) < 3000:
    fails.append('页面正文疑似过短')

if fails:
    print('\nFAIL')
    for f in fails:
        print(' ×', f)
    sys.exit(1)
print('\n全部通过：引文逐字命中库内文件；门墙 36 格与机算一致；无长划线；每行 · ≤1；无私有区字符；零外部依赖')
