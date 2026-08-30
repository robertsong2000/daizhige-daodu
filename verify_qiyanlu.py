#!/usr/bin/env python3
# 启颜录 页面核验：.q 逐字对库（双侧）+ 千字文跨库 + 机数 + 排版红线
import re, sys, html
from html.parser import HTMLParser
from collections import Counter, OrderedDict

PAGE = 'qiyan-lu.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/启颜录.txt'
QZW = '/home/robertsong/workspace/claude/daizhige-simplified/儒藏/启蒙蒙学/千字文.txt'

page = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()
qzw = open(QZW, encoding='utf-8').read()

errs, warns = [], []
def chk(cond, msg):
    if not cond: errs.append(msg)
def warn(cond, msg):
    if not cond: warns.append(msg)

def norm(s):
    out = []
    for ch in s:
        if ch.isspace(): continue
        cat = None
        o = ord(ch)
        if (0x3000 <= o <= 0x303F) or (0xFF00 <= o <= 0xFFEF and not (0xFF21 <= o <= 0xFF5A)) \
           or ch in '「」『』“”‘’·，。、；：？！〈〉《》()(){}[]<>' or o < 0x2E80 and not ch.isalnum() \
           or (0x2018 <= o <= 0x201F):
            continue
        out.append(ch)
    return ''.join(out)

# ---------- 库本机数 ----------
libn = norm(lib)
total = len(lib)
hans = sum(1 for c in lib if 0x3400 <= ord(c) <= 0x9FFF or 0xF900 <= ord(c) <= 0xFAFF or 0x20000 <= ord(c) <= 0x2FFFF)
chk(total == 20903, f'总字符 {total} != 20903')
chk(hans == 15493, f'汉字 {hans} != 15493')

lines = lib.split('\n')
upidx = next(i for i, l in enumerate(lines) if l.strip() == '●卷下')
secs_up = [l.strip()[1:] for l in lines[:upidx] if l.strip().startswith('○')]
secs_dn = [l.strip()[1:] for l in lines[upidx:] if l.strip().startswith('○')]
chk(secs_up == ['论难', '辩捷', '昏忘', '嘲诮'], f'卷上四目 {secs_up}')
chk(len(secs_dn) == 64, f'卷下目 {len(secs_dn)} != 64')
dup = [k for k, v in Counter(secs_dn).items() if v > 1]
chk(sorted(dup) == sorted(['山东人', '诸葛恪', '封抱一']), f'重目 {dup}')

def paras(target):
    out, cur = [], None
    for l in lines:
        s = l.strip()
        if s.startswith('○'): cur = s[1:]; continue
        if s.startswith('●'): cur = None; continue
        if s and cur == target: out.append(s)
    return out

for name, exp in [('论难', 7), ('辩捷', 6), ('昏忘', 14), ('嘲诮', 13)]:
    n = len(paras(name))
    chk(n == exp, f'{name} 段数 {n} != {exp}')

tags = re.findall(r'（《太平广记》卷([^）]+)）', lib)
tc = Counter(tags)
chk(len(tags) == 17, f'广记签 {len(tags)} != 17')
chk(len(tc) == 15, f'卷次种数 {len(tc)} != 15')
chk(tc['一六四'] == 2 and tc['二四五'] == 2 and tc['二五○'] == 1 and tc['二六○'] == 1, f'签分布 {tc}')
chk(lib.count('（同前）') == 46, f"同前 {lib.count('（同前）')} != 46")
chk(len(re.findall(r'（《类说》卷一四）', lib)) == 1, '类说签 != 1')

for w, n in [('大笑', 36), ('应声', 24), ('高祖', 23), ('侯白', 26), ('杨素', 4),
             ('无以对', 6), ('无以应', 6), ('无以报', 1), ('借一而得两', 4),
             ('□', 37), ('ボ', 14), ('动莆', 21), ('动筒', 9)]:
    c = lib.count(w)
    chk(c == n, f'{w} {c} != {n}')
chk(lib.count('旁卧放气') == 1 and lib.count('傍卧放气') == 1, '旁/傍卧放气 计数不符')
upart = lib[:lib.index('●卷下')]
dnpart = lib[lib.index('●卷下'):]
chk(upart.count('动莆') == 21 and dnpart.count('动莆') == 0, '动莆 应全在卷上')
chk(lib.count('动筒') == 9 and upart.count('动筒') == 0, '动筒 应全在卷下')

