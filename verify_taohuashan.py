#!/usr/bin/env python3
# 桃花扇 导读页核验：全页 .q 引文逐段对库 + 出目墙对表 + 机器计数 + 排版红线
import re, sys, unicodedata

ROOT = '/home/robertsong/workspace/claude/daizhige-daodu/'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/诗藏/剧曲/桃花扇.txt'
PAGE = ROOT + 'taohua-shan.html'

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB,  encoding='utf-8').read()
errs = []
def chk(cond, msg):
    if not cond: errs.append(msg)

def norm(s):
    out = []
    for ch in s:
        if ch.isspace(): continue
        c = unicodedata.category(ch)
        if c.startswith('P') or c.startswith('S'): continue
        out.append(ch)
    return ''.join(out)

libnorm = norm(lib)
pagenorm = norm(re.sub(r'<[^>]+>', '', page))

# ---------- 库本实测 ----------
nchars = len(re.sub(r'\s', '', lib))
chk(nchars == 100817, f'全帙字数 {nchars} != 100817')

CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def cn2n(s):
    if s == '十': return 10
    if '十' in s:
        a, _, b = s.partition('十')
        return (CN.get(a, 1) if a else 1) * 10 + (CN.get(b, 0) if b else 0)
    return CN[s]

lines = lib.split('\n')
heads = []
for l in lines:
    t = l.strip()
    m = re.match(r'^(●?)(试一出|闰二十出|加二十一出|续四十出|第[一二三四五六七八九十]+出)[　\s]+(\S.*)$', t)
    if m:
        heads.append({'bullet': m.group(1) == '●', 'num': m.group(2),
                      'name': re.sub(r'[　\s]', '', m.group(3))})
chk(len(heads) == 43, f'出目标题 {len(heads)} != 43')
chk(sum(1 for h in heads if h['bullet']) == 1, '●题前符号应恰 1 处')
numbered = [cn2n(h['num'][1:-1]) for h in heads if h['num'].startswith('第')]
chk(sorted(numbered) == [n for n in range(1, 41) if n != 15], f'正出编号异常: {sorted(numbered)}')
headkeys = {h['num'] + h['name'] for h in heads}

# ---------- .q 收集（标签平衡扫描，剥 .who） ----------
TAG = re.compile(r'<(/?)([a-zA-Z0-9]+)([^>]*)>')
VOID = {'br', 'hr', 'img', 'meta', 'link', 'input'}
KEEP = {'span', 'blockquote', 'div', 'b', 'em', 'small', 'i', 'p', 'a', 'strong'}

def span_block(s, start):
    """start 为某开标签内 class 属性处；返回 (该元素 inner, 元素结束位置)"""
    tagopen = s.rindex('<', 0, start)
    outer = re.match(r'<([a-zA-Z0-9]+)', s[tagopen:]).group(1).lower()
    i = s.index('>', start) + 1
    stack = [outer]
    j = i
    while True:
        t = TAG.search(s, j)
        if not t: raise RuntimeError('unbalanced at %d' % start)
        name, closing = t.group(2).lower(), t.group(1) == '/'
        if closing:
            if stack and stack[-1] == name: stack.pop()
        elif name not in VOID:
            stack.append(name)
        j = t.end()
        if not stack:
            return s[i:t.start()], j

def strip_who(inner):
    out, pos = [], 0
    for m in re.finditer(r'class="([^"]*)"', inner):
        if 'who' in m.group(1).split():
            tagstart = inner.rindex('<', 0, m.start())
            _, end = span_block(inner, m.start())
            out.append(inner[pos:tagstart]); pos = end
    out.append(inner[pos:])
    return ''.join(out)

qtexts = []
for m in re.finditer(r'class="([^"]*)"', page):
    if 'q' in m.group(1).split():
        inner, _ = span_block(page, m.start())
        text = re.sub(r'<[^>]+>', '', strip_who(inner))
        qtexts.append(text)

chk(len(qtexts) >= 30, f'.q 引文仅 {len(qtexts)} 段，疑似漏抓')
for i, t in enumerate(qtexts):
    n = norm(t)
    chk(len(n) >= 5, f'.q#{i+1} 过短: {t[:20]}')
    chk(n in libnorm, f'.q#{i+1} 不在库内: {t[:42]}')

