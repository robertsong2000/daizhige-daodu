#!/usr/bin/env python3
# 周易参同契 页面核验：引文双侧逐字（库本命中+页面反扫）+ 库本机数 + 排版红线
import re, sys
from html.parser import HTMLParser

PAGE = 'cantongqi.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/道藏/藏外/周易参同契.txt'

page = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()

errs = []
def chk(cond, msg):
    if not cond: errs.append(msg)

def norm(s):
    out = []
    for ch in s:
        if ch.isspace(): continue
        o = ord(ch)
        if (0x3000 <= o <= 0x303F) or (0xFF00 <= o <= 0xFFEF and not (0xFF21 <= o <= 0xFF5A)) \
           or ch in '「」『』“”‘’·，。、；：？！〈〉《》()(){}[]<>' or (o < 0x2E80 and not ch.isalnum()) \
           or (0x2018 <= o <= 0x201F):
            continue
        out.append(ch)
    return ''.join(out)

libn = norm(lib)
pagen = norm(page)

# ---------- 库本机数 ----------
libnw = re.sub(r'\s', '', lib)
chk(len(libnw) == 7748, f'库本去空白字符 {len(libnw)} != 7748')
chk(libnw.count('○') == 90, f'○段 {libnw.count("○")} != 90')
chk(libnw.count('【') == 2, f'【篇 {libnw.count("【")} != 2')
chk('【鼎器歌】' in lib and '【赞序】' in lib, '缺鼎器歌或赞序')
for w, n in [('火',27),('金',29),('月',25),('日',33),('龙',17),('虎',9),('丹',4),('铅',4),
             ('汞',1),('水银',1),('姹女',2),('黄芽',4),('流珠',3),('还丹',3),('鼎',7),
             ('坎',9),('离',13),('乾坤',10),('会稽',1),('魏',0),('参同契',4)]:
    c = libnw.count(w)
    chk(c == n, f'库本「{w}」{c}见 != {n}见')

# ---------- 期望引文清单（库本命中 + 页面在场，双侧）----------
# 省略号……表示节引，逐段拆开双侧校验
EXPECTED = [
    '晦至朔旦。震来受符。',
    '火记六百篇。所趣等不殊。文字郑重说。世人不熟思。',
    '若遂结舌喑。绝道获罪诛。写情着竹帛。又符泄天符。犹豫增叹息。俛仰缀斯愚。',
    '陶冶有法度。未忍悉陈敷。略述其纲纪。枝条见扶疏。',
    '吾不敢虚说。仿效圣人文。',
    '至要言甚露。昭昭不我欺',
    '大易情性。各如其度。黄老用究。较而可御。炉火之事。真有所据。三道由一。俱出径路。',
    '乾坤者易之门户。众卦之父母。坎离匡郭。运毂正轴。',
    '内以养己。安静虚无',
    '参同契者。敷陈梗概。不能纯一。泛滥而说。纤微未备。阔略仿佛。',
    '三日出为爽。震庚受西方。八日兑受丁。上弦平如绳。十五干体就。盛满甲东方。蟾蜍与兔魄。日月气双明。',
    '十六转受统。巽辛见平明。艮直于丙南。下弦二十三。坤乙三十日。东北丧其朋。节尽相禅与。继体复生龙。',
    '名者以定情。字者缘性言。金来归性初。乃得称还丹。',
    '河上姹女。灵而最神。得火则飞。不见埃尘。鬼隐龙匿。莫知所存。将欲制之。黄芽为根。',
    '金以砂为主。禀和于水银',
    '太阳流珠。常欲去人。卒得金华。转而相因。',
    '故铅外黑。内怀金华。被褐怀玉。外为狂夫。',
    '知白守黑。神明自来。白者金精。黑者水基。',
    '色转更为紫。赫然成还丹。粉提以一丸。刀圭最为神。',
    '丹砂木精。得金乃并。金水合处。木火为侣。四者混沌。列为龙虎。',
    '金入于猛火。色不夺精光。',
    '术士服食之。寿命得长久。',
    '发白皆变黑。齿落生旧所。老翁复丁壮。耆妪成姹女。',
    '世间多学士。高妙负良才。邂逅不遭遇。耗火亡货财。',
    '千举必万败。欲黠反成痴。',
    '捣治羌石胆。云母及礜磁。硫黄烧豫章。泥澒相炼飞。',
    '不得其理。难以妄言。竭殚家产。妻子饥贫。自古及今。好者亿人。讫不谐遇。希有能成。',
    '昼夜不卧寐。晦朔未尝休。身体日疲倦。恍惚状若痴。',
    '遽以夭命死。腐露其形骸。',
    '遂使宦者不仕。农夫失耘。商人弃货。志士家贫。吾甚伤之。',
    '若以野葛一寸。巴豆一两。入喉辄僵。……虽周文揲蓍。孔子占象。扁鹊操针。巫咸扣鼓。安能令苏。复起驰走。',
    '假使二女共室。颜色甚姝。令苏秦通言。张仪结媒。发辩利舌。奋舒美辞。推心调谐。合为夫妻。弊发腐齿。终不相知。',
    '燕雀不生凤。狐兔不乳马。水流不炎上。火动不润下。',
    '牝鸡自卵。其雏不全。',
    '圆三五。寸一分。口四八。两寸唇。长尺二。厚薄匀。腹齐三。坐垂温。阴在上。阳下奔。首尾武。中间文。',
    '临炉定铢两。五分水有余。',
    '始文使可修。终竟武乃陈。候视加谨慎。审察调寒温。周旋十二节。节尽更须亲。',
    '耳目口三宝。固塞勿发扬。真人潜深渊。浮游守规中。',
    '淫淫若春泽。液液象解冰。从头流达足。究竟复上升。',
    '反者道之验。弱者德之柄。',
    '浊者清之路。昏久则昭明。',
    '偃月法鼎炉',
    '会稽鄙夫。幽谷朽生。挟怀朴素。不乐欢荣。栖迟僻陋。忽略利名。执守恬淡。希时安平。宴然闲居。乃撰斯文。',
    '委时去害。依托丘山。循游寥廓。与鬼为邻。',
    '百世一下。遨游人间。',
    '汤遭厄际。水旱隔并。',
    '命参同契。微览其端。辞寡意大。后嗣宜遵。',
    '千周灿彬彬兮。万遍将可睹。神明或告人兮。心灵乍自悟。探端索其绪兮。必得其门户。',
    '露见枝条。隐藏本根。托号诸石。覆谬众文。',
    '参同契者。辞隐而道大。言微而旨深。',
    '故复作此。命五相类。',
    '复卦建始萌。长子继父体。因母立兆基。',
    '仰以成泰。刚柔并隆。',
    '干健盛明。广被四邻。',
    '道穷则反。归乎坤元。',
    '剥烂肢体。消灭其形。',
    '渐历大壮。侠列卯门。',
    '姤始纪序。履霜最先。',
    '遁去世位。收敛其精。',
    '终坤始复。始循连环',
    '合符行中',
    '亦犹和胶补釜。以涂疮',
]

