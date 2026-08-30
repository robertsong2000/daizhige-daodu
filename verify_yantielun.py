#!/usr/bin/env python3
# 盐铁论页核验：引文逐字对库 + 说话人归属 + 机数复算 + 排版红线
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/儒藏/语录/盐铁论.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yantie-lun.html'

QUE = chr(0xe511)   # 库内「榷」缺文码点
HONG = chr(0xea1f)  # 库内「弘」缺文码点

raw = open(LIB, encoding='utf-8').read()
s = re.sub(r'【[^【】]*】', '', raw)  # 剥注净正文
page = open(PAGE, encoding='utf-8').read()

fails = []
def check(name, cond, detail=''):
    if cond:
        print(f'  ok  {name}')
    else:
        fails.append(name)
        print(f'FAIL  {name} {detail}')

def norm(x):
    # 只保留 CJK 意音文字（含扩展区）→ 顺带剥掉全部标点/空白/PUA
    return ''.join(c for c in x if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0003ffff')

# ---------- 页面 .q 提取（标签配平，跳过 .lost 与 .qzhu 内容） ----------
def collect_q(html):
    html = re.sub(r'<span class="qzhu">[^<]*</span>', '', html)
    html = re.sub(r'<span class="lost">[^<]*</span>', '', html)
    html = re.sub(r'<span class="hl">([^<]*)</span>', r'\1', html)
    toks = re.split(r'(<[^>]+>)', html)
    out, depth, buf = [], 0, []
    for tk in toks:
        if tk.startswith('<'):
            m = re.match(r'<(/?)(\w+)', tk)
            if not m:
                continue
            closing, tag = m.groups()
            if closing:
                if depth > 0:
                    depth -= 1
                    if depth == 0:
                        out.append(''.join(buf)); buf = []
            else:
                cls = re.search(r'class="([^"]*)"', tk)
                c = cls.group(1) if cls else ''
                if 'q' in c.split():
                    if depth == 0:
                        depth = 1; buf = []
                    else:
                        depth += 1
        else:
            if depth > 0:
                buf.append(tk)
    return out

qs = collect_q(page)
qn = [norm(x) for x in qs]

QUOTES = [
 '惟始元六年有诏书使丞相御史与所举贤良文学语',
 '问民间所疾苦',
 '窃闻治人之道坊淫佚之原广道徳之端抑末利而开仁义毋示以利然后教化可兴而风俗可移也',
 '愿罢盐鐡酒均输所以进本退末广利农业便也',
 '先帝哀边人之久患苦为虏所系获也故修障塞饬烽燧屯戍以备之',
 '边用度不足故兴盐铁设酒置均输蕃货长财以佐助边费',
 '今议者欲罢之内空府库之藏外乏执备之用使备塞乗城之士饥寒于边将何以澹之罢之不便也',
 '余结髪束修年十三幸得宿卫给事辇毂之下以至卿大夫之位获禄受赐六十有余年矣',
 '车马衣服之用妻子仆养之费量入为出俭节以居之',
 '富在术数不在劳身利在势居不在力耕也',
 '儒皆贫羸衣冠不完安知国家之政县官之事乎',
 '夫贱不周知贫不妨行',
 '山东天下之腹心贤士之战塲也',
 '古者夫妇之好一男一女而成家室之道',
 '及后士一妾大夫二诸侯有侄娣九女而已',
 '今诸侯百数卿大夫十数中者侍御富者盈室',
 '是以女或旷怨失时男或放死无匹',
 '古者采椽茅茨陶桴复穴足御寒暑蔽风雨而已',
 '采椽茅茨非先王之制也君子节奢刺俭俭则固',
 '法能刑人而不能使人廉能杀人而不能使人仁',
 '古者伤人有创者刑盗有赃者罚杀人者死今取人兵刃以伤人罪与杀人同得无非其至意与',
 '余覩盐鐡之义观乎公卿文学贤良之论意指殊路各有所出或上仁义或务权利',
 '贤良茂陵唐生文学鲁万生之伦六十余人咸聚阙庭',
 '是时丞相车千秋御史大夫桑羊皆不悦文学贤良之议',
 '奏罢酒均输而盐鐡卒不变',
 '桑大夫据当世合时变推道术尚权利辟畧小辩虽非正法',
 '执法者国之辔衔刑罚者国之维檝',
]

ZHU = {
 '是时丞相车千秋御史大夫桑羊皆不悦文学贤良之议',
 '奏罢酒均输而盐鐡卒不变',
}
NS_RAW = norm(raw)
NS = norm(s)

print('== 引文逐字核验（页面 .q 对库，剥注去标点） ==')
check(f'.q 元素恰 {len(QUOTES)} 个', len(qs) == len(QUOTES), f'实际 {len(qs)}')
for i, q in enumerate(QUOTES):
    if q in ZHU:
        check(f'引文{i+1:02d} 在库·注文 {q[:14]}…', norm(q) in NS_RAW)
    else:
        check(f'引文{i+1:02d} 在库 {q[:14]}…', norm(q) in NS)
for i, q in enumerate(qn):
    check(f'引文页{i+1:02d} 是期望清单之一', q in [norm(x) for x in QUOTES], q[:20])

print('== 缺位邻接断言（缺文码点位置钉死） ==')
check('酒榷均输 本议·文学', '愿罢盐鐡酒' + QUE + '均输' in s)
check('设酒榷置均输 本议·大夫', '边用度不足故兴盐铁设酒' + QUE + '置均输' in s)
check('桑弘羊 杂论注', '是时丞相车千秋御史大夫桑' + HONG + '羊皆不悦' in raw)
check('奏罢酒榷 杂论注', '文学贤良之议奏罢酒' + QUE + '均输而盐鐡卒不变' in raw)

print('== 说话人归属 ==')
def nearest_label(anchor):
    i = s.find(anchor)
    labs = [(m.start(), m.group(0)) for m in re.finditer(r'(文学曰|大夫曰|贤良曰|御史曰|丞相史曰)', s[:i])]
    return labs[-1][1] if labs else None
for anchor, who in [
    ('古者采椽茅茨陶桴复穴', '贤良曰'),
    ('古者夫妇之好', '贤良曰'),
    ('富在术数', '大夫曰'),
    ('儒皆贫羸', '大夫曰'),
    ('夫贱不周知', '文学曰'),
    ('山东天下之腹心', '贤良曰'),
    ('法能刑人', '文学曰'),
    ('古者伤人有创', '文学曰'),
    ('余结髪束修', '大夫曰'),
    ('余覩盐鐡之义', None),  # 客曰不在正则集，单独验
]:
    if who is None:
        check('杂论为客曰框架', s.find('客曰余覩盐鐡之义') >= 0)
    else:
        check(f'{anchor[:8]}…→{who}', nearest_label(anchor) == who, nearest_label(anchor))

print('== 机数复算（页面数字 vs 现算） ==')
n_net = len(re.sub(r'\s', '', s))
n_all = len(re.sub(r'\s', '', raw))
n_notes = n_all - n_net
lab = lambda x: f'{x:,}'
check('正文净 51,646', lab(n_net) == '51,646', n_net)
check('全帙 183,642', lab(n_all) == '183,642', n_all)
check('注文 131,996', lab(n_notes) == '131,996', n_notes)
check('注 2,481 处', raw.count('【') == 2481)
spk = {'文学曰': 122, '大夫曰': 113, '贤良曰': 26, '御史曰': 16, '丞相史曰': 16, '客曰': 1}
for k, v in spk.items():
    check(f'{k}={v}', s.count(k) == v, s.count(k))
titles = re.findall(r'[一-鿿]{1,4}第[一二三四五六七八九十]{1,3}', s)
check('六十篇', len(titles) == 60, len(titles))
check('张之象卷头 11', raw.count('明　张之象　注') == 11)
check('钦定四库全书 14', raw.count('钦定四库全书') == 14)
check('榷缺文净 9', s.count(QUE) == 9, s.count(QUE))
check('弘缺文净 7', s.count(HONG) == 7, s.count(HONG))
check('桑宏羊 2', s.count('桑宏羊') == 2)
check('寛 60 / 宽 0', raw.count('寛') == 60 and raw.count('宽') == 0)
check('盐鐡 39 / 盐铁 38 净', s.count('盐鐡') == 39 and s.count('盐铁') == 38)
pu = [c for c in s if 0xE000 <= ord(c) <= 0xF8FF]
check('净文 PUA 128 处 55 种', len(pu) == 128 and len(set(pu)) == 55, f'{len(pu)}/{len(set(pu))}')
i29, j29 = s.find('散不足第二十九'), s.find('救匮第三十')
seg29 = s[i29:j29]
check('散不足 2,855 字', lab(len(re.sub(r'\s', '', seg29))) == '2,855', len(re.sub(r'\s', '', seg29)))
check('古者 31 / 今 33', seg29.count('古者') == 31 and seg29.count('今') == 33)
check('俛仰未应对 1 见', s.count('大夫俛仰未应对') == 1)
check('御史大夫曰 1 见', s.count('御史大夫曰') == 1)
for num in ['51,646', '131,996', '183,642', '2,481', '128', '55', '二千八百五十五', '31', '33']:
    check(f'页面出现 {num}', num in page)

print('== 排版红线 ==')
m_big = re.search(r'大夫<span>([^<]+)</span>', page)
check('静默大字五字逐字在库', bool(m_big) and ('大夫' + m_big.group(1)) in s, m_big.group(1) if m_big else 'miss')
check('无长划线 — –', '—' not in page and '–' not in page)
bad = [ln for ln in page.split('\n') if ln.count('·') > 1]
check('每行 · ≤ 1', not bad, str(bad[:3]))
check('页脚来源声明', '殆知阁简体库' in page and 'verify_yantielun.py' in page)
check('页脚时代提醒', '时代' in page)
check('链接总目', 'href="mulu.html"' in page)
check('缺字虚框', page.count('class="lost"') == 5, page.count('class="lost"'))

print()
if fails:
    print(f'未通过 {len(fails)} 项'); sys.exit(1)
print(f'全部通过：引文 {len(QUOTES)} 段 + 机数/红线断言')