# ---------- 独立抽检清单（防漏 class） ----------
QUOTES = [
 '借离合之情，写兴亡之感，实事实人，有凭有据。',
 '老夫原是南京太常寺一个赞礼,爵位不尊，姓名可隐。',
 '那满座宾客，怎晓得我老夫就是戏中之人！',
 '最喜无祸无灾，活了九十七岁，阅历多少兴亡，又到上元甲子。',
 '古董先生谁似我？非玉非铜，满面包浆裹。剩魄残魂无伴伙，时人指笑何须躲。',
 '公子侯生，秣陵侨寓，恰偕南国佳人；谗言暗害，鸾凤一宵分。',
 '这些妆奁酒席，约费二百余金，皆出怀宁之手。',
 '官人之意，不过因他助俺妆奁，便要徇私废公；那知道这几件钗钏衣裙，原放不到我香君眼里。',
 '脱裙衫，穷不妨；布荆人，名自香。',
 '平康巷，他能将名节讲；偏是咱学校朝堂，偏是咱学校朝堂，混贤奸不问青黄。',
 '便等他三年；便等他十年；便等他一百年；只不嫁田仰。',
 '忍寒饥，决不下这翠楼梯。',
 '奴家就死不下此楼。',
 '你看血喷满地，连这诗扇都溅坏了。',
 '你看疏疏密密，浓浓淡淡，鲜血乱蘸。不是杜鹃抛；是脸上桃花做红雨儿飞落，一点点溅上冰绡。',
 '樱唇上调朱，莲腮上临稿，写意儿几笔红桃。补衬些翠枝青叶，分外夭夭，薄命人写了一幅桃花照。',
 '便面小，血心肠一万条；手帕儿包，头绳儿绕，抵过锦字书多少。',
 '赵文华陪着严嵩，抹粉脸席前趋奉；丑腔恶态，演出真鸣凤。俺做个女祢衡，挝渔阳，声声骂；看他懂不懂。',
 '堂堂列公，半边南朝，望你峥嵘。出身希贵宠，创业选声容，后庭花又添几种。',
 '东林伯仲，俺青楼皆知敬重。干儿义子从新用，绝不了魏家种。',
 '冰肌雪肠原自同，铁心石腹何愁冻。',
 '奴家已拚一死。吐不尽鹃血满胸，吐不尽鹃血满胸。',
 '俺史可法率三千子弟，死守扬州，那知力尽粮绝，外援不至。',
 '撇下俺断篷船，丢下俺无家犬；叫天呼地千百遍，归无路，进又难前。',
 '俺史可法亡国罪臣，那容的冠裳而去。',
 '你看茫茫世界，留着俺史可法何处安放。累死英雄，到此日看江山换主，无可留恋。',
 '长江一线，吴头楚尾路三千。尽归别姓，雨翻云变。寒涛东卷，万事付空烟。',
 '我想扬州梅花岭，是他老人家点兵之所，待大兵退后，俺去招魂埋葬，便有史阁部千秋佳城了。',
 '呵呸！两个痴虫，你看国在那里，家在那里，君在那里，父在那里，偏是这点花月情根，割他不断么？',
 '看鲜血满扇开红桃，正说法天花落。',
 '亏了俺桃花扇扯碎一条条，再不许痴虫儿自吐柔丝缚万遭。',
 '白骨青灰长艾萧，桃花扇底送南朝；不因重做兴亡梦，儿女浓情何处消。',
 '山松野草带花桃，猛抬头秣陵重到。残军留废垒，瘦马卧空壕。',
 '野火频烧，护墓长楸多半焦。山羊群跑，守陵阿监几时逃？',
 '横白玉八根柱倒，堕红泥半堵墙高，碎琉璃瓦片多，烂翡翠窗棂少。',
 '罢灯船端阳不闹，收酒旗重九无聊。白鸟飘飘，绿水滔滔。',
 '你记得跨青溪半里桥，旧红板没一条。',
 '行到那旧院门，何用轻敲，也不怕小犬哰哰。',
 '俺曾见金陵王殿莺啼晓，秦淮水榭花开早，谁知道容易冰消。',
 '眼看他起朱楼',
 '眼看他宴宾客',
 '眼看他楼塌了',
 '这青苔碧瓦堆，俺曾睡风流觉，将五十年兴亡看饱。',
 '那乌衣巷不姓王，莫愁湖鬼夜哭，凤凰台栖枭鸟。',
 '残山梦最真，旧境丢难掉，不信这舆图换稿。诌一套《哀江南》，放悲声唱到老。',
 '长桥已无片板，旧院剩了一堆瓦砾。',
 '建业城啼夜鬼，维扬井贮秋尸；樵夫剩得命如丝，满肚南朝野史。',
]
for q in QUOTES:
    n = norm(q)
    chk(n in libnorm, f'抽检不在库内: {q[:30]}')
    chk(n in pagenorm, f'抽检不在页面: {q[:30]}')

