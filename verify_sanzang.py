#!/usr/bin/env python3
"""核验 sanzang-fashi-zhuan.html：引文逐字对库 + 机数 + 排版红线。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'sanzang-fashi-zhuan.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/佛藏/大藏经/杂藏/史传部/大唐大慈恩寺三藏法师传.txt'

FULL = re.sub(r'\s', '', open(LIB, encoding='utf-8', errors='ignore').read())

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

LIB_N = norm(FULL)

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

# ---------- .q 块引文（页面 .q 覆盖的库本原句，逐字比对经 norm） ----------
QUOTES = [
 "法师讳玄奘。俗姓陈。陈留人也。",
 "意欲远绍如来。近光遗法。",
 "诵业易成风骨难得。若度此子必为释门伟器。",
 "未发之间凉州访牒又至云。有僧字玄奘欲入西蕃。所在州县宜严候捉。",
 "师须实语必是弟子为图之。",
 "弟子不能去。家累既大。而王法不可干也。",
 "纵使切割此身如微尘者终不相引。",
 "上无飞鸟下无走兽。复无水草。",
 "我先发愿若不至天竺终不东归一步。今何故来。宁可就西而死。岂归东而生。",
 "是时四夜五日无一渧沾喉口腹干燋。几将殒绝",
 "至第五夜半忽有凉风触身。冷快如沐寒水。遂得目明马亦能起。",
 "王与侍人前后列烛。自出宫迎法师入后院。",
 "云弟子自闻师名喜忘寝食。量准涂路知师今夜必至。与妻子皆未眠读经敬待。",
 "遂誓不食以感其心。于是端坐。水浆不涉于口三日。至第四日王觉法师气息渐惙。深生愧惧。乃稽首礼谢云。任师西行乞垂早食。",
 "请共对佛更结因缘。遂共入道场礼佛。对母张太妃共法师约为兄弟。任师求法。还日请住此国三年受弟子供养。",
 "将升法座王又低跪为蹬。令法师蹑上。日日如此。",
 "若其问有一字无理能难破者。请断首相谢。",
 "五印度中有十八国王到。谙知大小乘僧三千余人到。婆罗门及尼干外道二千余人到。那烂陀寺千余僧到。",
 "自是邪徒戢翼。竟十八日无一人发论。",
 "大乘众号曰摩诃耶那提婆。此云大乘天。小乘众号曰木叉提婆。此云解脱天。",
 "帝又察法师堪公辅之寄。因劝归俗助秉俗务。",
 "今遣从俗。无异乘流之舟使弃水而就陆不唯无功亦徒令腐败也。愿得毕身行道以报国恩。",
 "师尚能孤游绝域。今此行盖同跬步。安足辞焉。",
 "玄奘从西域所得梵本六百余部。一言未译。",
 "所以敬崇此塔拟安梵本。",
 "时三藏亲负篑畚担运砖石。首尾二周功业斯毕。",
 "玄奘今年六十有五。必当卒命于此伽蓝。",
 "至龙朔三年冬十月二十三日功毕绝笔。合成六百卷。",
 "具录所翻经论。合七十四部。总一千三百三十八卷。",
 "弟子光等问。和上决定得生弥勒内院不。法师报云。得生。言讫喘息渐微。少间神逝。",
 "复口说偈教傍人云。南无弥勒如来应正等觉。愿与含识速奉慈颜。南无弥勒如来所居内众。愿舍命已必生其中。",
 "帝闻之哀恸伤感。为之罢朝曰。朕失国宝矣。",
]

# 叙述中的内联引文（.q 之外）
INLINE = [
 "于洛阳度二七僧",
 "出家意何所为",
 "誓游西方以问所惑",
 "禁约百姓不许出蕃",
 "少时胡人乃拔刀而起，徐向法师，未到十步许又回。",
 "千里行资一朝斯罄",
 "但为无上正法来耳。",
 "何不强行而更卧也。",
 "甘澄镜澈",
 "衣不及带。跣足出迎。",
 "岂期今日重见乡人。",
 "每日进食王躬捧槃",
 "充法师往还二十年所用之资",
 "法师者是奴弟。欲求法于婆罗门国。",
 "古来法尔事不可违",
 "支那国法师立大乘义，破诸异见，自十八日来无敢论者。",
 "伤触法师者斩其首。毁骂者截其舌。",
 "自是德音弥远矣。",
 "而清言既交遂不知日昃",
 "从足向上渐冷最后顶暖",
 "见北方有白虹四道。从北亘南贯井宿直至慈恩塔院。",
 "至麟德元年二月玉华宫舍化",
]

fails = []
# 1. .q 引文双验：库本子串 + 页面 .q 文本子串
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

# 2. 「」反扫（内联引文兜底）
for m in re.finditer(r'「([^」]+)」', body):
    s = norm(m.group(1))
    if s and s not in LIB_N:
        fails.append(f"[反扫未中] 「{m.group(1)[:40]}…」" if len(m.group(1)) > 40 else f"[反扫未中] 「{m.group(1)}」")

# 3. 排版红线
if '—' in html or '–' in html:
    fails.append("[红线] 出现长划线 —/–")
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f"[红线] 第{i}行 · 超限: {line.strip()[:50]}")

# 4. 机数断言
def cnt(s, lib): return lib.count(s)
marks = len(re.findall('大唐大慈恩寺三藏法师传卷第[一二三四五六七八九十]+', FULL))
checks = [
 ("全帙去空白 92762", len(FULL) == 92762),
 ("卷标记 19 处", marks == 19),
 ("库本作 曲文泰", '曲文泰' in FULL),
 ("库本作 石字槃陀", '姓石字槃陀' in FULL),
 ("李大亮都督凉州", '李大亮为凉州都督' in FULL),
 ("二七僧", '于洛阳度二七僧' in FULL),
 ("黄金一百两", '黄金一百两银钱三万' in FULL),
 ("亲负篑畚在卷七区段", 57780 <= FULL.find('时三藏亲负篑畚') < 65778),
 ("断首相谢在卷五区段", 40107 <= FULL.find('断首相谢') < 50423),
 ("堪公辅之寄在卷六区段", 50437 <= FULL.find('堪公辅之寄') < 57766),
 ("朕失国宝在卷十区段", 85970 <= FULL.find('朕失国宝') ),
 ("页脚 核验", '逐字核验' in html),
 ("页脚 来源", 'daizhigev20' in html),
 ("title 含书名", '三藏法师传' in re.search(r'<title>(.*?)</title>', html).group(1)),
]
for name, ok in checks:
    if not ok:
        fails.append(f"[机数] {name}")

qblocks = len(re.findall(r'class="[^"]*\bq\b[^"]*"', body))
print(f".q 块标记数: {qblocks}, QUOTES: {len(QUOTES)}, INLINE: {len(INLINE)}, qtext norm 长度: {len(QN)}")

if fails:
    print(f"\nFAIL ({len(fails)}):")
    for f in fails:
        print(" ", f)
    sys.exit(1)
print(f"PASS: {len(QUOTES)} 条 .q + {len(INLINE)} 条 inline 引文逐字对库通过；机数 {len(checks)} 项通过；排版红线通过。")
