# -*- coding: utf-8 -*-
"""靖康传信录 导读页核验：引文双侧、反扫、红线、机数。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'jingkang-chuanxinlu.html'
LIB  = '../daizhige-simplified/史藏/志存记录/靖康传信录.txt'

lib = open(LIB, encoding='utf8').read()
page = open(PAGE, encoding='utf8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

NL, NP = norm(lib), norm(page)
fail = []

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

qc = QC(); qc.feed(page)
collected = [norm(x) for x in qc.out if norm(x)]
print(f'[收集] .q 共 {len(qc.out)} 块，归一后非空 {len(collected)} 块')

QUOTES = [
 "时靖康二年岁次丁未二月二十五日，长沙漕厅翠蔼堂录。",
 "记其实而无隐，庶几后之览者有感于斯文。",
 "故余于此录记其实而无隐，庶几后之览者有感于斯文。",
 "譬犹病者证候既明，当用毒药而不用，虽暂得安，疾必再来，此必至之理也。",
 "元年正月三日，差充行营司参谋官。四日，除尚书右丞、充留守。五日，改充亲征行营使。",
 "寻落职，责授保静军节度副使，建昌军安置。寻移宁江。",
 "一身之进退荣辱、天下之安危利害，纷然如此，岂非真梦耶",
 "冈势隐辚如沙碛，然三面据水，前枕雾泽陂，即孳生马监之所，刍豆山积。",
 "金人兵至，径趋其所，实药师导之。",
 "濠河惟樊家冈一带以禁地不许开凿，诚为浅狭，然以精兵强弩占据，可以无虞。",
 "仓有粟、豆四十万石",
 "其后，勤王之师集城外者，赖之以济。",
 "闻诸道路，宰执欲奉陛下出狩，以避狄。果有之，宗社危矣。",
 "天下城池，岂复有如都城者",
 "李纲莫能将兵出战否",
 "陛下不以臣为庸懦，倘使治兵，愿以死报。",
 "至祥曦殿，则禁卫皆已擐甲，乘舆服御皆已陈列，六宫袱被皆将升车矣。",
 "尔等愿以死守宗社乎？愿扈从以巡幸乎？",
 "原以死守宗社！不居此，将安之",
 "卿留朕，治兵御寇专以委卿，不令稍有疏虞。",
 "每读一句，将士声诺。须臾，六军皆感泣流涕。",
 "修楼橹、挂毡幕、安炮坐、设弩床、运砖石、施燎炬、垂檑木、备火油，凡防守之具，无不备。",
 "自五日至八日，治防守之具粗毕，而贼马已抵城下，寨于牟驼冈。",
 "是夕，金人攻西水门，以大船数十只顺汴流相继而下。",
 "大船至，即以长钩摘就岸，投石碎之。",
 "又于中流安排扠木，及运蔡京家山石叠门道间，就水中斩获百余人。",
 "自禁中如新城酸枣门，几二十里。行夹道委巷中，惟恐贼之已登城也。",
 "虏箭集于城上如猬毛",
 "俾认，即皆汉人首级也。",
 "如获奸细，捕人亲执出头，验实推赏，辄杀者斩！",
 "自卯至未申间，杀贼数千。",
 "卿性刚，不可以往。",
 "棁、望之等，北面再拜，膝行而前。",
 "须犒师之物：金五百万两，银五千万两，绢、彩各一百万匹，马、驼、驴、骡之属各以万计。",
 "出事目一纸，付棁等达朝廷。",
 "唯唯，不能措一词",
 "此乃一妇人女子尔",
 "大概有五：欲称尊号，一也；欲得归朝人，二也；欲增岁币，三也；欲求犒师之物，四也；欲割疆土，五也。",
 "至于疆土，则祖宗之地，子孙当以死守，不可以尺寸与人。",
 "凡争逾两时，无一人助余言者。",
 "许奴婢及亲属人等及诸色人告，以半赏之。都城大扰。",
 "上曰：“卿可往收榜，毋得告讦。”",
 "彼以孤军入重地，正犹虎豹自投于槛阱中，当以计取之，不可以角一旦之力。",
 "吾勤王之师集城下者二十余万",
 "不过六万人",
 "其精兵不过三万人",
 "在道君朝为童贯所抑，未尝朝见",
 "欲生擒所谓斡离不者，取今上皇帝以归。",
 "斯须之间，中使三至，责以军令",
 "用兵乃大臣李纲与姚平仲结构，非朝廷意。",
 "佥议欲缚余以与之，而使人反以为不可。",
 "军民闻之，不期而集者数千万人，填塞驰道、街巷，呼声震地，舁登闻鼓于东华门，击破之。",
 "不得报，则杀伤内侍二十余人",
 "余泣拜请死，上亦泣。",
 "余既登城，令施放，有引炮自便，能中贼者，厚赏。夜，发霹雳炮以击，贼军皆惊呼。",
 "相去二十余里",
 "将士知朝廷之论二三，悉解体，不复有邀击之意，第遥护之而已。",
 "犹以舟行为缓，则乘肩舆；又以为缓，则于岸侧得搬运砖瓦船乘载。饥甚，于舟人处得炊饼一枚，分食之。是夜，行数百里。",
 "为宗社计，岂可复论此。",
 "公辅助皇帝，捍城、守宗社有大功，若能调和父子间，使无疑阻，当书青史，垂名万世。",
 "倘疑情不解，如所谓窃斧者，则为患不细。",
 "耿南仲当以尧舜之道辅陛下，而其人暗而多疑，所言不足深采。",
 "今拜大将如呼小儿，可乎",
 "此非为边事，乃欲缘此以去公，则都人无辞耳。",
 "上旦怒，将有杜邮之赐，奈何。",
 "上录《裴度传》以赐。",
 "亲贤臣、远小人，此先汉之所以兴隆也；亲小人、远贤臣，此后汉之所以倾颓也。",
 "朝廷既正，君子道长，则所以捍御外患者有不难也。",
 "翌日，进师，以七月初抵河阳。",
 "臣总师道出巩、洛，望拜诸陵寝，潸然流涕。",
 "既而果有言余专主战议、丧师费财者，又指言十罪。",
 "扶持天下之势转危为安几成，而为庸懦谗慝者坏之，为可惜也。",
 "朝廷不通耗者累月",
 "探箧中取自上龙飞余遭遇以来，被受御笔内批，及表、劄、章、奏等，命笔吏编次之",
 "京师之围未解",
]

miss_lib = miss_page = 0
for q in QUOTES:
    qn = norm(q)
    if qn not in NL:
        miss_lib += 1; fail.append(f'库本无：{q[:26]}')
    if qn not in NP and not any(qn in c for c in collected):
        miss_page += 1; fail.append(f'页面未载：{q[:26]}')
print(f'[引文] 期望 {len(QUOTES)} 条：库本缺 {miss_lib}，页面缺 {miss_page}')

sweep_bad = [c for c in collected if c not in NL]
if sweep_bad:
    for c in sweep_bad[:5]: fail.append(f'.q 非库内子串：{c[:30]}')
print(f'[反扫] .q→库本 不命中 {len(sweep_bad)} 块')

body = re.sub(r'<style[\s\S]*?</style>', '', page)
body = re.sub(r'<script[\s\S]*?</script>', '', body)
bad_jh = [m.group(1) for m in re.finditer(r'「([^」]*)」', body) if norm(m.group(1)) not in NL]
for b in bad_jh[:5]: fail.append(f'「」反扫不命中：{b[:30]}')
print(f'[「」反扫] 完成，不命中 {len(bad_jh)} 处')

for bad, name in [('—', '长划线'), ('–', '短划线')]:
    if bad in body: fail.append(f'红线：出现{name}')
dot_lines = [ln for ln in body.split('\n') if ln.count('·') > 1]
if dot_lines: fail.append(f'红线：{len(dot_lines)} 行出现多个 ·')
print(f'[红线] 长短划线 0，多 · 行 {len(dot_lines)}')

exp = {
    '去空白': len(re.sub(r'\s', '', lib)),
    '汉字': len(re.findall(r'[㐀-鿿]', lib)),
}
if exp['去空白'] != 21778: fail.append(f"去空白 {exp['去空白']} != 21778")
if exp['汉字'] != 18301: fail.append(f"汉字 {exp['汉字']} != 18301")
for w, n in [('余', 214), ('道君', 64), ('斩', 17), ('金人', 56), ('门', 47), ('城', 85),
             ('贼', 45), ('三镇', 14), ('霹雳', 1), ('登闻鼓', 1), ('牟驼冈', 2),
             ('翠蔼堂', 1), ('邦昌', 3), ('膝行', 1)]:
    c = lib.count(w)
    if c != n: fail.append(f'库本「{w}」{c} != {n}')
for s in ['二万一千七百七十八', '一万八千三百零一', '二百一十四见', '六十四见', '十七见',
          '二见', '一见', '之一百五十一']:
    if s not in page: fail.append(f'页面缺实测句：{s}')
print('[机数] 库本与页面实测句断言完成')

for ch in page:
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF or o >= 0x20000:
        fail.append(f'页面含私用/扩展区字符 U+{o:X}')
if '之一百五十一' not in page: fail.append('页面缺自编号 之一百五十')
print('[杂项] 生僻字与自编号检查完成')

if fail:
    print('\n== FAIL ==')
    for f in fail: print(' -', f)
    sys.exit(1)
print(f'\n== PASS ==  .q {len(collected)} 块 / 期望 {len(QUOTES)} 条 / 引文·反扫·红线·机数全过')
