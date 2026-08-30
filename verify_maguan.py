#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核验 马关议和中之伊李问答 导读页：引文双侧逐字 + 机数 + 排版红线。"""
import re, sys
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/马关议和中之伊李问答.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/maguan-yili-wenda.html'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
fails = []

def chk(cond, msg):
    if not cond:
        fails.append(msg)
        print('FAIL', msg)
    else:
        print('ok  ', msg)

VOID = {'meta','link','br','img','hr','input','source','wbr'}

class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.qdepth = 0
        self.cur = None
        self.out = []
        self.alltext = []
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        cls = dict(attrs).get('class') or ''
        isq = 'q' in cls.split()
        if isq:
            self.qdepth += 1
            if self.qdepth == 1:
                self.cur = []
        self.stack.append((tag, isq))
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            t, isq = self.stack.pop()
            if isq:
                self.qdepth -= 1
                if self.qdepth == 0 and self.cur is not None:
                    self.out.append(''.join(self.cur))
                    self.cur = None
            if t == tag:
                break
    def handle_data(self, data):
        self.alltext.append(data)
        if self.cur is not None:
            self.cur.append(data)

def norm(s):
    return ''.join(ch for ch in s if 0x3400 <= ord(ch) <= 0x9FFF or 0x20000 <= ord(ch) <= 0x3FFFF)

qc = QC()
qc.feed(page)
page_qnorms = [norm(x) for x in qc.out if norm(x)]
page_norm_all = norm(''.join(qc.alltext))

QUOTES = [
"中堂此来一路顺风否？","一路风顺，惟在成山停泊一日。承两位在岸上预备公馆，谢谢。",
"顷阅敕书甚属妥善，惜无御笔签名耳！","此系各国俗尚不同；盖用御宝，即与御笔签名无异。",
"即彼此相问年岁",
"我今年七十三矣，不料又与贵大臣相遇于此！",
"亚细亚洲，我中、东两国最为邻近，且系同文，讵可寻仇？今暂时相争，总以永好为事。如寻仇不已，则有害于华者未必于东有益也。",
"庶我亚洲黄种之民，不为欧洲白种之民所侵蚀也。",
"中堂之论甚惬我心。十年前我在津时，已与中堂谈及；何至今一无变更？本大臣深为抱歉！",
"现在日军并未至大沽、天津、山海关等处，何以所拟停战条款内竟欲占据？",
"凡议停战，两国应均沾利益；华军以停战为有益，故我军应据此三处为质。",
"我为直隶总督，三处皆系直隶所辖；如此，于我脸面有关。试问伊藤大人设身处地，将何以为情？",
"战端一开，伊于胡底，讵能逆料？",
"初战之始，我两国譬如两人走路，相距数里耳；今则相距数百迈，回首难矣！",
"纵令再走数千里，岂能将我国人民灭尽乎？",
"我两国比邻，此事如两孩相斗，转瞬即和；且相好更甚于前",
"是日鸿章自会议所归，途次中倭刺客（小山丰太郎）枪弹伤颧，创甚；日本国主遣医慰治。警问播欧、亚，议甚沸，倭亦惧。",
"大日本大皇帝因二十八日之忧，抱歉殊深！特谕本大臣等即允停战，无庸苛求，惟须订明日期界域",
"今日复见中堂重临，伤已平复，不胜幸甚！",
"中堂见我此次节略，但有「允」、「不允」两句话而已！","难道不准分辩？","只管辩论，但不能减少。",
"博文面致尽头约稿，谓其此次节略，中国但允、不允两言而决，无多费时日",
"中国请尔为首相如何？","当奏皇上，甚愿前往。","奏如不允，尔不能去。",
"既得地税，尚要赔款，将如之何？","无法！",
"譬如养子，既欲其长，又不喂乳，其子不死何待！","中国岂可与孩提并论。",
"二万万为数甚巨，必请再减；营口，还请退出；台湾，不必提及！",
"广岛有六十余只运船停泊，计有二万吨运，今日已有数船出口，兵粮齐备",
"赔款还须请再减五千万，台湾不能相让！","如此，当即遣兵至台湾！",
"中堂起席，与伊藤作别。握手时，再请将赔款大减；伊藤笑而摇头，云不能再减而散。",
"如此凶狠条款，签押又必受骂；奈何？","任彼胡说。如此重任，彼亦担当不起，中国惟中堂一人能担此任！",
"我早已说明，已让至尽头地步；主意已定，万不能改，我亦甚为可惜。",
"此事难办已极，还请贵大臣替我酌量，我实在无法酌量！",
"初约本不愿改，因念中堂多年交情，故减万万。","如此口紧手辣，将来必当记及！",
"贵国何必急急，台湾已是口中之物！","尚未下咽，饥甚。","两万万足可疗饥；换约后尚须请旨派员，一月之期甚促。",
"我接台湾巡抚来电：闻将让台湾，台民鼓噪，誓不肯为日民。","听彼鼓噪，我自有法。",
"此话并非相吓，乃好意直言相告","我亦闻此事",
"中国将管理下开地方之权并将该地方所有堡垒、军器、工厂及一切属公对象，永远让与日本。",
"台湾全岛及所有附属各岛屿。","中国约将库平银二万万两交与日本，作为赔偿军费。",
"两国立即各派大员至台湾限于本约批准后两个月内交接清楚",
"一切堡垒、枪炮与公家对象，皆交日本武官收管",
"定于光绪二十一年四月十四日，即日本明治二十八年五月初八日在烟台互换",
"此停战条约约明于光绪二十一年三月二十六日，即明治二十八年四月二十日中午十二点钟届满",
"光绪二十一年三月二十三日、明治二十八年四月十七日订于下之关（缮写两分）。",
"大清帝国钦差头等全权大臣太子太傅文华殿大学士北洋通商大臣直隶总督一等肃毅伯爵李鸿章",
"中国赔偿军费库平银三万万两，分五期以三年为度交清",
"而赔款减至库平银二万万两，分六期以七年归偿，未偿以先，给息五厘",
"倭乃索我赎费库平银一万万两，徐减及五千万两","三国公断以三千万两赎辽东，倭人听之",
"是役款议成，割膏腴（台湾全省并澎湖列岛）、偿巨款（其赔费银二万三千万两，其我国自用兵费及赔款息银不在内）；商利之失，尤为无穷漏卮。",
"膏血竭于内、边防堕于外，岌岌不可终日。说者谓中国泰否通塞之机，或决于是云。",
"大清帝国钦差全权大臣二品顶戴前出使大臣李经方",
"大日本帝国全权办理大臣内阁总理大臣从二位勋一等伯爵伊藤博文",
"大日本帝国全权办理大臣外务大臣从二位勋一等子爵陆奥宗光",
]

