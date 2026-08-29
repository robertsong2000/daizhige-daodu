import re, html

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/wujing-zongyao.html'
BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/兵家/武经总要.txt'

def cjk(s):
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

page = html.unescape(open(PAGE, encoding='utf-8').read())
page_c = cjk(re.sub(r'<[^>]+>', '', page))

book = open(BOOK, encoding='utf-8').read()
book_c = cjk(book)

quotes = [
    '宋 曾公亮丁度等',
    '故一人学战，教成十人；十人学战，教成百人；百人学战，教成千人；千人学战，教成万人；万人学战，教成三军之众。此教兵之率也。',
    '守城之道，无恃其不来，恃吾有以待之；无恃其不攻，恃吾有所不可攻。',
    '晋州硫黄十四两，窝黄七两，焰硝二斤半，麻茹一两，干漆一两，砒黄一两，定粉一两，竹茹一两，黄丹一两，黄蜡半两，清油一分，桐油半两，松脂一十四两，浓油一分。',
    '右以晋州硫黄、窝黄、焰硝同捣，罗砒黄、定粉、黄丹同研，干漆捣为末，竹茹、麻茹即微炒为碎末，黄蜡、松脂、清油、桐油、浓油同熬成膏。入前，药末旋旋和匀，以纸五重裹衣，以麻缚定，更别熔松脂傅之。',
    '又有火箭，施火药于箭首，弓弩通用之。其傅药轻重，以弓力为准。',
    '旧法：军中咨事，若以文牒往来，须防泄漏；以腹心报覆，不惟劳烦，亦防人情有时离叛。今约军中之事，略有四十余条，以一字为暗号：',
    '请弓、请箭、请刀、请甲、请枪旗、请锅幕、请马、请衣赐、请粮料、请草料、请车牛、请船、请攻城守具、请添兵、请移营、请进军、请退军、请固守、未见贼、见贼讫、贼多、贼少、贼相敌、贼添兵、贼移营、贼进兵、贼退兵、贼固守、围得贼城、解围城、被贼围、贼围解、战不胜、战大胜、战大捷、将士投降、将士叛、士卒病、都将病、战小胜。',
    '以旧诗四十字，不得令字重，每字依次配一条，与大将各收一本',
    '如不允，即空印之，使众人不能晓也。',
    '或出指南车及指南鱼以辨所向。指南车法，世不传。鱼法，用铁叶剪裁，长二寸，阔五分，首尾锐如鱼形，置炭中，火烧之，候通赤（以铁钤钤鱼首，出火，以尾正对子位，醮水盆中，没尾数分，则上以密器收之。用时置水碗于无风处，平放鱼在水面，令浮其首），当南向午也。',
    '油自火楼中出，皆成烈焰。',
    '中人皆糜烂，水不能灭。',
    '三弓床弩，前二弓，后一弓，世亦名八牛弩。张时，凡百许人。',
    '凡一发可中数十人，世谓之斗子箭，亦云寒鸦箭，言矢之纷散如鸦飞也。',
    '用火锥烙球，开声如霹雳，然以竹扇簸其烟焰，以薰灼敌人（放球者合甘草）。',
    '凡王师讨伐，料敌制胜，不离掌握之内，参合天人之理，则亏衄者鲜矣。',
    '夫临戎对敌，洞究术数，辨休生而去拘忌，则天人之际，有以相助欤。',
]

bad = 0
for q in quotes:
    qc = cjk(q)
    in_page = qc in page_c
    in_book = qc in book_c
    if in_page and in_book:
        print(f'OK    {q[:26]}')
    else:
        bad += 1
        print(f'FAIL  page={in_page} book={in_book}  {q[:26]}')

# 字验四十字军语与页面 CODES 数组一致性
m = re.search(r'var CODES = \[(.*?)\];', page, re.S)
codes = re.findall(r'"([^"]+)"', m.group(1))
codes_c = cjk('、'.join(codes) + '。')
list_q = cjk(quotes[7])
if codes_c == list_q and len(codes) == 40:
    print(f'OK    字验 CODES 数组 40 条，与原文一致')
else:
    bad += 1
    print(f'FAIL  CODES 数组不符: n={len(codes)}')

# 春望四十字无重复（书例要求「不得令字重」）
POEM = '国破山河在城春草木深感时花溅泪恨别鸟惊心烽火连三月家书抵万金白头搔更短浑欲不胜簪'
if len(POEM) == 40 and len(set(POEM)) == 40 and cjk(POEM) in page_c:
    print('OK    春望四十字无重复，且在页面中')
else:
    bad += 1
    print(f'FAIL  春望 len={len(POEM)} uniq={len(set(POEM))}')

# 排版禁则：长划线；渲染段内圆点（按源行与去标签后文本双重检查）
raw = open(PAGE, encoding='utf-8').read()
for ln, line in enumerate(raw.split('\n'), 1):
    if '—' in line or '–' in line:
        print(f'DASH  行{ln}: {line.strip()[:46]}')
        bad += 1
    if line.count('·') > 1:
        print(f'DOT   行{ln}: {line.strip()[:46]}')
        bad += 1
rendered = re.sub(r'<script.*?</script>', '', page, flags=re.S)
for blk in re.split(r'<[^>]+>', rendered):
    if blk.count('·') > 1:
        bad += 1
        print(f'DOT渲染段: {blk.strip()[:46]}')

print(f'\n{len(quotes)} 段引文 + 2 项结构检查，失败 {bad} 项')
