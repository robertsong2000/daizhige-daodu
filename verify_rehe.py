#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, sys, os
from html.parser import HTMLParser

REPO = '/home/robertsong/workspace/claude/daizhige-daodu'
PAGE = os.path.join(REPO, 'rehe-riji.html')
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/热河日记.txt'
NO = '之一百三十八'

html = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF:
            out.append(ch)
    return ''.join(out)

lib_n = norm(lib)

# ── QCollector：栈配平，class 恰含 q 的元素整块收集 ──
class QC(HTMLParser):
    VOID = {'br','img','meta','link','hr','input','source','area','base','col','embed','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.qdepth = None; self.buf = []; self.blocks = []
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        cls = dict(attrs).get('class') or ''
        toks = cls.split()
        if self.qdepth is None and 'q' in toks:
            self.qdepth = len(self.stack) + 1  # 深度在压栈后取
            self.buf = []
        self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack: self.stack.pop()
        if self.qdepth is not None and len(self.stack) < self.qdepth:
            self.blocks.append(''.join(self.buf))
            self.qdepth = None; self.buf = []
    def handle_data(self, data):
        if self.qdepth is not None:
            self.buf.append(data)

qc = QC(); qc.feed(html)
blocks = [b for b in qc.blocks]
blocks_n = [norm(b) for b in blocks]

fails = []
def chk(cond, msg):
    if not cond:
        fails.append(msg)

# ── 期望引文清单：库内逐字 + 页面在位 ──
EXPECTED = [
 "曷为后三庚子　记行程阴晴　将年以系月日也　曷称后　崇祯纪元后也　曷三庚子　崇祯纪元后三周庚子也　曷不称崇祯　将渡江　故讳之也　曷讳之　江以外淸人也　天下皆奉淸正朔　故不敢称崇祯也",
 "崇祯十七年　＿毅宗烈皇帝殉社稷　＿明室亡　于今百三十余年　曷至今称之",
 "淸人入主中国　而先王之制度变而为胡　环东土数千里划江而为国　独守先王之制度　是明　＿明室犹存于鸭水以东也　虽力不足以攘除戎狄　肃淸中原　以光复先王之旧　然皆能尊崇祯以存中国也",
 "崇祯百五十六年癸卯　洌上外史题",
 "后三庚子　我＿圣上四年 淸乾隆四十五年 六月二十四日辛未　朝小雨　终日乍洒乍止　午后渡鸭绿江　行三十里　露宿九连城",
 "红粉楼中别莫愁", "秋风数骑出边头", "画船箫鼓无消息", "肠断淸南第一州",
 "此江乃彼我交界处也　非岸则水　凡天下民彝物则　如水之际岸　道不他求　即在其际",
 "世爵自以背磨之石楞　缚绳断　遂起　脱朝鲜死者衣换着之　撺入朝鲜兵中以得免",
 "自念中原路绝　不如东出朝鲜　犹得免薙发左衽　遂走穿塞　隐金石山　燎羊裘裹木叶以咽之　数月得不死　遂渡鸭绿江",
 "世爵年八十余卒　子孙蕃衍至百余人　而犹同居云",
 "忽然意沮　直欲自此径还　不觉腹背沸烘",
 "中国　胡也　小人不愿",
 "此书皆我东所有　故吾老爷不览此书目云尔",
 "我念吾东家贫好读书百千兄弟等　鼻端六月恒垂晶珠　愿究此法以免三冬之苦",
 "吾今日始知人生本无依附　只得顶天踏地而行矣",
 "喜极则可以哭矣", "怒极则可以哭矣", "乐极则可以哭矣",
 "爱极则可以哭矣", "恶极则可以哭矣", "欲极则可以哭矣",
 "今临辽野　自此至山海关一千二百里　四面都无一点山　干端坤倪　如黏胶线缝　古雨今云　只是苍苍　可作一场",
 "闻名应驻马　寻香且停车",
 "皇帝于昨年己亥为全韵诗　详载陷城始末　且曰　明臣之不降者　我祖宗尙加恩　而燕京君臣漠不相关　功罪不明　欲其不亡　得乎",
 "当＿皇明末运　用舍顚倒　功罪不明　其视熊廷弼　袁崇焕之死　可谓自坏其长城矣　恶可免后代之讥哉",
]
for q in EXPECTED:
    qn = norm(q)
    chk(qn in lib_n, f'库本无此引文: {q[:24]}…')
    chk(any(qn in b for b in blocks_n), f'页面 .q 未载: {q[:24]}…')

# ── 反扫：每块 .q 都必须在库本 ──
for i, b in enumerate(blocks_n):
    if b and b not in lib_n:
        fails.append(f'.q #{i} 反扫失败: {b[:30]}…')
chk(len(blocks) >= 25, f'.q 块数过少: {len(blocks)}')

# ── 「」反扫 ──
raw = re.sub(r'<[^>]+>', '', html)
for m in re.findall(r'「([^」]*)」', raw):
    mn = norm(m)
    chk(mn in lib_n, f'「」引文库内无: {m[:24]}')

# ── 排版红线 ──
chk('—' not in html, '出现长划线 —')
chk('–' not in html, '出现短划线 –')
for ln in raw.splitlines():
    c = ln.count('·')
    chk(c <= 1, f'一行内 · 超限({c}): {ln.strip()[:40]}')

# ── 列表行（富先生书目，非 .q，逐项对库） ──
BARE = ["影梅庵忆语","冒襄辟疆着","幽梦影","张潮着","虞初新志","张潮山来着",
        "日知录","北平古今记","顾炎武着","焚书共六册 藏书共十八册","李贽卓吾着"]
for b in BARE:
    chk(norm(b) in lib_n, f'书目条目库内无: {b}')

# ── 沿革链芯片逐字对库 ──
CHAIN = ["汉襄平辽阳","秦曰辽东","卫满朝鲜","公孙度","高句丽","契丹称南京",
         "金称东京","元置行省","＿皇明置定辽卫","今升为辽阳州"]
for c in CHAIN:
    chk(norm(c) in lib_n, f'沿革链芯片库内无: {c}')
for c in CHAIN:
    chk(c in html, f'页面缺沿革芯片: {c}')

# ── 机数（库本侧） ──
hz = len([c for c in lib if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x2FFFF])
chk(hz == 21929, f'库本汉字数 {hz} != 21929')
chk(lib.count('热河') == 3, f'热河 全帙 {lib.count("热河")} != 3')
body = ''.join(lib.splitlines()[i] for i in (9,11,12,13,14,17,19,21,23,25,27,29,31,45))
chk(body.count('热河') == 0, '渡江录正文出现热河')
chk(lib.count('＿') == 19, f'＿ {lib.count("＿")} != 19')
chk(lib.count('淸') == 37, f'淸 {lib.count("淸")} != 37')
chk(lib.count('靑') == 19, f'靑 {lib.count("靑")} != 19')
chk(lib.count('飮') == 13, f'飮 {lib.count("飮")} != 13')
chk(lib.count('窓') == 9,  f'窓 {lib.count("窓")} != 9')
chk(lib.count('尙') == 10, f'尙 {lib.count("尙")} != 10')
chk(lib.count('晩') == 5,  f'晩 {lib.count("晩")} != 5')
chk(lib.count('{') == 35 and lib.count('}') == 35, '括注对数 != 35')
stamps = re.findall(r'[一二三四五六七八九]?十?[一二三四五六七八九]?日[甲乙丙丁戊己庚辛壬癸]', lib)
chk(len(stamps) == 15, f'日戳 {len(stamps)} != 15')

# ── 机数（页面侧） ──
for s in ['21929','35','19','明日将入沈阳','热河未至','崇祯纪元']:
    chk(s in html, f'页面缺机数/关键串: {s}')
chk(html.count('class="stamp ') + html.count('class="stamp"') == 15, '页面日戳 != 15')
chk(html.count('stamp hot') == 8, f'热点日戳 {html.count("stamp hot")} != 8（七精读+乙酉止点）')

# ── 跨链存在 ──
for f in ['yingmei-an-yiyu.html','youmengying.html']:
    chk(os.path.exists(os.path.join(REPO, f)), f'跨链文件不存在: {f}')
    chk(f'href="{f}"' in html, f'页面缺跨链: {f}')

# ── 序号 ──
chk(NO in html, '页面缺序号')
chk(html.count(NO) == 3, f'序号出现 {html.count(NO)} 次 != 3')

print(f'.q 块数: {len(blocks)}')
if fails:
    print(f'FAIL {len(fails)}')
    for f in fails: print('  ✗', f)
    sys.exit(1)
print('PASS 全部核验通过')
