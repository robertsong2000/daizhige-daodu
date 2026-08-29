#!/usr/bin/env python3
"""瘟疫论导读页核验：引文逐字比对 + 排版规则"""
import re, sys

PAGE = 'wenyi-lun.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/医藏/瘟疫论.txt'

VARIANT = {'冐': '冒', '歳': '岁', '呉': '吴', '隂': '阴', '菓': '果'}
PUNCT = re.compile(r'[\s　，。、；：？！「」『』（）()【】《》〈〉·…—–\-/.,;:?!"\'　]+')

def norm(s: str) -> str:
    for k, v in VARIANT.items():
        s = s.replace(k, v)
    return PUNCT.sub('', s)

# 引文：页面上显示的每段原文，均须同时存在于库内文件与页面
QUOTES = [
    '然气无形可求无象可见况无声复无臭何能得睹得闻',
    '以伤寒法治之不效乃推求病源着为此书瘟疫一证始有绳墨之可守亦可谓有功于世矣',
    '误作伤寒治之多死',
    '此气之来无论老少强弱触之者即病邪自口鼻而入',
    '昔有三人冒雾早行空腹者死饮酒者病饱食者不病',
    '邪之所着有天受有传染所感虽殊其病则一',
    '内不在藏府外不在经络舍于夹脊之内去表不远附近于胃乃表里之分界是为半表半里',
    '三味协力直达其巢穴使邪气溃败速离膜原是以为达原也',
    '夫疫之传有九然亦不出乎表里之间而已矣',
    '一日之间而有三变数日之法一日行之',
    '或时众人头面浮肿俗名为大头瘟是也',
    '或时声哑俗名为虾蟆瘟是也',
    '缓者朝发夕死急者顷刻而亡',
    '牛病而羊不病鸡病而鸭不病人病而禽兽不病究其所伤不同因其气各异也',
    '能知以物制气一病只有一药',
    '不烦君臣佐使品味加减之劳矣',
    '又名疫者以其延门合户如徭役之役众人均等之谓也',
    '设此证不服药或投缓剂羁迟二三日必死',
    '本气充满邪不易入',
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
    print(f'{tag} 库内={in_src} 页面={in_page}  {q[:24]}……')
    if not (in_src and in_page):
        fails.append(q)

# 排版规则：禁长划线；渲染文本每行 · 至多 1 个
if '—' in html or '–' in html:
    fails.append('发现长划线 —/–')
    print('FAIL 发现长划线')

text = re.sub(r'<[^>]+>', '\n', html)
lines = [l for l in text.split('\n') if l.strip()]
for i, l in enumerate(lines):
    c = l.count('·')
    if c > 1:
        fails.append(f'行内多间隔号: {l[:40]}')
        print(f'FAIL 一行多·({c}): {l[:40]}')

# 引文元素抽查：.q 与 .bigq 逐段核对（先去来源行；节引允许按标点分段后逐段在库内）
for m in re.finditer(r'class="q[^"]*"[^>]*>(.*?)<span class="src">|class="bigq">(.*?)</div>', html, re.S):
    body = next(g for g in m.groups() if g is not None)
    body = re.sub(r'<[^>]+>', '', body)
    if not body.strip():
        continue
    pieces = [norm(p) for p in re.split(r'[，。；：？！…]+', body) if len(norm(p)) >= 6]
    missing = [p for p in pieces if p not in src_norm]
    if missing:
        fails.append(f'.q 未核验: {missing[0][:20]}')
        print('FAIL .q 段不在库内:', missing[0][:24])

print(f'\n引文 {len(QUOTES)} 条，失败 {len(fails)} 项')
sys.exit(1 if fails else 0)
