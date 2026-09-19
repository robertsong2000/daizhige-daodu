# -*- coding: utf-8 -*-
"""真灵位业图导读页 build + 核验。引文全部由库本锚点切片生成，零誊写。"""
import re, sys, html

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/道藏/正统道藏洞真部/谱箓类/洞玄灵宝真灵位业图.txt'
TPL = 'zhenling-weiye-tu.tpl.html'
OUT = 'zhenling-weiye-tu.html'

raw = open(SRC, encoding='utf-8').read()

Q = {
 'qtitle': ('洞玄灵宝真灵位业图', '洞玄灵宝真灵位业图'),
 'qxu1': ('夫仰镜玄精，说景耀之巨细；俯眄平区，见岩海之崇深。搜访人纲，究朝斑之品序；研综天经，测真灵之阶业。', '测真灵之阶业'),
 'qxu3': ('辄以浅识下生，轻品上圣，升降失序，梯级乖本，戄贻谪玄府，络咎冥司。', '络咎冥司'),
 'qxu4': ('虽同号真人，真品乃有数，俱目仙人，仙亦有等级千亿。', '仙亦有等级千亿'),
 'qxu5': ('犹如野夫出朝廷，见朱衣令史，句骊入中国，呼一切为参军。岂解士庶之贵贱，辩爵号异同乎。', '辩爵号异同乎'),
 'q1a': ('上合虚皇道君应号元始天尊。', '上合虚皇道君应号元始天尊。'),
 'q1b1': ('东明高上虚皇道君。', '东明高上虚皇道君。'),
 'q1b2': ('西华高上虚皇道君。', '西华高上虚皇道君。'),
 'q1b3': ('北玄高上虚皇道君。', '北玄高上虚皇道君。'),
 'q1b4': ('南朱高上虚皇道君。', '南朱高上虚皇道君。'),
 'q1c1': ('玉皇道君。', '玉皇道君。'),
 'q1c2': ('高上玉帝。', '高上玉帝。'),
 'q1c3': ('上皇天帝。', '上皇天帝。'),
 'q1d': ('右玉清境，元始天尊为主，已下道君', '并不与下界相关'),
 'q2a': ('上清高圣太上玉晨玄皇大道君。', '为万道之主。'),
 'q2l': ('左圣南极南岳真人左仙公太虚真人赤松子。黄老君弟子，裴君师。', '裴君师。'),
 'q2b': ('司命东岳上真卿太元真人茅君。大茅君，讳盈，字叔申。', '字叔申。'),
 'q2c': ('左卿仙侯真君许君。讳穆，南岳夫人弟子，事晋为护军长史，退居句曲山。', '退居句曲山。'),
 'q2d': ('侍帝晨东华上佐司命杨君。', '侍帝晨东华上佐司命杨君。'),
 'q2e': ('清灵真人裴君。汉右扶风人，汉时得道。', '汉时得道。'),
 'q2f': ('右辅小有洞天太素清虚真人四司三元右保公王君。讳褒，魏夫人师，下教矣。', '下教矣。'),
 'q2k': ('侍帝晨右仙公许君。长史子，讳翙。', '讳翙。'),
 'q2w': ('紫虚元君领上真司命南岳魏夫人。讳华存，字贤安，小有王君弟子，杨君师。', '杨君师。'),
 'q2h': ('紫清上宫九华真妃。姓安，晋朝降于茅山。', '晋朝降于茅山。'),
 'q2i': ('董双成。', '董双成。'),
 'q2j': ('西王母侍女王上华。', '西王母侍女王上华。'),
 'q3n': ('右圣金阙帝晨后圣玄元道君。壬辰运当　下生。', '下生。'),
 'q3a': ('太极金阙帝君姓李。壬辰下教，太平主。', '太平主。'),
 'q3b': ('太极上真公孔丘。', '明晨侍郎三天司真颜回。'),
 'q3c': ('玄圃真人轩辕黄帝。', '受灵宝五符。'),
 'q3d': ('帝舜。服九转神丹，入于九疑山，而得道矣。', '而得道矣。'),
 'q3e': ('夏禹。', '见西王母。'),
 'q3o': ('帝尧。', '帝尧。'),
 'q3h': ('无上真人文始先生尹喜。', '无上真人文始先生尹喜。'),
 'q3i': ('北极真人安期生。', '北极真人安期生。'),
 'q3j': ('太极左仙公葛玄。吴时下演灵宝，下为地仙。', '下为地仙。'),
 'q3p': ('萧史。', '萧史。'),
 'q3q': ('弄玉。', '弄玉。'),
 'q3k': ('韦编郎庄周。', '秦佚。'),
 'q3g': ('司马季主。受西灵子都剑解之道。', '剑解之道。'),
 'q4a': ('太清太上老君。为太清道主，下临万民。', '下临万民。'),
 'q4b': ('正一真人三天法师张讳道陵。', '正一真人三天法师张讳道陵。'),
 'q4c': ('五岳君。五百年而一替。', '五百年而一替。'),
 'q4c2': ('河伯。此三条，是得道之人所补。', '是得道之人所补。'),
 'q4d': ('高上将军。', '号四将军。'),
 'q4g': ('此并太清三天东宫之真官，章奏关启学道所得。', '章奏关启学道所得。'),
 'q4f': ('元始天王。西王母之师。', '西王母之师。'),
 'q4h': ('张子房。', '张子房。'),
 'q4i': ('东方朔。', '马明生。'),
 'q4j': ('墨翟。宋大水解。', '墨翟。宋大水解。'),
 'q4k': ('彭铿。西入流沙。', '彭铿。西入流沙。'),
 'q4e': ('葛洪。隐罗浮山。', '葛洪。隐罗浮山。'),
 'q5a': ('九宫尚书。姓张，名奉，字公先，河内人。', '河内人'),
 'q5b': ('右保召公奭。从罗南明公受此位。', '从罗南明公受此位。'),
 'q6a': ('右禁郎定录真君中茅君。治华阳洞天。', '治华阳洞天。'),
 'q6c': ('施存。一号婉盆子。孔子弟子三千人，数得道。', '数得道。'),
 'q6d': ('葛玄。字孝先，丹阳句曲人，稚川之从祖也。初在长山，乘虎使鬼，无处不至，位在太极宫。', '位在太极宫。'),
 'q6g': ('许迈。字叔玄，小名映，改名远游，东华为地仙矣。', '东华为地仙矣。'),
 'q6f': ('扁鹊弟子五人：', '子游。'),
 'q6i': ('鲍靓。南海太守。', '南海太守。'),
 'q6b': ('易迁宫。八十三人。', '并女真。'),
 'q6e': ('许肇。先在罗酆都，为东明公右司晨。', '为东明公右司晨。'),
 'q6e2': ('许肇。已度九宫位矣。', '已度九宫位矣。'),
 'q7a': ('酆都北阴大帝。炎帝大庭氏，讳履甲，天下鬼神之宗，治罗酆山，三千年而一替。', '三千年而一替。'),
 'q7b1': ('北帝上相秦始皇。', '北帝上相秦始皇。'),
 'q7b2': ('北帝太傅魏武帝。', '北帝太傅魏武帝。'),
 'q7c': ('西明公领北帝师周文王。比少傅。', '比少傅。'),
 'q7d1': ('鬼官北斗君周武王。治一天宫。', '治一天宫。'),
 'q7d2': ('三官都禁郎齐桓公。姓姜，名小白。', '姓姜，名小白。'),
 'q7d3': ('水官司命晋文公。姓姬，名重耳。', '姓姬，名重耳。'),
 'q7e': ('大禁晨二人，位比尚书令。', '大禁晨二人，位比尚书令。'),
 'q7f': ('汉光武帝。孙文台。名坚。', '名坚。'),
 'q7l': ('宾友荀或。字文若，魏武谋臣，汉尚书令。', '汉尚书令。'),
 'q7t': ('宾友汉高祖。', '宾友汉高祖。'),
 'q7u': ('宾友孙策。', '宾友孙策。'),
 'q7g1': ('北帝侍晨八人，位比侍中。', '北帝侍晨八人，位比侍中。'),
 'q7g2': ('徐庶。字文直。庞德。字令明。', '字令明。'),
 'q7h1': ('刘备。字玄德。', '刘备。字玄德。'),
 'q7k': ('郭嘉。', '备养子。'),
 'q7m': ('李广。汉将。', '李广。汉将。'),
 'q7o': ('主非使者严白虎。吴时人，为孙策所杀。', '为孙策所杀。'),
 'q7i': ('右号为四镇，各领鬼兵万人，各有长马，复有小镇数百，各领鬼兵数千人。', '鬼兵数千人'),
 'q7n': ('西河侯陶侃。字士行，亦领兵数千。', '亦领兵数千。'),
 'q7p': ('监海伯治东海温太真。位比大将军。', '位比大将军。'),
 'q7s': ('北帝南门亭长二人：', '代郄鉴。'),
 'q7r': ('西门郎十六人。未显。主天下房庙血食之鬼，亦应隶四明公。', '亦应隶四明公。'),
 'q7q': ('杀鬼地映日游。三鬼，北帝常使杀人，无姓名。', '无姓名。'),
 'q7j': ('右鬼官，见有七十五职，名显者凡一百一十九人。', '名显者凡一百一十九人。'),
 'qend1': ('虽同号真人，真品乃有数', '真品乃有数'),
 'qend2': ('俱目仙人，仙亦有等级千亿', '仙亦有等级千亿'),
}
PUNCT = re.compile('[\\s\u3000\u201c\u201d\u2018\u2019\u300c\u300d\u300e\u300f\uff08\uff09()\\[\\]\u3010\u3011,\uff0c.\u3002;\uff1a?\uff01!\u3001\u00b7\u300a\u300b\u3008\u3009\u0022\u0027\u2026]+')
def norm(s):
    return PUNCT.sub('', s)