miss_lib = []
miss_page = []
for e in EXPECTED:
    for frag in [f for f in e.split('……') if f]:
        fn = norm(frag)
        if fn not in libn: miss_lib.append(frag[:24])
        if fn not in pagen: miss_page.append(frag[:24])
chk(not miss_lib, f'期望引文 {len(miss_lib)} 段未命中库本: {miss_lib}')
chk(not miss_page, f'期望引文 {len(miss_page)} 段不在页面: {miss_page}')

# ---------- 页面 .q 收集（剔除 .src 注）----------
page_q = re.sub(r'<span class="src">[\s\S]*?</span>', '', page)
QCOL = []
for m in re.finditer(r'<q class="q">([\s\S]*?)</q>|<div class="q">([\s\S]*?)</div>', page_q):
    txt = m.group(1) if m.group(1) is not None else m.group(2)
    txt = re.sub(r'<[^>]+>', '', txt)
    if txt.strip(): QCOL.append(txt)

bad = 0
for q in QCOL:
    frags = [norm(f) for f in q.split('…') if f.strip()]
    for f in frags:
        if f and f not in libn:
            bad += 1
            print(f'  [X] .q 未命中库本: {f[:40]}')
chk(bad == 0, f'{bad} 枚 .q 段未过库本核验')

# ---------- 「」反扫：所有引号内容必须是库本原文 ----------
body_no_style = re.sub(r'<style>[\s\S]*?</style>', '', page)
vis = re.sub(r'<[^>]+>', '', body_no_style)
brbad = []
for m in re.finditer(r'「([^」]*)」', vis):
    bn = norm(m.group(1))
    if not bn: continue
    if bn not in libn: brbad.append(m.group(1)[:24])
chk(not brbad, f'「」反扫 {len(brbad)} 处未命中库本: {brbad}')

# ---------- 页面机数文案 ----------
for txt in ['全帙 7,748 字符', '凡九十段', '【鼎器歌】', '【赞序】', '本系列第 120 篇《神仙传》',
            '殆知阁导读之一百七十二']:
    chk(txt in page, f'页面机数文案缺: {txt[:24]}')

# ---------- 编号 / 卷次 ----------
chk(page.count('之一百七十二') == 3, f'编号出现 {page.count("之一百七十二")} 次 != 3（title+kicker+footer）')
chk(page.count('卷六') >= 2, '卷六出现不足')
chk(page.count('工造') >= 2, '工造出现不足')
chk('<title>周易参同契 · 殆知阁导读之一百七十二</title>' in page, 'title 不符')

# ---------- 页脚要素 ----------
for t in ['殆知阁简体库', '逐字核验', 'robertsong2000/daizhigev20', 'daizhige-daodu',
          '不可效仿', '操作手册', '流传通说']:
    chk(t in page, f'页脚缺: {t}')

# ---------- 排版红线 ----------
chk('—' not in page and '–' not in page, '存在长划线')
for i, l in enumerate(page.split('\n'), 1):
    c = l.count('·')
    chk(c <= 1, f'第 {i} 行有 {c} 枚 ·: {l.strip()[:60]}')
vis2 = re.sub(r'github\.com/[A-Za-z0-9/\-]+', '', vis)
en = re.findall(r'[A-Za-z]{2,}', vis2)
chk(not en, f'可见文本英文残留: {en[:8]}')
chk('<script' not in page.lower(), '存在 script')
chk('src=' not in page.lower(), '存在 src=')
chk('url(' not in page.lower(), '存在 url(')
for h in re.findall(r'href="([^"]*)"', page):
    chk(re.fullmatch(r'[a-z0-9\-]+\.html', h), f'外链或异常 href: {h}')

print()
print('=== 机数摘要 ===')
print(f'库本 {len(libnw)} 字符（去空白）/ ○段 {libnw.count("○")} / 附【鼎器歌】【赞序】')
print(f'期望引文 {len(EXPECTED)} 条（省略号拆段后逐段双侧），页面 .q 段 {len(QCOL)} 枚')
print(f'「」反扫全部命中库本；红线：无长划线、每行·≤1、无 script/src/url、href 全相对')
print()
if errs:
    print('FAIL:')
    for e in errs: print(' x', e)
    sys.exit(1)
print('ALL PASS')
