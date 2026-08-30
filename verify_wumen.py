#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_wumen.py — 《无门关》导读页核验：引文逐字对库 + 结构 + 机数 + 红线"""
import re, sys
from html.parser import HTMLParser

PAGE = 'wumen-guan.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/佛藏/大藏经/论藏/诸宗部/无门关.txt'

raw_lib = open(LIB, encoding='utf-8').read()
lib_nospace = re.sub(r'\s', '', raw_lib)

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

libn = norm(lib_nospace)

page = open(PAGE, encoding='utf-8').read()

# ---------- 1. 收集页面全部 .q（栈配平，剥内嵌标签；回溯最近 q 祖先收字） ----------
VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'area', 'source', 'wbr'}
class QCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.qs = []          # 收集完成的 q 文本
        self.stack = []       # [tag, is_q, buf]
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        cls = dict(attrs).get('class', '') or ''
        is_q = 'q' in cls.split()
        self.stack.append([tag, is_q, []])
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                t, is_q, buf = self.stack.pop(i)
                if is_q:
                    outer = next((x for x in reversed(self.stack) if x[1]), None)
                    if outer is not None:
                        outer[2].extend(buf)
                    else:
                        self.qs.append(''.join(buf))
                else:
                    outer = next((x for x in reversed(self.stack) if x[1]), None)
                    if outer is not None and buf:
                        outer[2].extend(buf)
                return
    def handle_data(self, data):
        q = next((x for x in reversed(self.stack) if x[1]), None)
        if q is not None:
            q[2].append(data)

qc = QCollector()
qc.feed(page)
page_qs = [re.sub(r'\s+', '', q) for q in qc.qs]
page_qs = [q for q in page_qs if q]

errs, warns = [], []

# ---------- 2. 逐条 .q 对库 ----------
seen = {}
for q in page_qs:
    qn = norm(q)
    if not qn:
        errs.append(f'空引文: {q[:30]}')
        continue
    if qn not in libn:
        errs.append(f'引文不在库本: {qn[:60]}')
    seen[qn] = seen.get(qn, 0) + 1
for qn, n in seen.items():
    if n > 1:
        warns.append(f'引文复现 {n} 次（刻意复现则忽略）: {qn[:30]}')

