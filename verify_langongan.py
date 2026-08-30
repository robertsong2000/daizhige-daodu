#!/usr/bin/env python3
# 核验 langongan.html（蓝公案导读）引文、结构、机数、排版红线
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/langongan.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/话本/蓝公案.txt'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
errors, warnings = [], []

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

NORM_LIB = norm(lib)

# ---------- 引文收集器（html.parser 栈配平，跳过 VOID） ----------
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class QCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.quotes = []      # 每个顶层 q 块的收集文本
        self.cur = None       # 当前正在收集的 q 索引栈
        self.qstack = []
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        cls = dict(attrs).get('class', '') or ''
        isq = 'q' in cls.split()
        if isq:
            self.qstack.append([])
        self.stack.append(tag)
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in VOID: return
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack: self.stack.pop()
        cls = None
        if self.qstack:
            pass
    def handle_data(self, data):
        if self.qstack:
            self.qstack[-1].append(data)
    def close(self):
        super().close()

# 上面的收集器对嵌套 q 处理不足，改用带类判定的栈方案：
class QC2(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []       # (tag, isq)
        self.results = []     # [ [text,...], ... ] per open q
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        cls = dict(attrs).get('class', '') or ''
        isq = 'q' in cls.split()
        if isq:
            self.results.append([])
        self.stack.append((tag, isq))
    def handle_endtag(self, tag):
        if tag in VOID: return
        # 配平
        while self.stack and self.stack[-1][0] != tag:
            self.stack.pop()
        if not self.stack:
            return
        t, isq = self.stack.pop()
        if isq and self.results:
            pass  # 闭合时文本已在块内
    def handle_data(self, data):
        if self.stack and self.stack[-1][1]:
            if self.results:
                self.results[-1].append(data)
    def done(self):
        return [''.join(x) for x in self.results]

# 更稳的实现：任何时刻处于某个 q 内（即使嵌套）都收集到最外层该 q
class QC3(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []       # tags
        self.qdepth = 0
        self.bufs = []
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        cls = dict(attrs).get('class', '') or ''
        if 'q' in cls.split() and self.qdepth == 0:
            self.bufs.append([])
            self.qdepth = 1
        elif 'q' in cls.split():
            self.qdepth += 1
        self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in VOID: return
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack: self.stack.pop()
        # 弹出时若跨过 q 边界，qdepth 相应减一：简化为按栈重算
        d = 0
        # 重算当前栈上的 q 数量：不可知（starttag 已丢 class），用计数器维护
    def handle_data(self, data):
        if self.qdepth > 0 and self.bufs:
            self.bufs[-1].append(data)
    def done(self):
        return [''.join(x) for x in self.bufs]

# 采用显式维护 qdepth 的简化解析器
class QParse(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.qdepth = 0
        self.bufs = []
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        if 'q' in cls.split():
            if self.qdepth == 0:
                self.bufs.append([])
            self.qdepth += 1
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        if self.qdepth > 0 and self.bufs:
            self.bufs[-1].append(data)
    def close(self):
        # endtag 处理：在 feed 过程中即时维护
        super().close()

# 上面 endtag 无法知道 class，改用正则方案（本页结构简单、无嵌套 q）
def collect_q_by_regex(html):
    quotes = []
    # 顶层含 q 的元素：span/blockquote/p/div，其内可能有嵌套 span（无 q 类）
    pat = re.compile(r'<(span|p|div|blockquote|h[1-6]|em|b|i|small)([^>]*\bclass="[^"]*\bq\b[^"]*"[^>]*)>(.*?)</\1>', re.S)
    pos = 0
    while True:
        m = pat.search(html, pos)
        if not m: break
        quotes.append(m.group(3))
        pos = m.end()
    return quotes

raw_q = collect_q_by_regex(page)
def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)
page_quotes = [norm(strip_tags(x)) for x in raw_q]
page_quotes = [x for x in page_quotes if x]

QUOTES = [
 # hero
 "素楮耳！","亦收之。",
 # 到任
 "潮阳一县，岁征民米军屯一万一千余石","大吏以余承乏，代庖兹邑。冬十月十八日抵任",
 "廪无粒米，仓无遗谷，军士多鸠形鹄面","悬釜嗷嗷",
 "猝闻亭外人众哄然一声，差役拥挤，向东角门走出","书吏禀请退堂，曰：“图差散矣。”",
 "欲上东山耶？","大开城门纵之去","众差闻余语怪异，皆伫立耸听",
 "至四鼓鸡鸣而毕，无敢有一名不到者","我昔在军中，视三十万贼如草芥，况东山一卷石，直用靴尖踢平耳。",
 # 没字词
 "手展一楮戴头上","没字也，惟空楮而已。",
 "不识字，又短于财，代书者为李阿梅所阻，莫我肯代。","我等亦知夫死已久",
 "月给与食米一石","李阿梅亦欢欣叩首，转身吐舌而去","目动言肆",
 # 幽魂对质
 "钩距毕施，刑法用尽",
 "我已牒城隍尊神，约于令夜二更，提出杨仙友鬼魂，与汝质对。汝等虽有百喙，亦难以掩饰矣。",
 "此以手捧心、血染红衣者是已","惟罗明珠、江子千、江立清三人低首不视，若为弗闻也。",
 "仙友言，祸由立清，终不肯使活，将夺其魄于道。","甫三日，而立清卒。潮人遂以为真有鬼神也。",
 # 三宄盗尸
 "诘朝诣验，空圹无尸。","偷尸者，王士毅也。",
 "密呼壮役林才，语之曰：“汝去衣帽，先驱入邑城，疾趋东门旅店，问潮客王士毅投宿几日，寓何房舍，舍中有一人，缚以来。”",
 "字迹与原状若合符节","非公龙图再世，我兄弟死不瞑目矣！",
 # 死丐得妻子
 "遍体并无他伤","而指甲泥沙，实为投河确据","何以尸首腐烂，竟似半月有余",
 "众皆骇愕","汝五人分途追缉，无不获者","百姓环庭聚观者数千人，皆拊掌大笑。",
 # 兄弟讼田
 "汝两人各伸一足，合而夹之。能忍耐不言痛者，则田归之矣。",
 "但不知汝等左足痛乎？右足痛乎？左右惟汝自择，我不相强。",
 "汝两人各伸一不痛之足来！","阿明、阿定答曰：“皆痛也。”",
 "汝两足尚不忍舍其一，汝父两子，肯舍其一乎？",
 "命隶役以铁索一条两系之，封其钥口，不许私开",
 "便溺粪秽，同蹲同立，顷刻不能相离。",
 "言及舍寺斋僧，便当大板扑死矣。","使秃子收渔人之利，汝父九泉之下能瞑目乎？",
 "兄弟、妯娌相亲相爱，百倍曩时",
 # 猪血有灵
 "火烈爆震罐破，灶两足被汤沃烂","呼阿辰、阿完、阿尾至其家，啖以粥食","复以白米六升给之",
 "面有菜色","何以其面独有红白之色","是日买半斤猪血为羹，以供早膳，留小半杯蘸笔书呈。",
 "余已离任矣","向非血呈之功，何能文移往返数月？","陈兴泰抵掌笑语，以为猪血有灵也。",
 # 第廿五案
 "杀非辜之人命，以保一己之功名，此事岂我为之哉不如削职，入深山读书，仍不失故吾也。",
 "潮阳县亦在旦夕，且祸烈于我百倍。直张目俟之耳。",
 "余以奉参离任，其网漏吞舟与否？则俟后之君子矣。",
 "作者受诬罢官后，将雍正五（１７２７）年任广东潮州府普宁知县、后又兼署潮阳县两年间的审案，选录成书。",
]

QN = [norm(q) for q in QUOTES]

# 1. 每条 QUOTES 必须在库本
for i, qn in enumerate(QN):
    if qn not in NORM_LIB:
        errors.append(f"引文不在库本: {QUOTES[i][:30]}")

# 2. 每条 QUOTES 必须出现在页面 .q 中
missing_page = [QUOTES[i] for i, qn in enumerate(QN) if qn not in page_quotes]
if missing_page:
    errors.append(f"{len(missing_page)} 条引文未在页面 .q 中出现: {[m[:16] for m in missing_page]}")

# 3. 页面 .q 与 QUOTES 逐条对齐（页面不许多出未申报的引文）
extra = [x for x in page_quotes if x not in QN]
if extra:
    errors.append(f"页面有 {len(extra)} 个未申报的 .q 引文: {[e[:18] for e in extra]}")

# 4. 反扫：文本节点中不得出现字面「」（.q 的「」由 CSS 生成，源码中不应存在；剔除 style/script）
page_nt = re.sub(r'<style>.*?</style>', '', page, flags=re.S)
page_nt = re.sub(r'<script>.*?</script>', '', page_nt, flags=re.S)
text_only = re.sub(r'<[^>]+>', '', page_nt)
for mm in re.finditer(r'「([^」]*)」', text_only):
    errors.append(f"字面「」引文须进 .q: {mm.group(1)[:20]}")

# 5. 红线
if '—' in page: errors.append("页面含长划线 —")
if '–' in page: errors.append("页面含短划线 –")
for ln_i, ln in enumerate(page.split('\n'), 1):
    c = ln.count('·')
    if c > 1:
        errors.append(f"第{ln_i}行有 {c} 个·")
    if '—' in ln or '–' in ln:
        pass

# 6. 机数：库本
no_ws = re.sub(r'\s', '', lib)
if len(no_ws) != 122578:
    errors.append(f"库本去空白字数不符: {len(no_ws)}")
qmark = lib.count('？')
if qmark != 686:
    errors.append(f"半角问号数不符: {qmark}")
yi = lib.count('译文')
if yi != 24:
    errors.append(f"译文标记数不符: {yi}")

# 24 回目：目录序与正文序一致，且回目名各 2 见
hs = re.findall(r'第[一二三四五六七八九十]+则\s+(\S+)', lib)
if len(hs) != 48:
    errors.append(f"回目头总数不符: {len(hs)}")
toc, body = hs[:24], hs[24:]
if toc != body:
    errors.append("目录序与正文序不一致")
for name in set(body):
    if lib.count(name) < 2:
        errors.append(f"回目出现不足 2 次: {name}")

# 页面回目墙两列与正文 1..12 / 13..24 对应
wall_html = page[page.find('class="wall"'):page.find('class="sec" id="meizi"')]
wall_names = re.findall(r'<li[^>]*>(?:<a href="#\w+">)?([一-龥]{2,})(?:</a>)?</li>', wall_html)
if len(wall_names) != 24:
    errors.append(f"回目墙条数不符: {len(wall_names)}")
else:
    if wall_names[:12] != body[:12]:
        errors.append(f"回目墙前十二与库本不符: {wall_names[:12]} vs {body[:12]}")
    if wall_names[12:] != body[12:]:
        errors.append(f"回目墙后十二与库本不符: {wall_names[12:]} vs {body[12:]}")

# 7. 页面结构与序号
if '之一百一十四' not in page:
    errors.append("页面缺序号 之一百一十四")
if '<title>蓝公案 · 殆知阁导读之一百一十四</title>' not in page:
    errors.append("title 不符")
for a in ['id="meizi"','id="youhun"','id="sanguan"','id="sigaai"','id="xiongdi"','id="zhuxue"','id="case25"','id="daoren"','id="mulu24"']:
    if a not in page:
        errors.append(f"缺锚点 {a}")
for kw in ['殆知阁简体库','daizhigev20','逐字核验','时代局限']:
    if kw not in page:
        errors.append(f"页脚/正文缺关键词 {kw}")

# 8. .q 总数对账
if len(page_quotes) != len(QUOTES):
    errors.append(f".q 总数不符: 页面 {len(page_quotes)} vs 清单 {len(QUOTES)}")

print(f"库本 126130 字符　去空白 {len(no_ws)}　半角问号 {qmark}　译文段 {yi}")
print(f"回目 24 则　引文清单 {len(QUOTES)} 条　页面 .q {len(page_quotes)} 块")
if warnings:
    print("WARN:", *warnings, sep='\n  ')
if errors:
    print("FAIL:", *errors, sep='\n  ')
    sys.exit(1)
print("ALL PASS")
