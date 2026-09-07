#!/usr/bin/env python3
"""核验 chiya.html：引文逐字对库 + 删夹注取正文 + 则目机数 + 排版红线。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'chiya.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/赤雅.txt'

raw = open(LIB, encoding='utf-8', errors='ignore').read()
# 库本条目内夹注（辑校汇注）：整括号删除，取正文口径
FULL = re.sub(r'（一本[^）]*）', '', raw)

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

# ---------- .q 块引文 ----------
QUOTES = [
 "余穷历九郡，南尽衡山，然后知先王建国亲侯，其道大也。",
 "四府三十七州，形势宛然一衰周战国图。",
 "税未输而越关者，许射之。既输，暮行露宿，货物狼藉，无敢睨者。",
 "四人专主击刺，三人专主割首。所获首级，七人共之。",
 "不如令者斩，退缩者斩，走者斩。",
 "狼兵鸷悍，天下称最。",
 "峒女于春秋时，布花果、笙箫于名山，五丝刺同心结、百纽鸳鸯囊，选峒中之少好者，伴峒官之女，名曰天姬队。",
 "先献人头一枚，名吴将军首级。予观祭时以桄榔面为之",
 "五月五日，聚诸虫豸之毒者，并置器内，自相吞食，最后独存者曰蛊。",
 "出一丸啖之，立吐奇怪。",
 "予久客其中，习知其方。",
 "水作青罗带，山为碧玉簪。",
 "鬼门关，十人去九不还。",
 "予大书四字其上，曰：“诗人鲊翁。”",
 "如楼通天，如阙刺霄，如修竿，如高旗，如人怒",
 "灵渠自北而南，三十二陡。",
 "予过陡时，水长月明，如层台叠壁，从天而下。",
 "予行十日，抵兴安，至今梦魂时时见之。",
 "绿珠井，在白州双角山下，有七孔",
 "善吹笛，传其弟子宋伟，后入宋明帝宫。",
 "父老然之，即日徙石。",
 "予在绿鸦山见之",
 "未饮先谢，既饮辄醉，知予之无机也。",
 "伏波铜鼓，深三尺许，面径三尺五寸",
 "鼓面环绕作蛙黾十数，昂首欲跳。",
 "瘴起时，望之有气一道，上冲如柱",
 "人若伏地，从其自掷，则无恙。",
 "春曰青草，夏曰黄梅，秋曰新禾，冬曰黄茅。",
 "避色如避难，冷暖随时换。少饮卯时酒，莫吃申时饭。",
 "清夜闻歌，每能自叫。",
 "盘公以名马五十匹易之。",
 "惟帝不自有其黄屋之尊，而躬巡于鸟言卉服之域。",
]

# 叙述中的内联引文（.q 之外）
INLINE = [
 "其乐五合，其旗五方，其衣五彩",
 "中之者为痞闷，为疯痖，为汗死",
 "旁围渐缩如腰",
 "蛇蛊、晰蜴蛊、蜣螂蛊",
 "先置食中，味增百倍",
 "夜出有光，熠如曳彗",
 "光积生影",
 "是名金蚕",
 "人面猿身，最机警",
 "通八方言",
 "声如二八女子",
 "嗜酒好屐",
 "客必东人",
 "踊跃出视",
 "远交近攻",
 "割村为质",
 "秦人置郡时所植",
 "诞女必丽",
 "幼女何罪",
 "赛神宴客时时击之",
 "重赀求购，多至千牛",
 "两粤滇黔皆有",
 "渐大如车轮，四下掷人",
 "能以少击众",
 "皆实录也",
 "如笋出地，各不相倚",
]

# 则目（○ 开头条目名，库本存在即可）
ENTRIES = ["土司世胄","形势","法制","岑家兵略","狼兵","瑶人祀典","云亸君兵法",
 "浪花歌","天姬破蛊","山川论略","鬼门关","阳朔道上诸峰","七百里松阴古道",
 "灵渠","绿珠井","猩猩","伏波铜鼓","瘴母","四瘴","治瘴","瘴中要诀",
 "绿珠玉笛","舜至苍梧"]

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
        fails.append(f"[库本无] {q}")
    if qn not in QN:
        fails.append(f"[页面缺] {q}")

# 2. 排版红线：长划线、行内·密度
for i, line in enumerate(html.splitlines(), 1):
    if '—' in line or '–' in line:
        fails.append(f"[长划线] 第{i}行")
    if line.count('·') > 1:
        fails.append(f"[·密度] 第{i}行 {line.strip()[:40]}")

# 3. 机数断言
items = re.findall(r'　　○[^\n]{1,15}', FULL)
checks = [
 ("全帙去空白 26538", len(re.sub(r'\s', '', raw)) == 26538),
 ("则目 197 条", len(items) == 197),
 ("三卷俱存", '●卷上' in FULL and '●卷中' in FULL and '●卷下' in FULL),
 ("卷序 上中下", FULL.find('●卷上') < FULL.find('●卷中') < FULL.find('●卷下')),
 ("末条舜至苍梧", '舜至苍梧' in FULL and FULL.find('○舜至苍梧') > FULL.find('○绿珠玉笛')),
 ("瘴组在卷下", FULL.find('○瘴母') > FULL.find('●卷下')),
 ("伏波铜鼓存在", '伏波铜鼓，深三尺许' in FULL),
 ("页脚 核验", '逐字核验' in html),
 ("页脚 来源链接", 'daizhigev20' in html),
 ("title 含书名", '赤雅' in re.search(r'<title>(.*?)</title>', html).group(1)),
 ("篇号 212 两处", html.count('第212篇') == 2),
 ("墨底纸白", '#191917' in html and '#e8e4dc' in html),
 ("赭金点缀", '#c9963f' in html),
 ("无外部脚本", '<script src' not in html and '<link' not in html),
 ("生平时限申报", '通行史传' in html),
]
for name, ok in checks:
    if not ok:
        fails.append(f"[机数] {name}")

for e in ENTRIES:
    if ('○' + e) not in FULL:
        fails.append(f"[则目] 库本无 ○{e}")

qblocks = len(re.findall(r'class="[^"]*\bq\b[^"]*"', body))
print(f".q 块标记数: {qblocks}, QUOTES: {len(QUOTES)}, INLINE: {len(INLINE)}, 则目: {len(ENTRIES)}, qtext norm 长度: {len(QN)}")

if fails:
    print(f"\nFAIL ({len(fails)}):")
    for f in fails:
        print(" ", f)
    sys.exit(1)
print(f"PASS: {len(QUOTES)} 条 .q + {len(INLINE)} 条 inline + {len(ENTRIES)} 则目逐字对库通过；机数 {len(checks)} 项通过；排版红线通过。")
