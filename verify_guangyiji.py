#!/usr/bin/env python3
"""核验 guangyi-ji.html：引文逐字对库 + 名签墙 + 机数 + 排版红线。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'guangyi-ji.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/广异记.txt'

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

# ---------- .q 块引文 ----------
QUOTES = [
 "予欲观天人之际，变化之兆，吉凶之源，圣有不知，神有不测。",
 "此书二十卷，用纸一千幅，盖十余万言，虽景命不融，而铿锵之韵固可以辅于神明矣。",
 "二子钺、雍，陈其先志，泣请父友况得而叙之。",
 "一名养神芝。其叶似菰，生不丛，一株可活千人。",
 "妇人指云：“中心床坐，须鬓白者，徐君也。”",
 "君知秦始皇时徐福耶？”曰：“知之。”“此则是也。",
 "张三令持此取三百千贯钱，彼当与君也。",
 "邻人曰：“此刘道玄宅也，十余年无居者。”",
 "王云：“是五十年前来茯苓主顾，今有二千余贯钱在药行中。”",
 "昨夕梦见五六人追，云是张仙唤搊筝，临别，以林檎系裙带上。",
 "性至孝，以其父在颍州，乃盗官马往以迎省。",
 "我用刀砍，至其身则手懦，不知何也。",
 "时人呼为“三刀师”，谓是起敬菩萨。",
 "王形貌甚伟，头有两角，问颂曰：“公作官，不横取人财否？”",
 "王令检簿。检讫，云：“甚善甚善！既无勾当，即宜还家。衣裳得无隳坏耶？”",
 "如得五千贯，当送汝还。",
 "纸钱五千贯，理易办。",
 "入井即活，更何所之。”遂推颂落井而活",
 "君安所居，道里远近宜速还家，不出十日，必死。",
 "汝是新死鬼，官家捉汝，何得有官乎！",
 "门榜云：“中丞理冤屈院。”",
 "若不相值，几成闲鬼，三五百年，不得变转，何其痛哉！",
 "土耳，何能为！",
 "须臾，楼上云昏电掣，既风且雷，酒肉飞扬，众人危惧。",
 "独污金刚者，曳出楼外数十丈而震死。",
 "因回指云：“我珠在殿宝帐东北角。”使人求之，果得焉。",
]

# 叙述中的内联引文（.q 之外）
INLINE = [
 "至德初",
 "同登一科",
 "饶州录事参军",
 "有文集二十卷",
 "半身枯黑",
 "有疾者服之，皆愈",
 "乾元中",
 "诵《金刚经》十余年",
 "铁铃乞食",
 "千人斋供",
 "暴卒",
 "有司",
 "母老子幼",
 "衣裳",
 "不出十日，必死",
 "施食",
 "京兆",
 "中丞理冤屈院",
 "三五百年，不得变转",
 "鸟雀不敢近",
 "酒肉",
 "曳出楼外数十丈而震死",
 "高宗王皇后后身",
 "武妃所生",
 "我珠在殿宝帐东北角",
 "使人求之，果得焉",
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

# 4. 零外部依赖
for pat in ('<script', 'src=', '@import', '@font-face', 'url(', '<link'):
    if pat in html.replace('SRC', ''):
        fails.append(f"[红线] 疑似外部依赖: {pat}")
for ch in html:
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF:
        fails.append(f"[红线] 私用区字符 U+{o:04X}")
        break

# 5. 名签墙：四十面小牌必须都是库本则目
TITLES = ["徐福","仆仆先生","张李二公","刘清真","麻阳村人","慈心仙人","石巨","王老",
 "李仙人","衡山隐者","潘尊师","秦时妇人","何二娘","边洞玄","张连翘","辅神通",
 "郑相如","婺州金刚","长安县系囚","卢氏","陈利宾","王宏","田氏","李惟燕",
 "孙明","三刀师","宋参军","刘鸿渐","张喜猷","魏恂","周颂","卢弁",
 "李及","阿六","郜澄","王勋","周哲滞妻","刘长史女","岐王范","太华公主"]
for t in TITLES:
    if ('○' + t) not in FULL:
        fails.append(f"[则目] 库本无 ○{t}")

# 6. 机数断言
items = re.findall(r'　　○[^\n]{1,15}\n', open(LIB, encoding='utf-8').read())
checks = [
 ("全帙去空白 103869", len(FULL) == 103869),
 ("则目 301 条", len(items) == 301),
 ("首则徐福", items[0].endswith('徐福\n')),
 ("末则太华公主", items[-1].endswith('太华公主\n')),
 ("库本讹字 刺吏在三刀师条", '刺吏崔昭' in FULL),
 ("库本作 未尝欢毅", '未尝欢毅' in FULL),
 ("库本作 郭子潢(序中讹字例)", '郭子潢' in FULL),
 ("卷首次序 张李二公在刘清真前", FULL.find('○张李二公') < FULL.find('○刘清真')),
 ("页脚 核验", '逐字核验' in html),
 ("页脚 来源链接", 'daizhigev20' in html),
 ("title 含书名", '广异记' in re.search(r'<title>(.*?)</title>', html).group(1)),
 ("篇号 207 两处", html.count('第207篇') == 2),
 ("墨底纸白", '#191917' in html and '#e8e4dc' in html),
 ("朱砂点缀", '#c0453c' in html),
]
for name, ok in checks:
    if not ok:
        fails.append(f"[机数] {name}")

qblocks = len(re.findall(r'class="[^"]*\bq\b[^"]*"', body))
print(f".q 块标记数: {qblocks}, QUOTES: {len(QUOTES)}, INLINE: {len(INLINE)}, 名签: {len(TITLES)}, qtext norm 长度: {len(QN)}")

if fails:
    print(f"\nFAIL ({len(fails)}):")
    for f in fails:
        print(" ", f)
    sys.exit(1)
print(f"PASS: {len(QUOTES)} 条 .q + {len(INLINE)} 条 inline + {len(TITLES)} 面名签逐字对库通过；机数 {len(checks)} 项通过；排版红线通过。")
