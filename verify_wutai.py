#!/usr/bin/env python3
# verify_wutai.py　东坡乌台诗案 导读页核验：.q/.e 双侧逐字对库 + 「」反扫 + 名单点验 + 红线 + 机数 + 结构断言
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/wutai-shian.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/东坡乌台诗案.txt'
MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

PUNCT = '，。、：；！？「」『』（）·〈〉《》【】〔〕"",.!?;:()\'"'
def norm(s: str) -> str:
    return ''.join(ch for ch in s if not ch.isspace() and ch not in PUNCT)

lib_norm = norm(lib)
page_norm = norm(page)

fails = []
def check(name, cond, detail=''):
    if cond:
        print(f'  PASS  {name}')
    else:
        fails.append(name)
        print(f'  FAIL  {name}  {detail}')

# ---------- 文本收集器：全文 + .q 块(剔除 .src) + .e 格 + .nm 名单 ----------
class TC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.all_text = []
        self.q_blocks = []   # list[str]
        self.e_texts = []    # roster cell bodies
        self.walls = {}      # data-list -> [names]
        self.cur_q = None
        self.q_suppress = 0
        self.q_depth = 0
        self.e_depth = 0
        self.cur_e = None
        self.wall_stack = []
        self.nm_stack = []
    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.skip += 1
            return
        cls = (dict(attrs).get('class') or '')
        dl  = dict(attrs).get('data-list')
        parts = cls.split()
        if 'q' in parts and tag == 'div':
            if self.q_depth == 0:
                self.cur_q = []
            self.q_depth += 1
        if 'src' in parts or 'lb' in parts:
            self.q_suppress += 1
        if 'e' in parts and tag == 'span':
            self.cur_e = []
            self.e_depth += 1
        if dl:
            self.wall_stack.append(dl)
            self.walls.setdefault(dl, [])
        if 'nm' in parts and self.wall_stack:
            self.nm_stack.append(len(self.all_text))
            self.walls[self.wall_stack[-1]].append([])
    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.skip = max(0, self.skip - 1)
            return
        if tag == 'div' and self.q_depth > 0:
            self.q_depth -= 1
            if self.q_depth == 0 and self.cur_q is not None:
                self.q_blocks.append(''.join(self.cur_q))
                self.cur_q = None
        if ('src' in tag or True) and self.q_suppress and tag == 'span':
            pass
        if tag == 'span' and self.e_depth:
            self.e_depth -= 1
            if self.e_depth == 0 and self.cur_e is not None:
                self.e_texts.append(''.join(self.cur_e))
                self.cur_e = None
        if tag == 'div' and self.wall_stack:
            self.wall_stack.pop()
        if tag == 'span' and self.nm_stack and self.wall_stack:
            pass
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_data(self, d):
        if self.skip:
            return
        self.all_text.append(d)
        if self.cur_q is not None and self.q_suppress == 0:
            self.cur_q.append(d)
        if self.cur_e is not None:
            self.cur_e.append(d)
        if self.wall_stack and self.nm_stack:
            idx = self.nm_stack[-1] if False else None
            if self.walls[self.wall_stack[-1]]:
                self.walls[self.wall_stack[-1]][-1].append(d)
    def handle_starttag_nm_close(self):
        pass
    # 简化：nm 名单末尾统一在结束后截断到下一 span —— 用 handle_endtag 无法精确，
    # 改为在 handle_data 里按当前 span 边界收集：见下 handle_starttag 中 push 空列表。

tc = TC()
tc.feed(page)
page_all = '\n'.join(tc.all_text)
page_all_norm = norm(page_all)

# nm 收集修正：上面按 data-list 分组、每遇 .nm push 新列表，跨名字会串行累积。
# 重新用正则抽名单（可靠）：每面墙的 HTML 片段内逐个 <span class="nm...">text</span>
walls = {}
for m in re.finditer(r'<div class="wall" data-list="([^"]+)">(.*?)</div>', page, re.S):
    key, seg = m.group(1), m.group(2)
    walls[key] = re.findall(r'<span class="nm[^"]*">([^<]*)</span>', seg)

# ---------- 1. .q 引文双侧对库 ----------
check('q块数量', len(tc.q_blocks) == 13, f'got {len(tc.q_blocks)}')
for i, q in enumerate(tc.q_blocks):
    t = q.strip()
    if not t:
        continue
    check(f'q{i:02d}对库', norm(t) in lib_norm, t[:24])

