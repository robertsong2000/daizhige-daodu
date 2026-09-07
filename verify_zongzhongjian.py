#!/usr/bin/env python3
# 宗忠简集 页面核验：引文双侧逐字（库本命中+页面反扫）+ 库本机数 + 排版红线
import re, sys
from html.parser import HTMLParser

PAGE = 'zongzhongjian-ji.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/宗忠简集.txt'

page = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()

errs = []
def chk(cond, msg):
    if not cond: errs.append(msg)

def norm(s):
    out = []
    for ch in s:
        if ch.isspace(): continue
        o = ord(ch)
        if (0x3000 <= o <= 0x303F) or (0xFF00 <= o <= 0xFFEF and not (0xFF21 <= o <= 0xFF5A)) \
           or ch in '「」『』“”‘’·，。、；：？！〈〉《》()(){}[]<>' or (o < 0x2E80 and not ch.isalnum()) \
           or (0x2018 <= o <= 0x201F):
            continue
        out.append(ch)
    return ''.join(out)

libn = norm(lib)

class TP(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buf = []
    def handle_data(self, d):
        self.buf.append(d)
tp = TP(); tp.feed(page)
text = ''.join(tp.buf)
pagen = norm(text)

# ---------- 库本机数 ----------
libnw = re.sub(r'\s', '', lib)
chk(len(libnw) == 60911, f'库本去空白字符 {len(libnw)} != 60911')
for v in ['巻一','巻二','巻三','巻四','巻五','巻六','巻七','巻八']:
    chk(libnw.count('宗忠简集' + v) == 2, f'库本「{v}」头 {libnw.count("宗忠简集"+v)} != 2')
for w, n in [('乞回銮',23),('系第',24),('奏请',27),('过河',12),('髙宗',32),('汪黄',7),
             ('闻车驾将还阙贺表',1),('闻车驾议还阙贺表',1)]:
    c = libnw.count(w)
    chk(c == n, f'库本「{w}」{c}见 != {n}见')
chk(libnw.count('乞回銮疏【') == 15, f'乞回銮疏目 {libnw.count("乞回銮疏【")} != 15')
chk(libnw.count('乞回銮表【') == 4, f'乞回銮表目 {libnw.count("乞回銮表【")} != 4')
chk('系第九次' in libnw and '系第十次' in libnw, '贺表第九第十次标记不在库本')
chk('连呼过河者三' in libnw and '无一语及家事' in libnw, '临终句不在库本')

# ---------- 期望引文清单（库本命中 + 页面在场，双侧）----------
EXPECTED = [
 '泽孤忠耿耿，精贯三光，其奏劄规画时势详明恳切',
 '是编自一巻至六巻皆劄子状疏诗文襍体，七巻八巻为遗事附录',
 '偶阅宗泽忠简集，爱其乞回銮诸疏，不忍释手。既终卷，乃知章凡二十四上，而髙宗漠然也。',
 '读其疏者未尝不嘉其血诚、赏其卓识、叹其孤忠',
 '三代之得天下也，得其民也。得其民有道：得其心也。得其心有道：所欲与之聚之，所恶勿施尔也',
 '陛下何不认我宗庙乎？何不眷顾我朝廷乎？',
 '臣犬马之年巳七十矣，陛下不以臣衰老无用，付之东京留钥。',
 '都城贴然，风物如旧，人人延颈跂踵，日夜徯望圣驾还阙',
 '既过河，则山寨忠义之民相应者不啻百万',
 '统押人马自游家渡过河，会约河西忠义统制等，商议随宜措画',
 '极力保护河梁，以俟大兵过河，毋致临期误事',
 '恭闻明命，肃诏回銮，欢腾率土之谣，和浃中天之气，里闾喜悦，如婴孺之将见慈亲，道路光辉，若翳霾而忽曕白日',
 '强敌长驱，京邑阽危，此忠臣义士痛心疾首、勤王报国之秋也。而宰臣迁家，郡守逾垣，缙绅士大夫陆窜水奔，使人主婴孤城以自守，无一犯难者。',
 '世道之衰，一至此乎！太息之余，以诗自道。',
 '连呼过河者三，无一语及家事。',
 '吾度不起此疾。古云：出师未防身先死，长使英雄泪满襟。',
 '狃于和议，不用其言，亦竟无收拾其文者',
 '至宁宗嘉定间，四明楼昉乃缀辑散佚，以成是集',
 '中兴之业实始基焉，宗公力也',
 '乃汪黄谬计，非公本谋也',
 '考史称泽力请高宗还汴疏凡二十余上，本传不尽录其文，今集中所载仅十八篇，犹佚其十',
 '遣少尹范世延机幕宗颕诣维扬奏请回銮疏',
 '奏乞回銮仍以六月进兵渡河疏',
 '营缮楼橹城壁，扫除宫禁阙廷',
]

print(f'申报引文 {len(EXPECTED)} 段')
for s in EXPECTED:
    sn = norm(s)
    chk(sn in libn, f'库本未命中: {s[:18]}...')
for s in EXPECTED:
    sn = norm(s)
    chk(sn in pagen, f'页面缺失: {s[:18]}...')

# ---------- 反扫：申报之外无库本成句（>=12 汉字连续）复用 ----------
resid = pagen
for s in EXPECTED:
    resid = resid.replace(norm(s), '■')
han = re.compile(r'[㐀-鿿]{12,}')
for m in han.finditer(resid):
    frag = m.group()
    if frag in libn:
        errs.append(f'申报外复用库本成句: {frag[:40]}')

# ---------- 排版红线 ----------
for ch, name in [('—','—(em dash)'), ('–','–(en dash)'), ('‒','figure dash'), ('―','horizontal bar')]:
    cnt = text.count(ch) + page.count(ch)
    chk(cnt == 0, f'禁用字符 {name} 出现 {cnt} 次')
bad = [ln for ln in text.splitlines() if ln.count('·') > 1]
chk(not bad, f'{len(bad)} 行 · 超过 1 个: {bad[:3]}')
for kw in ['殆知阁古代文献', '逐字核验', '时代局限', 'mulu.html']:
    chk(kw in text, f'页脚缺「{kw}」')

# ---------- 报告 ----------
if errs:
    print(f'\nFAIL ({len(errs)}):')
    for e in errs: print(' ', e)
    sys.exit(1)
print(f'PASS: 引文{len(EXPECTED)}段双侧命中；库本60911字/八卷头/乞回銮系列计数断言通过；无申报外复用；红线(禁长划线/·每行≤1/页脚)通过')
