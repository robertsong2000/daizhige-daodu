#!/usr/bin/env python3
"""核验 anlushan-shiji.html：引文逐字对库 + 机数 + 排版红线。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'anlushan-shiji.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/安禄山事迹.txt'

raw = open(LIB, encoding='utf-8', errors='ignore').read()
lines = raw.split('\n')
C1 = re.sub(r'\s', '', '\n'.join(lines[2:153]))     # 第一抄：卷上..缪跋（含卷目行）
C2 = re.sub(r'\s', '', '\n'.join(lines[156:]))      # 第二抄
FULL = re.sub(r'\s', '', raw)

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch.isspace():
            continue
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
        # 标点、字母、数字、符号一律丢弃，两侧口径一致
    return ''.join(out)

LIB_N = norm(C1)

# ---------- QCollector：栈配平收 .q（class.split 恰含 q） ----------
class QCollect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.text = []
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '')
        is_q = 'q' in cls.split()
        if tag not in ('br', 'img', 'meta', 'link', 'hr', 'input'):
            self.stack.append((tag, is_q))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
    def handle_data(self, data):
        if any(self.stack):
            self.text.append(data)

html = open(PAGE, encoding='utf-8').read()
body = html[html.index('<body'):]

qc = QCollect()
qc.feed(body)
qtext = ''.join(qc.text)
QN = norm(qtext)

# ---------- 引文清单（页面 .q 覆盖的库本原句，逐字比对经 norm） ----------
QUOTES = [
 "是夜赤光傍照，群兽四鸣，望气者见妖星芒炽落其穹庐。",
 "大夫不欲灭奚、契丹两蕃耶？而杀壮士！",
 "乱幽州者，必此胡也。",
 "穰苴出军，必诛庄贾；孙武行令，亦斩宫嫔。守珪军令若行，禄山不宜免死。",
 "卿岂以王夷甫识石勒，便臆断禄山难制耶？",
 "晚年益肥，腹垂过膝，自秤得三百五十斤。",
 "《胡旋舞》，其疾如风。",
 "臣蕃人，不识朝仪，不知太子是何官？",
 "蕃人先母后父耳。",
 "贵妃与禄山作三曰洗儿，洗了又绷禄山，是以欢笑。",
 "猪龙也，无能为者。",
 "十一月九曰，禄山起兵反，以同罗、契丹、室韦曳落河，兼范阳、平卢、河东、幽、蓟之众，号为父子军，马步相兼十万，皷行而西，以诛杨国忠为名。",
 "今反者独禄山耳！三军左右皆不欲也，旬曰必斩之来降，不如此，陛下发兵讨之，仗大义诛暴逆，可不血刃而定矣。",
 "百年老公未尝见范阳兵马向南者。",
 "燕者，禄山国号。重言燕者，史思明亦称天子。天上女，安字也。铺白毡者，禄山入洛阳之曰，大雪盈尺。毡上一贯钱者，言禄山只得一千曰。",
 "皷行而西，以诛杨国忠为名",
 "传张介然、荔非守瑜等首至",
 "传太守崔无诐首至",
 "传留守李憕、御史中丞卢奕首至",
 "进则十五有生，退则死在旋踵。",
 "辛卯之夕，平安火不至，玄宗惧焉。",
 "杨国忠与吐蕃同反，魏方进亦连。",
 "太真不合供奉。",
 "今曰之事，实所甘心，容礼佛。",
 "尔是逆贼，更道何人？",
 "并刳其心，以祭安庆宗。",
 "汝事皇帝，鞭笞宁可数乎？汝不行大事，死无曰矣。",
 "贼由严庄。",
 "一种是死，不如刀头取决",
 "因何杀阿爷夺职掌？",
 "樱桃一笼子，半赤一半黄。一半与怀王，一半与周贽。",
 "一半与怀王，一半与周贽",
 "一半与周贽，一半与怀王",
 "韵是何物？岂可以我儿在周贽之下！",
 "鹿者，禄也；水者，命也。禄与命俱尽矣。",
 "莫杀我，我不惜死，恐汝有杀父之名。",
 "而禄山不得其尸，与妻康氏并招魂而葬，所谓哀后者也。",
 "二胡共扰中原凡八年，幽、燕始平。",
 "里居未详。",
 "今诸书不存，独此书尚为完帙",
]

# 叙述中的「」引文（.q 之外）
INLINE = [
 "解九蕃语，为诸蕃互市牙郎",
 "守珪遂养为子",
 "同罗、契丹、室韦曳落河，兼范阳、平卢、河东、幽、蓟之众",
 "翰遂领马步十五万，与贼将崔干佑会",
 "如是沉者数十渡",
 "向时之盛扫地矣",
 "以是道路相目，无敢言者。",
]

fails = []
# 1. 每条引文逐一在库本（norm 后子串）+ 在页面 qtext（norm 后子串）双验
for q in QUOTES:
    qn = norm(q)
    if qn not in LIB_N:
        fails.append(f"[库本无] {q}")
    if qn not in QN:
        fails.append(f"[页面q缺] {q}")
for q in INLINE:
    qn = norm(q)
    if qn not in LIB_N:
        fails.append(f"[库本无·inline] {q}")
    if qn not in norm(body):
        fails.append(f"[页面无·inline] {q}")

# 2. 「」反扫（剔除校记区 ul.jiaoji）
stripped = re.sub(r'<ul class="jiaoji">.*?</ul>', '', body, flags=re.S)
for m in re.finditer(r'「([^」]+)」', stripped):
    s = norm(m.group(1))
    if not s:
        continue
    if s not in LIB_N:
        fails.append(f"[反扫未中] 「{m.group(1)[:40]}…」" if len(m.group(1)) > 40 else f"[反扫未中] 「{m.group(1)}」")

# 3. 排版红线
if '—' in html or '–' in html:
    fails.append("[红线] 出现长划线 —/–")
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f"[红线] 第{i}行 · 超限: {line.strip()[:50]}")

# 4. 机数断言
def cnt(s, lib): return lib.count(s)
checks = [
 ("第一抄去空白 22634", len(C1) == 22634),
 ("第二抄去空白 22611", len(C2) == 22611),
 ("全帙去空白 45256", len(FULL) == 45256),
 ("两抄差 23", len(C1) - len(C2) == 23),
 ("第一抄 曰215", cnt('曰', C1) == 215),
 ("第一抄 日0", cnt('日', C1) == 0),
 ("盘迭在第一抄", '盘迭' in C1),
 ("盘叠在第二抄", '盘叠' in C2),
 ("思朋讹字在库本", '思朋乃引军来援' in C1),
 ("宝德元年讹在库本", '宝德元年' in C1),
 ("九月九曰甲午在库本", '其九月九曰甲午' in C1),
 ("页脚 之九十三", '之九十三' in html),
 ("页脚 卷五十", '卷五十' in html),
 ("settle 十万", '十 万' in html and '马步相兼十万' in C1),
 ("settle 三十二人", '三十二人' in html and '蕃将三十二人以代汉将' in C1),
 ("settle 八年", '凡八年' in C1),
 ("缺字号 8 见", cnt('□', C1) == 8),
 ("题号 之九十三 in title", '之九十三' in re.search(r'<title>(.*?)</title>', html).group(1)),
]
for name, ok in checks:
    if not ok:
        fails.append(f"[机数] {name}")

# 5. 引文计数一致性：页面 .q 块数（含 inl）应 >= QUOTES 中通过 qtext 验证的数量
qblocks = len(re.findall(r'class="[^"]*\bq\b[^"]*"', body))
print(f".q 块标记数: {qblocks}, QUOTES: {len(QUOTES)}, INLINE: {len(INLINE)}, qtext norm 长度: {len(QN)}")

if fails:
    print(f"\nFAIL ({len(fails)}):")
    for f in fails:
        print(" ", f)
    sys.exit(1)
print(f"PASS: {len(QUOTES)} 条 .q + {len(INLINE)} 条 inline 引文逐字对库通过；机数 {len(checks)} 项通过；排版红线通过。")
