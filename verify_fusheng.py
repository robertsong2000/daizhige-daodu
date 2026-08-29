# -*- coding: utf-8 -*-
"""浮生六记导读页核验：引文逐字比对 + 排版规则。"""
import re, sys, unicodedata

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/fusheng-liuji.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/浮生六记.txt'

PUNC = set('''，。、；：？！“”‘’「」『』（）《》〈〉·…—–　 ()[]{}.,;:?!'"-_/\\''')

def norm(s):
    s = re.sub(r'<[^>]+>', '', s)
    out = []
    for ch in s:
        if ch in PUNC or ch.isspace():
            continue
        n = unicodedata.normalize('NFKC', ch)
        out.append(n)
    return ''.join(out)

book = open(SRC, encoding='utf-8').read()
nbook = norm(book)
html = open(HTML, encoding='utf-8').read()

fails = []

# 1. 页面所有 .q 引文必须是库内文件子串（去标点归一后）
qs = re.findall(r'class="[^"]*\bq\b[^"]*"[^>]*>(.*?)</(?:span|b)>', html, re.S)
if not qs:
    fails.append('未找到任何 .q 引文')
for i, q in enumerate(qs, 1):
    nq = norm(q)
    if not nq:
        fails.append(f'引文{i}为空')
    elif nq not in nbook:
        fails.append(f'引文{i}不在库内文件: {q[:40]}')
print(f'[引文] 页面共 {len(qs)} 段 .q，问题 {sum(1 for f in fails if f.startswith("引文"))} 个')

# 2. 必须出现的核心引文清单（库内来源，逐字）
CORE = [
    '东坡云：“事如春梦了无痕”，苟不记之笔墨，未免有辜彼苍之厚。',
    '芸暗牵余袖，随至其室，见藏有暖粥并小菜焉。',
    '秋侵人影瘦，霜染菊花肥',
    '余执朱文，芸执白文',
    '来世卿当作男，我为女子相从。',
    '布衣菜饭，可乐终身，不必作远游计也。',
    '情之所钟，虽丑不嫌。',
    '后憨为有力者夺去，不果。芸竟以之死。',
    '留蚊于素帐中，徐喷以烟，使其冲烟飞鸣，作青云白鹤观，果如鹤唳云端，怡然称快。',
    '以丛草为林，以虫蚁为兽，以土砾凸者为丘，凹者为堑',
    '谈官宦升迁、公廨时事、八股时文、看牌掷色，有犯必罚酒五厅。',
    '慷慨豪爽、风流蕴藉、落拓不羁、澄静缄默。',
    '汝携妇别居，勿使我见',
    '芸出巷十数步，已疲不能行，使妪提灯，余背负之而行。',
    '昔一粥而聚，今一粥而散，若作传奇，可名《吃粥记》矣。',
    '知己如君，得婿如此，妾已此生无憾！',
    '若布衣暖，菜饭饱，一室雍雍，优游泉石，如沧浪亭、萧爽楼之处境，真成烟火神仙矣。',
    '死生有命。君果关切，伴我何如？',
    '重阳日，邻冢皆黄，芸墓独青。',
    '奉劝世间夫妇，固不可彼此相仇，亦不可过于情笃。',
    '恩爱夫妻不到头',
    '余游幕三十年来，天下所未到者，蜀中、黔中与滇南耳。',
    '花开数十里，一望如积雪，故名“香雪海”',
    '但期合意，不论风水',
    '至丁卯秋，琢堂降官翰林，余亦入都。所谓登州海市，竟无从一见。',
]
page_norm = norm(re.sub(r'<[^>]+>', ' ', html))
for c in CORE:
    nc = norm(c)
    if nc not in nbook:
        fails.append(f'核心引文不在库内: {c[:20]}')
    elif nc not in page_norm:
        fails.append(f'核心引文未上页: {c[:20]}')
print(f'[清单] 核心引文 {len(CORE)} 条，全部要求在库内且上页')

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

# 6. 视觉规范色
for c, k in [('#191917', '墨底'), ('#e8e4dc', '纸白'), ('#5e8fbb', '石青')]:
    if c.lower() not in html.lower():
        fails.append(f'缺规范色 {k}')
print('[配色] 墨底/纸白/石青检查完成')

print()
if fails:
    print('FAIL')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('ALL PASS')