src_n = norm(raw)
quotes = {}
for k, (a, b) in Q.items():
    if not a.endswith(b) and a.endswith(b + '。'):
        b = b + '。'
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
    val = '<q data-k="' + k + '">' + html.escape(re.sub(r'\s+', '', frag)) + '</q>'
    page = page.replace(pat, val)
left = re.findall(r'%Q:[a-z0-9]+%', page)
assert not left, 'unreplaced tokens: %s' % left
open(OUT, 'w', encoding='utf-8').write(page)

# ---------- checks ----------
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.qtexts = []
        self.qdepth = 0
        self.cur_q = None
        self.visible = []
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
for qt in p.qtexts:
    if norm(qt) not in src_n:
        fails.append('q not in src: ' + qt[:30])
vis = norm(''.join(p.visible))
windows = {src_n[i:i+6] for i in range(len(src_n) - 5)}
hits = [vis[i:i+6] for i in range(len(vis) - 5) if vis[i:i+6] in windows]
if hits:
    fails.append('white-text collisions: ' + ' | '.join(sorted(set(hits))[:12]))
if '—' in page or '–' in page:
    fails.append('forbidden dash found')
for seg in p.visible + p.qtexts:
    for ln in seg.split('\n'):
        if ln.count('·') > 1:
            fails.append('multi · line: ' + ln[:40])
if len(p.qtexts) < 30:
    fails.append('q count low: %d' % len(p.qtexts))

print('q count:', len(p.qtexts))
print('visible chars:', len(vis))
if fails:
    print('CHECK FAILED:')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
