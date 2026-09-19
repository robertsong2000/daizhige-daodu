#!/usr/bin/env python3
"""今言 导读页构建+核验。锚点切片引文,零誊写;token 注入 tpl;反扫六字窗。"""
import re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/今言.txt'
TPL = 'jinyan.tpl.html'
OUT = 'jinyan.html'
NO = sys.argv[1] if len(sys.argv) > 1 else '469'

raw = open(LIB, encoding='utf-8').read()

def norm(s):
    return ''.join(c for c in s if '㐀' <= c <= '鿿' or '豈' <= c <= '﫿')

libn = norm(raw)

def cut(a, b=None, pre=0, post=0):
    """从锚 a 起(可前移 pre 字),到锚 b 止(可后延 post 字)。"""
    i = raw.find(a)
    assert i >= 0, f'锚不存在: {a}'
    s = i - pre
    if b is None:
        e = i + len(a)
    else:
        j = raw.find(b, i)
        assert j >= 0, f'尾锚不存在: {b}'
        e = j + len(b)
    e += post
    seg = raw[s:e]
    assert not any(0xE000 <= ord(c) <= 0xF8FF for c in seg), f'PUA in {a!r}'
    return seg

Q = {
 'XUOPEN':   cut('文献不足', '视已成事。」'),
 'XUQUOTE':  cut('予有取焉', '盍与古言并梓之？」'),
 'XU344':    cut('述今言三百四十四条', '藏之故箧中。'),
 'XUEND':    cut('嘉靖丙寅二月既望郑晓识。'),
 'TI1':      cut('今言四卷，明郑晓撰', '此书补吾学编所未备。'),
 'TI2':      cut('此书之辅吾学编而行', '东观汉纪。'),
 'TIFEN':    cut('凡三百四十四条', '为证言、术言者十之一。'),
 'SHAONIAN': cut('生有异资', '以必为君子自矢。'),
 'PIGU':     cut('日披故牍', '人争传写之。'),
 'YANZHANG': cut('以争「大礼」廷杖。'),
 'WUGUSHI':  cut('治中迁知府，例也。', '无故事。'),
 'SHEBING':  cut('今兵事方棘', '乞归之营伍。'),
 'BUYI':     cut('角巾布衣与乡里父老游处', '见者不知其贵人也。'),
 'TAIZU':    cut('高皇戊辰生', '入淮西从郭元帅。'),
 'JIANWEN1': cut('建文君，洪武丁巳生。'),
 'JIANWEN2': cut('七年而嗣帝位。四年而亡。'),
 'GECHU':    cut('革除建文年号', '洪武有三十五年。'),
 'XIAOZONG1':cut('成化庚寅生于西宫。'),
 'XIAOZONG2':cut('越六年而宪宗始知之', '遂立为太子。'),
 'YINGZONG': cut('十四年而北狩', '居南宫。'),
 'SHIZONG':  cut('入承大统时', '少一岁。'),
 'BEI1':     cut('碑文以虏入寇京城为景泰元年', '辛未景泰二年也。'),
 'DU1':      cut('虏至德胜门实正统十四年十月事。'),
 'DU2':      cut('上皇入南宫实景泰元年八月事。'),
 'PAN':      cut('此名臣大功业', '岂足尽信！'),
 'YUQING':   cut('兵部侍郎于谦趋上掖监国止', '「请殿下坐。」'),
 'CHIJIA':   cut('玉盘径尺者十四', '马数万匹。'),
 'HUIXIN':   cut('中国已立皇帝', '行当决战。'),
 'PA0':      cut('我发大炮击虏', '斩其首铁颈元帅。'),
 'BANGWEN':  cut('谕回、达、奚、汉有能擒斩也先来献者', '封国公'),
 'ZONGLU':   cut('出战所以护京师', '安上皇也。'),
 'HENHUA':   cut('直至北京正阳门外', '再相会。」'),
 'JISI':     cut('万寿圣节前二日己巳', '虏自独石边外东行。'),
 'JIEBAO':   cut('请宽主忧臣辱之虑', '安内攘外之功。」'),
 'POKE':     cut('是日申时', '京城戒严。'),
 'CHENGXIA': cut('城外居民被伤千万', '声彻西苑。'),
 'QISHI':    cut('丁尚书、杨侍郎死于西市。'),
 'CHUKOU':   cut('己丑，仍出古北口去。'),
 'ZHANG1':   cut('勘奏者言虏杀我男妇六万', '焚庐舍万区。'),
 'ZHANG2':   cut('通计男妇死且掠者', '盖六十万。'),
 'ZHANG3':   cut('城外京、边军竟不曾与虏一战。'),
 'HUIHUI':   cut('回回司天监黑的儿、阿都剌', '迭里月实十四人'),
 'YILU1':    cut('凡天下道里', '横一万一千七百五十里。'),
 'YILU2':    cut('为驿九百四十。'),
 'KEIMING':  cut('瀚海为镡', '永清沙漠。」'),
 'GAOQIANG': cut('夺爵降庶人，安置高墙。', '载堉封爵如故。'),
 'WOKOU':    cut('倭恃华人为耳目', '借倭为爪牙'),
 'CODA1':    cut('述今言三百四十四条，藏之故箧中。'),
 'CODA2':    cut('予不能止也。'),
 'CODA3':    cut('「不习为吏，视已成事。」'),
}

