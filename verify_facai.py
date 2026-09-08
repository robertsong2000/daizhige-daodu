# -*- coding: utf-8 -*-
"""发财秘诀 引文核验：页面所有 <q> 引文与库内文件去标点归一逐字比对，另查排版禁则。"""
import re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/发财秘诀.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/facai-mijue.html'

def norm(s):
    out = []
    for ch in s:
        if ch.isspace() or unicodedata.category(ch).startswith('P') or unicodedata.category(ch).startswith('S'):
            continue
        out.append(ch)
    return ''.join(out)

text = norm(open(LIB, encoding='utf-8').read())
html = open(HTML, encoding='utf-8').read()

quotes = []
for m in re.finditer(r'<q>(.*?)</q>', html, re.S):
    inner = re.sub(r'<[^>]+>', '', m.group(1))
    quotes.append(('q', inner.strip()))

# 散落在注释、注音、账条里的原文短语，一并核验
EXTRAS = [
    '随买，随吹；随吹，随破。',
    '五百数十元',
    '三十二担',
    '那乩忽然乱动一阵，然后判出十五日无事五个字来',
    '开炮攻城，轰天震地的，攻了一日一夜',
    '楼字写',
    '十啤令卜',
    '犹如中国读的三字经一般',
    '噃棉',
    'KiLong－Famine',
    '略略懂了两句',
    '也斯哪',
    '拉姆罢温',
    '好不威风有体面',
    '越是这种冷门说话，越是不能不留心。万一东家要说起来，回答不出，岂不要受他两句',
    '追月',
    '小批减取一角',
    '知微子命相',
    '买地皮为甚不转道契',
    '代人做枪',
    '短衣缩食',
    '馨我所有',
    '二十年中坐致者，已达万金。天之待阁下者不为不厚，阁下乃天与勿取',
    '速与阎罗王商量，把你本有的人心，挖去换上一个兽心。',
    '你若要发财',
    '金四开',
    '不止五万两',
]
bad = []
for kind, q in quotes + [('extra', x) for x in EXTRAS]:
    nq = norm(q)
    if not nq:
        bad.append((q, 'EMPTY'))
        continue
    if nq not in text:
        bad.append((q, 'NOT FOUND'))

print(f'共 {len(quotes)+len(EXTRAS)} 处引文，未通过 {len(bad)} 处')
for q, why in bad:
    print('  FAIL[%s] %s' % (why, q[:70]))

# 排版红线：长划线
for ch, name in (('—', 'em-dash'), ('–', 'en-dash')):
    if ch in html:
        bad.append((name, 'DASH'))
        print('排版FAIL: 页面含 %s' % name)

# 渲染行·计数：按源码可见文本行近似检查（style/script 内跳过）
in_block = False
dot_fail = 0
for line in html.split('\n'):
    ls = line.strip()
    if ls.startswith('<style>') or '<style>' in ls: in_block = True
    if '</style>' in ls: in_block = False; continue
    if ls.startswith('<script') or '<script>' in ls: in_block = True
    if '</script>' in ls: in_block = False; continue
    if in_block: continue
    if ls.count('·') > 1:
        dot_fail += 1
        print('排版FAIL: 一行内·超过1个 → %s' % ls[:80])
bad += [('-', 'DOT')] * dot_fail

sys.exit(1 if bad else 0)