# A/B/C 引文三向核验
chk(len(QUOTES) == 66, f'引文清单 66 条（实际 {len(QUOTES)}）')
bad_lib = [q for q in QUOTES if q not in lib]
chk(not bad_lib, f'全部引文在库本中逐字命中（未命中 {len(bad_lib)}）')
for q in bad_lib[:5]:
    print('   未命中:', q[:40])

bad_page = [q for q in QUOTES if not any(norm(q) in pn for pn in page_qnorms)]
chk(not bad_page, f'全部引文均被页面 .q 载用（缺载 {len(bad_page)}）')
for q in bad_page[:5]:
    print('   缺载:', q[:40])

sweep_bad = [pn for pn in page_qnorms if pn not in norm(lib)]
chk(not sweep_bad, f'页面全部 .q 反扫均能在库本命中（反扫失败 {len(sweep_bad)}）')
for pn in sweep_bad[:5]:
    print('   反扫失败:', pn[:60])
chk(len(page_qnorms) >= 65, f'页面 .q 块数 {len(page_qnorms)} >= 65')

# 机数：库本
chk(len(lib) == 40238, f'全帙 40,238 字（实际 {len(lib)}）')
nonws = len(re.sub(r'\s', '', lib))
chk(nonws == 37218, f'去空白 37,218（实际 {nonws}）')

lines = [l.strip() for l in lib.split('\n')]
def sess(a, b):
    seg = lines[a-1:b]
    return sum(1 for l in seg if re.match(r'^(伊|李|陆|参议)云：', l))
counts = [sess(14,148), sess(150,322), sess(324,440), sess(442,768), sess(770,1390)]
chk(counts == [59,81,51,159,294], f'五次发言 {counts} == [59,81,51,159,294]')
chk(sum(counts) == 644, f'发言总计 {sum(counts)} == 644')
def cnt(pat):
    return sum(1 for l in lines if re.match(pat, l))
chk(cnt(r'^伊云：') == 314, f'伊云 {cnt(r"^伊云：")} == 314')
chk(cnt(r'^李云：') == 324, f'李云 {cnt(r"^李云：")} == 324')
chk(cnt(r'^陆云：') == 5, '陆云 5')
chk(cnt(r'^参议云：') == 1, '参议云 1')

