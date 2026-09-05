#!/usr/bin/env python3
# verify_hongguang.py　弘光实录钞 导读页核验：.q 双侧逐字对库 + 「」反扫 + 红线 + 机数 + 结构断言
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/hongguang-shiluchao.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/弘光实录钞.txt'

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

PUNCT = '，。、：；！？「」『』（）·〈〉《》【】〔〕"",.!?;:()\'"'
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

# ---------- 1. .q 收集器 ----------
VOID = {'br','img','meta','link','hr','input','path','circle','rect','line','polyline','polygon'}
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
        self.stack.append((tag, 'q' in cls.split()))
        if 'q' in cls.split():
            if self.cur is not None:
                self.blocks.append(self.cur); self.cur = ''
            else:
                self.cur = ''
            self.qdepth = len(self.stack)
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

bad = [b[:24] for b in qblocks if b not in lib_norm]
check('全部 .q 块逐字对库命中', not bad, f'未命中: {bad}')

# ---------- 2. 关键引文清单（双侧） ----------
EXPECTED = [
"时戊戌年冬十月甲子朔",
"年来幽忧多疾，旧闻日落；十年三徙，聚书复阙。后死之责，谁任之乎？",
"「实录」国史也，今子无所受命，冒然称之，不已僭乎",
"帝之不道，虽竖子小夫，亦计日而知其亡也。然诸坏政，皆起于利天下之一念。",
"壬寅，福王即皇帝位，以明年为弘光元年。",
"庚寅，黄得功、高杰相攻。",
"马士英密令燮伪上此报，以绝人望。",
"甲午，帝出奔。",
"睿音琅然，而睿容具日月表",
"乃使其私人杨文骢，持空头笺，命其不问何王，遇先至者，即填写迎之。",
"文骢至淮上，有破舟河下，中有一人，或曰：福王也。",
"士英以七不可之书用凤督印之成案，于是可法事事受制于士英矣。",
"臣按：士英之所以挟可法，与可法之所以受挟于士英者，皆为定策之异议也。",
"史可法亦恐四镇之不悦己也。急封爵以慰之，君子知其无能为矣。",
"时宗周在丹阳萧寺中，危坐终日，刺者肃然不敢加害。",
"监国素袍角带，对百官恸哭",
"见两大星夹日而行，钟山紫气中五色云见",
"福王则七不可（谓贪、淫、酗酒、不孝、虐下、不读书、干预有司也）。",
"帝之不道，虽竖子小夫，亦计日而知其亡也。",
"南都之建，帝之酒色几何，而东南之金帛聚于士英；士英之金帛几何，而半世之恩仇快于犬铖。",
"孽逆原任署正徐禹英希阮大铖旨，参顾杲、黄宗羲南都防乱揭。",
"遣降将李世春说降，可法叱之。",
"又遣乡约捧令旨至，可法使健丁投令旨并乡约于水。",
"可法呼副将史得威，以遗表、遗书授之曰：「死，葬我于高皇帝之侧」！",
"可法大呼「史可法在此」。",
"可法曰：「天朝大臣，岂肯偷生作万世罪人」。遂遇害。",
"北兵破扬州，大学士史可法、知府任民育、诸生高孝缵、王士秀死之北兵遂屠其城。",
"端伯书大明忠臣黄端伯七字与之",
"端伯曰：「吾志已决」，不能易矣。始命杀之。",
"端伯趺坐，为偈曰：「觌面绝商量，独露金刚王。问我安身处，刀山是道场」。",
"甲辰，帝被执，靖国公黄得功死之。",
"得功死而帝北狩。至明年八月遇害。",
"及帝出走，南中士民相聚而之于狱，即位一日，北兵乃入。",
"六月二十四日，下令剃发",
"留此发以见先帝耳",
"朝华而冠，夕□而髡；与丧乃心，宁死乃身",
"吾血不当落尘中",
"此吾毕命之所",
"吾头岂汝可断",
"以此劳公",
"天一可同公建义，独不可同公死乎",
"先生之千秋在此刻也",
"降则何待今日；吾之所以不死者，图反命耳。今国破，有死而已",
"杀之无血，唯白乳满地。",
"曾不一年而酒色、金帛、恩仇不知何在！",
"弘光南渡，得手钞便为信史。",
"后死之责，谁任之乎？",
]
miss_lib  = [q[:20] for q in EXPECTED if norm(q) not in lib_norm]
miss_page = [q[:20] for q in EXPECTED if not any(norm(q) in b for b in qblocks)]
check(f'关键引文清单库本侧全中({len(EXPECTED)}条)', not miss_lib, str(miss_lib))
check('关键引文清单页面侧全中', not miss_page, str(miss_page))
check('.q 块数与清单规模相称', len(qblocks) == 48, f'页面 .q={len(qblocks)}（期望 48）')