pua = [c for c in lib if 0xE000 <= ord(c) <= 0xF8FF]
chk(len(pua) == 48, f'PUA 见 {len(pua)} != 48')
chk(len(set(pua)) == 26, f'PUA 种 {len(set(pua))} != 26')
dong = lib[lib.index('○石动筒'):lib.index('○刘焯')]
chk(dong.count('□') == 37, f'石动筒条 □ {dong.count("□")} != 37（全书□应全在此条）')

tang = sum(1 for i, l in enumerate(lines) if l.strip().startswith('○') and i + 1 < len(lines) and lines[i + 1].strip().startswith('唐'))
chk(tang == 24, f'唐开头 {tang} != 24')

# ---------- 千字文跨库 ----------
qz_lines = []
for l in qzw.split('\n'):
    s = l.strip()
    if not s or s.startswith('千字文') or s.startswith('周兴嗣'): continue
    toks = [t for t in s.split('　') if len(t) == 4]
    qz_lines.append(toks)
# 每行繁简对照重复两行，取并集
qz_toks = set()
for toks in qz_lines: qz_toks.update(toks)
i0 = lib.index('敬白社官')
i1 = lib.index('（《太平广记》卷二五二）', i0)
qishe = norm(re.sub(r'[，。、；：？！]', '', lib[i0:i1]))
hits = sorted(t for t in qz_toks if t in qishe)
chk(len(hits) == 40, f'乞社段千字文四字句 {len(hits)} != 40: {hits}')

