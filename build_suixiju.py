# -*- coding: utf-8 -*-
"""随息居饮食谱导读页 build + 核验。引文全部由库本锚点切片生成，零誊写。"""
import re, sys, html

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/饮馔/随息居饮食谱.txt'
TPL = 'suixiju-yinshipu.tpl.html'
OUT = 'suixiju-yinshipu.html'

raw = open(SRC, encoding='utf-8').read()

Q = {
 'x1': ('今夏，石米八千，斤朱四十', '茫茫浩劫，呼吁无门'),
 'x2': ('无事可为，无路可走', '悠悠长夜，枵腹无聊'),
 'x3': ('丐得枯道人秃笔一枝', '题曰《饮食谱》'),
 'x4': ('咸丰十一年辛酉秋七月睡乡散人书于随息居', '咸丰十一年辛酉秋七月睡乡散人书于随息居'),
 'h1': ('士雄年十四失怙', '厨无宿舂'),
 'h2': ('赠余斋名曰', '勿以内顾为忧'),
 'h3': ('遂自号半痴', '遂自号半痴'),
 'h4': ('乙卯冬，携眷回籍', '堂名归砚'),
 'h5': ('讵上年春，省垣失事', '幸缒城归'),
 'h6': ('今旅濮院，麸核充饥', '今旅濮院，麸核充饥'),
 'h7': ('我生不辰，兔爰兴叹', '我生不辰，兔爰兴叹'),
 'h7b': ('因易字曰梦隐', '因易字曰梦隐'),
 'h8': ('而后路茫茫，惟有不忘沟壑耳', '而后路茫茫，惟有不忘沟壑耳'),
 'h9': ('知味者鲜，且藏稿以俟之', '知味者鲜，且藏稿以俟之'),
 'b1': ('辛酉八月中旬随息子又题', '辛酉八月中旬随息子又题'),
 'g1': ('并绞汁服，名天生甘露饮', '并绞汁服，名天生甘露饮'),
 'g2': ('一名天生白虎汤', '一名天生白虎汤'),
 'g3': ('榨浆名天生复脉汤', '榨浆名天生复脉汤'),
 'd1': ('温疫、热狂', '勿药可瘳'),
 'd2': ('清下焦之热，煮饭补阴中之阳', '清下焦之热，煮饭补阴中之阳'),
 'd3': ('中煤炭毒，灌之即苏', '中煤炭毒，灌之即苏'),
 'l1': ('凡人饮食，盖有三化', '三曰胃化，蒸变传运'),
 'l2': ('用得其宜，远胜诸药', '用得其宜，远胜诸药'),
 'm1': ('至病人、产妇，粥养最宜', '而较糯不黏也'),
 'm2': ('煮粥时，稍加入之，香美异常，尤能醒胃', '煮粥时，稍加入之，香美异常，尤能醒胃'),
 'm3': ('凡煮粥宜用井泉水', '凡煮粥宜用井泉水'),
 'f1': ('贫窭之家', '蔬中圣品也'),
 'f2': ('处处能造，贫富倏宜', '广大教主也'),
 'f3': ('冬月冻透者味尤美', '冬月冻透者味尤美'),
 't1': ('别有一种水蜜桃，熟时吸食，味如甘露', '洵是仙桃'),
 'o1': ('果中蜜品，久食休粮', '果中蜜品，久食休粮'),
 'j1': ('将壳击碎，再入瓷罐内，多加粗茶叶，同煨三日', '不甚闭滞也'),
 'e1': ('暖胃生津，性与葛根相似', '月必一食也'),
 'y1': ('初则富贵人吸之', '而盗贼满天下'),
 'y2': ('以口腹之欲，致毒流宇内，涂炭生民，洵妖物也，智者远之', '以口腹之欲，致毒流宇内，涂炭生民，洵妖物也，智者远之'),
 'y3': ('人不知其为劫剂，遂诧以为神丹', '人不知其为劫剂，遂诧以为神丹'),
 'y4': ('欲罢不能，噬脐莫及，乃致速死', '毋蹈覆辙'),
 'db': ('不料其为鸦片烟之先兆也', '不料其为鸦片烟之先兆也'),
 'n1': ('解鸦片毒，生南瓜捣汁频灌', '永无后患'),
}
PUNCT = re.compile("[\\s\u3000\u201c\u201d\u2018\u2019\u300c\u300d\u300e\u300f\uff08\uff09()\\[\\]\u3010\u3011,\uff0c.\u3002;\uff1a?\uff01!\u3001\u00b7\u300a\u300b\u3008\u3009\u0022\u0027\u2026\uff1b:\u25a1\ufe41]+|[\ue000-\uf8ff]")
def norm(s):
    return PUNCT.sub('', s)

src_n = norm(raw)
quotes = {}
for k, (a, b) in Q.items():
    i = raw.find(a)
    assert i >= 0, 'start anchor missing: ' + k
    if a == b:
        frag = raw[i:i + len(a)]
    else:
        j = raw.find(b, i + len(a))
        assert j >= 0, 'end anchor missing: ' + k
        frag = raw[i:j + len(b)]
    assert norm(frag) in src_n, 'slice broken: ' + k
    quotes[k] = frag

PUA = re.compile("[\ue000-\uf8ff]")
def disp(s):
    return PUA.sub('□', s)

tpl = open(TPL, encoding='utf-8').read()
page = tpl
for k, frag in quotes.items():
    pat = '%%Q:' + k + '%%'
    assert ('<q data-k="' + k + '">' + pat + '</q>') in tpl, 'token not wrapped in q: ' + k
    page = page.replace(pat, html.escape(disp(frag)))
left = re.findall(r'%Q:[a-z0-9]+%', page)
assert not left, 'unreplaced tokens: %s' % left
open(OUT, 'w', encoding='utf-8').write(page)

# ---------- checks ----------
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skipctx = []
        self.qtexts = []
        self.qdepth = 0
        self.cur_q = None
        self.nodes = []
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
            self.nodes.append(data)

p = P(); p.feed(page)

fails = []
for qt in p.qtexts:
    if norm(qt) not in src_n:
        fails.append('q not in src: ' + qt[:30])
windows = {src_n[i:i+6] for i in range(len(src_n) - 5)}
WHITELIST = {'随息居饮食谱'}   # 书名自指
hits = []
for node in p.nodes:
    nv = norm(node)
    for i in range(len(nv) - 5):
        w = nv[i:i+6]
        if w in windows and w not in WHITELIST:
            hits.append(w)
if hits:
    fails.append('white-text collisions: ' + ' | '.join(sorted(set(hits))[:12]))
if '—' in page or '–' in page:
    fails.append('forbidden dash found')
for seg in p.nodes + p.qtexts:
    for ln in seg.split('\n'):
        if ln.count('·') > 1:
            fails.append('multi interpunct line: ' + ln[:40])
if len(p.qtexts) < 30:
    fails.append('q count low: %d' % len(p.qtexts))

print('q count:', len(p.qtexts))
if fails:
    print('CHECK FAILED:')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
