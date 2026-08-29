#!/usr/bin/env python3
"""救荒本草导读页核验：引文逐字比对 + 排版规则"""
import re, sys

PAGE = 'jiuhuang-bencao.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/农家/救荒本草.txt'

VARIANT = {}
PUNCT = re.compile(r'[\s　，。、；：？！「」『』（）()【】《》〈〉·…—–\-/.,;:?!"\'　]+')

def norm(s: str) -> str:
    for k, v in VARIANT.items():
        s = s.replace(k, v)
    return PUNCT.sub('', s)

# 引文：页面上出现的每段原文，均须同时存在于库内文件与页面
QUOTES = [
    '救荒本草八卷明周王朱橚撰橚明太祖第五子洪武十一年封十四年就藩开封建文时废徙云南成祖复其爵洪熙元年薨谥曰定',
    '购田夫野老得甲坼勾萌者四百余种植于一圃躬自阅视俟其滋长成熟乃召画工绘之为圗',
    '神农品尝草木以疗斯民之疾殿下区别草木欲济斯民之饥同一仁心之用也',
    '而于可茹以充腹者则未之及也',
    '人情于饱食暖衣之际多不以冻馁为虞一旦遇患难则莫知所措',
    '今天下方乐雍熈泰和之治禾麦产瑞家给人足不必论及于荒政',
    '其榆钱煮糜羮食佳但令人多睡',
    '榆皮刮去其上干燥皴澁者取中间软嫩皮剉碎晒干炒焙极干捣磨为面拌糠麧草末蒸食取其滑泽易食',
    '榆皮与檀皮为末服之令人不饥',
    '出蚕蛾时切不可取抝令蛾子赤烂蚕妇忌食',
    '患气人食之动冷疾不可与面同食令人背闷服丹石人不可食',
    '以其叶青梗赤花黄根白子黒故名五行草',
    '服食家蒸曝蜜和饵之断谷长生',
    '又云杂白蜜食令人生虫',
    '救饥采嫩苗叶煠熟水浸淘净油盐调食',
]

html = open(PAGE, encoding='utf-8').read()
src = open(SRC, encoding='utf-8').read()
page_norm = norm(re.sub(r'<[^>]+>', '', html))
src_norm = norm(src)

fails = []
for q in QUOTES:
    nq = norm(q)
    in_src = nq in src_norm
    in_page = nq in page_norm
    tag = 'OK ' if (in_src and in_page) else 'FAIL'
    print(f'{tag} 库内={in_src} 页面={in_page}  {q[:26]}……')
    if not (in_src and in_page):
        fails.append(q)

# 排版规则：禁长划线；渲染文本每行 · 至多 1 个
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

# 外部依赖检查：不允许 http(s) 资源引用（页脚纯文字链接除外）
if re.search(r'(src|href)\s*=\s*["\']https?:', html):
    fails.append('外部资源引用')
    print('FAIL 存在外部资源引用')

print()
if fails:
    print(f'共 {len(fails)} 项失败'); sys.exit(1)
print(f'全部通过：{len(QUOTES)} 条引文 + 排版规则')
