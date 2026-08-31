# -*- coding: utf-8 -*-
"""忠介烬余集 导读页核验：引文双侧、「」反扫、红线、机数。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'zhongjie-jinyuji.html'
LIB  = '../daizhige-simplified/集藏/四库别集/忠介烬余集.txt'
NO   = '之一百一二十一'   # commit 前定号后与页面同步 sed

lib  = open(LIB, encoding='utf8').read()
page = open(PAGE, encoding='utf8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

NL, NP = norm(lib), norm(page)
fails = []
def chk(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

# ---------- 1. 收集 .q（栈配平，VOID 跳过；.src 预剥离防污染） ----------
page_q = re.sub(r'<span class="src">[^<]*</span>', '', page)
VOID = {'meta','link','br','hr','img','input','source','wbr','area','base','col','embed','track'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.qstack, self.cur, self.out = [], [], None, []
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        cls = dict(attrs).get('class') or ''
        qs = 'q' in cls.split()
        self.stack.append(tag)
        if self.cur is not None:
            self.qstack.append(self.cur)
        elif qs:
            self.cur = []
            self.qstack.append(self.cur)
        elif self.qstack:
            self.cur = self.qstack[-1]
    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if self.qstack:
            ended = self.cur is self.qstack[-1]
            self.qstack.pop()
            if ended:
                self.out.append(''.join(self.cur))
                self.cur = self.qstack[-1] if self.qstack else None
    def handle_data(self, d):
        if self.cur is not None:
            self.cur.append(d)

qc = QC(); qc.feed(page_q)
collected = [norm(x) for x in qc.out if norm(x)]
print(f'[收集] .q 共 {len(qc.out)} 块，归一后非空 {len(collected)} 块')

# ---------- 2. 期望引文清单：双侧断言 ----------
QUOTES = [
 "仓卒间为友人投火灭迹",
 "吏曰：内监监税兹土十有六载，院藩臬府及县暨诸董戎事者，畴弗与交欢？何独绝之？",
 "余大笑抗声曰：余始至，若弗余知，以余为何如人？竟弗往。",
 "于四月十四日薄暮，闻诸行户踵监门哀鸣求直，监诱入阖门尽絷之，百端鱼肉。赴援者蚁聚于外，发箭挥刀，被髪流血者皆是也。",
 "税监恐惧，身登峻阁，火箭雨集，烈焰耀天，悲声动地。",
 "然民庐化作飞灰，已三十余家。",
 "余开而读之，不觉奋衣振起，举茶瓯掷地，曰：异哉！",
 "处变之道有三：销变于未变为最，应变于临变而得正者，上也。",
 "独坐静思，长安花不如故园柳。三百五十人中，未知肝胆谁是。",
 "月中分兵部观政，殊无政可观，不过作揖打恭、升堂画卯而已。天下事之虚文相蒙者，多类是。",
 "当知银子取不尽，好官做不尽。去角予齿，两足添翼，造物自有定数，安用营营为哉？",
 "幸叨一第，不敢云报国。固穷二字，原吾軰本来面目。并此而丧，何以自立？",
 "负诸亲友尚有还日，取诸民间必无还期。",
 "弟尝思：古人惟判一死字，便做出许多大事业，压倒一世；今人惟爱一官字，便露出许多头面，压倒一世。今古之不相及，大槩如此。",
 "彼独以白须挺立冡宰前，了无退避，无不拊掌。",
 "勿谓燕市中无荆卿、髙渐离也。",
 "朝事至此，真汉唐宋未有之党祸也。吾軰一身不足计，惟目睹六君子之惨毒，直使人肝肠摧裂。",
 "弟索于堂上，尽付烈焰。",
 "弟行只在此两日内矣。一生向志节一路着力，是弟不济处，故出门便与宦官作仇，毕竟以此軰结局，然不可谓非天之所以成我也。",
 "弟自十六日入县署中，一腔愤泪、万种爱縁，俱化作铁肠石心矣。",
 "只是昨朝之变，意外理外，今进退两难耳。",
 "大丈夫猛拚一死，何事不可做？末后一着，定当俊伟。",
 "如此风波，合城无不惊怖，弟作一欢喜顺受想，空空坦坦，正觉快活。临时事尚当竖起脊梁，作一个生铁铸就底人，以不负知己。",
 "二鼓登舟，旌旗戈戟相望于道，周生此行亦可谓不落莫矣。",
 "朝夕与虎狼为伍，亦觉无入不自得也。呵呵。",
 "原拟以长儿托年兄覆庇，细思有殴杀缇骑之变，中途正色遣归，不敢违命而返，又恐增一累耳。",
 "四月朔日渡江，一路风光尽觉自在。自邮夫贩客、妇女儿童，无不攀车垂涕者，即焦头烂额軰如狼如虎，亦皆感恩而泣。",
 "弟忽罹此，所谓雷霆雨露，均属圣恩，在臣子只应欢喜顺受。臣罪当诛兮，天王圣明，古人之言，殆非欺我也。",
 "丙寅三月十五日余被逮。越宿，朱徳升、朱完天、邹虚王、殷汝劼同卧县署，相对谈笑。虚王、汝劼各出素扇索书，遂录壬戌南还留别文起、孟长之作。嗟乎，在今日又增一罪案矣。",
 "客途无复附书频，此夕衔杯怆别辰。明月一天遥寄影，雄文千古尔疑神。",
 "抗手悲歌出帝都，几行愤泪洒征途。中朝豺虎方盈阙，东土烽烟又逼吴。",
 "听鸣笛之忼慨兮，妙声绝而复寻。余毎读之，未尝不沾襟，遂题是集曰寻声谱。",
 "玉壶以为可忆，搔首展眉，逾刻遂全，是大竒事。锺元曰：鬼神通之也。亟索笔录之。",
 "闻道奚囊投烈焰，记来只字抵千金。",
 "一到都门岁几更，天南天北不胜情。秦闗戎马闻时急，闽海风涛见欲惊。",
 "相思盈抱向谁开，回首衡阳雁不来。三十功名淹海国，百年心事吊荒台。",
 "喜从玉壶记忆得周忠介旧寄二诗赋此",
 "国朝康熙间，竒逢门人汤斌巡抚江苏，以谱贻靖，附刻集后。",
 "以忤魏忠贤为所罗织，逮治拷掠，杀之于狱。崇祯初追谥忠介，事迹具明史本传。",
 "观区区题扇一诗，异代且珍重传之，则是集什一仅存，固未可聴其湮没矣。",
]
for i, q in enumerate(QUOTES):
    n = norm(q)
    inlib = n in NL
    inpage = any(n in c or c in n for c in collected) and any(n == c for c in collected) or any(n in c for c in collected)
    chk(inlib, f'引文{i:02d} 在库内：{q[:22]}…')
    chk(inpage, f'引文{i:02d} 在页面.q：{q[:22]}…')

# 每个收集块都必须能在库内找到（防拼引）
for j, c in enumerate(collected):
    chk(c in NL, f'收集块{j:02d} 逐字命中库内（{len(c)}字）')
chk(all(not (norm(q) not in NL) for q in QUOTES), '期望清单无一脱库')

# ---------- 3. 「」反扫（剥 style/script 后） ----------
body = re.sub(r'<style>.*?</style>', '', page, flags=re.S)
body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)
for m in re.finditer(r'「([^」]*)」', body):
    n = norm(m.group(1))
    if n:
        chk(n in NL, f'「」反扫：{m.group(1)[:18]}')

# ---------- 4. 排版红线 ----------
chk('—' not in page, '无长划线 —')
chk('–' not in page, '无短划线 –')
for ln_no, ln in enumerate(page.split('\n'), 1):
    if '·' in ln:
        c = ln.count('·')
        chk(c <= 1, f'第{ln_no}行 · 数 {c} ≤ 1')

# ---------- 5. 机数 ----------
ns = ''.join(ch for ch in lib if not ch.isspace())
cn = sum(1 for ch in lib if 0x3400 <= ord(ch) <= 0x9FFF or 0x20000 <= ord(ch) <= 0x3FFFF)
chk(len(lib) == 16753, f'库本 raw {len(lib)} == 16753')
chk(len(ns) == 15938, f'去空白 {len(ns)} == 15938')
chk(cn == 15899, f'汉字 {cn} == 15899')
chk('一万五千八百九十九' in page, '页内汉字总数口径')

# 卷界
i2 = lib.find('忠介烬余集巻二', 4000)
i3 = lib.find('忠介烬余集巻三', 10000)
seg2 = lib[i2:i3]
seg3 = lib[i3:]

def titles(seg):
    out = []
    for ln in seg.split('\n'):
        s = ln.strip()
        if s and not s.startswith('　') and not s.startswith('●') and len(s) < 30:
            out.append(s)
    return out

t2 = [x for x in titles(seg2) if x not in ('忠介烬余集巻二', '（明）周顺昌 撰', '忠介烬余集卷二')]
chk(len(t2) == 25, f'卷二尺牍 {len(t2)} == 25')
chk(sum(1 for x in t2 if '文湛持' in x) == 7, '与文湛持书 7 通')
chk(seg2.count('弟') == 91, f'卷二「弟」{seg2.count("弟")} == 91')
chk(lib.count('呵呵') == 2, '呵呵恰 2 见（皆在被逮途中）')

# 卷一
iv1 = lib.find('福州髙珰纪事')
seg1 = lib[iv1-40:i2]
t1 = [x for x in titles(seg1) if x in ('福州髙珰纪事', '申详税监变异縁由附后', '吏部揭帖')]
chk(len(t1) == 3, '卷一纪事公移 3 篇')

# 卷三：文 5 + 诗 7
prose3 = ['送中丞绵贞周公南归序', '龙树庵放生池记', '募建弥勒阁文', '题竺坞募田疏', '题血书莲华经']
chk(all(x in seg3 for x in prose3), '卷三杂文 5 篇齐')
poem3 = ['甲寅冬夜梦社中兄弟', '赴闽路占', '赠浒墅闗尹', '咏梅', '愁', '寄内', '秋斋偶成寄华子仲通']
chk(all(x in seg3 for x in poem3), '卷三诗 7 题齐')
chk(seg3.count('次韵　　') == 7, f'寻声谱次韵 {seg3.count("次韵　　")} == 7')

# 寻声谱账目：原 2 + 和 8 + 引 1 + 识 2
chk('寄怀干岳年兄' in seg3, '原诗一题在')
chk('其二' in seg3, '原诗其二在')
chk('喜从玉壶记忆得周忠介旧寄二诗赋此' in seg3, '鹿善继赋此一题在')
chk('寻声谱引' in page or '谱引' in page, '页内称引')
nums = 2 + 8 + 1 + 2
chk(nums == 13 and '十三件文字' in page, '谱中十三件文字 = 2+8+1+2')

# 页内其余事实锚
for k in ['三十余家', '被伤死者四人内外各二', '放火杀人乗机劫财', '丙寅三月十五日余被逮',
          '举箧藏尽付诸火', '鬼神通之也', '搔首展眉', '遂题是集曰寻声谱', '故名烬余',
          '臣等谨案忠介烬余集三巻明周顺昌撰']:
    chk(k in NL or norm(k) in NL, f'库锚：{k[:16]}')
chk(NO in page, f'页内序号 {NO} 在场（title 与 kicker）')

# ---------- 结果 ----------
print()
if fails:
    print(f'✗ {len(fails)} 项未过')
    for f in fails[:20]:
        print('  -', f)
    sys.exit(1)
print(f'✓ 全部通过：{len(QUOTES)} 条期望引文、{len(collected)} 个收集块、反扫+红线+机数')
