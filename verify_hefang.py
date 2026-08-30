#!/usr/bin/env python3
# 河防一览页核验：引文逐字对库 + 问答机数 + 复算 + 排版红线
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/河防一览.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/hefang-yilan.html'

raw = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()

fails = []
def check(name, cond, detail=''):
    if cond:
        print(f'  ok  {name}')
    else:
        fails.append(name)
        print(f'FAIL  {name} {detail}')

def norm(x):
    return ''.join(c for c in x if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0003ffff')

# ---------- 页面 .q 提取（标签配平） ----------
def collect_q(html):
    toks = re.split(r'(<[^>]+>)', html)
    out, depth, buf = [], 0, []
    for tk in toks:
        if tk.startswith('<'):
            m = re.match(r'<(/?)(\w+)', tk)
            if not m:
                continue
            closing, tag = m.groups()
            if closing:
                if depth > 0:
                    depth -= 1
                    if depth == 0:
                        out.append(''.join(buf)); buf = []
            else:
                cls = re.search(r'class="([^"]*)"', tk)
                c = cls.group(1) if cls else ''
                if 'q' in c.split():
                    if depth == 0:
                        depth = 1; buf = []
                    else:
                        depth += 1
        else:
            if depth > 0:
                buf.append(tk)
    return out

qs = collect_q(page)
qn = [norm(x) for x in qs]

QUOTES = [
 '神非他即水之性也',
 '归天归神误事最大',
 '黄流最浊以斗计之沙居其六若至伏秋则水居其二矣以二升之水载八升之沙非极汛溜必致停滞',
 '水分则势缓势缓则沙停沙停则河饱尺寸之水皆由沙面止见其髙水合则势猛势猛则沙刷沙刷则河深寻丈之水皆由河底止见其卑',
 '筑堤束水以水攻沙水不奔溢于両旁则必直刷乎河底一定之理必然之势',
 '支河一开正河必夺',
 '以水刷沙如汤沃雪',
 '水自刮除成空',
 '缕堤即近河濵束水太急怒涛湍溜必至伤堤',
 '遥堤离河颇逺或一里余或二三里伏秋暴涨之时难保水不至堤然出岸之水必浅既逺且浅其势必缓缓则堤自易保也',
 '积水顺堤直下仍归大河',
 '异常暴涨之水则任其宣泄少杀河伯之怒',
 '从否固难强之',
 '彼亦不得不以遥堤为家也',
 '耸峙蜿蜒如山之状',
 '両堤延亘一千五百余里',
 '但有刷损者随刷随补毋使崩卸少暇则督令取土堆积堤上若子堤然',
 '湏置立五更牌面分发南北两岸恊守官并管工委官照更挨发各铺传逓如天字铺发一更牌至二更时前牌未到日字铺即差人挨查系何铺稽迟',
 '须督堤夫捆札龙尾小埽摆列堤面如遇风浪大作将前埽用绳桩悬系附堤水面纵有风浪随起随落足以护卫',
 '须督各铺夫役毎名各置斗笠蓑衣遇有大雨各夫穿带堤面摆立时时巡视',
 '毎堤三里原设铺一座毎铺夫三十名计毎夫分守堤一十八丈',
 '毎夫分守堤一十八丈',
 '验堤之法用铁锥筒探之或间一掘试堤式贵坡切忌陡峻如根六丈顶止须二丈俾马可上下故谓之走马堤',
 '毎方广一丈高一尺为一方计四工土近者毎工银三分',
 '通漕于河则治河即以治漕会河于淮则治淮即以治河合河淮而同入于海则治河淮即以治海',
 '权豪势要之家侵占阻截违例盗决河防',
 '责有所归尔其慎之',
 '既而以其犹未赅备复加増削',
 '故生平规画总以束水攻沙为第一义',
 '后来虽时有变通而言治河者终以是书为凖的',
 '大抵司空成规具在纵有天灾纵有小通变治法不出其范围之外故曰河防一览为平成之书',
]

NS = norm(raw)

print('== 引文逐字核验（页面 .q 对库，去标点存异体） ==')
check(f'.q 元素恰 {len(QUOTES)} 个', len(qs) == len(QUOTES), f'实际 {len(qs)}')
for i, q in enumerate(QUOTES):
    check(f'库有 引文{i+1:02d} {q[:12]}…', q in NS)
expected = [norm(x) for x in QUOTES]
for i, q in enumerate(qn):
    check(f'页引文{i+1:02d} 在期望清单', q in expected, q[:20])

print('== 逐段锚定（引文出自声称的卷次） ==')
def seg_of(marker_lo, marker_hi):
    i = raw.find(marker_lo, 600)          # 跳过卷首提要
    j = raw.find(marker_hi, i + 10)
    return raw[i:j]
V2 = seg_of('河防一览卷二', '河防一览卷三')
V3 = seg_of('河防一览卷三', '河防一览卷四')
V4 = seg_of('河防一览卷四', '河防一览卷五')
check('卷二含 束水攻沙核心问答', '水分则势缓势缓则沙停' in norm(V2))
check('卷二含 神论与沙账', '归天归神误事最大' in norm(V2) and '黄流最浊以斗计之沙居其六' in norm(V2))
check('卷四含 夜防五更牌', '湏置立五更牌面' in norm(V4))
check('卷四含 走马堤与铁锥筒', '验堤之法用铁锥筒探之' in norm(V4))
check('卷三含 太行堤', '耸峙蜿蜒如山之状' in norm(V3))

print('== 机数复算（页面数字 vs 现算） ==')
ns = re.sub(r'\s', '', raw)
lab = lambda x: f'{x:,}'
check('全帙去空白 220,160', lab(len(ns)) == '220,160', len(ns))
check('卷至十四', '河防一览卷十四' in raw)
qa = V2.count('或有问于驯曰') + V2.count('问者曰')
check('辨惑四十五问', qa == 45, qa)
cjk = lambda s: len([c for c in s if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0003ffff'])
bh = cjk(V2)
check('辨惑一万一千余字', 11000 < bh < 12000, bh)
check('束水攻沙 1 见', raw.count('束水攻沙') == 1, raw.count('束水攻沙'))
check('筑堤束水 2 见', raw.count('筑堤束水') == 2, raw.count('筑堤束水'))
check('埽 194 见', raw.count('埽') == 194, raw.count('埽'))
check('四万八千一百二十二丈在库', '四万八千一百二十二丈' in ns)
check('铺制账 540=30×18', 3 * 180 == 540 and 540 // 30 == 18)
for num in ['220,160', '四十五问', '八十余篇', '二十七年', '四万八千一百二十二丈', '一百五十四公里', '194']:
    check(f'页面出现 {num}', num in page)
check('页面一里一百八十丈折算说明', '一里一百八十丈' in page)

print('== 排版红线 ==')
check('无长划线 — –', '—' not in page and '–' not in page)
bad = [ln for ln in page.split('\n') if ln.count('·') > 1]
check('每行 · ≤ 1', not bad, str(bad[:3]))
check('页脚来源声明', '殆知阁简体库' in page and 'verify_hefang.py' in page)
check('页脚时代提醒', '时代局限' in page)
check('链接总目', 'href="mulu.html"' in page)
check('SVG 图不少于 10 幅', page.count('<svg') >= 10, page.count('<svg'))
check('赭金点缀', '#c9963f' in page)
check('墨底纸白', '#191917' in page and '#e8e4dc' in page)

print()
if fails:
    print(f'未通过 {len(fails)} 项'); sys.exit(1)
print(f'全部通过：引文 {len(QUOTES)} 段 + 机数/红线断言')