# ---------- 十二祥瑞 ----------
chips = re.findall(r'<span><i>[^<]*</i>([^<]+)</span>', page)
chk(len(chips) == 12, f'祥瑞签 {len(chips)} != 12')
for c in chips:
    chk(norm(c) in libnorm, f'祥瑞签不在库内: {c}')
chk(norm('，'.join(chips) + '。') in libnorm, '祥瑞十二签连读与库本不符')

# ---------- 出目墙 ----------
slots = re.findall(r'<div class="slot([^"]*)"><span class="n">(.*?)</span><span class="nm">([^<]+)</span></div>', page)
chk(len(slots) == 44, f'出目墙格数 {len(slots)} != 44（43 实 + 1 缺）')
miss = [s for s in slots if 'miss' in s[0]]
chk(len(miss) == 1 and miss[0][1] == '第十五出' and miss[0][2] == '缺', '缺格标注不对')
seen = set()
for cls, n, nm in slots:
    if 'miss' in cls: continue
    key = re.sub(r'[●\s]', '', re.sub(r'<[^>]+>', '', n)) + nm
    chk(key in headkeys, f'出目格不在库本标题集: {key}')
    seen.add(key)
chk(seen == headkeys, f'出目墙与库本标题集不一致，差: {headkeys ^ seen}')
hot = [s for s in slots if 'hot' in s[0]]
chk({s[2] for s in hot} == {'却奁', '守楼', '寄扇', '骂筵', '沈江', '入道'}, '选读高亮格异常')
fr = [s for s in slots if 'fr' in s[0]]
chk(len(fr) == 4, f'框架出格 {len(fr)} != 4')

# ---------- 哀江南七站 ----------
stas = re.findall(r'<div class="sta"><div class="pai">([^<]+)<small>([^<]+)</small></div><div class="sq">(.*?)</div></div>', page, re.S)
chk(len(stas) == 7, f'哀江南站 {len(stas)} != 7')
for pai, where, sq in stas:
    chk(pai in {'北新水令', '驻马听', '沉醉东风', '折桂令', '沽美酒', '太平令', '离亭宴带歇指煞'},
        f'曲牌名异常: {pai}')
    chk(norm(re.sub(r'<[^>]+>', '', sq)) in libnorm, f'站内引文不在库内: {pai}')

# ---------- 日期线 ----------
ribs = re.findall(r'<div class="r"><b>([^<]+)</b><small>([^<]+)</small></div>', page)
chk(len(ribs) == 10, f'日期签 {len(ribs)} != 10')
for name, date in ribs:
    if date == '三十六年':
        chk(name == '首尾相隔' and 1684 - 1648 == 36, '三十六年换算不符')
        chk('康熙二十三年' in lib and '1684' in page and '1648' in page, '首尾年份标注缺失')
    else:
        chk(date in lib, f'日期不在库内: {name} {date}')

# ---------- 戏比书老十五年 ----------
chk('康熙三十八年' in page and 1699 - 1684 == 15, '十五年悖论标注不符')

# ---------- 页面统计数字 ----------
chk('100,817' in page and f'{nchars:,}' == '100,817', '全帙字数页码不符')
chk('43</b>' in page, '统计 43 缺失')
chk('39<span' in page, '统计 39/40 缺失')

# ---------- 页脚引文计数 ----------
m = re.search(r'本页引文 (\d+) 处', page)
chk(bool(m), '页脚缺引文计数')
if m: chk(int(m.group(1)) == len(qtexts), f'页脚计数 {m.group(1)} != 实抓 {len(qtexts)}')

# ---------- 排版红线 ----------
chk('—' not in page, '出现长划线 —')
chk('–' not in page, '出现短划线 –')
for i, ln in enumerate(page.split('\n'), 1):
    c = ln.count('·')
    chk(c <= 1, f'第{i}行有 {c} 个 ·')

# ---------- 结果 ----------
print(f'.q 引文 {len(qtexts)} 段全部对库通过' if not errs else '')
for e in errs: print('FAIL:', e)
print('ALL PASS' if not errs else f'{len(errs)} FAILURES')
sys.exit(1 if errs else 0)
