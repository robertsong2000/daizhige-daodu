# -*- coding: utf-8 -*-
# 引文核验：原本革象新书（子藏/算法/原本革象新书.txt）
# 规则：展示引文与库内文件去标点、去空白、异体字归一后逐字比对
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/算法/原本革象新书.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/gexiang-xinshu.html'

import re, sys

VAR = {'歳':'岁','厯':'历','歴':'历','逺':'远','髙':'高','葢':'盖','寛':'宽',
       '踈':'疏','疎':'疏','宻':'密','郤':'却','穽':'阱','毬':'球','黒':'黑',
       '隂':'阴','徳':'德','疉':'叠','乗':'乘','縁':'缘','隠':'隐','遯':'遁',
       '説':'说','毎':'每','胷':'胸','聨':'联'}

def norm(s):
    s = ''.join(VAR.get(c, c) for c in s)
    return ''.join(c for c in s if '一' <= c <= '鿿')

src = open(SRC, encoding='utf-8').read()
clean = src.replace(' ', '').replace('\n', '').replace('\r', '').replace('　', '')
nsrc = norm(src)

QUOTES = [
 '室有小罅，虽不皆圆，而罅景所射，未有不圆。及至日食，则罅景亦如所食分数。罅虽宽窄不同，景却周径相等，但宽者浓而窄者淡。',
 '是故小景随光之形，大景随空之象，断乎无可疑者。',
 '予始未悟其理，因熟思之。',
 '向右阱东边减却五百烛',
 '楼板之景缺其半于西',
 '乃小景随日月亏食之理也',
 '千数交错，周遍叠砌，则总成一景而圆。',
 '仰观楼板之景左尖右方',
 '大景随空之象，各自方尖，不随烛光而圆缺。',
 '烛也，光也，窍也，景也，四者消长胜负皆所当论。',
 '以黑漆球于檐下映日，则其球必有光，可以转射暗壁。太阴圆体即黑漆球也。',
 '月体本无圆缺，乃是月体之光暗半轮转旋，人目不能尽察，故言其圆缺耳。',
 '为月之黑体所障，故云日食，然日体未尝有损，所谓食者，强名而已。',
 '若将赤球比月，大小相同，共悬一索，日上月下，相去稍远。人在其下正望之，则黑球遮尽赤球，比若食既；傍视而分远近之差，即食数有多寡也。',
 '日食修德，月食修刑。所谓救之者，非能救其食，是乃观乎天文以察时变，不得不儆戒耳。',
 '日月之食乃所行交道常数，虽太平盛世有所不免。',
 '盖岁浅则差少，未觉；久而积差渐多，不容不改。要当随时测验，以求天数之真。',
 '近世康节先生作皇极经世书，以十二万九千六百年为宇宙之终始，世人多信其说。以愚观之，实不可准。',
 '是将整齐之数推不齐之运，犹月皆大尽而无小尽，亦不置闰矣。造历者不取其说，良有以夫。',
 '夫灶火甚炎，可比午中矣，然甑蒸之气犹未甚盛；及其甑蒸气盛，则灶火已稍衰矣。在后灶火尽灭，可比子中矣，然甑蒸之气又良久而后始衰。寒暑之理，岂非积久而气盛乎。',
 '今人斜卷麻苎之絘，周遭往返，非复故处，丝渐移重复缠络而成团者，名曰絘团。以喻此理最切。',
 '谓闰月指两辰之间者，可发一笑欤。',
 '方为数之始，圆为数之终。圆始于方，方终于圆，周髀之术无出于此矣。',
 '试泛舟江湖，但见舟所到之处隆起，而水之来不见其首，水之去不见其尾。洞庭之广，日月若出没其中，远山悉在环曲下，不为障也。',
 '盖天之学不特知天体浑圆，并知地体亦浑圆，可谓测验至精至密，汉以来言浑天者不逮也。',
 '强加之盖天以便于攻之，其亦诬矣。',
 '其覃思推究，颇亦发前人所未发；于今法为疏，于古法则为已密。在元以前谈天诸家，犹为有心得者。',
 '月体中用大远镜窥见其有高下，故月之向日有吐光处有不吐光处。',
 '上天下地，地下无天，亦无南极。',
 '北斗近南则高而小，近北则低而大，',
 '如此则盖天之谬明矣。',
 '术数之家主于测算，未可以文章工拙相绳',
 '于讹误之处并以今法加案驳正，而仍存其说',
 '自至元年辛巳行之至今',
 '当今泰定甲子',
 '或曰名敬字子恭，或曰友钦，弗能详也',
 '饶之德兴人',
 '其先于宋有属籍',
 '汉王房十二世以友字联名',
 '围三尺径一尺，是六角之田。',
 '三千一百四十一寸五分九厘二毫有奇',
 '三尺一寸四分一厘五毫九丝二忽',
 '以一百一十三乘之果得三百五十五尺',
 '角数愈多而其为方者不复方。',
 '渐加渐展，渐满渐实。',
 '节节求之，虽至千万次其数终不穷。',
 '此以小数求之，不若改为大数。',
 '隐遁自晦',
 '不知其名若字',
]

fails = 0
for i, q in enumerate(QUOTES, 1):
    nq = norm(q)
    assert nq, '空引文 #%d' % i
    if '防' in q:
        print('FAIL #%d 引文含库本讹字(防)：%s' % (i, q)); fails += 1; continue
    if nq not in nsrc:
        print('FAIL #%d 未命中：%s' % (i, q)); fails += 1

# 事实核对
facts = [
    ('去空白字数', len(clean) == 33095),
    ('卷三目录作巻三', '革象新书巻三' in clean),
    ('提要纪年', '乾隆四十六年九月恭校上' in clean),
    ('总纂官', '纪昀' in clean and '陆锡熊' in clean and '孙士毅' in clean),
    ('卷一', '革象新书卷一' in clean), ('卷二', '革象新书卷二' in clean),
    ('卷四', '革象新书卷四' in clean), ('卷五', '革象新书卷五' in clean),
    ('篇目样例', all(t in nsrc for t in ['小罅光景','乾象周髀','句股测天','盖天舛理','浑仪制度','五纬距合','地域远近'])),
    ('元会运世讹作元防运世', '元防运世' in clean),
]
for name, ok in facts:
    if not ok:
        print('FAIL 事实：%s' % name); fails += 1

# 页面排版红线
html = open(HTML, encoding='utf-8').read()
if '—' in html or '–' in html:
    print('FAIL 页面含长划线'); fails += 1
for ln, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        print('FAIL 行%d 含%d个·：%s' % (ln, line.count('·'), line.strip()[:60])); fails += 1
if any(0xE000 <= ord(c) <= 0xF8FF for c in html):
    print('FAIL 页面含私用区字符'); fails += 1
for bad in ['<script src', '<link ', '<img ', '@import', 'http://', 'https://cdn']:
    if bad in html.replace('https://github.com/robertsong2000/daizhige-daodu', ''):
        print('FAIL 页面含外部依赖：%s' % bad); fails += 1
if html.count('<section') != html.count('</section>') or html.count('<div') != html.count('</div>'):
    print('FAIL 标签不配对 section:%d/%d div:%d/%d' % (
        html.count('<section'), html.count('</section>'), html.count('<div'), html.count('</div>')))
    fails += 1

print('引文 %d 条，事实 %d 项，排版 5 规则' % (len(QUOTES), len(facts)))
print('ALL PASS' if fails == 0 else 'FAILED: %d' % fails)
sys.exit(0 if fails == 0 else 1)
