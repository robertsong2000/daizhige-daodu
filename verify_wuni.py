#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""吴逆取亡录 导读页核验：引文双侧 + 跨库分源 + 红线 + 机数"""
import re, sys, os

REPO = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(REPO, 'wuni-quwang-lu.html')
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/吴逆取亡录.txt'
LIBS = {
    'main': LIB,
    'qs':   '/home/robertsong/workspace/claude/daizhige-simplified/史藏/正史/清史稿.txt',
    'ycxz': '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/虞初新志.txt',
    'mcj':  '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/梅村集.txt',
    'ms':   '/home/robertsong/workspace/claude/daizhige-simplified/儒藏/诗经/毛诗正义.txt',
}

def norm(s):
    return ''.join(c for c in s if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0002ffff')

# ---------- 主库引文（页面 .q 且 库本） ----------
QUOTES = [
 "余转侧兵间，濒死而幸不死，爰就耳目所及笔之，以见覆亡之祸实所自取",
 "使当日归藩辽左，克守臣节，则带砺河山，永保无疆之庥，岂不懿哉？",
 "我世祖章皇帝",
 "王师",
 "少时逐一骑，射之堕，下马欲取其首，其人故佯死，突挥刀刃三桂中鼻，故鼻左微凹",
 "目瞻视，隆准无须",
 "鼻左微凹",
 "吾君已矣，尔父命在须臾，及今早降，不失通侯之位",
 "是胁我耳，我至即释，何患！",
 "陈姬无恙乎？",
 "大丈夫不能保一女子，何面目见天下人！",
 "见我军戴缨帽如万朵红云，风卷而西，遽策马走，呼曰：“败矣！”",
 "传檄入都，言奉太子至",
 "及登辇，则辫而短后衣者，睿亲王也，咸愕眙不知所为，罗拜道左",
 "吾主已于去岁登极，此皇叔摄政王也。",
 "时尚未知圆圆消息也",
 "三桂前部得圆圆于途，报至，大喜，于营次设锦幄，鼓吹前导，迎以归",
 "不可使滇中一日无事。",
 "三桂谨受教",
 "李定国等引众四扰，患在门户",
 "土司反复，易被煽动，患在肘腋",
 "投诚将士，乘机生心，患在腠理",
 "惟有剿净根株，庶可一劳永逸",
 "重楼复道，规制拟大内",
 "因圆圆齿已长，张氏亦老，更罗致艳冶，以歌舞自娱",
 "就食缅人，为所制，与定国等隔绝不通，已不能有所为",
 "将军既毁我室，又欲取我子",
 "即不为仆怜，独不念先帝乎？",
 "即不念先帝，独不念二祖列宗乎？",
 "即不念二祖列宗，独不念己之祖若父乎？",
 "仆今日兵衰力弱，茕茕孑立，区区之命，悬于将军之手",
 "倘得与太平草木，同沾雨露于新朝，惟将军是命",
 "三桂不答",
 "三桂不答，自木邦趋缅城",
 "持贝叶文纳款",
 "晋王李定国至矣，请出就晋王军。",
 "宜骈首",
 "彼曾为君，全其首领可也。",
 "进帛于滇城之篦子坡，太子等皆就缢，复焚其尸",
 "明社之厄，虽由闯贼",
 "实亡于三桂手",
 "虽仍以永历纪年，其实扶余自王，金炉朱火，自兹熄矣",
 "特允三桂撤归锦州",
 "三桂初意要旨慰留，可从容部署。命下，愕然气沮",
 "出关乞师，犹可以力弱自解。永历已窜缅中，必擒而杀之，此不可解矣。况成功之后，万不能终守臣节。篦子坡之事，可一再行之乎？",
 "阴扼各关隘，听入不听出",
 "吴三桂自去其平西亲王爵，称天下都招讨兵马大元帅",
 "铸钱曰“利用通宝”，蓄发易衣冠，帜色用白，步骑皆以白毡为帽",
 "伪檄所至，叛者四起，势同鼎沸",
 "滇中雷电风雪，一时兼作",
 "西寺塔顶铜凤有声呜呜，数日不止",
 "展翼方丈余，状貌丑怪，博物者不能识其名",
 "人咸知为不详，而三桂不悟也",
 "事平再议，犹欲三桂悔悟自投，曲赐矜全也",
 "上念应熊久在近侍，不忍加戮",
 "将应熊及子世霖处绞，其余幼子免死入宫",
 "三桂闻之大恨",
 "贼党思悦其意，相率劝进",
 "十七年三月朔，改衡州为定天府，僭帝号。建元昭武，册妻张氏为后",
 "将设朝，淫雨泥泞，藉松针于地，始克成礼",
 "有犬登其案而坐",
 "三桂心恶之，遂病噎",
 "继之下痢，口不能言，八月十七日毙于衡州",
 "城中樵采路绝，人相食",
 "刎颈不殊，再刃乃死，伪后郭氏殉焉",
 "析三桂骸骨，传示天下，距谋叛时恰八年云",
 "析三桂骸骨，传示天下",
 "下马欲取其首",
 "函首驰献",
 "又欲取我子",
 "应熊及子世霖处绞",
 "口不能言",
 "势同鼎沸",
 "天下大定",
]
# ---------- 跨库引文（.q data-src 分源） ----------
XQUOTES = [
 ("二十一年春，从议政王大臣请，析三桂骸，传示天下。悬世璠首于市", "qs"),
 ("能以圆圆见赠，吾当保公家，先于保国也", "ycxz"),
 ("恸哭六军俱缟素，冲冠一怒为红颜。", "mcj"),
 ("全家白骨成灰土，一代红妆照汗青。", "mcj"),
 ("既取我子，无毁我室", "ms"),
]

fail = 0
def chk(cond, msg):
    global fail
    if not cond:
        fail += 1
        print('FAIL:', msg)

html = open(PAGE).read()
libs = {k: norm(open(v).read()) for k, v in LIBS.items()}

# ---- .q 收集（html.parser 栈配平，VOID 不入栈，深度标记法） ----
from html.parser import HTMLParser
VOID = {'br','meta','link','img','hr','input'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.qs = []      # (src, text)
        self.cur = None
        self.qdepth = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if 'q' in (a.get('class') or '').split():
            self.cur = {'src': a.get('data-src', 'main'), 'buf': []}
            self.qdepth = len(self.stack)
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack:
            self.stack.pop()
            if self.cur is not None and len(self.stack) < self.qdepth:
                self.qs.append((self.cur['src'], ''.join(self.cur['buf'])))
                self.cur = None
    def handle_data(self, d):
        if self.cur is not None:
            self.cur['buf'].append(d)

p = QC()
p.feed(html)
page_qs = [(src, norm(t)) for src, t in p.qs]
main_on_page = [t for src, t in page_qs if src == 'main']

print(f'页面 .q 块数: {len(page_qs)}（主库 {len(main_on_page)} + 跨库 {len(page_qs)-len(main_on_page)}）')
chk(len(page_qs) >= len(QUOTES) + len(XQUOTES) - 10, 'q 块数过少，收集器疑似漏抓')

# 主库引文：在页面 + 在库本 双侧
for t in QUOTES:
    tn = norm(t)
    chk(tn in libs['main'], f'库本缺：{t[:24]}')
    chk(tn in main_on_page, f'页面 .q 缺：{t[:24]}')

# 跨库引文：data-src 与库源匹配 + 在页面
for t, src in XQUOTES:
    tn = norm(t)
    chk(tn in libs[src], f'{src} 缺：{t[:24]}')
    chk((src, tn) in page_qs, f'页面缺 data-src={src} 的引文：{t[:24]}')

# 页面 .q 不得捏造：每个主库 .q 必须是库本子串
for src, t in page_qs:
    if src == 'main':
        chk(t in libs['main'], f'页面 .q 非库本子串：{t[:30]}')
    else:
        chk(t in libs[src], f'页面 .q 非 {src} 子串：{t[:30]}')

# ---- 「」反扫（剔 style/script 与校记讨论区） ----
body = re.sub(r'<style.*?</style>', '', html, flags=re.S)
body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
body = re.sub(r'<section class="block paper-sect jiaoji".*?</section>', '', body, flags=re.S)
text = re.sub(r'<[^>]+>', '', body)
for m in re.finditer(r'「([^」]+)」', text):
    inner = norm(m.group(1))
    if inner:
        chk(inner in libs['main'], f'反扫：正文「」引文非库本子串：{m.group(1)[:26]}')

# ---- 红线 ----
chk('—' not in html and '–' not in html, '出现长划线')
chk(not re.search(r'[-\U00020000-\U0002ffff]', html), '页面出现 PUA/Ext-B 字形')
for i, line in enumerate(html.split('\n'), 1):
    n = line.count('·')
    chk(n <= 1, f'第{i}行有 {n} 个 ·')
chk(html.count('三桂不答') >= 2, '「三桂不答」应多次出现')

# ---- 机数 ----
raw = open(LIB).read()
total = len(raw)
nospace = len(re.sub(r'\s', '', raw))
han = len([c for c in raw if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0002ffff'])
paras = len([l for l in raw.split('\n') if l.strip()]) - 1
print(f'库本机数：total={total} 去空白={nospace} 汉字={han} 段={paras}')
chk(total == 5848, 'total≠5848')
chk(nospace == 5776, '去空白≠5776')
chk(han == 4814, '汉字≠4814')
chk(paras == 22, '正文段数≠22')
chk(f'去空白 {nospace:,} 字'.replace(',', ',') in html, '页面 hero 机数与库本不符')
chk('5,776' in html, '页面未标 5,776')
chk('5,848' in html, '校记未标 5,848')
chk('4,814' in html, '校记未标 4,814')
chk('一百一十八' in html, '页内缺序号之一百一十八')
for w in ['苍弁山樵', '恰八年', '三桂不答', '篦子坡', '松针']:
    chk(w in html, f'页面缺关键词 {w}')

print('PASS' if fail == 0 else f'共 {fail} 处失败')
sys.exit(1 if fail else 0)
