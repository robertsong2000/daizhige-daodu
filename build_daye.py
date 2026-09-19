# -*- coding: utf-8 -*-
"""大业杂记导读页 build + 核验。引文全部由库本锚点切片生成，零誊写。"""
import re, sys, html

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/大业杂记.txt'
TPL = 'daye-zaji.tpl.html'
OUT = 'daye-zaji.html'

raw = open(SRC, encoding='utf-8').read()

Q = {
 'c1': ('术人章仇太翼表奏云', '此其验也'),
 'c2': ('帝览表，怆然有迁都之意', '改洛州为豫州'),
 'c3': ('发河南道诸州郡兵夫五十馀万', '通龙舟'),
 'c4': ('自东都至江都二千余里，树荫相交', '自京师至江都离宫四十余所'),
 'c5': ('东都大城，周回七十三里一百五十步', '北逾谷水'),
 'c6': ('城南东西各两重，北三重，南临洛水，开大道，对端门，名端门街，一名天津街。阔一百步，道傍植樱桃石榴两行', '道傍植樱桃石榴两行'),
 'c7': ('端门即宫南正门', '正当龙门'),
 'c8': ('有天津浮桥，跨水长一百三十步', '各高百余尺'),
 'c9': ('其龙舟，高四十五尺', '朱丝网络'),
 'c10': ('其引船人普名', '分为三番'),
 'c11': ('每一番引舟有三百六十人', '少壮者为之'),
 'c12': ('皇后御次水殿，名翔螭舟', '殿脚有九百人'),
 'c13': ('发洛口部五十日乃尽，舳舻相继二百余里', '二十余万'),
 'c14': ('于时天下丰乐，虽此差科，未足为苦', '未足为苦'),
 'c15': ('元年夏五月，筑西苑，周二百里', '屈曲绕龙鳞渠'),
 'c16': ('庭植名花，秋冬即剪杂彩为之', '剪采为芰荷'),
 'c17': ('风亭月观，皆以机成', '若有神变'),
 'c18': ('苑内造山为海', '山高出水百余尺'),
 'c19': ('每秋八月，月明之夜', '入西苑，歌管'),
 'c20': ('一日之内，嶷然峙立', '以为神异'),
 'c21': ('见两童子衣赤，两童子衣青', '为龙之所藏隐'),
 'c22': ('忽有大鱼，似鲤有角', '亦唐兴之兆'),
 'c23': ('改吴床为交床、胡瓜为白路黄瓜', '昆仑紫瓜'),
 'c24': ('造五色饮，以扶芳叶为青饮', '为黄饮'),
 'c25': ('周八里，通门十二，其内一百二十行，三千余肆', '三千余肆'),
 'c26': ('市四壁有四百余店，重楼延阁，互相临映，招致商旅，珍奇山积', '珍奇山积'),
 'c27': ('十二月，敕开江南河', '欲东巡会稽'),
 'c28': ('布兵夫周币四面有七十万人', '六十日成'),
 'c29': ('常役八十余万人', '八十余万人'),
}
PUNCT = re.compile('[\\s\u3000\u201c\u201d\u2018\u2019\u300c\u300d\u300e\u300f\uff08\uff09()\[\]\u3010\u3011,\uff0c.\u3002;\uff1a?\uff01!\u3001\u00b7\u300a\u300b\u3008\u3009\u0022\u0027\u2026\uE000-\uF8FF\u25a0]+')
def norm(s):
    return PUNCT.sub('', s)

src_n = norm(raw)
quotes = {}
for k, (a, b) in Q.items():
    i = raw.find(a)
    assert i >= 0, 'start anchor missing: ' + k
    if a.endswith(b):
        frag = raw[i:i + len(a)]
    else:
        j = raw.find(b, i + len(a))
        assert j >= 0, 'end anchor missing: ' + k
        frag = raw[i:j + len(b)]
    assert norm(frag) in src_n, 'slice broken: ' + k
    quotes[k] = frag

tpl = open(TPL, encoding='utf-8').read()
page = tpl
for k, frag in quotes.items():
    pat = '%%Q:' + k + '%%'
    val = '<q data-k="' + k + '">' + html.escape(frag) + '</q>'
    page = page.replace(pat, val)
left = re.findall(r'%Q:[a-z0-9]+%', page)
assert not left, 'unreplaced tokens: %s' % left
open(OUT, 'w', encoding='utf-8').write(page)

# ---------- checks ----------
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, skip) skip=True when inside script/style or q
        self.qtexts = []
        self.qdepth = 0
        self.cur_q = None
        self.visible = []        # (context, text) outside q/script/style
        self.skipctx = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skipctx.append(tag)
        elif tag == 'q':
            self.qdepth += 1
            self.cur_q = [] if self.qdepth == 1 else self.cur_q
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skipctx:
            self.skipctx.pop()
        elif tag == 'q' and self.qdepth:
            self.qdepth -= 1
            if self.qdepth == 0:
                self.qtexts.append(''.join(self.cur_q))
                self.cur_q = None
    def handle_data(self, data):
        if self.skipctx:
            return
        if self.qdepth:
            self.cur_q.append(data)
        else:
            self.visible.append(data)

p = P(); p.feed(page)

fails = []
# a) q verbatim
for qt in p.qtexts:
    if norm(qt) not in src_n:
        fails.append('q not in src: ' + qt[:30])
# b) visible text six-window scan
vis = norm(''.join(p.visible))
windows = {src_n[i:i+6] for i in range(len(src_n) - 5)}
hits = [vis[i:i+6] for i in range(len(vis) - 5) if vis[i:i+6] in windows]
if hits:
    fails.append('white-text collisions: ' + ' | '.join(sorted(set(hits))[:12]))
# c) forbidden dashes anywhere
if '—' in page or '–' in page:
    fails.append('forbidden dash found')
# d) interpunct per rendered line
for seg in p.visible + p.qtexts:
    for ln in seg.split('\n'):
        if ln.count('·') > 1:
            fails.append('multi · line: ' + ln[:40])
# e) q count
if len(p.qtexts) < 25:
    fails.append('q count low: %d' % len(p.qtexts))

print('q count:', len(p.qtexts))
print('visible chars:', len(vis))
if fails:
    print('CHECK FAILED:')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
