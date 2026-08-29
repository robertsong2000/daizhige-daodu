import re, html

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/cuzhi-jing.html'
BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/促织经.txt'

def cjk(s):
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

page = html.unescape(open(PAGE, encoding='utf-8').read())
page = re.sub(r'<[^>]+>', '', page)  # 去标签
page_c = cjk(page)

book = open(BOOK, encoding='utf-8').read()
book_c = cjk(book)

quotes = [
    '暖则在郊，寒则附人，若有识其时者。拂其首则尾应之，拂其尾则首应之，似有解人意者。',
    '天下有不容尽之物，君子有独好之理。',
    '夫养虫者如养兵，选虫如选将。',
    '下盆徐徐养之，不可便斗。',
    '夫中秋促织，如人中年，观虫者亦须推度。',
    '最后须用熟虾，并熟蟹脚中肉、热鳗鱼脊上肉食之，忌有油处。',
    '盆中莫斗，斗有屈输；笼内输赢有准。',
    '两架芡不许过棚，如横点正，不许挑拨，动各存礼法。',
    '白不如黑，黑不如赤，赤不如黄。',
    '盆须用古，器必要精。',
    '百口赢者不为奇，一口赢者胜百口。',
    '蛩有四病：一仰头，二练牙，三卷须，四撼腿',
    '若犯其一，切不可托之',
    '有头大、腿长、背阔、齿强者，必定好争斗',
    '腿长有胜无输，身狭少赢多败。',
    '秃须秃尾小无爪，此物见之不足惜',
    '促织儿，王彦章，一根须短一根长。只固全胜三十六，人总呼为王铁枪。体烦恼，莫悲伤，世间万物有无常。昨宵忽值严霜降，好似南柯梦一场。',
    '一轮明月浸波中，万里碧天光皎洁',
    '纵有金玉雕笼，都是世情虚色。',
    '赌赛有千般之变化',
    '赌花管取满头装',
    '即当收之',
    '白露渐旺',
    '寒露渐绝',
    '长不斗阔，黑不斗黄，薄不斗厚，嫩不斗苍，好不斗异，弱不斗强，小不斗大，有病不斗',
]

bad = 0
for q in quotes:
    qc = cjk(q)
    in_page = qc in page_c
    in_book = qc in book_c
    status = 'OK' if (in_page and in_book) else 'FAIL'
    if status == 'FAIL':
        bad += 1
        print(f'{status}  page={in_page} book={in_book}  {q[:30]}')
    else:
        print(f'{status}  {q[:30]}')

print(f'\n{len(quotes)} 段引文，失败 {bad} 段')

# 禁则检查：长划线、单行多圆点
raw = open(PAGE, encoding='utf-8').read()
for line_no, line in enumerate(raw.split('\n'), 1):
    if '—' in line or '–' in line:
        print(f'DASH  行{line_no}: {line.strip()[:50]}')
        bad += 1
    if line.count('·') > 1:
        print(f'DOT   行{line_no}: {line.strip()[:50]}')
        bad += 1
print('排版禁则检查完成' if bad == 0 else '存在违规')
