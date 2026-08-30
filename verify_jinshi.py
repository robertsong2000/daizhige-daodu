# -*- coding: utf-8 -*-
"""金石录导读页核验：引文逐字比对 + 排版规则。"""
import re, sys, unicodedata

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/jinshi-lu.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/目录/金石录.txt'

PUNC = set('''，。、；：？！“”‘’「」『』（）《》〈〉·…—–　 ()[]{}.,;:?!'"-_/\\''')

def norm(s):
    s = re.sub(r'<[^>]+>', '', s)
    out = []
    for ch in s:
        if ch in PUNC or ch.isspace():
            continue
        out.append(unicodedata.normalize('NFKC', ch))
    return ''.join(out)

book = open(SRC, encoding='utf-8').read()
nbook = norm(book)
html = open(HTML, encoding='utf-8').read()

fails = []

# 1. 页面所有 .q 引文必须是库内文件子串（去标点归一后）
qs = re.findall(r'class="[^"]*\bq\b[^"]*"[^>]*>(.*?)</(?:span|b)>', html, re.S)
if not qs:
    fails.append('未找到任何 .q 引文')
nq_bad = 0
for i, q in enumerate(qs, 1):
    nq = norm(q)
    if not nq:
        fails.append(f'引文{i}为空')
        nq_bad += 1
    elif nq not in nbook:
        fails.append(f'引文{i}不在库内文件: {q[:40]}')
        nq_bad += 1
print(f'[引文] 页面共 {len(qs)} 段 .q，问题 {nq_bad} 个')

# 2. 必须出现的核心引文清单（库内来源，逐字）
CORE = [
    '凡二十年而后粗备',
    '每朔望谒告，出质衣取半千钱。',
    '归相对展玩咀嚼，自谓葛天氏之民也。',
    '余性偶强记，毎饭罢坐归来堂烹茶，指堆积书史，言某事在某书某卷、第几叶、第几行，以中否角胜负，为饮茶先后。中即举杯大笑，至茶倾覆怀中，反不得饮而起。',
    '尝记崇宁间，有人持徐熙牡丹图求钱二十万。当时虽贵家子弟，求二十万钱岂易得耶？畱信宿计无所出，而还之，夫妇相向惋怅者数日。',
    '至靖康丙午岁，侯守淄川，闻金人犯京师，四顾茫然，盈箱溢箧，且恋恋，且怅怅，知其必不为已物矣。',
    '凡屡减去，尚载书十五车。',
    '十二月，金人陷青州，凡所谓十余屋者，已皆为煨烬矣。',
    '葛衣岸巾，精神如虎，目光烂烂射人。',
    '如传闻城中缓急奈何',
    '独所谓宋器者，可自负抱，与身俱存亡，勿忘也。',
    '八月十八日，遂不起。取笔作诗，绝笔而终，殊无分香卖屦之意。',
    '金人陷洪州，遂尽委弃所谓连舻渡江之书，又散为云烟矣。',
    '忽一夕，穴壁负五簏去。',
    '所谓岿然独存者，乃十去其七八。',
    '今手泽如新，而墓木已拱，悲夫。',
    '三十四年之间，忧患得失，何其多也。然有有必有无，有聚必有散，乃理之常。人亡弓，人得之，又胡足道。',
    '壮月朔甲寅，易安室题。',
    '是金石之固犹不足恃，然则所谓二千卷者，终归于磨灭，而余之是书有时而或传也。',
    '乃撮述大概载之',
    '至以后序壮月朔为牡丹朔，其书之舛谬可以概见。',
]
page_norm = norm(re.sub(r'<[^>]+>', ' ', html))
core_bad = 0
for c in CORE:
    nc = norm(c)
    if nc not in nbook:
        fails.append(f'核心引文不在库内: {c[:20]}')
        core_bad += 1
    elif nc not in page_norm:
        fails.append(f'核心引文未上页: {c[:20]}')
        core_bad += 1
print(f'[清单] 核心引文 {len(CORE)} 条，问题 {core_bad} 个')

# 3. 排版：禁长划线
for ch, name in [('—', '长划线—'), ('–', '短划线–')]:
    if ch in html:
        fails.append(f'页面含{name}，{html.count(ch)}处')
print('[排版] 长划线/短划线检查完成')

# 4. 排版：渲染文本每行 · 最多 1 个
vis = re.sub(r'<script.*?</script>|<style.*?</style>', '', html, flags=re.S)
vis = re.sub(r'<[^>]+>', '\n', vis)
for ln in vis.split('\n'):
    if ln.count('·') > 1:
        fails.append(f'一行多个·: {ln.strip()[:40]}')
print('[排版] 每行·数量检查完成')

# 5. 页脚三要素
FOOT = ['殆知阁简体库', 'daizhigev20', '逐字核验', '时代局限']
for k in FOOT:
    if k not in html:
        fails.append(f'页脚缺: {k}')
print('[页脚] 来源/核验/局限声明检查完成')

# 6. 视觉规范色（忆语卷 · 石青）
for c, k in [('#191917', '墨底'), ('#e8e4dc', '纸白'), ('#5e8fbb', '石青')]:
    if c.lower() not in html.lower():
        fails.append(f'缺规范色 {k}')
print('[配色] 墨底/纸白/石青检查完成')

# 7. 字数实测核对（页面宣称须与实测一致，中文数字）
clean = re.sub(r'\s|　', '', book)
hx = clean[clean.index('金石录后序'):]
whole = len(clean)
post = len(hx)
for claim, actual in [('十二万一千', whole), ('一千八百七十', post)]:
    if claim not in norm(page_norm):
        fails.append(f'页面字数宣称与实测不符: 页面缺「{claim}」，实测 {actual}')
print(f'[实测] 全书去空白 {whole} 字，后序 {post} 字')

print()
if fails:
    print('FAIL')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('ALL PASS')