# ---------- 页面 .q 收集 ----------
class QCollector(HTMLParser):
    VOID = {'br', 'img', 'meta', 'link', 'hr', 'input', 'source'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.qs = []
        self.buf = None
        self.drop = 0
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        cls = dict(attrs).get('class', '') or ''
        names = cls.split()
        isq = 'q' in names
        if self.buf is not None:
            self.stack.append(self.buf)
            if not isq: self.drop += 1
        elif isq:
            self.drop = 0
        if isq:
            self.buf = []
        self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        while self.stack:
            top = self.stack.pop()
            if top == tag: break
        if self.buf is not None:
            if self.stack and isinstance(self.stack[-1], list):
                self.drop = max(0, self.drop - 1)
                if self.drop == 0:
                    self.qs.append(''.join(self.buf))
                    self.buf = self.stack.pop()
            else:
                self.qs.append(''.join(self.buf))
                self.buf = None
    def handle_data(self, d):
        if self.buf is not None: self.buf.append(d)

col = QCollector()
col.feed(page)
pageqs = [q.strip() for q in col.qs if q.strip()]
print(f'页面 .q 共 {len(pageqs)} 枚')

bad = 0
for q in pageqs:
    qn = norm(q)
    if not qn: continue
    if qn not in libn:
        bad += 1
        print(f'  [X] 未命中库本: {q[:60]}')
chk(bad == 0, f'{bad} 枚 .q 未过库本核验')

# 页面内引文查重（refrain 允许，仅提醒）
dups = [q for q, c in Counter(pageqs).items() if c > 1]
if dups: warns.append(f'页面内重复引文: {dups}')

# 期望引文双侧断言
EXPECTED = [
 '合家齐拍掌，神明大歆飨。买奴合婢来，一个分成两。',
 '隋侯白，州举秀才至京，机辩捷，时莫之比。',
 '每上番日，即令谈戏弄，或从旦至晚，始得归。',
 '且问法师一个小义，佛常骑何物？',
 '或坐千叶莲花，或乘六牙白象。',
 '佛骑牛。',
 '经云：世尊甚奇特，岂非骑牛？',
 '何以知之？',
 '坐皆大笑。',
 '比来每经之上，皆云价值百千两金；未知百千两金，总有几斤？',
 '法师遂无以对。一坐更笑。',
 '看弟子有几个脚？',
 '向有两脚，今有一脚，若为得无一无二？',
 '若其二是真，不应有一脚，脚既得有一，明二即非真。',
 '弟子闻天无二日，土无二王，今者天子一人，临御四海，法师岂更得云无一？',
 '于是僧遂嘿然无以应，高祖抚掌大笑。',
 '天有何姓？',
 '先生可不见《孝经》云：父子之道，天性也。此岂不是天姓？',
 '达者七十二人，几人已着冠？',
 '经传无文。',
 '《论语》云冠者五六人，五六三十也；童子六七人，六七四十二也，岂非七十二人？',
 '今是何日？',
 '日是佛儿。',
 '今日佛生。',
 '佛是日儿。',
 '三个阿师，并不解樗蒲',
 '可不闻樗蒲人云：三个秃不敌一个卢。阿师何由可得？',
 '既为汝师，复为汝公，在三之义，顿居其两。',
 '今日之热，总由徐常侍来。',
 '徐常待年几？',
 '小于如来五岁，大于孔子二年。',
 '此公甚小。',
 '昔殷迁顽人，本居兹邑，今之存者，并是其人。',
 '鸠盘荼鬼，今在门外。',
 '毗舍',
 '鬼，乃住其中。',
 '汝国马价贵贱？',
 '若形容粗壮，虽无伎俩，堪驮物，直四五贯已上；',
 '绝无伎俩，旁卧放气，一钱不直。',
 '山东人多仁义，借一而得两。',
 '关中人亦甚聪明，问一而知二。',
 '有人问：比来多雨，渭水涨不？报曰：灞涨。岂非问一而知二？',
 '必须得容头者。',
 '以其腹中宛宛，正是好容头处，便言是帽，取而归。',
 '愿公口还得出气，眼还得见明，头还依旧动，脚还不废行。子子孙孙俱载帽，长住屋里坐萌萌。',
 '神明与福，令一奴而成两婢也。',
 '乌豆，从你不识我，而背我走去，可畏我不识你，而一时着尾子。',
 '偷我麦饭者只是此人。此贼犹不知足，故自仰面看我。',
 '王之为字，在言为讠王，近犬便狂，加颈足而为焉，施角尾而成羊。',
 '安乇为虐，在丘为虚，生男成虏，配马成驴。',
 '去头则是兀明，出颈则是无明，减半则是无目，变声则是无盲。',
 '焉是你，元来本姓匡，拗你尾子东北出，背上负王郎。',
 '绵绢，割却两耳只有面。',
 '善为笑言，然合于道',
 '漆城荡荡，寇来不能上。即欲漆之极易，难为荫室。',
 '橘生于江南，至江北为枳，枝叶相似，其实味且不同，水土异也。',
 '寡人反取病焉。',
 '我亲卿爱卿，是以卿卿。我不卿卿，谁当卿卿？',
 '流可枕，石可漱乎？',
 '所以枕流，欲洗其耳；所以漱石，欲砺其齿。',
 '边为姓，孝为字；腹便便，五经笥；但欲眠，思经事；寐与周公通梦，静与孔子同意，师而可嘲，出何典记？',
 '卒律葛答。',
 '承大家热铛子头，更作一个。',
 '郭璞《游仙诗》云：青溪千余仞，中有一道士。臣作云：青溪二千仞，中有两道士。岂不胜伊一倍？',
 '可不闻《论语》云：子在，回何敢死。',
 '向在省门，会卒无处见称，既闻道是出六斤，斟酌只应是六斤半。',
 '旦来遭见贤尊，愿郎君且避道。',
 '背共屋许大，肚共碗许大，口共盏许大。',
 '此是胡燕窠。',
 '有物大如狗，而貌极似牛',
 '此是犊子。',
 '取五月五日南墙下雪雪涂涂即即治。',
 '五月无雪，腊月何处有蛇咬？',
 '并我五也。',
 '冢子地握槊，星宿天围棋；开昙瓮张口，卷席床剥皮。',
 '相送重相送，相送至桥头；培堆两眼泪，难按满胸愁。',
 '臣作夜梦随陛下行，落一厕中出来，□□□□舐之。',
 '又齐文宣帝曰',
 '切闻政本于农，当须务兹稼穑，若不云腾致雨，何以税熟贡新？圣上臣伏戎羌，爱育黎首，用能闰余成岁，律吕调阳。',
 '酒则川流不息，肉则似兰斯馨，非直菜重芥姜，兼亦果珍李柰。',
 '但知悚惧恐惶，实若临深履薄。',
 '面作天地玄，鼻有雁门紫；既无左达丞，何劳罔谈彼。',
 '眼能日月盈仄，为有陈根委翳。',
 '不别似兰斯馨，都由雁门紫塞。',
 '我不卿卿，谁当卿卿？',
]
page_all = norm(''.join(pageqs))
miss = []
for e in EXPECTED:
    en = norm(e)
    inpage = en in page_all
    inlib = en in libn
    if not inpage: miss.append(('页面缺', e))
    if not inlib: miss.append(('库本缺', e))
for m in miss: print('  [X]', m[0], m[1][:50])
chk(not miss, f'{len(miss)} 条期望引文双侧断言未过')

# 千字文高亮句双侧
KWH = ['云腾致雨', '税熟贡新', '臣伏戎羌', '爱育黎首', '闰余成岁', '律吕调阳',
       '川流不息', '似兰斯馨', '菜重芥姜', '果珍李柰', '悚惧恐惶', '临深履薄']
for k in KWH:
    chk(k in lib and k in qzw and k in page, f'千字文高亮 {k} 双侧未过')
    chk(k in hits, f'千字文高亮 {k} 不在 40 句清单内')
chk('务资稼穑' in qzw and '务兹稼穑' in lib and '务兹稼穑' in page, '兹/资 异文对断言未过')
chk('务资稼穑' not in lib and '务兹稼穑' not in qzw, '兹/资 异文两形越界')

# chips 与库本卷下目序全等
chips = re.findall(r'<span class="chip(?: lit)?">([^<]+)</span>', page)
chk(len(chips) == 64, f'chips {len(chips)} != 64')
secs_strip = [re.sub(r'[-]', '', x) for x in secs_dn]
chk(chips == secs_strip, f'chips 序与库本目序不符: {[ (a,b) for a,b in zip(chips,secs_strip) if a!=b ][:5]}')

# sign chips 17 枚
signs = re.findall(r'<span class="sign(?: alt)?">([^<]+)<', page)
chk(len(signs) == 17, f'sign {len(signs)} != 17')

# 页面机数文案
for txt in ['卷上二十一见都写作「莆」', '九见写作「筒」', '全书三十七个缺字符', '四字句共 <b>四十</b> 句',
            '同前四十六处', '广记签十七处（十五个卷次）', '开口便是「唐」字', '二十四目', '应声二十四见', '六十四目', '二十六种四十八见', '十四见',
            '务资稼穑，乞社作务兹稼穑']:
    chk(txt in page, f'页面机数文案缺: {txt[:24]}')

# 编号
n113 = page.count('之一百一十三')
chk(n113 == 3, f'编号之一百一十三出现 {n113} 次 != 3（title+kicker+footer）')
chk(page.count('卷六十五') >= 2, '卷六十五出现不足')

# 页脚三要素
for t in ['殆知阁简体库', '逐字核验', '时代局限', 'robertsong2000/daizhigev20', 'daizhige-daodu']:
    chk(t in page, f'页脚缺: {t}')

# ---------- 排版红线 ----------
body_no_style = re.sub(r'<style>.*?</style>', '', page, flags=re.S)
chk('—' not in page and '–' not in page, '存在长划线')
for i, l in enumerate(page.split('\n'), 1):
    c = l.count('·')
    chk(c <= 1, f'第 {i} 行有 {c} 枚 ·: {l.strip()[:60]}')
vis = re.sub(r'<[^>]+>', '', body_no_style)
vis = re.sub(r'github\.com/[A-Za-z0-9/\-]+', '', vis)
en = re.findall(r'[A-Za-z]{2,}', vis)
chk(not en, f'可见文本英文残留: {en[:8]}')

print()
print('=== 机数摘要 ===')
print(f'库本 {total} 字符 / 汉字 {hans} / 卷上四目 {len(secs_up)} / 卷下目 {len(secs_dn)}（重目 {dup}）')
print(f'签：广记 {len(tags)} 处 {len(tc)} 卷次（{dict(tc)}）类说 1 同前 46')
print(f'大笑 36 应声 24 侯白 26 高祖 23 动莆 21 动筒 9 □ 37（全在石动筒条）PUA 26 种 48 见 假名ボ 14')
print(f'千字文四字句命中 {len(hits)}')
print(f'页面 .q {len(pageqs)} 枚全部过库本核验；期望清单 {len(EXPECTED)} 条双侧过')
print()
if warns:
    print('WARN:')
    for w in warns: print(' -', w)
if errs:
    print('FAIL:')
    for e in errs: print(' x', e)
    sys.exit(1)
print('ALL PASS')
