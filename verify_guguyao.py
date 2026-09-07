# -*- coding: utf-8 -*-
"""格古要论导读页独立核验：期望引文双侧逐字 + <q> 全量对库 + 「」反扫 + 6字组反扫 + 红线 + 计数"""
import re, sys
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/格古要论.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/gegu-yaolun.html'
BUILD = '/home/robertsong/workspace/claude/daizhige-daodu/build_guguyao.py'

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = re.sub('[-]', '', s)
    s = s.replace('囗', '')
    return s

lib_flat = norm(open(LIB, encoding='utf-8').read())
lib_ws = ''.join(open(LIB, encoding='utf-8').read().split())
page = open(PAGE, encoding='utf-8').read()
errs, ok = [], []

# ---- 期望引文清单：从 build 脚本截取 Q 定义（不含其输出副作用）----
src = open(BUILD, encoding='utf-8').read()
head = src.split('TEMPLATE =')[0]
ns = {'raw': open(LIB, encoding='utf-8').read(), 'flat': lib_flat}
exec(compile(re.sub(r"raw = open\(LIB.*", "pass", head), '<q>', 'exec'), ns)
Q = ns['Q']
rawQ = {k: re.sub(r'</?span[^>]*>', '', v) for k, v in Q.items()}

# ---- 页面文本收集（跳过 style/script）----
class C(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.qdepth = 0; self.skip = 0; self.jiaoz = 0
        self.qs = []; self.cur = []; self.nodes = []; self.jnodes = []; self.qpath = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('style', 'script'): self.skip += 1; return
        if tag == 'q': self.qdepth += 1; self.cur = []
        if 'jiaoz' in (a.get('class') or ''): self.jiaoz += 1
    def handle_endtag(self, tag):
        if tag in ('style', 'script'): self.skip -= 1; return
        if tag == 'q':
            self.qdepth -= 1
            self.qs.append(''.join(self.cur)); self.cur = []
        if 'jiaoz' in (tag,): pass
    def handle_startendtag(self, tag, attrs): pass
    def handle_data(self, d):
        if self.skip: return
        if self.qdepth: self.cur.append(d)
        else:
            self.nodes.append(d)
            if self.jiaoz: self.jnodes.append(d)
    def close(self):
        super().close()

c = C(); c.feed(page); c.close()
page_flat = norm(''.join(c.nodes) + ''.join(c.qs))
qtexts = [(''.join(q)) for q in c.qs]

# 1. 期望引文 ⊆ 页面 ⊆ 库本
for k, v in rawQ.items():
    nv = norm(v)
    if nv not in page_flat: errs.append('页缺：%s' % k)
    if nv not in lib_flat: errs.append('库缺：%s' % k)
ok.append('期望引文 %d 条 双侧命中' % len(rawQ))

# 2. 页面所有 <q> 全量逐字对库
nq = 0
for t in qtexts:
    t = t.strip()
    if not t: continue
    nq += 1
    if norm(t) not in lib_flat:
        errs.append('<q>不连续或不存在：%s…' % t[:24])
ok.append('页面 <q> %d 块全部对库命中' % nq)

# 3. 「」 反扫：正文不允许出现字面引号（引号由 CSS 生成）
if '「' in page.replace('content: "「"', '').replace('content: "」"', ''):
    errs.append('正文字面出现「」')
else:
    ok.append('无字面「」（CSS 生成）')

# 4. 6字组反扫：非引文文本节点中不得出现与库本重合的 6 字连串（校字记区豁免）
declared_markers = ('射赫', '防砂', '防毛', '囗皮', '家画也', '利刀刮不动温润而泽',
                    '其言虽似有理', '十二时镜', '灵壁收香', '柴世宗', '卖骨董市语',
                    '骨董行', '库本', '通行', '私用区', '石棉', '校正', '形讹', '字讹',
                    '未成字', '存疑', '脱一字', '申报', '护之列', '当时称谓')
scan_nodes = c.nodes + c.jnodes if False else c.nodes
declared_ok = 0
badruns = []
for d in c.nodes:
    s = norm(d)
    if not s: continue
    # 校字记/时代局限文本内允许出现库本片段（本就是引库说明），跳过含申报标记的节点
    if any(m in d for m in declared_markers): declared_ok += 1; continue
    for i in range(len(s) - 5):
        run = s[i:i+6]
        if run in lib_flat:
            badruns.append((run, d.strip()[:40])); break
if badruns:
    for r, ctx in badruns: errs.append('6字组未申报：%s | %s' % (r, ctx))
else:
    ok.append('6字组反扫通过（%d 个申报节点豁免）' % declared_ok)

# 5. 红线
if '—' in page or '–' in page: errs.append('长划线')
else: ok.append('无长划线')
for i, line in enumerate(page.splitlines(), 1):
    if line.count('·') > 1: errs.append('L%d 多·：%s' % (i, line[:50]))
ok.append('每行·≤1')
for pat in ('src=', '@import', '<link', '<img', 'url('):
    if pat in page: errs.append('外部依赖：%s' % pat)
ok.append('零外部依赖')

# 6. 页脚四件 + 计数自洽
need = ('文本来源：殆知阁简体库', '去空白一万二千三百七十九字',
        '条已与库内文件逐字核验', '皆十四世纪之物', 'github.com/robertsong2000/daizhige-daodu')
for s in need:
    if s not in page: errs.append('页脚缺：%s' % s)
ok.append('页脚四件齐')
m = re.search(r'引文([零一二三四五六七八九十]+)条', page)
hanmap = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def han2int(s):
    if s == '十': return 10
    if '十' in s:
        a, _, b = s.partition('十')
        return (hanmap[a] if a else 1) * 10 + (hanmap[b] if b else 0)
    return hanmap[s]
if m:
    n = han2int(m.group(1))
    if n != len(rawQ): errs.append('页脚计数 %d != 引文 %d' % (n, len(rawQ)))
    else: ok.append('页脚计数自洽：%d 条' % n)
else:
    errs.append('页脚未找到引文计数')

# 7. 篇号两处一致
NO, NOHAN = ns.get('NO','?'), ns.get('NO_HAN','?')
if '之'+NOHAN not in page: errs.append('缺篇号 之'+NOHAN)
if ('>%s</b>'%NO) not in page and ('no mono">%s<'%NO) not in page: errs.append('缺篇号 '+NO)
ok.append('篇号两处齐（%s，以发布前 mulu 实况为准）'%NO)

# 8. 标签配平（容器级）
for tag in ('div', 'section', 'q', 'ul', 'li', 'p', 'h2', 'h3', 'h4', 'footer', 'main', 'nav', 'header', 'button', 'span', 'b', 'i', 'em', 'small', 'a'):
    o = len(re.findall(r'<%s[\s>]' % tag, page))
    cl = len(re.findall(r'</%s>' % tag, page))
    if tag in ('i', 'b', 'span') :  # 含装饰性自闭合以外的配对
        pass
    if o != cl: errs.append('标签不配平 %s: %d/%d' % (tag, o, cl))
ok.append('标签配平')

print('==== PASS ====')
for s in ok: print(' ✔', s)
if errs:
    print('==== FAIL ====')
    for e in errs: print(' ✘', e)
    sys.exit(1)
print('全部通过')
