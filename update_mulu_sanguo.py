#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""断言式更新 mulu.html：三国志通俗演义（嘉靖壬午本）/ 鼎足卷。篇号卷号commit前一刻动态解析。"""
import re, sys

P = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
s = open(P, encoding='utf-8').read()

CN = '零一二三四五六七八九'

def cn2int(t):
    t = t.replace('两', '二')
    m = re.match(r'^([一二三四五六七八九零两十百]+)$', t)
    assert m, f'非纯中文数字: {t}'
    total, num = 0, 0
    for ch in t:
        d = CN.index(ch) if ch in CN else 2
        if ch == '百':
            total += (num or 1) * 100
            num = 0
        elif ch == '十':
            total += (num or 1) * 10
            num = 0
        else:
            num = num * 10 + d
    return total + num

def int2cn(n):
    assert 1 <= n < 1000
    out = ''
    if n >= 100:
        out += CN[n // 100] + '百'
        n %= 100
        if n == 0:
            return out
        if n < 10:
            return out + '零' + CN[n]
    if n >= 10:
        if n // 10 > 1 or not out:
            out += CN[n // 10]
        out += '十'
        n %= 10
    if n:
        out += CN[n]
    return out

def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, f'锚断言失败: {old!r} 出现 {c} 次(期望 {n})'
    s = s.replace(old, new)

# 查重
for w in ['三国志通俗演义', 'sanguo-yanyi', '鼎足卷', '卷三百五十四']:
    assert w not in s, f'{w} 已存在'

# 取号：kicker 声称值 + 1
kicker = re.search(r'([零一二三四五六七八九十百]+)篇导读合订', s).group(1)
K = cn2int(kicker)
my_no = K + 1

# 卷数：当前声称值 + 1（新卷）
vol = re.search(r'([零一二三四五六七八九十百]+)卷分编', s).group(1)
C = cn2int(vol)
my_vol = C + 1

rep(f'{int2cn(K)}篇导读合订', f'{int2cn(my_no)}篇导读合订')

# sub 短文数可能滞后，按现值 +1
m = re.search(r'([零一二三四五六七八九十百]+)篇短文', s)
V = cn2int(m.group(1))
rep(f'{int2cn(V)}篇短文', f'{int2cn(V + 1)}篇短文')

rep(f'{int2cn(C)}卷分编', f'{int2cn(my_vol)}卷分编')

# footer 核验行也可能滞后
m = re.search(r'([零一二三四五六七八九十百]+)篇导读，2026 年 9 月编', s)
F = cn2int(m.group(1))
rep(f'{int2cn(F)}篇导读，2026 年 9 月编', f'{int2cn(my_no)}篇导读，2026 年 9 月编')

# 卷名链尾：sub 段末追加
i = s.find('卷分编')
j = s.find('</p>', i)
assert j > 0 and '卷' in s[j - 40:j], '链尾定位异常'
s = s[:j] + '，鼎足卷问鼎' + s[j:]

VOL = f'''  <div class="vol" style="--vc: var(--c1)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c1)">叁百伍拾肆</div>
        <h2>卷三百五十四 · 鼎足</h2>
        <div class="vsub">朱砂 · 集藏小说</div>
      </div>
      <p class="vol-desc">一部你熟到不用介绍、但你多半没见过它本来面目的书：嘉靖壬午刻本是现存最早的三国演义版本，开卷没有滚滚长江东逝水，第一句是后汉桓帝崩灵帝即位；毛宗岗父子后来的大改本把它的许多细节盖住了。本卷收〈三国志通俗演义〉嘉靖壬午本导读一篇，页面做成问鼎开卷壳：首屏青铜问鼎三足点亮书名显形钤壬午印；卷首三谜开卷无词文体有度稗官自重；序里三分魏蜀吴三柱各挂庸愚子考语；名场面五折横滑看原始台词，桃园一誓温酒一盏其酒尚温三顾一庐赤壁一火白帝一托；二十四卷开架原生折叠目录二百四十则全量照录；尾屏竖排欲知三国苍生苦右起三列钤鼎足印。引文经脚本与库内文件去标点、归一逐字比对通过（四十四q，白话反扫六字窗零撞）。</p>
      <a class="entry" href="sanguo-yanyi.html">
        <span class="no mono">{my_no}</span>
        <span class="ti">三国志通俗演义<small>明罗贯中编次，据集藏小说库本嘉靖壬午重印本，去空白约七十一万字（含重印前言、庸愚子序、修髯子引），正文二十四卷二百四十则，每卷十则。现存最早刻本，弘治甲寅庸愚子序称文不甚深言不甚俗事纪其实亦庶几乎史，嘉靖壬午修髯子引缀俚语四十韵。书眼＝开卷无词：毛本开篇临江仙词是清人挪来的，嘉靖本开门见山后汉桓帝崩灵帝即位，你熟悉的桥段多半是后来加的工。名场面：桃园结义誓词不求同年同月同日生；温酒斩华雄其酒尚温；三顾之恩不容不去；赤壁满江火滚；白帝托孤君可自为成都之主，外加马谡言过其实不可大用的看死一句。卷首序言先给三家写好考语，万古奸贼钉给曹操。版式＝问鼎开卷壳（朱砂）：青铜问鼎三足点亮显名；卷首三谜纸笺；序里三分三柱；名场面五折横滑；二十四卷开架折叠目录全量照录；尾屏竖排钤鼎足印。校字记：库本汉容之胄（通行汉景）、桃圆（通行桃园）等讹字照录或避引。时代局限：尊刘贬曹正统史观、黄巾写作贼寇、女子作离间筹码皆旧时代底色，照录立此存照。引文经脚本与库内文件去标点、归一逐字比对通过（四十四q，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">sanguo-yanyi.html</span>
      </a>
    </div>
  </div>

</footer>
</body>'''

rep('\n</footer>\n</body>', '\n' + VOL)

open(P, 'w', encoding='utf-8').write(s)
print(f'mulu updated: {my_no} 三国志通俗演义(嘉靖壬午本) / 卷三百五十四·鼎足')