# ---------- 2. EXPECTED 双侧 ----------
EXPECTED = [
 '愚不识时，难以追陪新进；老不生事，或能牧养小民',
 '愚弄朝廷，妄自尊大',
 '至于包藏祸心，怨望其上，讪讟慢骂而无复人臣之节者，未有如轼也',
 '初无学术，滥得时名，偶中异科，遂叨儒馆',
 '言伪而辨，行伪而坚，先王之法当诛',
 '轼所为讥讽文字传于人者甚众，今犹取镂板而鬻于市者进呈',
 '愚不适时',
 '老翁七十自腰镰，惭愧春山笋蕨甜。岂是闻韶解忘味，迩来三月食无盐',
 '意山中之人，饥贫无食，虽老亦自采笋蕨充饥；时盐法峻急，僻远之人无盐食，动经数月',
 '山中小民，岂能食淡而乐乎！以讥讽盐法太急也',
 '先生独何事，四方望陶冶。儿童诵君实，走卒知司马。抚掌笑先生，年来效喑哑',
 '四海苍生，望司马执政。陶冶天下，以讥讽见在执政，不得其人。又言儿童走卒，皆知姓字，终当进用',
 '新法不便，终当用司马光',
 '吴儿生长狎涛渊，冒利忘生不自怜。东海若知明主意，应教斥卤变桑田',
 '言此事之必不可成，讥讽朝廷水利之难成也',
 '今年七月二十八日，中使皇甫遵到湖州勾摄轼前来，至八月十八日，赴御史台出头',
 '除《山村》诗外，其余文字并无干涉时事',
 '二十二日，又虚称更无往复诗等文字',
 '二十四日，又虚称别无讥讽嘲咏诗赋等应系干涉文字',
 '又虚称即别不曾与文字往还',
 '三十日，却供通自来与人有诗赋往还人数姓名',
 '据轼供说其间隐讳有未尽者',
 '结按具状申奏',
 '委是忘记，误有供通，即非讳避',
 '准律，作匿名文字，谤讪朝政及中外臣僚，徒二年',
 '报上不以实，徒一年',
 '其苏轼合追两官，勒停放',
 '苏轼可责授检校水部员外郎充黄州团练副使，本州岛安置，不得签书公事',
 '你将取《佛入涅盘》及《桃花雀竹》等，我待要朱繇、武宗元画《鬼神》',
 '于诜处换得紫衣二道与思大师',
 '作诗赋等文字讥讽朝政阙失等事',
]
for j, e in enumerate(EXPECTED):
    n = norm(e)
    check(f'EXP{j:02d}在库', n in lib_norm, e[:20])
    check(f'EXP{j:02d}在页', n in page_all_norm, e[:20])

# ---------- 3. 「」反扫 ----------
for k, m in enumerate(re.finditer(r'「([^」]*)」', page_all)):
    inner = m.group(1)
    if not inner.strip():
        continue
    check(f'「」{k:02d}对库', norm(inner) in lib_norm, inner[:24])

# ---------- 4. 红线：长划线 ----------
check('禁长划线', '—' not in page and '–' not in page)

# ---------- 5. 每行 · ≤1 ----------
bad_lines = [i for i, ln in enumerate(page.split('\n')) if ln.count('·') > 1]
check('每行·≤1', not bad_lines, str(bad_lines[:5]))

# ---------- 6. 英文白名单 ----------
ALLOW = {'github', 'com', 'http', 'https', 'robertsong', 'daizhige', 'daodu', 'txt'}
toks = set(re.findall(r'[A-Za-z]+', page_all))
check('英文白名单', toks <= ALLOW, str(toks - ALLOW))

# ---------- 7. 机数页脚（实时重算） ----------
raw_n = len(lib)
nsp_n = len(re.sub(r'\s', '', lib))
check('机数-总字符', f'{raw_n:,}' in page, f'{raw_n:,}')
check('机数-去空白', f'{nsp_n:,}' in page, f'{nsp_n:,}')

# ---------- 8. 结构断言 ----------
check('弹章四张', page.count('class="zhang"') == 4)
check('对读三组', page.count('class="caseblock"') == 3)
check('登记格七格', len(tc.e_texts) == 7, f'got {len(tc.e_texts)}')
for i, e in enumerate(tc.e_texts):
    check(f'格{i}对库', norm(e) in lib_norm, e[:24])
check('收坐二十九', len(walls.get('shouzuo', [])) == 29, f'got {len(walls.get("shouzuo", []))}')
check('承受四十七', len(walls.get('chengshou', [])) == 47, f'got {len(walls.get("chengshou", []))}')
check('名单合计七十六', len(walls.get('shouzuo', [])) + len(walls.get('chengshou', [])) == 76)
sz = '、'.join(walls.get('shouzuo', []))
cs = '、'.join(walls.get('chengshou', []))
check('收坐名单对库', norm(sz) in lib_norm)
check('承受名单对库', norm(cs) in lib_norm)
for fam in ['王诜', '苏辙', '黄庭坚', '司马光', '曾巩']:
    check(f'收坐含{fam}', fam in walls.get('shouzuo', []))
check('承受含欧阳修', '欧阳修' in walls.get('chengshou', []))
check('责授印', '责授' in page and 'class="stamp"' in page)
check('计数文案四道弹章', '四道弹章' in page)
check('计数文案三十九条供状', '三十九条供状' in page)
check('计数文案收坐二十九人', '收坐二十九人' in page or '收坐</b>，收到讥讽文字而不申缴，二十九人' in page or '二十九人' in page)
check('计数文案四十七人', '四十七人' in page)
check('返回总目链接', 'href="mulu.html"' in page)
check('核验块存在', '核验与说明' in page and '殆知阁简体库' in page and '时代局限' in page)
check('仓库链接', 'github.com/robertsong2000/daizhige-daodu' in page)

# ---------- 9. 编号自标三处 ----------
check('编号三处', page.count('之一百五十九') >= 3, f'got {page.count("之一百五十九")}')
check('标题编号', '殆知阁导读之一百五十九' in page)

# ---------- 10. mulu 联动 ----------
mulu = open(MULU, encoding='utf-8').read()
check('mulu条目存在', 'href="wutai-shian.html"' in mulu)
check('mulu编号158', 'class="no mono">158<' in mulu)
check('mulu计数kicker', '一百五十九篇导读合订' in mulu)
check('mulu计数sub', '一百五十九篇短文' in mulu)
check('mulu计数footer', '一百五十九篇导读，2026' in mulu)
pd = mulu.find('卷二十三 · 判牍')
mypos = mulu.find('wutai-shian.html')
nexth = mulu.find('<h2>', pd)
check('mulu判牍卷归类', pd < mypos < nexth, f'{pd} {mypos} {nexth}')

print()
if fails:
    print(f'共 {len(fails)} 项失败'); sys.exit(1)
print('全部通过')
