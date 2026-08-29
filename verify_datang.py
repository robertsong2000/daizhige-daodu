#!/usr/bin/env python3
# 核验 datang-xiyuji.html：引文逐字、计数复核、排版红线
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'daizhige-simplified')
SRC_MAIN = os.path.join(LIB, '史藏/地理/大唐西域记.txt')
SRC_XTANG = os.path.join(LIB, '史藏/正史/新唐书.txt')
PAGE = os.path.join(HERE, 'datang-xiyuji.html')

fails = []
def check(name, cond, detail=''):
    print(('PASS' if cond else 'FAIL'), name, detail)
    if not cond:
        fails.append(name)

def norm(s):
    return ''.join(ch for ch in s if ch.isalnum())

raw = open(PAGE, encoding='utf-8').read()
page = norm(re.sub(r'<[^>]+>', '', raw))

src_main = open(SRC_MAIN, encoding='utf-8').read()
src_xtang = open(SRC_XTANG, encoding='utf-8').read()

# ---- 上页引文（.q 块，27 处）：库内 26 + 跨库 1 ----
QUOTES_MAIN = [
 '亲践者一百一十国，传闻者二十八国',
 '十九年正月，届于长安。所获经论六百五十七部，有诏译焉',
 '以贞观三年仲秋朔旦，褰裳遵路',
 '二十年秋七月，绝笔杀青',
 '书行者，亲游践也；举至者，传闻记也',
 '陋博望之非远，嗤法显之为局',
 '所列凡一百三十八国，中摩揭陀一国厘为八、九两卷，记载独详',
 '史所录者朝贡之邦，此所记者经行之地也',
 '明永乐三年太监郑和见国王阿烈苦柰儿事，是今之锡兰山，即古之僧伽罗国也',
 '吴氏刊本误连入正文也',
 '邻有贤主，国之祸也',
 '象军五千，马军二万，步军五万',
 '于六年中，臣五印度',
 '五年一设无遮大会，倾竭府库，惠施群有，惟留兵器，不充檀舍',
 '大唐国在何方？经途所亘，去斯远近',
 '盛矣哉！彼土群生，福感圣主',
 '从此北行三十余里，至那烂陁(唐言施无厌。)僧伽蓝',
 '五印度僧万里云集',
 '每日正中，有一丈夫从日轮中乘马会此',
 '母则汉土之人，父乃日天之种，故其自称汉日天种',
 '鼠大如猬，其毛则金银异色',
 '敬欲相助，愿早治兵。旦日合战，必当克胜',
 '爰命庸才，撰斯方志',
 '负燕雀之资，厕鹓鸿之末',
 '想千载如目击，览万里若躬游',
 '唐释玄奘译，辩机撰',
]
QUOTE_CROSS = ['与浮屠辩机乱，帝怒，斩浮屠']

# ---- 散文引用（页内未作引文块，但逐字核对来源）----
PROSE = ['凡七百八十言', '凡五百七十九言', '凡五百二十夹，总六百五十七部']

for i, q in enumerate(QUOTES_MAIN, 1):
    c = src_main.count(q)
    check(f'Q{i:02d} 源唯一', c == 1, f'(count={c}) {q[:18]}...')
    check(f'Q{i:02d} 页内在位', norm(q) in page, q[:18])
for i, q in enumerate(QUOTE_CROSS, 1):
    c = src_xtang.count(q)
    check(f'跨库Q{i} 新唐书源唯一', c == 1, f'(count={c})')
    check(f'跨库Q{i} 页内在位', norm(q) in page, q[:18])
for q in PROSE:
    check(f'散文「{q[:8]}」源唯一', src_main.count(q) == 1)
check('散文页内在位', norm('五百二十夹') in page and norm('六百五十七部') in page)

# ---- 页内序号（撞号顺延后应与 mulu 条目一致）----
check('页首序号 之五十五', '之五十五' in raw)

# ---- 页脚引文计数与实际一致 ----
qcount = len(re.findall(r'class="[^"]*\bq\b', raw))
check('.q 元素恰 27', qcount == 27, f'(实际 {qcount})')
check('页脚计数 27', '引文 27 处（库内 26、跨库 1）' in raw)

# ---- 国数账：卷标目录解析 ----
cn = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
def zh2int(s):
    if '十' not in s: return cn[s]
    a, b = s.split('十')
    v = (cn[a] if a else 1) * 10 + (cn[b] if b else 0)
    return v
toc = []
for line in src_main.split('\n'):
    m = re.match(r'^(卷[一二三四五六七八九十]+)[\s　]+([一二三四五六七八九十]+)国\s*$', line.strip())
    if m:
        toc.append((m.group(1), m.group(2)))
    if len(toc) == 12:
        break
exp = [('卷一','三十四'),('卷二','三'),('卷三','八'),('卷四','十五'),('卷五','六'),('卷六','四'),
       ('卷七','五'),('卷八','一'),('卷九','一'),('卷十','十七'),('卷十一','二十三'),('卷十二','二十二')]
check('库本卷标目录十二卷', toc == exp, f'(解析到 {len(toc)} 卷)')
total = sum(zh2int(n) for _, n in toc)
check('卷标国数合计 139', total == 139, f'(实际 {total})')
check('110+28=138', 110 + 28 == 138)
check('页含 一百三十九国', norm('一百三十九国') in page)
check('页含 一百三十八国', norm('一百三十八国') in page)
for v, n in toc:
    check(f'路引{v}·{n}国 在位', norm(v + n + '国') in page)

# ---- 字数机算 ----
whole = len(src_main.replace('\n', '').replace(' ', ''))
lines = src_main.split('\n')
i_start = next(i for i, l in enumerate(lines) if l.strip().startswith('卷一') and '国' in l and i > 30)
i_end = next(i for i, l in enumerate(lines) if l.strip() == '记赞' and i > 100)
main_chars = len(''.join(lines[i_start:i_end]).replace('　', ''))
check('正文 126,331', main_chars == 126331, f'(实际 {main_chars})')
check('全帙 134,929', whole == 134929, f'(实际 {whole})')
check('页含 126,331', '126,331' in raw)
check('页含 134,929', '134,929' in raw)

# ---- 校记申报在位 ----
check('校记提缺字 U+E837', 'U+E837' in raw)
check('校记提 甲𦈐', '𦈐' in raw)
check('校记提那烂陁', '那烂陁' in raw)

# ---- 排版红线 ----
check('无长划线', '—' not in raw and '–' not in raw)
bad = [i + 1 for i, line in enumerate(raw.split('\n')) if line.count('·') > 1]
check('每行·至多1', not bad, f'(违规行 {bad})')
check('无外部依赖', 'http' not in raw.replace('github.com/robertsong2000/daizhigev20', ''))

print()
print('FAILED:', fails if fails else '无，全过')
sys.exit(1 if fails else 0)
