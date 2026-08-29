#!/usr/bin/env python3
"""竹书纪年导读页核验：引文逐字比对（三源文件）+ 排版规则 + 字符数核对"""
import re, sys

PAGE = 'zhushu-jinian.html'
BASE = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/编年/'
SRCS = {
    '今本': BASE + '竹书纪年.txt',
    '疏证': BASE + '今本竹书纪年疏证.txt',
    '辑证': BASE + '竹书纪年辑证.txt',
}

VARIANT = {}
PUNCT = re.compile(r'[\s　，。、；：？！「」『』（）()【】《》〈〉·…—–\-/.,;:?!"\'\']+')

def norm(s: str) -> str:
    for k, v in VARIANT.items():
        s = s.replace(k, v)
    return PUNCT.sub('', s)

# (来源, 引文)：页面与对应库内文件双重比对
QUOTES = [
    ('今本', '其书言当禅舜。遂让舜。'),
    ('今本', '自东迁以后始纪晋事，王即位皆不书。'),
    ('今本', '伊尹放太甲于桐，乃自立。'),
    ('今本', '七年，王潜出自桐，杀伊尹，天大雾三日，乃立其子伊陟、伊奋，命复其父之田宅而中分之。'),
    ('今本', '约按：伊尹自立，盖误以摄政为真尔。'),
    ('今本', '今王终二十年。'),
    ('疏证', '乃复用惠、孙二家法，一一求其所出，始知今本所载殆无一不袭他书。其不见他书者，不过百分之一，又率空洞无事实，所增加者年月而已。'),
    ('疏证', '是犹捕盗者之获得真赃。'),
    ('疏证', '然余惧后世复有陈逢衡辈为是纷纷也，故写而刊之，俾与《古本辑校》并行焉。'),
    ('辑证', '昔尧德衰，为舜所囚也。'),
    ('辑证', '舜囚尧于平阳，取之帝位。'),
    ('辑证', '益干启位，启杀之。'),
    ('辑证', '太甲杀伊尹。'),
    ('辑证', '夏年多殷。'),
    ('辑证', '懿王元年，天再旦于郑。'),
    ('辑证', '自武王灭殷以至幽王，凡二百五十七年。'),
    ('辑证', '舜囚尧，复偃塞丹朱，使不与父相见也。'),
    ('辑证', '后稷放帝子丹朱于丹水。'),
    ('辑证', '文丁杀季历。'),
    ('辑证', '自周受命至穆王百年，非穆王寿百岁也。'),
    ('辑证', '盖正文与注出于一人所搜集也。'),
]

html = open(PAGE, encoding='utf-8').read()
src_norm = {k: norm(open(v, encoding='utf-8').read()) for k, v in SRCS.items()}
page_norm = norm(re.sub(r'<[^>]+>', '', html))

fails = []
for s, q in QUOTES:
    nq = norm(q)
    in_src = nq in src_norm[s]
    in_page = nq in page_norm
    tag = 'OK ' if (in_src and in_page) else 'FAIL'
    print(f'{tag} [{s}] 库内={in_src} 页面={in_page}  {q[:26]}……')
    if not (in_src and in_page):
        fails.append(q)

# 字符数核对：页面宣称的实测数须与库内文件一致
for label, fname, shown in [('今本', '竹书纪年.txt', '23,499'), ('疏证', '今本竹书纪年疏证.txt', '65,227'), ('辑证', '竹书纪年辑证.txt', '171,716')]:
    actual = len(open(SRCS[label], encoding='utf-8').read())
    ok = f'{actual:,}' == shown and shown in html
    print(f'{"OK " if ok else "FAIL"} 字符数 {label} 页面={shown} 实测={actual:,}')
    if not ok:
        fails.append(f'字符数 {label}')

# 排版规则：禁长划线；渲染文本每行 · 至多 1 个；无外部资源引用
if '—' in html or '–' in html:
    fails.append('发现长划线 —/–')
    print('FAIL 发现长划线')

text = re.sub(r'<[^>]+>', '\n', html)
lines = [l for l in text.split('\n') if l.strip()]
bad = [(i, l) for i, l in enumerate(lines) if l.count('·') > 1]
if bad:
    fails.append('行内 · 超限')
    for i, l in bad:
        print(f'FAIL 行内多·: {l[:50]}')

if re.search(r'(src|href)\s*=\s*["\']https?:', html):
    fails.append('外部资源引用')
    print('FAIL 存在外部资源引用')

print()
if fails:
    print(f'共 {len(fails)} 项失败'); sys.exit(1)
print(f'全部通过：{len(QUOTES)} 条引文 + 字符数 + 排版规则')