# ---------- 3. 关键引文清单（必须全部命中） ----------
QUOTES = [
    '大道无门　　千差有路　　透得此关　　乾坤独步',
    '宋 宗绍编', '参学比丘弥衍宗绍编',
    '佛语心为宗。无门为法门。既是无门。且作么生透。',
    '从门入者。不是家珍。从缘得者。始终成坏。',
    '遂将古人公案。作敲门瓦子。随机引导学者。竟尔抄录。不觉成集。',
    '初不以前后叙列。共成四十八则。通曰无门关。',
    '第一强添几个注脚。大似笠上顶笠。',
    '硬要习翁赞扬。又是干竹绞汁。',
    '一掷莫教一滴落江湖。千里乌骓追不得。',
    '旹绍定改元解制前五日。杨岐八世孙无门比丘慧开谨识。',
    '绍定二年正月初五日。恭遇天基圣节。臣僧慧开。预于元年十二月初五日。印行拈提佛祖机缘四十八则。祝延今上皇帝圣躬万岁万岁万万岁。',
    '慈懿皇后功德报因佑慈禅寺前住持传法臣僧慧开谨言',
    '赵州和尚因僧问。狗子还有佛性。也无。州云无。',
    '如吞了个热铁丸。相似吐又吐不出。',
    '昼夜提撕。莫作虚无会。莫作有无会。',
    '逢佛杀佛。逢祖杀祖。于生死岸头得大自在。',
    '尽平生气力。举个无字。',
    '狗子佛性　　全提正令　　才涉有无　　丧身失命',
    '大修行底人还落因果。也无。',
    '五百生堕野狐身',
    '师云。不昧因果。老人于言下大悟。',
    '以杖挑出一死野狐。乃依火葬。',
    '将谓。胡须赤更有赤须胡。',
    '不落因果。为甚堕野狐。不昧因果。为甚脱野狐。',
    '不落不昧　　两采一赛　　不昧不落　　千错万错',
    '俱胝和尚。凡有诘问。唯举一指。',
    '胝闻。遂以刃断其指。',
    '吾得天龙一指头禅。一生受用不尽。',
    '俱胝并童子悟处。不在指头上。',
    '俱胝钝置老天龙　　利刃单提勘小童　　巨灵抬手无多子　　分破华山千万重',
    '世尊昔在灵山会上。拈花示众。是时众皆默然。惟迦叶尊者破颜微笑。',
    '吾有正法眼藏涅槃妙心实相无相微妙法门。不立文字教外别传。付嘱摩诃迦叶。',
    '黄面瞿昙傍若无人。压良为贱。悬羊头卖狗肉。',
    '设使迦叶不笑。正法眼藏又作么生传。',
    '拈起花来　　尾巴已露　　迦叶破颜　　人天罔措',
    '吃粥了也未。',
    '洗钵盂去。',
    '赵州开口见胆。露出心肝',
    '只为分明极　　翻令所得迟　　早知灯是火　　饭熟已多时',
    '泉云。平常心是道。',
    '拟向即乖',
    '道不属知。不属不知。知是妄觉。不知是无记。',
    '州于言下顿悟。',
    '南泉被赵州发问。直得瓦解冰消分疏不下。',
    '春有百花秋有月　　夏有凉风冬有雪　　若无闲事挂心头　　便是人间好时节',
    '如何是佛。门云干屎橛。',
    '家贫难辨素食。事忙不及草书。',
    '动便将屎橛来。撑门拄户。佛法兴衰可见。',
    '闪电光　　击石火　　眨得眼　　已蹉过',
    '此衣表信。可力争耶。',
    '我来求法。非为衣也。',
    '不思善不思恶。正与么时那个是明上座。本来面目。',
    '明当下大悟。遍体汗流。',
    '如人饮水冷暖自知。',
    '譬如新荔支剥了壳。去了核送在尔口里。只要尔咽一咽。',
    '描不成兮画不就　　赞不及兮休生受　　本来面目没处藏　　世界坏时渠不朽',
    '达磨面壁。二祖立雪断臂云。弟子心未安。乞师安心。磨云。将心来。与汝安。祖云。觅心了不可得。磨云。为汝安心竟。',
    '缺齿老胡。十万里航海特特而来。可谓是无风起浪。',
    '西来直指　　事因嘱起　　挠聒丛林　　元来是尔',
    '文殊绕女人三匝。鸣指一下。乃托至梵天。尽其神力。而不能出。',
    '假使百千文殊亦出此女人定不得',
    '须臾罔明大士从地涌出。',
    '鸣指一下。女人于是从定而出。',
    '释迦老子做者一场杂剧。不通小小。',
    '出得出不得　　渠侬得自由　　神头并鬼面　　败阙当风流',
    '山云。麻三斤。', '门云干屎橛。', '祖云。即心是佛。', '祖曰。非心非佛。',
    '老不识羞。才开臭口。家丑外扬。',
    '粗餐易饱。细嚼难饥。',
    '无庵欲赘。一语又成四十九则。',
    '第四十九则语',
    '止止不须说我法妙难思。',
    '大藏五千卷。维摩不二门。总在里许。',
    '语火是灯　　掉头弗应　　惟贼识贼　　一问即承',
    '淳祐丙午季夏初吉安晚居士书于西湖渔庄',
    '作四十八则语。判断古德公案。大似卖油饼。',
    '再打一枚足成大衍之数。',
    '检校少保宁武军节度使京湖安抚制置大使兼屯田大使兼夔路策应大使兼知江陵府汉东郡开国公食邑二千一百户食实封陆佰户',
    '孟珙　跋',
    '瑞岩近日有无门　掇向绳床判古今　凡圣路头俱截断　几多蟠蛰起雷音',
    '无门首座',
    '旧板磨灭故。重命工锓梓毕。这板置于武藏州兜率山广园禅寺也。',
    '应永乙酉十月十三日　干缘比丘　常牧',
    '循规守矩。　　无绳自缚。',
    '念起即觉。　　弄精魂汉。',
    '努力今生须了却。　　莫教永劫受余殃。',
    '我手何似佛手。', '我脚何似驴脚。', '人人有个生缘。',
    '佛手驴脚生缘。　　非佛非道非禅。　　莫怪无门关险。　　结尽衲子深冤。',
    '在者里。',
    '上三十三天。筑著帝释鼻孔。东海鲤鱼打一棒。雨似盆倾。',
    '一人向深深海底。行簸土扬尘。一人于高高山顶。立白浪滔天。',
    '正眼观来。二大老总未识路头在。',
    '直饶著著在机先　　更须知有向上窍',
    '若透得无门关。早是钝置无门。',
    '若透不得无门关。亦乃辜负自己。',
    '从上佛祖垂示机缘。据款结案。初无剩语。',
    '掉臂度关。不问关吏。',
    '压良为贱', '无风起浪',
]
for q in QUOTES:
    qn = norm(q)
    if qn not in libn:
        errs.append(f'清单引文不在库本: {qn[:50]}')
    if qn not in norm(page):
        errs.append(f'清单引文不在页面: {qn[:50]}')

