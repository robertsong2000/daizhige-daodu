#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""松漠纪闻导读页核验：.q 引文逐字比对 + 非q引文 + 排版红线 + 机算复核"""
import re, sys

LIB = 'daizhige-simplified/史藏/志存记录/松漠纪闻.txt'
PAGE = 'daizhige-daodu/songmo-jiwen.html'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
ok, fail = 0, []

def chk(name, cond):
    global ok
    if cond: ok += 1
    else: fail.append(name); print('FAIL:', name)

def norm(s):
    s = re.sub(r'<[^>]+>', '', s)
    return ''.join(ch for ch in s if ch.isalnum())

LIBN = norm(lib)
PAGEN = norm(page)

# ---------- 分区 ----------
i_xu = lib.index('《松漠纪闻续》'); i_ba = lib.index('右《松漠纪闻》二卷')
i_bu = lib.index('[宋]洪皓《松漠纪闻补遗》')
zheng, xu, ba, bu = lib[:i_xu], lib[i_xu:i_ba], lib[i_ba:i_bu], lib[i_bu:]

def paras(region):
    return [p.strip() for p in region.split('\n\n') if p.strip()]

pz, px, pba, pbu = paras(zheng), paras(xu), paras(ba), paras(bu)
n_zheng, n_xu = len(pz) - 1, len(px) - 1          # 去卷题
n_bu = len(pbu) - 2                                # 去卷题、去末跋
chk('正卷30条', n_zheng == 30)
chk('续27条', n_xu == 27)
chk('补遗10段', n_bu == 10)
chk('跋恰1段', len(pba) == 1)

# ---------- 全帙字数 ----------
total = len(re.sub(r'\s', '', lib))
chk('全帙14624', total == 14624)
chk('页内14624', '全帙 14624 字' in page)

# ---------- .q 引文 ----------
qs = []
for m in re.finditer(r'<(span|blockquote|div)\b[^>]*\bclass="[^"]*\bq\b[^"]*"[^>]*>(.*?)</\1>', page, re.S):
    qs.append((m.group(1), m.group(2)))
chk('q元素数量52', len(qs) == 52)
for tag, body in qs:
    t = norm(body)
    if t not in LIBN:
        chk('q逐字:' + t[:24], False)
for tag, body in qs:
    if norm(body) in LIBN: ok += 1

# ---------- 非q引文（正文叙述中直接引用的库内字句） ----------
for extra in ['以牛粪覆棚种之', '虽得一鼠，亦褫皮藏去', '潜易它纸',
              '创艾而火其书', '秃节来归', '先君衔使十五年']:
    chk('extra:' + extra, norm(extra) in PAGEN and norm(extra) in LIBN)

# ---------- 机算：驿路 ----------
route = lib[lib.index('自上京至燕'):lib.index('去天甚近') + 5]
seg_route = route[:route.index('三十里至燕。') + len('三十里至燕。')]
hops = re.findall(r'([一二三四五六七八九十百]+)里至', seg_route)
D = dict(zip('一二三四五六七八九', range(1, 10)))
def c2n(s):
    if s == '十': return 10
    if '百' in s:
        h, rest = s.split('百'); v = D[h] * 100
        if not rest: return v
        v += 10 if rest == '十' else (D[rest[1]] + 10 if rest[0] == '十' else D[rest[-1]])
        return v
    if '十' in s:
        a, b = s.split('十'); return (D.get(a, 1) * 10) + (D.get(b, 0) if b else 0)
    return D[s]
sums = sum(c2n(h) for h in hops)
chk('驿路65程', len(hops) == 65)
chk('驿路合计2750', sums == 2750)
for s in ['2750', '1315', '1034', '5099', '六十五程']:
    chk('页内' + s, s in page)

# ---------- 机算：口粮 ----------
kou = lib[lib.index('虏之待中朝使者'):lib.index('天眷二年')]
def items(seg):
    return [x for x in re.split(r'[，。]', seg) if x.strip()]
fufu = items(kou[kou.index('曰给') + 2: kou.index('上节')])
shang = items(kou[kou.index('上节') + 2: kou.index('中节')])
zhong = items(kou[kou.index('中节') + 2: kou.index('下节')])
xia   = items(kou[kou.index('下节') + 2:])
chk('使副12项', len(fufu) == 12)
chk('上节5项', len(shang) == 5)
chk('中节5项', len(zhong) == 5)
chk('下节5项', len(xia) == 5)
chk('页内凡12项', page.count('凡 12 项') == 1)
chk('页内凡5项x3', page.count('凡 5 项') == 3)

# ---------- 予七见 ----------
yus = {
    '予尝自宾州涉江过其寨': zheng, '予顷与其千户李靖相知': zheng,
    '赵与予相识颇久': zheng, '予过河阴': zheng, '予衔命十五年': zheng,
    '与予所藏董羽画出水龙绝相似': xu, '予携以归': xu,
}
inl_q = ' '.join(b for tg, b in qs)
for y, region in yus.items():
    chk('库内予:' + y, lib.count(y) == 1 and y in region)
    chk('页内予:' + y, y in page)
chk('予正5续2', sum(1 for y, r in yus.items() if y in zheng) == 5 and
               sum(1 for y, r in yus.items() if y in xu) == 2)
chk('页内正5续2注', '正卷五见，续二见' in page)

# ---------- 库本怪相 ----------
chk('问号7处', lib.count('?') == 7)
chk('页内问号申报', '半角问号 7 处' in page)
for ch, n in [('𠡠', 4), ('𬤇', 1), ('𬶍', 1)]:
    chk('生僻字%d%s' % (n, ch), lib.count(ch) == n)
chk('页内三种六见', '三种六见' in page)
for s in ['正月十六曰', '纵偷一曰', '七月七曰']:
    chk('曰代日' + s, lib.count(s) == 1)
chk('页内曰代日申报', '多以「曰」代「日」' in page)
chk('十有一事申报', '十有一事' in page and '恰十段' in page)

# ---------- 排版红线 ----------
chk('无长划', '—' not in page and '–' not in page)
bad = [i for i, line in enumerate(page.split('\n')) if line.count('·') > 1]
chk('每行·≤1', not bad)

# ---------- 序号与页脚 ----------
chk('title之六十七', '导读之六十八' in page)
chk('kicker之六十七', '殆知阁导读之六十八' in page)
foot = page[page.index('<footer'):page.index('</footer>')]
chk('页脚之六十七', '导读之六十八' in foot)
chk('页脚引文数', ('引文 %d 段' % len(qs)) in page)
chk('页脚来源', 'daizhigev20' in page)
chk('页脚时代提醒', '史料眼光' in page)

print('PASS %d / FAIL %d' % (ok, len(fail)))
sys.exit(1 if fail else 0)