html = open(TPL, encoding='utf-8').read()
for k, v in Q.items():
    html = html.replace(f'§Q_{k}§', f'<q>{v}</q>')
html = html.replace('§NO§', NO)
left = re.findall(r'§[^§]*§', html)
assert not left, f'模板token残留: {left}'

# ---------- checker ----------
body = html[html.index('<body>'):]
# 1) q/qv 通道:每个 q 的归一文本必须是库本子串
depth = 0; buf = []; qs = []; out_txt = []
i = 0
tokens = re.split(r'(<[^>]+>)', body)
for t in tokens:
    if t.startswith('<'):
        tag = re.match(r'<\s*/?\s*(q|qv)\b', t, re.I)
        if tag:
            if t.startswith('</'):
                depth -= 1
                if depth == 0:
                    qs.append(''.join(buf)); buf = []
            else:
                if depth == 0:
                    out_txt.append(''.join(buf)); buf = []
                depth += 1
        continue
    if depth:
        buf.append(t)
    else:
        out_txt.append(t)
if depth != 0:
    print('FAIL: q/qv 未闭合')
    sys.exit(1)
out_txt.append(''.join(buf))

bad = 0
for s in qs:
    n = norm(s)
    if not n:
        continue
    if n not in libn:
        bad += 1
        print(f'FAIL 引文不在库本: {s[:40]}…')
print(f'引文通道: {len([s for s in qs if norm(s)])} 条 q, {bad} 处不匹配')

# 2) 反扫:非引文文本(含 script 字面量)六字窗不得命中库本
plain = norm(''.join(out_txt))
miss = 0
for k in range(6, len(plain)):
    w = plain[k-6:k]
    if w in libn:
        miss += 1
        print(f'FAIL 反扫: …{plain[max(0,k-14):k]}【{w}】…')
print(f'白话反扫: 六字窗 {miss} 撞')

# 3) 硬规则
for ch, name in [('—','长划'), ('–','en-dash')]:
    if ch in html:
        print(f'FAIL 含{name}'); miss += 1
for ln in html.split('\n'):
    if ln.count('·') > 1:
        print('FAIL 单行·超1:', ln.strip()[:60]); miss += 1

if bad or miss:
    sys.exit(1)
open(OUT, 'w', encoding='utf-8').write(html)
print(f'OK -> {OUT} (第{NO}篇) 库本{len(libn)}字')