# ---------- 3. 「」反扫 ----------
body_wo_style = re.sub(r'<style[\s\S]*?</style>|<script[\s\S]*?</script>', '', page)
quoted = re.findall(r'「([^」]*)」', body_wo_style)
rev_bad = [s for s in quoted if norm(s) and norm(s) not in lib_norm]
check('「」反扫全中库本', not rev_bad, str(rev_bad))
print(f'    「」反扫样本数：{len(quoted)}')

# ---------- 4. 排版红线 ----------
check('无长划线 —', '—' not in page)
check('无短划线 –', '–' not in page)
line_dot_bad = [ln for ln in page.splitlines() if ln.count('·') > 1]
check('每行 · ≤ 1', not line_dot_bad, str(line_dot_bad[:2]))
vis = re.sub(r'<style[\s\S]*?</style>|<script[\s\S]*?</script>|<[^>]+>', '', body_wo_style)
eng = [w for w in re.findall(r'[A-Za-z]{3,}', vis) if w not in ('github','com','http','https','robertsong','daizhige','daodu','txt')]
check('正文无英文残留', not eng, str(set(eng)))

# ---------- 5. 机数 ----------
total = len(lib); ns = len(''.join(lib.split()))
han = sum(1 for c in lib if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x3FFFF)
print(f'[5] 库本机数：total={total} ns={ns} han={han}')
check('页脚 total', f'{total:,}' in page)
check('页脚 ns', f'{ns:,}' in page)

# ---------- 6. 结构断言 ----------
n_juan = len(re.findall(r'<div class="juan["\s]', page))
check('卷历五格(四卷+附录)', n_juan == 5, f'page={n_juan}')
JTAG = ['卷一','卷二','卷三','卷四','附录']
jtags = re.findall(r'<div class="jtag">([^<]+)</div>', page)
check('卷签文字齐', jtags == JTAG, str(jtags))
m_qi = re.search(r'<div class="qi">([\s\S]*?)</div>', page)
spans = re.findall(r'<span>([^<]+)</span>', m_qi.group(1)) if m_qi else []
check('七不可七印', len(spans) == 7, str(spans))
QI = ['贪','淫','酗酒','不孝','虐下','不读书','干预有司']
qi_missing = [q for q in QI if f'<span>{q}</span>' not in page]
check('七印文字齐', not qi_missing, str(qi_missing))
n_dd = len(re.findall(r'<div class="(song|an)">', page))
check('对读双栏', n_dd == 2, f'page={n_dd}')
n_person = len(re.findall(r'<div class="person">', page))
check('群像五人', n_person == 5, f'page={n_person}')
PERSONS = ['王若之','马纯仁','吴应箕','江天一','懋第']
p_missing = [p for p in PERSONS if p not in page]
check('群像名齐', not p_missing, str(p_missing))
check('题眼在页', '国史既亡，则野史即国史也' in page)
check('阙字照录', '夕□而髡' in page)
check('页内自标 之一百六十四', page.count('之一百六十四') == 3, f"count={page.count('之一百六十四')}")
check('页脚书名', '弘光实录钞' in page)
check('史臣与通行题名并记', '古藏室史臣' in page and '黄宗羲' in page)
check('文震亨双声并记', '文震亨' in page)

print()
if fails:
    print(f'FAILED: {len(fails)} 项 -> {fails}')
    sys.exit(1)
print('ALL PASS')
