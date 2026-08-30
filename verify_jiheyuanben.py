#!/usr/bin/env python3
# 核验 jihe-yuanben.html：引文逐字对库 + 排版红线 + 机数复算
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/jihe-yuanben.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/算法/几何原本.txt'
errs, warns = [], []

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
        elif ch.isascii() and ch.isalnum():
            out.append(ch)
    return ''.join(out)

# ---------- 1. 收集页面 .q（标签配平栈；.lost/.who/.cap/.ot 注文剥除，嵌套 q 双记） ----------
class QC(HTMLParser):
    DROP = {'lost', 'who', 'cap', 'ot'}
    def __init__(self):
        super().__init__()
        self.stack, self.spans, self.cur = [], [], None
    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get('class') or '')
        toks = cls.split()
        parent_drop = self.stack[-1][2] if self.stack else False
        # q 捕获开启即重置 drop（注内引文仍须核验）；q 内部的注文继续剥除
        drop = bool(set(toks) & self.DROP) or (parent_drop and 'q' not in toks)
        self.stack.append((tag, toks, drop))
        if 'q' in toks:
            self.cur = {'buf': [], 'outer': self.cur}
    def handle_endtag(self, tag):
        while self.stack:
            t, toks, _ = self.stack.pop()
            if t == tag:
                if self.cur and 'q' in toks:
                    txt = ''.join(self.cur['buf'])
                    self.spans.append((norm(txt), txt))
                    up = self.cur['outer']
                    if up is not None:
                        up['buf'].append(txt)
                    self.cur = up
                break
    def handle_data(self, d):
        if self.cur is not None and self.stack and not self.stack[-1][2]:
            self.cur['buf'].append(d)

html = open(PAGE, encoding='utf-8').read()
qc = QC(); qc.feed(html)
pageq = [n for n, _ in qc.spans if len(n) >= 2]
lib = open(LIB, encoding='utf-8').read()
libnorm = norm(lib)

# ---------- 2. 期望引文清单（全部逐字取自库本） ----------
EXPECTED = [
 "几何原本者度数之宗所以穷方圆平直之情尽规矩准绳之用也",
 "因请其象数诸书更以华文独谓此书未译则他书俱不可得论",
 "盛有元元本本师曹习之学而毕丧于祖龙之",
 "毕丧于祖龙之",
 "汉以来多任意揣摩如盲人射的虚发无效或依儗形似如持萤烛象得首失尾",
 "将以习人之灵才令细而确也",
 "余以为小用大用实在其人如邓林伐材栋梁榱桷恣所取之耳",
 "大者修身事天小者格物穷理",
 "趋欲先其易信",
 "凡论几何先从一防始自防引之为线线展为靣靣积为体是名三度",
 "防者无分",
 "线有长无广",
 "试如一平靣光照之有光无光之间不容一物是线也",
 "两防之间至径者直线也稍曲则绕而长矣",
 "靣者止有长有广",
 "想一线横行所留之迹即成靣也",
 "界者一物之终始",
 "防为线之界线为靣之界靣为体之界体不可为界",
 "圜者一形于平地居一界之间自界至中心作直线俱等",
 "求作者不得言不可作",
 "自此防至彼防求作一直线",
 "有界直线求从彼界直行引长之",
 "不论大小以防为心求作一圜",
 "设一度于此求作彼度较此度或大或小",
 "尝见庄子称一尺之棰日取其半万世不竭",
 "公论者不可疑",
 "全大于其分",
 "直角俱相等",
 "全与诸分之并等",
 "有二横直线或正或偏任加一纵线若三线之间同方两角小于两直角则此二横直线愈长愈相近必至相遇",
 "欲明此理宜察平行线不得相遇者界说卅四加一垂线即三线之间定为直角",
 "于有界直线上求立平边三角形",
 "凡为圜自心至界各线俱等",
 "彼此俱与他等则彼与此自相等",
 "先以甲为心乙为界作丙乙丁圜次以乙为心甲为界作丙甲丁圜两圜相交于丙于丁",
 "一直线求作理分中末线",
 "其书每卷有界说有公论有设题",
 "先其易者次其难者由浅而深由简而繁推之至于无以复加而后已",
 "卷一论三角形卷二论线卷三论圆卷四论圆内外形卷五卷六俱论比例",
 "欧几里得未详何时人",
 "原书十三卷五百余题",
 "今止六卷者徐光启自谓译受是书此其最要者也",
 "西洋欧几里得撰利玛窦译而徐光启所笔受也",
 "吴淞徐光启书",
 "乾隆四十六年十二月恭校上",
 "不用为用众用所基",
 "真可谓万象之形囿百家之学海",
 "由显入微从疑得信",
]

