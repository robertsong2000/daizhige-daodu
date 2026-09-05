#!/usr/bin/env python3
# verify_yishuo.py　医说 导读页核验：「」反扫 + 关键引文双侧 + 红线 + 机数 + 结构断言
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yishuo.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/医说.txt'

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

PUNCT = '，。、：；！？「」『』（）·〈〉《》【】〔〕？！…—－﹏～'
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

# ---------- 1. 「」反扫：页面全部「」文本必须命中库本 ----------
body_wo_style = re.sub(r'<style[\s\S]*?</style>|<script[\s\S]*?</script>', '', page)
quoted = re.findall(r'「([^」]*)」', body_wo_style)
rev_bad = []
for s in quoted:
    if norm(s) and norm(s) not in lib_norm:
        rev_bad.append(s)
check('「」反扫全中库本', not rev_bad, str(rev_bad))
print(f'    「」反扫样本数：{len(quoted)}')

# ---------- 2. .q 彩色文本也要逐字命中（含非「」包裹的 .q） ----------
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.qs = []; self.cur = None; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.skip += 1; return
        cls = dict(attrs).get('class', '') or ''
        self.stack.append('q' in cls.split())
        if 'q' in cls.split():
            self.cur = ''
    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.skip -= 1; return
        while self.stack:
            isq = self.stack.pop()
            if isq and self.cur is not None:
                self.qs.append(self.cur); self.cur = None
            break
    def handle_data(self, d):
        if self.skip: return
        if self.cur is not None:
            self.cur += d
qc = QC(); qc.feed(page)
qbad = [q[:20] for q in qc.qs if norm(q) and norm(q) not in lib_norm]
check('全部 .q 片段逐字命中库本', not qbad, str(qbad))
print(f'    .q 片段数：{len(qc.qs)}')

# ---------- 3. 关键引文清单（双侧） ----------
EXPECTED = [
    '医之伐病，犹将之伐敌也',
    '凡书之有及于医者必记之，名曰医说',
    '始见则曰已得几事矣',
    '其意欲满千事',
    '源流深远',
    '嘻。吾见子之心矣。方寸之地虚矣，几圣人也。',
    '遂密使人刺杀之',
    '年百余岁而儿有壮容，时人谓之仙',
    '风毒上攻，若刺头出少血即愈矣',
    '此可斩也。天子头上岂是试出血处耶',
    '医之议病理不加罪。且吾头重闷殆不能忍，出血未必不佳',
    '鸣鹤刺百会及脑户出血。上曰：吾眼明矣',
    '此天赐我师也。躬负缯宝以遗鸣鹤',
    '士大夫服丹砂死者前后固不一，余所目击',
    '水中澄其下略有丹砂，盖积于中与毒俱出也',
    '十年间亲见此二人，可以为戒矣',
    '宁食野葛，不服五石',
    '每语，喉中必有物作声相应',
    '遂取蓝捩汁而饮之，少顷吐出肉块，长二寸余，人形悉具',
    '药有阴功陈楼间处堂上呼卢喝六作五',
    '铅不死硫黄飞去',
    '犹累累如细砂',
    '葛之消酒，硫黄之化铅，皆载经方',
    '苟不知病源，而以古方从事，未见其可也',
    '殆与穴坯挟刃之徒无异',
    '今书之以为世警',
]
page_text = re.sub(r'<[^>]+>', '', body_wo_style)
miss_lib = [q for q in EXPECTED if norm(q) not in lib_norm]
miss_page = [q for q in EXPECTED if norm(q) not in norm(page_text)]
check('关键引文库本侧全中', not miss_lib, str(miss_lib))
check('关键引文页面侧全中', not miss_page, str(miss_page))

# ---------- 4. 排版红线 ----------
check('无长划线 —', '—' not in page)
check('无短划线 –', '–' not in page)
line_dot_bad = [ln for ln in page.splitlines() if ln.count('·') > 1]
check('每行 · ≤ 1', not line_dot_bad, str(line_dot_bad[:2]))
vis = re.sub(r'<style[\s\S]*?</style>|<script[\s\S]*?</script>|<[^>]+>', '', body_wo_style)
eng = [w for w in re.findall(r'[A-Za-z]{3,}', vis) if w not in ('github','com','http','https','robertsong','daizhigev')]
check('正文无英文残留', not eng, str(set(eng)))

# ---------- 5. 机数 ----------
total = len(lib)
ns    = len(re.sub(r'\s+', '', lib))
han   = sum(1 for c in lib if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x3FFFF)
print(f'[5] 库本机数：total={total:,} nospace={ns:,} han={han:,}')
check('页脚 total', f'{total:,}' in page, f'{total:,}')
check('页脚 nospace', f'{ns:,}' in page, f'{ns:,}')
check('页脚 han', f'{han:,}' in page, f'{han:,}')

# ---------- 6. 结构断言 ----------
vols = ['卷一','卷二','卷三','卷四','卷五','卷六','卷七','卷八','卷九','卷十']
vol_bad = [v for v in vols if len(re.findall(f'　　{v}　', lib)) < 5]
check('库本十卷俱在（各卷标题多次出现）', not vol_bad, str(vol_bad))
MEN = ['三皇历代名医','论医','医书','本草','神医','针灸','诊法','诸风','伤寒','诸疟',
       '头风','眼疾','口齿喉舌耳','鼻衄吐血','喘嗽','心腹痛(淋附)','疝瘅痹','消渴','翻胃','鬲噎诸气',
       '脏腑泄痢','肠风痔疾','痈疽','疮','瘕','积','漏','香港脚','劳瘵','五绝病',
       '中毒','解毒','诸虫','蛇虫兽咬犬伤','汤火金疮','扑打伤','奇疾','心疾健忘','小儿','妇人',
       '疾症','养生修养调摄','服饵并药忌','食忌','金石药之戒','医功报应','神方','肿瘿']
check('库本四十八门名俱在', all(m in lib for m in MEN), str([m for m in MEN if m not in lib]))
page_men = [m for m in MEN if m.replace('(淋附)','') not in page]
check('页面门类柜四十八门齐', not page_men, str(page_men))
check('香港脚伤口在页且标注库本如此', '香港脚' in page and '库本' in page)
check('秦鸣鹤条目在库本（并唐史）', norm('秦鸣鹤不知何许人也为高宗侍医(并唐史)') in lib_norm)
check('唐与正条目属卷二神医', lib.find('　　卷二　神医') < lib.find('唐与正少年得脉法') != -1)
check('毛景条目属卷五诸虫', lib.find('　　卷五　诸虫') < lib.find('永州通判厅军员毛景') != -1)

# ---------- 7. 页内自标 ----------
check('页内自标 190 三处', page.count('之一百九十一') == 3, f"count={page.count('之一百九十')}")
check('页脚医说+张杲', '张杲撰　殆知阁导读之一百九十一' in page)

print()
if fails:
    print(f'FAILED: {len(fails)} 项 -> {fails}')
    sys.exit(1)
print('ALL PASS')
