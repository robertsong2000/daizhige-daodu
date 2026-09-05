#!/usr/bin/env python3
# verify_julu.py　橘录 导读页核验：.q 双侧逐字对库 + 「」反扫 + 红线 + 机数 + 结构断言
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/julu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/橘录.txt'

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
"予北人。平生恨不得见橘著花。",
"去年秋。把麾此来。得一亲见花而再食其实。以为幸。",
"荔子今有谱。得与牡丹、芍药花谱并行。而独未有谱橘者。子爱橘甚。橘若有待于子。不可以辞。",
"且妄欲自附于欧阳公、蔡公之后。",
"温人谓乳柑为真柑。意谓他种皆若假设者。而独真柑为柑耳。",
"泥山盖平阳一孤屿。大都块土。不过覆釜。",
"夫物理何可考耶。",
"皮薄而味珍。脉不粘瓣。食不留滓。一颗之核才一二。间有全无者。",
"擘之则香雾噀人。北人未之识者。一见而知其为真柑矣。",
"风味照座",
"带叶而折",
"有及尺以上围者",
"其色如丹",
"宾祭斥不用",
"光彩灼烁如金弹丸",
"外强中干",
"为亲庭寿",
"香气馥馥可以熏袖",
"都人初不甚贵，其后因温成皇后好食之，由是价重京师。",
"其体性终弱。不可以犯霜。不可以耐久。又名为女儿橘。",
"是橘之仆奴也。",
"他日有以乳橘为真柑者。特碔砆之似玉也。",
"物以罕见为奇。此橘是也。",
"千林已尽。乃始傲然冰雪中。",
"由其本性自然。不杂之人为。故其味全。",
"谁能迟十年之久以收效耶。",
"经年向阳之枝以为贴。去地尺余。细锯截之。剔其皮。两枝对接。",
"工之良者挥斤之间。气质随异。无不活者。",
"过时而不接。则花实复为朱栾。人力之有参于造化每如此。",
"凡采者竟日不敢饮。",
"人有掘地作坎。攀枝条之垂者。覆之以土。至明年盛夏时开取之。色味犹新。",
"每入花一重。则实香一重。使花多于香。",
"他时焚之。如在柑林中。",
"药贵于愈疾而已。孰辨其为真伪耶。",
"橘中之乐，不减商山，恨不能深根固蒂耳",
"后皇嘉树，橘徕服兮。受命不迁，生南国兮。",
"淳熙五年十月。延安韩彦直序。",
]
miss_page = [q[:20] for q in EXPECTED if not any(norm(q) in b for b in qblocks)]
miss_lib  = [q[:20] for q in EXPECTED if norm(q) not in lib_norm]
check('关键引文清单库本侧全中', not miss_lib, str(miss_lib))
check('关键引文清单页面侧全中', not miss_page, str(miss_page))
check('.q 块数与清单规模相称', len(qblocks) == 37, f'页面 .q={len(qblocks)}（期望 37）')

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
n_tie = len(re.findall(r'<div class="tie["\s]', page))
check('名门九帖', n_tie == 9, f'page={n_tie}')
n_wk = len(re.findall(r'<div class="wk["\s]', page))
check('工序九节', n_wk == 9, f'page={n_wk}')
WK = ['种治','始栽','培植','去病','浇灌','采摘','收藏','制治','入药']
wk_missing = [w for w in WK if f'<b>{w}</b>' not in page]
check('九节篇名齐', not wk_missing, str(wk_missing))
n_tag = len(re.findall(r'<div class="tag["\s]', page))
check('绰号签五枚', n_tag == 5, f'page={n_tag}')
FU = ['平阳一孤屿','不过覆釜','地不弥一里','香味圈']
fu_missing = [u for u in FU if u not in page]
check('覆釜档案卡四行齐', not fu_missing, str(fu_missing))
check('页内自标 154', page.count('之一百五十四') == 3, f"count={page.count('之一百五十四')}")
check('页脚橘录+韩彦直', '韩彦直' in page)
check('库本二十七种序数在库', lib.count('二十有七种') == 1)

print()
if fails:
    print(f'FAILED: {len(fails)} 项 -> {fails}')
    sys.exit(1)
print('ALL PASS')
