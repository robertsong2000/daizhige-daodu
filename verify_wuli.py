#!/usr/bin/env python3
# 物理小识 页面核验：.q 逐字对库 + 机数 + 排版红线
import re, sys

PAGE = 'wuli-xiaoshi.html'
LIB = '../daizhige-simplified/子藏/笔记/物理小识.txt'

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if (0x3400 <= o <= 0x9FFF) or (0x20000 <= o <= 0x3FFFF):
            out.append(ch)
    return ''.join(out)

def collect_q(html):
    # 标签平衡扫描器：抓 class 分词后恰含 q 的元素
    items = []
    for m in re.finditer(r'<(\w+)([^>]*)>', html):
        attrs = m.group(2)
        cm = re.search(r'class="([^"]*)"', attrs)
        if not cm or 'q' not in cm.group(1).split():
            continue
        tag = m.group(1)
        i = m.end()
        depth = 1
        while depth > 0:
            nxt = re.search(r'<(/?)%s\b[^>]*>' % tag, html[i:])
            if not nxt:
                raise AssertionError('.q 未闭合: %r' % html[m.start():m.start()+80])
            if nxt.group(1) == '':
                depth += 1
            else:
                depth -= 1
            i += nxt.end()
        items.append(html[m.end():i-len(tag)-3])
    return items

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)

html = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()
lib_n = norm(lib)

qs = collect_q(html)
print(".q 块数:", len(qs))
assert len(qs) == 22, "应 22 段引文"

seen = set()
for i, raw in enumerate(qs, 1):
    txt = strip_tags(raw)
    qn = norm(txt)
    assert qn, f'引文{i} 归一后为空'
    assert qn in lib_n, f'引文{i} 不在库内: {txt[:40]}'
    assert lib_n.count(qn) == 1, f'引文{i} 库内不唯一: {txt[:40]}'
    assert qn not in seen, f'引文{i} 页面重复'
    seen.add(qn)
print('22 段引文全部逐字命中且库内唯一')

# ---- 机数 ----
nospace = len(re.sub(r'\s', '', lib))
assert nospace == 157628, f'去空白 {nospace} != 157628'
heads = [l for l in lib.split('\n') if re.search(r'物理小识[卷巻]', l) and '撰' in l]
assert len(heads) == 12, f'卷头 {len(heads)} != 12'
assert any('巻八' in l for l in heads), '卷八卷头应为巻'
cats = [re.sub(r'\s', '', h).split('撰')[1] for h in heads]
assert len(set(cats)) == 11, f'类名 {len(set(cats))} != 11'
assert cats.count('鸟兽类') == 2
cnt = {k: lib.count(k) for k in ['【中通曰', '【暄曰', '【中履曰', '【中徳曰', '【中德曰']}
total = sum(cnt.values())
assert cnt == {'【中通曰': 97, '【暄曰': 66, '【中履曰': 43, '【中徳曰': 12, '【中德曰': 10}, cnt
assert total == 228
assert lib.count('中发曰') == 0
pua = [c for c in set(lib) if 0xE000 <= ord(c) <= 0xF8FF]
ext = [c for c in set(lib) if 0x20000 <= ord(c) <= 0x3FFFF]
assert len(pua) == 129, len(pua)
assert len(ext) == 57, len(ext)
assert lib.count('防') == 456
assert lib.count('中分十五门') == 1
print(f'机数过: 去空白 {nospace}, 卷头 12, 类名 11, 批注 {total} (中通97/暄66/中履43/中徳22/中发0), PUA 129 种, Ext 57 种, 防 456')

# 页面声明与机数一致
for phrase in ['二百二十八见', '九十七', '中发']:
    assert phrase in html, phrase

# ---- 排版红线 ----
assert '—' not in html, '长划线'
assert '–' not in html, '短划线'
text = strip_tags(html)
for ln in text.split('\n'):
    assert ln.count('·') <= 1, f'一行多·: {ln[:60]}'
print('红线过: 无 — –, 每行 · ≤ 1')
print('ALL PASS')
