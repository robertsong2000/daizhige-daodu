#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_baishigequ.py — 白石道人歌曲 导读页核验
双侧逐字：EXPECTED 每条须「在库本」且「在页面某 .q 块」；反扫：页面全部 .q 须「在库本」。
红线：禁 — – ；每行 · ≤1 ；「」内容须在库本；英文残留。机数：字数/空框/防/PUA/卷结构/调名/稼轩。
"""
import re, sys
from html.parser import HTMLParser

LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/诗藏/词集/白石道人歌曲.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/baishi-gequ.html'

lib  = open(LIB,  encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()

FAILS = []
def chk(cond, msg):
    if not cond:
        FAILS.append(msg)
        print('FAIL:', msg)

# ---------- norm：只保留 CJK 汉字 + □ + 私有区 ----------
def norm(s):
    out = []
    for c in s:
        o = ord(c)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF or c == '□' or 0xE000 <= o <= 0xF8FF:
            out.append(c)
    return ''.join(out)

NLIB = norm(lib)

# ---------- 收集页面 .q 块 ----------
VOID = {'br','img','meta','link','hr','input','area','base','col','embed','source','track','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.qdepth = 10**9; self.cur = None; self.outs = []
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        self.stack.append(tag)
        if self.cur is None:
            cls = (dict(attrs).get('class') or '').split()
            if 'q' in cls:
                self.qdepth = len(self.stack); self.cur = []
    def handle_endtag(self, tag):
        if tag in VOID: return
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack: self.stack.pop()
        if self.cur is not None and len(self.stack) < self.qdepth:
            self.outs.append(''.join(self.cur)); self.cur = None; self.qdepth = 10**9
    def handle_data(self, d):
        if self.cur is not None: self.cur.append(d)

qc = QC(); qc.feed(page)
blocks = [norm(b) for b in qc.outs if norm(b)]
chk(len(blocks) >= 60, f'收集 .q 块过少：{len(blocks)}')

# ---------- 反扫：每个 .q 都须在库本 ----------
for i, b in enumerate(blocks):
    chk(b in NLIB, f'.q 反扫 MISS #{i}: {b[:44]}')

# ---------- 期望清单：双侧 ----------
EXPECTED = [
 '词亦精深华妙尤善自度新腔故音节文采并冠绝一时',
 '其诗所谓自制新词韵最娇小红低唱我吹箫者风致尚可想见',
 '旧有毛晋汲古阁刋板仅三十四阕而题下小序往往不载原文康熙甲午陈撰刻其诗集以词附后亦仅五十八阕',
 '此本从宋椠翻刻最为完善',
 '巻一宋铙歌十四首越九歌十首琴曲一首',
 '巻二词三十三首总题曰令',
 '巻三词二十首总题曰慢',
 '巻四词十三首皆题曰自制曲',
 '别集词十八首不复标列总名疑后人所掇拾也',
 '其九歌皆注律吕于字旁琴曲亦注指法于字旁皆尚可解',
 '惟自制曲一巻及二巻鬲溪梅令杏花天影醉吟商小品玉梅令三巻之霓裳中序第一皆记拍于字旁',
 '宋代曲谱今不可见亦无人能歌莫辨其节奏安在然歌词之法仅仅留此一线录而存之安知无悬解之士能寻其分别者乎鲁鼓薛鼓亡其音而留其谱亦此意也',
 '越人好祠其神多古圣贤予依九歌为之辞且系其声使歌以祠之',
 '南蕤林南林黄太姑蕤姑太姑林黄太黄清清清应南林南央央帝旗群冕相舆聿来我妫我芸绿滋',
 '侧商之调久亡唐人诗云侧商调里唱伊州',
 '此调甚流美也',
 '予既得此调',
 '法并古怨',
 '日暮四山兮烟雾暗前浦将维舟兮无所',
 '过金谷兮花谢委尘土',
 '七一七六五',
 '上十','下七','六九','平声',
 '黄钟宫','黄钟商','黄钟角','黄钟变征侧','黄钟羽','黄钟变宫侧','黄钟清商',
 '淮左名都竹西佳处解鞍少住初程',
 '自胡马窥江去后废池乔木犹厌言兵',
 '清角吹寒都在空城',
 '二十四桥仍在波心荡□□□□一□□□□□□□□□□冷月无声',
 '念桥边红药年年知为谁生',
 '淳熙丙申至日余过维扬夜雪初霁荠麦弥望入其城则四顾萧条寒水自碧暮色渐起戍角悲吟予怀怆然感慨今昔因自度此曲千岩老人以为有黍离之悲也',
 '予颇喜自制曲初率意为长短句然后恊以律故前后阕多不同',
 '登祝融因得其祠神之曲曰黄帝盐苏合香又于乐工故书中得商调霓裳曲十八阕皆虚谱无辞',
 '予方羇游感此古音不自知其辞之怨抑也',
 '丙午之冬发沔口丁未正月二日道金陵北望淮楚风日清淑小舟挂席容与波上',
 '燕鴈无心太湖西畔随云去数峰清苦商畧黄昏雨',
 '第四桥边拟共天随住今何许凭防怀古残柳参差舞',
 '辛亥之冬予载雪诣石湖止既月授简索句且征新声作此两曲石湖把玩不已使工妓肄习之音节谐婉乃名之曰暗香疎影',
 '予因祝曰得一席风径至居巢当以平韵满江红为迎送神曲言讫风与笔俱驶顷刻而成',
 '书以绿笺沈于白浪辛亥正月晦也',
 '仙姥来时正一望千顷翠澜',
 '土人祠姥輙能歌此词',
 '丙辰岁与张功父防饮张达可之堂',
 '好事者或以二三十万钱致一枚镂象齿为楼观以贮之',
 '淝水东流无尽期当初不合种相思梦中未比丹青见暗里忽惊山鸟啼',
 '谁教岁岁红莲夜两处沈吟各自知',
  '予每自度曲吟洞箫商卿輙歌而和之极有山林缥缈之思',
 '中夕相呼步垂虹星斗下垂错杂渔火朔吹凛凛巵酒不能支朴翁以衾自纒犹相与行吟',
 '此行既归各得五十余解',
 '予去武昌十年故人有泊舟鹦鹉洲者闻小姬歌此词问之颇能道其事还吴为予言之兴怀昔游且伤今之离索也',
 '月冷龙沙尘清虎落今年汉酺初赐新翻小部曲',
 '使以哑觱栗吹之其韵极美亦曰瑞鹤仙影',
 '凡能吹竹者便能过腔也',
 '庆元五年青龙在己亥番阳民姜夔顿首上尚书',
 '臣今制曲辞十四首昧死以献',
 '讨者弗戮执者弗刘',
 '其辞舒和与前作异',
 '歌曲特文人余事耳或者少谐音律白石留心学古有志雅乐',
 '嘉泰壬戌刻于云间之东岩其家转徙自随珍藏者五十载淳祐辛亥复归嘉禾郡斋',
 '端午日菊坡赵与訔书',
 '千岁令威夫岂偶然',
 '此书俾他人抄录故多有悮字今将善本勘雠方可人意',
 '宋姜防撰防有綘帖平续书谱诗集诗说俱别着录',
 '防绛唇',
 '防芳心休诉琵琶解语',
 '秋水且涸荷叶出地防丈',
 '空叹时序侵防',
 '合下四四下一一上勾尺下工工下凡凡六下五五一五黄大太夹姑仲防林夷南无应',
 '即其声比无字防高余皆以下字为凖',
 '予自孩防从先人宦于古沔女须因嫁焉',
 '黍离之悲',
 '鬲溪梅令','隔溪梅令',
 '黄木香赠辛稼轩','北固楼次稼轩韵',
 '淮南皓月冷千山冥冥归去无人管',
 '万古西湖寂寞春惆怅谁能赋',
 '丙辰之冬予留梁溪将诣淮而不得因梦思以述志',
]
ALLQ = '\n'.join(blocks)
for q in EXPECTED:
    nq = norm(q)
    chk(nq in NLIB, f'库本无：{q[:36]}')
    chk(any(nq in b for b in blocks), f'页面 .q 未载：{q[:36]}')
print(f'EXPECTED 双侧: {len(EXPECTED)} 条核对完毕')

# ---------- 红线 ----------
chk('—' not in page and '–' not in page, '存在长划线')
for i, l in enumerate(page.split('\n')):
    chk(l.count('·') <= 1, f'第{i}行 · 超一枚')
for m in re.finditer(r'「([^」]+)」', page):
    chk(m.group(1) in lib, f'「」内容不在库本：{m.group(1)[:20]}')
body = re.sub(r'<(style|script)[\s\S]*?</\1>', '', page)
body = re.sub(r'<[^>]+>', '', body)
words = set(w for w in re.findall(r'[A-Za-z]{4,}', body))
chk(words <= {'github','robertsong','mulu','daizhigev','html'}, f'英文残留：{words}')

# ---------- 机数：库本实测 ----------
nospace = len(re.sub(r'\s', '', lib))
han = sum(1 for c in lib if '㐀' <= c <= '鿿')
box = lib.count('□')
fang = lib.count('防')
pua_n = sum(1 for c in lib if 0xE000 <= ord(c) <= 0xF8FF)
pua_d = len(set(c for c in lib if 0xE000 <= ord(c) <= 0xF8FF))
print(f'库本实测：去空白 {nospace}　汉字 {han}　□ {box}　防 {fang}　PUA {pua_n} 见 {pua_d} 种')
chk(nospace == 15870, '去空白字数不符')
chk(han == 14117, '汉字数不符')
chk(box == 1436, '□ 总数不符')
chk(fang == 76, '防 总数不符')
chk(pua_n == 75 and pua_d == 18, 'PUA 计数不符')
chk(lib.count('【平声】') == 1, '【平声】活口数不符')
chk(lib.count('稼轩') == 4, '稼轩见数不符')

# 分卷 □（按行切片）
lines = [l.strip() for l in lib.split('\n') if l.strip()]
def idx(name):
    for i, l in enumerate(lines):
        if l == name: return i
i1, i2, i3, i4 = idx('白石道人歌曲巻一'), idx('白石道人歌曲巻二'), idx('白石道人歌曲巻三'), idx('白石道人歌曲巻四')
ib, ip = idx('白石道人歌曲别集'), idx('白石道人歌曲跋')
segs = {'v1': lines[i1:i2], 'v2': lines[i2:i3], 'v3': lines[i3:i4], 'v4': lines[i4:ib], 'vb': lines[ib:ip]}
cnt = {k: sum(s.count('□') for s in v) for k, v in segs.items()}
print('分卷□：', cnt)
chk(cnt == {'v1': 67, 'v2': 194, 'v3': 95, 'v4': 1080, 'vb': 0}, f'分卷□不符 {cnt}')

# 页面计数声明
for s in ['15,870', '一千四百三十六', '七十六见', '七十五见、十八种', '一千零八十',
          '一百九十四', '九十五', '一百零九曲', '四首系于稼轩', '鹧鸪天七首']:
    chk(s in page, f'页面缺计数声明：{s}')

# 卷面结构：卷四 13 自制曲题逐名在库
vol4 = ['扬州慢','长亭怨慢','淡黄柳','石湖仙','暗香','疎影','惜红衣','角招','征招','秋宵吟','凄凉犯','翠楼吟','湘月']
chk(len(vol4) == 13, '卷四题数应为十三')
for tname in vol4:
    chk(tname in lib, f'卷四曲题不在库本：{tname}')

# 词部调名签十五枚（带宫调标签的曲题）
tags = ['隔溪梅令【仙吕调】','玉梅令【髙平调】','齐天乐【黄钟宫】','法曲献仙音【俗名大石　黄钟商】','琵琶仙【黄钟商】',
        '扬州慢【中吕宫】','长亭怨慢【中吕宫】','淡黄柳【正平调近】','石湖仙【越调】','暗香【仙吕宫】',
        '惜红衣【无射宫】','角招【黄钟角】','秋宵吟【越调】','凄凉犯【仙吕调犯商调】','翠楼吟【双调】']
chk(len(tags) == 15, '调名签应为十五枚')
for tg in tags:
    chk(tg in lib, f'调名签不在库本：{tg}')

# 越九歌十曲十调
you = [l for l in lines if l.startswith('右')]
chk(len(you) == 10, f'越九歌右调应为十见，实 {len(you)}')
nine_names = ['帝舜楚调','王禹吴调','越王越调','越相侧商调','项王古平调','涛之神双调','曹娥蜀侧调','厐将军高平调','旌忠中管商调','蔡孝子中管般瞻调']
for n in nine_names:
    chk(n in lib, f'九歌曲名不在库本：{n}')

# 鹧鸪天七首：鹧鸪天行至夜行船行之间，又行数 + 1
a = idx('鹧鸪天'); b = idx('夜行船')
duo = sum(1 for l in lines[a:b] if l == '又')
chk(duo + 1 == 7, f'鹧鸪天首数不符：{duo + 1}')

# 页面结构
chk('之一百三十' in page, '页内序号非 130')
chk('卷七十四' in page and '倚声' in page, '卷七十四 倚声 缺')
chk('github.com/robertsong2000/daizhigev20' in page, '缺库链接')
chk('mulu.html' in page and '逐字核验' in page and '宜批判地看' in page, '页脚三要素缺')

print()
if FAILS:
    print(f'共 {len(FAILS)} 项失败'); sys.exit(1)
print(f'ALL PASS　.q 块 {len(blocks)}　EXPECTED {len(EXPECTED)}　红线/机数/结构全过')
