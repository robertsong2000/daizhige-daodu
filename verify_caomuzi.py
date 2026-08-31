#!/usr/bin/env python3
# verify_caomuzi.py　草木子 导读页核验：.q 双侧逐字对库 + 「」反扫 + 红线 + 机数 + 结构断言
import re, sys
from html.parser import HTMLParser
from collections import Counter

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/caomuzi.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/草木子.txt'

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

PUNCT = '，。、：；！？「」『』（）·〈〉《》【】〔〕'
def norm(s: str) -> str:
    out = []
    for ch in s:
        if ch.isspace() or ch in PUNCT:
            continue
        out.append(ch)
    return ''.join(out)

lib_norm = norm(lib)

fails = []
def check(name, cond, detail=''):
    if cond:
        print(f'  PASS  {name}')
    else:
        fails.append(name)
        print(f'  FAIL  {name}  {detail}')

# ---------- 1. .q 收集器（栈配平，VOID 不入栈） ----------
VOID = {'br','img','meta','link','hr','input','path','circle','rect','text','line','polyline','polygon'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.blocks = []; self.cur = None
        self.texts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('style','script'):
            self.skip += 1; return
        if tag in VOID: return
        cls = dict(attrs).get('class','') or ''
        names = cls.split()
        self.stack.append((tag, 'q' in names))
        if 'q' in names:
            qdepth = len(self.stack)
            if self.cur is not None:
                # 嵌套 q：收外层，开新层（本页无嵌套，防御）
                self.blocks.append(self.cur); self.cur = ''
            else:
                self.cur = ''
            self.qdepth = qdepth
    def handle_endtag(self, tag):
        if tag in ('style','script'):
            self.skip -= 1; return
        if tag in VOID: return
        while self.stack:
            t, isq = self.stack.pop()
            if len(self.stack) < getattr(self, 'qdepth', 10**9) and self.cur is not None:
                self.blocks.append(self.cur); self.cur = None
            if t == tag: break
    def handle_data(self, d):
        if self.skip: return
        if self.cur is not None:
            self.cur += d
        self.texts.append(d)
qc = QC(); qc.feed(page)
qblocks = [b for b in (norm(x) for x in qc.blocks) if b]
print(f'[1] .q 块收集：{len(qblocks)} 块')

# 每块都必须是库本 norm 的子串
bad = [b[:24] for b in qblocks if b not in lib_norm]
check('全部 .q 块逐字对库命中', not bad, f'未命中: {bad}')

# ---------- 2. 关键引文清单（双侧：在页面 + 在库本） ----------
EXPECTED = [
"洪武戊午春。有司以令甲于二月望致祭于城隍神。未祭。群吏于后窃饮猪脑酒。县学生发其事。吏惧。浼众为之言。别生复言于分臬。予适至学。亦以株连而就逮。",
"幽忧于狱。恐一旦身先朝露。与草木同腐。实切悲之。",
"万一后之览者。牺尊而青黄以文之。未可知也。弃而为沟中之断。亦未可知也。",
"圄中独坐。闲而无事。见有旧签簿烂碎。遂以瓦研墨。遇有所得。即书之。日积月累。忽然满卷。",
"时洪武十一年岁次戊午冬十一月二十又七日。括苍龙泉静斋叶子奇世杰自序。",
"旧篇二十有二。今约为八。凡四卷。",
"叶子奇作是书。不下四万言。拔其尤语。不满三千字。",
"以此观之。地形如一亭子。中高而四方下。昆仑乃其结顶处。四下之檐。乃四方之国土。",
"窃料太阳乃火之精。其气亦类于人间之火也。火正当气焰之上。必有黑晕。观之灯烛可见。星家谓之暗虚。想即此也。",
"疥有虫。予尝使明视者针而得之。其大不能以半粟也。详细察之。有嘴黝然。有足纤然。有背隆然。善止善行。",
"至于火中生虫。则火鼠也。极南方有之。其毛以为火浣布。",
"阴山以北。积雪历世不消。生蛆如瓠。谓之雪蛆。味极甘美。",
"元朝自世祖混一之后。天下治平者六七十年。轻刑薄赋。兵革罕用。生者有养。死者有葬。行旅万里。宿泊如家。诚所谓盛也矣。",
"元朝自平南宋之后。太平日久。民不知兵。将家之子。累世承袭。骄奢淫佚。自奉而已。至于武事。略不之讲。但以飞觞为飞炮。酒令为军令。肉阵为军阵。讴歌为凯歌。兵政于是不修也久矣。",
"至正丙戌冬。日色如血。",
"司天监奏天狗星坠地。血食人间五千日。始于楚。徧及齐赵。终于吴。",
"至正十一年春正月二十日夜。京师清宁殿火。焚宝玩万计。由宦官熏鼠故也。",
"至正壬辰癸巳间。浙江潮不波。",
"昔宋末海潮不波而宋亡。元末海潮不波而元亡。亦天数之一终也。",
"乙未年中。江淮间群鼠拥集如山。尾尾相衔度江。",
"至正二十二年间。黄河自河东清者千余里。河鱼历历。大小可数。",
"传云。黄河清。圣人生。当有代朕者。",
"至正戊申九月。庚申帝弃元京。遁居应昌府。",
"忽有二狐自殿上出。",
"朕不可复作徽钦衔璧求活。为天下笑。即命北狩。",
"朝廷所降食钱。官吏多不尽给。河夫多怨。韩山童等因挟诈。阴凿石人。止开一眼。镌其背曰。莫道石人一只眼。此物一出天下反。预当开河道埋之。掘者得之。遂相为惊诧而谋乱。",
"元朝自混一以来。大抵皆内北国而外中国。内北人而外南人。",
"故贫极江南。富称塞北。见于伪诏之所云也。",
"元朝末年。官贪吏污。始因蒙古色目人罔然不知廉耻之为何物。其问人讨钱。各有名目。",
"所属始参曰拜见钱。","无事白要曰撒花钱。","逢节曰追节钱。","生辰曰生日钱。","管事而索曰常例钱。","送迎曰人情钱。","句追曰赍发钱。","论诉曰公事钱。",
"觅得钱多曰得手。除得州美曰好地分。补得职近曰好窠窟。",
"漫不知忠君爱民之为何事也。",
"元朝天下。长官皆其国人是用。至于风纪之司。又杜绝不用汉人南人。",
"元世祖定天下之刑。笞杖徒流绞五等。笞杖罪既定。曰天饶他一下。地饶他一下。我饶他一下。自是合笞五十。止笞四十七。合杖一百十。止杖一百七。",
"天下死囚。审谳已定。亦不加刑。皆老死于囹圄。",
"今之定都。惟上都大都耳。两处何为最佳。",
"上都国祚短。民风淳。大都国祚长。民风淫。遂定都燕之计。",
"法酒。用器烧酒之精液取之。名曰哈剌基。",
"其清如水。盖酒露也。",
"真者不冰。倾之则流注。伪者杂水即冰凌而腹坚矣。",
"及兵乱。国用不足。多印钞以贾兵。钞贱物贵。无所于授。其法遂废。",
"元世祖皇帝思太祖创业艰难。俾取所居之地青草一株。置于大内丹墀之前。谓之誓俭草。盖欲使后世子孙知勤俭之节。",
"元之可传。独北乐府耳。",
"解贼一金幷一鼓。迎官两鼓一声锣。金鼓看来都一样。官人与贼不争多。",
"又有无名子为诗嘲之曰。丞相造假钞。舍人做强盗。贾鲁要开河。搅得天下闹。",
"而先生仅得巴陵一簿。无罪放黜。以终其身。着数万言。犹自谓与草木同腐。悲夫。",
]
miss_page = []
miss_lib  = []
for q in EXPECTED:
    qn = norm(q)
    if qn not in lib_norm: miss_lib.append(q[:20])
    if not any(qn in b for b in qblocks): miss_page.append(q[:20])
check('关键引文清单库本侧全中', not miss_lib, str(miss_lib))
check('关键引文清单页面侧全中', not miss_page, str(miss_page))
check('.q 块数与清单规模相称', len(qblocks) == 53, f'页面 .q={len(qblocks)}（期望 53＝清单 53 条逐块对应）')

# ---------- 3. 「」反扫：页面叙述里所有「」文本必须是库内原文 ----------
body_wo_style = re.sub(r'<style[\s\S]*?</style>|<script[\s\S]*?</script>', '', page)
quoted = re.findall(r'「([^」]*)」', body_wo_style)
rev_bad = []
for s in quoted:
    if norm(s) and norm(s) not in lib_norm:
        rev_bad.append(s)
check('「」反扫全中库本', not rev_bad, str(rev_bad))
print(f'    「」反扫样本数：{len(quoted)}')

# ---------- 4. 排版红线 ----------
check('无长划线 —', '—' not in page)
check('无短划线 –', '–' not in page)
line_dot_bad = [ln for ln in page.splitlines() if ln.count('·') > 1]
check('每行 · ≤ 1', not line_dot_bad, str(line_dot_bad[:2]))

# 可见文本英残留（style/script 之外，允许来源链接）
vis = re.sub(r'<style[\s\S]*?</style>|<script[\s\S]*?</script>|<[^>]+>', '', body_wo_style)
eng = [w for w in re.findall(r'[A-Za-z]{3,}', vis) if w not in ('github','com','http','https','robertsong','daizhigev')]
check('正文无英文残留', not eng, str(set(eng)))

# ---------- 5. 机数：库本字数与页脚一致 ----------
total = len(lib)
ns    = len(re.sub(r'\s+', '', lib))
han   = sum(1 for c in lib if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x3FFFF)
print(f'[5] 库本机数：total={total} nospace={ns} han={han}')
check('页脚 total', f'{total:,}' in page, f'{total:,}')
check('页脚 nospace', f'{ns:,}' in page, f'{ns:,}')
check('页脚 han', f'{han:,}' in page, f'{han:,}')

# ---------- 6. 结构断言 ----------
PIAN = ['管窥篇','观物篇','原道篇','钩玄篇','克谨篇','杂制篇','谈薮篇','杂俎篇']
pian_missing = [p for p in PIAN if lib.count('○'+p) != 1]
check('库本八篇 ○ 篇头各恰一见', not pian_missing, str(pian_missing))
PIAN_SHORT = ['管窥','观物','原道','钩玄','克谨','杂制','谈薮','杂俎']
pian_page = [p for p in PIAN_SHORT if p not in page]
check('页面八篇篇名齐', not pian_page, str(pian_page))

APX = ['正德刻本序','万历重刻本序','乾隆重刻本序一','乾隆重刻本序二','同治重刻本序','快书刻节本草木子题词']
apx_missing = [a for a in APX if a not in lib]
check('库本附录六篇俱在', not apx_missing, str(apx_missing))

n_fee = len(re.findall(r'<div class="fee["\s]', page))
check('名目卡九枚（八钱卡＋黑话合卡）', n_fee == 9, f'page={n_fee}')
FEES = ['拜见钱','撒花钱','追节钱','生日钱','常例钱','人情钱','赍发钱','公事钱','得手','好地分','好窠窟']
fee_missing = [f for f in FEES if f not in page]
check('十一名目逐字在页', not fee_missing, str(fee_missing))

n_omen = len(re.findall(r'<div class="omen"', page))
check('灾异簿七行', n_omen == 7, f'page={n_omen}')

# 流传链六站
TL = ['洪武十一年','正德丙子','万历丙午','乾隆壬午','同治甲戌','殆知阁']
tl_missing = [t for t in TL if t not in page]
check('流传链六站齐', not tl_missing, str(tl_missing))
# 干支自报在库内
for gy in ['正德丙子','丙午夏日','乾隆二十七年岁在壬午','同治十三年甲戌','洪武十一年岁次戊午']:
    if norm(gy) not in lib_norm:
        fails.append(f'干支自报 {gy}')
        print(f'  FAIL  库内干支自报 {gy}')
print('  PASS  库内干支自报五处（正德丙子/万历丙午/乾隆壬午/同治甲戌/洪武戊午）' if not any('干支自报' in f for f in fails) else '')

# 三饶三行
check('三饶三行在页', all(s in page for s in ['天饶','地饶','我饶','合笞五十。止笞四十七']))

# 页面自标号
check('页内自标 125（title/kicker/footer）', page.count('之一百二十七') == 3, f"count={page.count('之一百二十七')}")
check('页脚草木子+叶子里子奇', '叶子奇撰　殆知阁导读之一百二十七' in page)

print()
if fails:
    print(f'FAILED: {len(fails)} 项 -> {fails}')
    sys.exit(1)
print('ALL PASS')