# ---------- 3. 逐条核验 ----------
uniq_fail = []
for q in EXPECTED:
    if q not in pageq:
        # 允许为某条长引文的子串（嵌套）的情况：检查它是否库内存在且页内作为更长 span 的一部分
        if q in libnorm and any(q in p for p in pageq):
            warns.append('嵌套子引文（不独立成 span）: ' + q[:24])
        else:
            errs.append('页面未找到 .q 引文: ' + q[:30])
    if q not in libnorm:
        errs.append('库本不含该引文: ' + q[:30])
    elif libnorm.count(q) != 1 and q not in uniq_fail:
        uniq_fail.append(q)
if uniq_fail:
    warns.append('库内多次出现（以整句入页保证唯一）: ' + ' | '.join(uniq_fail))

# ---------- 4. 排版红线 ----------
if '—' in html or '–' in html:
    errs.append('页面出现长划线')
for i, ln in enumerate(html.split('\n'), 1):
    if ln.count('·') > 1:
        errs.append(f'第{i}行 · 超过 1 枚')
if '·' not in html:
    pass
else:
    warns.append('页面含 · ，已逐行检查 ≤1')

# ---------- 5. 机数复算 ----------
p1 = lib.find('界说三十六则'); p2 = lib.find('求作四则'); p3 = lib.find('公论者不可疑'); p4 = lib.find('第一题')
jie = len(re.findall(r'第[一二三四五六七八九十]+界', lib[p1:p2]))
qiu = len(re.findall(r'第[一二三四五六七八九十]+求', lib[p2:p3]))
gong = len(re.findall(r'第[一二三四五六七八九十]+论', lib[p3:p4]))
if (jie, qiu, gong) != (36, 4, 19):
    errs.append(f'界说/求作/公论 计数异常: {jie}/{qiu}/{gong}')

nospace = len(lib.replace(' ', '').replace('\n', ''))
han = len(re.findall(r'[㐀-鿿]', lib))
for need, lab in [(f'{nospace:,}', '去空白字数'), (f'{han:,}', '汉字数')]:
    if need not in html:
        errs.append(f'页面缺机数 {lab}={need}')

for ch, n, lab in [('防', 169, '防'), ('点', 17, '点'), ('靣', 33, '靣'), ('圜', 886, '圜'), ('邉', 317, '邉')]:
    c = lib.count(ch)
    if c != n:
        errs.append(f'库本 {lab} 计数 {c} != 页面/校记 {n}')
if '一百六十九见' not in html or '十七见' not in html:
    errs.append('页面缺 防/点 讹字计数')

for v in '一二三四五六':
    if lib.count(f'几何原本卷{v}之首') != 2:
        errs.append(f'卷{v}之首 出现次数异常')

# 卷签顺序与提要句一致
tags = re.findall(r'<div class="vt">([^<]*)</div>', html)
if tags != ['三角形', '线', '圆', '圆内外形', '比例', '比例']:
    errs.append(f'卷签顺序异常: {tags}')

# 缺字虚框存在且「火」未混入引文
if '<span class="lost">火</span>' not in html:
    errs.append('缺字虚框丢失')
if norm('毕丧于祖龙之火') in libnorm:
    errs.append('库本竟含「祖龙之火」，虚框前提不成立')

# 页面骨架
if '导读之九十八' not in html or '殆知阁导读　之九十八' not in html:
    errs.append('页内序号非 98')
if '卷五十六 量法' not in html:
    errs.append('缺卷五十六 量法标属')
for need in ['github.com/robertsong2000/daizhigev20', '逐字核对', '传教语境']:
    if need not in html:
        errs.append('页脚缺: ' + need)

# ---------- 6. 汇总 ----------
print(f'.q spans 收集: {len(qc.spans)} 条（norm 后有效 {len(pageq)}）')
print(f'期望引文: {len(EXPECTED)} 条全数入页且库内可对' if not errs else '')
for w in warns: print('WARN:', w)
if errs:
    print('FAIL:')
    [print('  -', e) for e in errs]
    sys.exit(1)
print('ALL PASS')