treaty = lib[lib.find('约文全稿'):lib.find('鸿章乃旋天津')]
n1 = len(re.findall(r'第[一二三四五六七八九十]+款：', treaty))
tks = lib[lib.find('凡订约六款'):lib.find('初七日，博文')]
n2 = len(re.findall(r'第[一二三四五六七八九十]+款：', tks))
hl = lib[lib.find('凡七款：'):]
n3 = len(re.findall(r'第[一二三四五六七八九十]+款：', hl))
chk((n1, n2, n3) == (11, 6, 7), f'约文十一款/停战六款/还辽七款（实际 {n1}/{n2}/{n3}）')

chk(lib.count('万万') == 18, f'万万 18 见（实际 {lib.count("万万")}）')
chk(lib.count('二万万') == 6, '二万万 6 见')
chk(lib.count('三万万') == 2, '三万万 2 见')
chk(lib.count('五千万') == 11, '五千万 11 见')
chk(lib.count('三千万') == 6, '三千万 6 见')
chk(lib.count('□') == 14, f'缺字框 14（实际 {lib.count("□")}）')
chk(lib.count('倭') == 148, f'倭 148 见（实际 {lib.count("倭")}）')
chk(lib.count('台湾') == 57, f'台湾 57 见（实际 {lib.count("台湾")}）')
chk(lib.count('议款篇（第八）') == 2, '「议款篇（第八）」重出 2 见')

# 赔款总账：二万万 + 三千万 = 二万万三千万（与库本结语一致）
chk(20000 + 3000 == 23000 and '二万三千万两' in lib, '总账 20,000万+3,000万=23,000万，库本结语作二万三千万两')

# BARE：校记与旁记里的裸引
BARE = [
    ("议款篇（第八）", 2),
    ("即彼此相问年岁--伊藤五十五、陆奥五十二。", 1),
    ("我已说朋", 1), ("履次言朋", 1), ("应辨第一要事", 1),
    ("自应遭命", 1), ("互换乏后", 1), ("巳付利息", 1), ("此事甚为纠轕", 1),
    ("伊取报纸细看", 1), ("伊细想多时", 1),
    ("东方兵事纪略（一篇）姚锡光", 1),
    ("招商局□□轮船", 1), ("招商局□□商轮", 1),
    ("鸿章于□□寺", 1), ("凡□□日", 1), ("价□万万佛郎", 1), ("凡质□□年", 1),
]
for frag, want in BARE:
    c = lib.count(frag)
    chk(c == want, f'BARE「{frag[:18]}」库本 {c} 见（期望 {want}）')
for frag in ['我已说朋','履次言朋','应辨第一要事','自应遭命','互换乏后','巳付利息','此事甚为纠轕',
             '即彼此相问年岁--伊藤五十五','议款篇（第八）','伊取报纸细看','伊细想多时',
             '□□寺','凡□□日','□万万佛郎','□□年']:
    chk(frag in page_norm_all or frag in page, f'BARE「{frag[:18]}」页内已申报')
chk(page.count('招商局') >= 1 and '□□' in page, '页内缺字框 □□ 已申报')

# 页面自报机数
for s in ['发言 59 行','发言 81 行','发言 51 行','发言 159 行','发言 294 行',
          '二万万三千万两','六百四十四','四万零二百三十八','三万七千二百一十八',
          '伊云三百一十四','李云三百二十四','陆云五、参议云一',
          '五十九、八十一、五十一、一百五十九、二百九十四',
          '十一款','议款篇（第八）','缺字十四处',
          '殆知阁导读之一百一十二',
          '殆知阁简体库','逐字核验','时代局限']:
    chk(s in page, f'页面自报「{s}」在场')

# 排版红线
chk('—' not in page and '–' not in page, '无长划线 — –')
bad = [i+1 for i, l in enumerate(page.split('\n')) if l.count('·') > 1]
chk(not bad, f'每行 · 最多 1 枚（违规行 {bad[:8]}）')
chk(page.count('<html') == 1 and 'http-equiv' not in page.replace('X-UA-Compatible','XUA'), '单文件无外部请求')
chk(not re.search(r'https?://(?!github\.com/robertsong2000)', page), '除仓库链接外无外链')

print()
if fails:
    print(f'共 {len(fails)} 项未过')
    sys.exit(1)
print('全部通过')