# ---------- 4. 门墙结构：48 门序题与库本目录全等 ----------
door_sec = page.split('id="doorwall"')[1].split('</section>')[0]
doors = re.findall(r'<div class="door( lit)?"><span class="dno mono">(\d+)</span><span class="dti">(\S+)</span>', door_sec)
if len(doors) != 48:
    errs.append(f'门数 {len(doors)} != 48')
nums = [int(d[1]) for d in doors]
if nums != list(range(1, 49)):
    errs.append(f'门序不连续: {nums}')
lit = sum(1 for d in doors if d[0])
if lit != 10:
    errs.append(f'点亮门 {lit} != 10')
# 库本目录 48 题：逐行按全角空格切
toc_zone = raw_lib.split('　　目录')[1].split('目录(终)')[0]
toc = []
for ln in toc_zone.split('\n'):
    ln = ln.strip().strip('　')
    if not ln:
        continue
    for name in ln.split('　'):
        name = name.strip()
        if len(name) == 4:
            toc.append(name)
if len(toc) != 48:
    errs.append(f'目录解析 {len(toc)} 题 != 48: {toc}')
page_titles = [d[2] for d in doors]
if toc != page_titles:
    for i, (a, b) in enumerate(zip(toc, page_titles)):
        if a != b:
            errs.append(f'门{i+1} 题不符: 库本{a} vs 页面{b}')
            break
# 目录顺序 == 正文顺序
body_zone = raw_lib.split('目录(终)')[1].split('从上佛祖垂示机缘')[0]
pos = 0
for i, t in enumerate(toc):
    p = body_zone.find(t, pos)
    if p < 0:
        errs.append(f'正文缺则题: {t}')
        pos = len(body_zone)
    else:
        pos = p + len(t)
# 每题全书至少 2 见（目录+正文；无门曰复提至多 4 见）
for t in toc:
    c = lib_nospace.count(t)
    if not (2 <= c <= 4):
        errs.append(f'则题「{t}」全书 {c} 见，越界')

# ---------- 5. 机数断言（库本实测 == 页面宣称） ----------
def cnt(s): return lib_nospace.count(s)
checks = [
    ('无门曰', 48, '48'),
    ('颂曰', 50, '50'),
    ('无', 125, '125'),
    ('门', 108, '108'),
    ('赵州', 24, '24 见'),
    ('云门', 13, '13 见'),
    ('南泉', 11, '11 见'),
    ('迦叶', 9, '9 见'),
    ('文殊', 6, '6 见'),
    ('达磨', 4, '4 见'),
    ('如何是佛', 4, '四见'),
    ('若向者里', 15, '15'),
    ('且道', 18, '18'),
    ('者里', 17, '17'),
    ('转语', 7, '7'),
    ('其或未然', 7, '7'),
]
for k, libc, ptoken in checks:
    if cnt(k) != libc:
        errs.append(f'机数不符「{k}」: 库本 {cnt(k)} != 断言 {libc}')
    if ptoken not in page:
        errs.append(f'页面缺机数标记「{ptoken}」')
nc = len(re.sub(r'\s', '', raw_lib))
if nc != 9181:
    errs.append(f'全帙去空白 {nc} != 9181')
hn = sum(1 for c in lib_nospace if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x3FFFF)
if hn != 7949:
    errs.append(f'汉字 {hn} != 7949')
if '9,181' not in page: errs.append('页面缺 9,181')
if '7,949' not in page: errs.append('页面缺 7,949')
brackets = re.findall(r'\[[^\]]{1,12}\]', raw_lib)
if len(brackets) != 7:
    errs.append(f'拆字括注 {len(brackets)} != 7')
if '7 处' not in page: errs.append('页面缺「7 处」')
# 拆字段不得进入页面
for b in brackets:
    if b in page:
        errs.append(f'拆字括注进了页面: {b}')

# ---------- 6. 篇号 ----------
if '之一百零二' not in page: errs.append('缺篇号 之一百零二')

# ---------- 7. 红线 ----------
if '—' in page: errs.append('页面含长划线 —')
if '–' in page: errs.append('页面含 – ')
for i, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        errs.append(f'第{i}行 · 超限 ({line.count("·")})')
for ch in set(page):
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF or 0x20000 <= o <= 0x3FFFF:
        errs.append(f'页面含私用/Ext-B 字: {hex(o)}')

# ---------- 8. 页面引用计数自洽 ----------
if len(page_qs) < 60:
    warns.append(f'页面 .q 仅 {len(page_qs)} 条（<60，确认无漏包）')

print(f'.q 共 {len(page_qs)} 条；QUOTES {len(QUOTES)} 条；门 {len(doors)}（亮 {lit}）')
if errs:
    print(f'FAIL {len(errs)} 项:')
    for e in errs: print('  ✗', e)
    sys.exit(1)
print('PASS: 引文逐字对库 + 门墙结构 + 机数 + 红线 全过')
for w in warns: print('  ⚠', w)
