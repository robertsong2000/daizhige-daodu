#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清异录 导读页核验：引文双侧逐字对库 + 红线 + 机数"""
import re, sys, unicodedata
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/清异录.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/qingyilu.html'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
fails = []

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        if unicodedata.category(ch).startswith(('P', 'S')):
            continue
        out.append(ch)
    return ''.join(out)

LIBN = norm(lib)

def chk(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

# ---------- 1. 库本机数 ----------
lines = [l.strip() for l in lib.split('\n')]
heads = [l for l in lines if re.match(r'^\S+门（\S+事）$', l)]
CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def cnum(s):
    if s == '十': return 10
    if '十' in s:
        a, b = s.split('十')
        return (CN[a] if a else 1) * 10 + (CN[b] if b else 0)
    return CN[s]
claims = {}
for h in heads:
    m = re.search(r'（(\S+)事）', h)
    claims[h.split('门')[0] + '门'] = cnum(m.group(1))

chk(len(heads) == 37, f'库本门数=37 实测{len(heads)}')
chk(sum(claims.values()) == 658, f'门头自报合计=658 实测{sum(claims.values())}')
ix = next(i for i, l in enumerate(lines) if l == '卷下' and i > 100)
upper = [l for l in lines[:ix] if re.match(r'^\S+门（\S+事）$', l)]
lower = [l for l in lines[ix:] if re.match(r'^\S+门（\S+事）$', l)]
chk(len(upper) == 20 and len(lower) == 17, f'卷上{len(upper)}门/卷下{len(lower)}门 == 20/17')
chk(claims.get('器具门') == 54, f'器具门自报54 实测{claims.get("器具门")}')

bra = re.findall(r'[｛【\[][^｝】\]]{1,14}[｝】\]]', lib)
chk(len(bra) == 20, f'拆字括注=20 处 实测{len(bra)}')
extb = {c for c in lib if ord(c) > 0xFFFF}
chk(len(extb) == 15, f'Ext-B 种类=15 实测{len(extb)}')
c9 = sum(1 for c in lib if c == '𬬮')
chk(c9 == 9, f'U+2CB2E 九见 实测{c9}')
chk(not any(0xE000 <= ord(c) <= 0xF8FF for c in lib), '库本无 PUA')

# ---------- 2. 页面 .q 收集 ----------
class QCollector(HTMLParser):
    VOID = {'meta','link','br','hr','img','input','area','base','col','embed','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []   # (tag, is_q)
        self.qs = []
        self.cur = None   # 当前最内层 q 的文字桶
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        cls = dict(attrs).get('class', '') or ''
        isq = 'q' in cls.split()
        if isq and self.cur is None:
            self.cur = []
        self.stack.append((tag, isq))
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if not self.stack: return
        t, isq = self.stack.pop()
        if isq and self.cur is not None:
            self.qs.append(''.join(self.cur))
            self.cur = [] if any(iq for _, iq in self.stack) else None
    def handle_data(self, data):
        if self.cur is not None:
            self.cur.append(data)

p = QCollector()
p.feed(page)
page_qs = [norm(x) for x in p.qs if norm(x)]
print(f'页面 .q 共 {len(page_qs)} 块')

# ---------- 3. 引文双侧断言 ----------
QUOTES = [
 "是书皆采摭唐及五代新颖之语，分三十七门，各为标题，而注事实缘起于其下。",
 "独不伪造书名",
 "陈振孙《书录解题》以为不类宋初人语，胡应麟《笔丛》尝辨之。",
 "岂亦杂录旧文，删除未尽耶？",
 "大抵即谷所造，亦《云仙散录》之流，而独不伪造书名，故后人颇引为词藻之用。",
 "仕晋为知制诰，仓部郎中。仕汉为给事中。仕周为兵部侍郎，翰林承旨。入宋仍原官，加户部尚书。",
 "本唐彦谦之孙，避晋讳，改陶氏。",
 "相沿既久，遂亦不可废焉。",
 "李煜在国时，自作祈雨文曰：“尚乖龙润之祥。”",
 "炀帝幸江都，吴中贡糟蟹、糖蟹。每进御，则上旋洁拭壳面，以金缕龙凤花云贴其上。",
 "僖宗幸蜀，乏食，有宫人出方巾所包面半升许，会村人献酒一偏提，用酒溲面，煿饼以进。嫔嫱泣奉曰：“此消灾饼，乞强进半枚。”",
 "比丘尼梵正，庖制精巧，用鲊臛、脍脯、醢酱、瓜蔬，黄赤杂色，鬬成景物，若坐及二十人，则人装一景，合成辋川图小様。",
 "旧闻李太白好饮玉浮梁，不知其果何物。",
 "试取一盏至，则浮蛆酒脂也，乃悟太白所饮盖此耳。",
 "穆宗临芳殿赏樱桃，进西凉州蒲萄酒，帝曰：“饮此顿觉四体融和，真太平君子也。”",
 "置之缾中，酒也，酌于杯，注于肠，善恶喜怒交矣，祸福得失岐矣。",
 "一言蔽之，曰“祸泉”而已。",
 "日必饮，饮必醉，醉不厌，贫不悔，俗号“瓶盏病”。徧掲《本草》，细检《素问》，只无此一种药。",
 "载作汤十六法，以谓汤者茶之司命，若名茶而滥汤，则与凡末同调矣。",
 "天得一以清，地得一以宁，汤得一可建汤勲。",
 "茍用此汤，又安有茶耶？所以为大魔。",
 "和凝在朝，率同列递日以茶相饮，味劣者有罚，号为“汤社”。",
 "南汉地狭力贫，不自揣度，有欺四方傲中国之志，每见北人，盛夸岭海之强。",
 "见洛阳牡丹，大骇叹。有搢绅谓曰：“此名大北胜。”",
 "有一小室，窗牖焕明，器皆金纸，光莹四射，金采夺目。",
 "此室暂憇，令人金迷纸醉。",
 "瓠少味无韵，荤素俱不相宜，俗呼“净街槌”",
 "俗号虀为“百岁羹”，言至贫亦可具，虽百岁可长享也。",
 "“七郎中随身富贵，只赢得一座漆宅，岂可卤莽？”",
 "“解禀香三令，能遵水五申。”",
 "右莱州长史于义方《黑心符》一卷，录以传后。黑心者，继妇之德名也。陶氏子孙其戒之哉。",
 "“降酒先生风韵高，搅银公子更清豪。碎牙粉骨功成后，小碾当衔马脚槽。”",
 "凡举子入试，天命俊鬼三番旁护之，欲以振发其聪明",
 "一作“虞”，二本皆“廙”字，今从之",
]
for q in QUOTES:
    qn = norm(q)
    chk(qn in LIBN, f'库内命中：{q[:18]}…')
    chk(qn in page_qs, f'页面在位：{q[:18]}…')

for i, qn in enumerate(page_qs):
    if qn not in LIBN:
        chk(False, f'页面第{i+1}块 .q 库内无：{qn[:24]}…')
print(f'页面 {len(page_qs)} 块 .q 全量对库完成')

body = re.sub(r'<[^>]+>', '', page)
frags = re.findall(r'[「“]([^「」“”]{1,120})[」”]', body)
for f in frags:
    fn = norm(f)
    if fn and fn not in LIBN:
        chk(False, f'反扫引号片段库内无：{f}')
print(f'反扫 {len(frags)} 个引号片段完成')

# ---------- 4. 版面结构机数 ----------
men_words = re.findall(r'<div class="men[^"]*">([^<]+)<small>([^<]+)</small>', page)
chk(len(men_words) == 37, f'页面门 chips=37 实测{len(men_words)}')
for w, c in men_words:
    key, cv = w.strip(), c.strip()
    if key in claims:
        chk(claims[key] == cnum(cv.replace('事','')), f'门头 {key} 自报 {cv} 与库本一致')
    else:
        chk(False, f'门 chip {key} 库本无此门')

soups = [re.sub(r'\s', '', s) for s in re.findall(r'<div class="nm">([^<]+)</div>', page)]
exp_soups = ['得一汤','婴汤','百寿汤','中汤','断脉汤','大壮汤','富贵汤','秀碧汤','压一汤','缠口汤','减价汤','法律汤','一面汤','宵人汤','贼汤','魔汤']
chk(soups == exp_soups, f'十六汤格序全等 共{len(soups)}格')
for s in soups:
    chk(s in LIBN, f'汤名 {s} 库内可证')

m = re.search(r'class="pins">(.{0,800}?)</div>', page, re.S)
pin_list = re.findall(r'<span>([^<]+)</span>', m.group(1)) if m else []
chk(len(pin_list) == 15, f'牡丹品 chips=15 实测{len(pin_list)}')
for nm in pin_list:
    chk(norm(nm) in LIBN, f'牡丹品 {nm} 库内可证')

# ---------- 5. 红线 ----------
chk('—' not in page and '–' not in page, '无长划线 — –')
bad = [i for i, line in enumerate(page.split('\n'), 1) if line.count('·') > 1]
chk(not bad, f'每行 · ≤1（违例行 {bad}）')

chk('之一百零五' in page, 'kicker 序号 之一百零五')
chk('殆知阁古代文献简体库' in page and 'github.com/robertsong2000/daizhigev20' in page, '页脚来源与仓库链接')
chk('逐字核验' in page, '页脚核验声明')
chk('时代局限' in page, '页脚时代局限提醒')
chk('六百五十八' in page and '三十七门' in page, '页内机数词在位')

print()
if fails:
    print(f'共 {len(fails)} 项失败'); sys.exit(1)
print('ALL PASS')
