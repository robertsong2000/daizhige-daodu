import json, re, sys

LIB = '../daizhige-simplified/史藏/地理/台海使槎录.txt'
PAGE = 'taihai-shichalu.html'

norm = lambda s: re.sub(r'\s+', '', s)
lib = norm(open(LIB, encoding='utf-8').read())
raw = open(PAGE, encoding='utf-8').read()
text = re.sub(r'<[^>]+>', '', re.sub(r'<script[\s\S]*?</script>', '', raw))
pt = norm(text)
fails = []

# 1 引文双侧核验
qs = json.load(open('quotes_taihai.json', encoding='utf-8'))
for k, v in qs.items():
    nv = norm(v)
    if nv not in lib:
        fails.append(f'[库本缺] {k}')
    if nv not in pt:
        fails.append(f'[页面缺] {k}')
print(f'引文 {len(qs)} 条 双侧核验 {"通过" if not fails else "失败"}')

# 2 标签名物词（单元格 / 飓历 / 界标 / 卷次 / 机数用词）
TAGS = [
    # 三体与预测
    '倏发倏止', '常连日夜不止', '北风初烈', '或至连月',
    '正、二、三、四月发者', '五、六、七、八月发者',
    '断虹', '破帆梢', '屈鲎', '风草', '划水仙', '九降',
    # 飓历
    '接神飓', '玉皇飓', '关帝飓', '乌狗飓', '白须飓', '上帝飓', '真人飓', '马祖飓',
    '佛子飓', '屈原飓', '彭祖飓', '彭婆飓', '洗炊笼飓', '鬼飓', '灶君飓', '魁星飓',
    '张良飓', '观音飓', '水仙王飓', '翁爹飓', '普庵飓', '送神飓', '火盆飓', '送年风',
    '初四日', '初九日', '十三日', '念九日', '初二日', '初三日', '十五日', '念三日',
    '初五日', '十二日', '十八日', '初一日', '十六日', '十九日', '初十日',
    '念六日', '念七日', '念四日已后',
    # 六考与社名
    '居处', '饮食', '衣饰', '婚嫁', '丧葬', '器用',
    '新港', '大武郡', '半线', '大肚', '崩山八社', '上澹水',
    '北路诸罗番一', '南路凤山番一', '南路凤山傀儡番二', '南路凤山琅峤十八社三',
    '赤嵌笔谈', '番俗六考', '番俗杂记', '鲁序',
    # 矩阵格关键词
    '状如覆舟', '姑待', '萨豉宜', '牵手', '马歹', '螺钱',
    '门绘红毛人像', '约期会饮', '马卓', '嘴琴挑之', '守丧三月', '小刀',
    '猫邻', '几鲁', '包练', '绵堵混', '马邻', '螺蛤壳为碗',
    '凿山为壁', '都都', '止露两目', '猫六', '神姊', '篾篮',
    '另室而居', '蒸其液为酒', '束腹至胸', '海蛤', '鹿皮包裹', '均如汉人',
    '圭茅', '香米', '日一浴', '突肉', '班柔少里堂敖敖', '大蒲仑',
    # 歌名
    '新港社别妇歌', '麻豆社思春歌', '湾里社诫妇歌', '琅峤待客歌',
    # 卷八与赤嵌目录
    '生番', '熟番', '社商', '社饷', '捕鹿', '番役', '土官馈献', '番界',
    '吞霄澹水之乱', '驭番', '附题咏',
    '原始', '星野', '形势', '洋', '潮', '气候', '海船', '城堡', '赋饷',
    '武备', '习俗', '祠庙', '商贩', '进贡', '泉井围石', '杂着', '纪异',
    '伪郑附略', '朱逆附略',
    # 界标与饷数
    '竹堑', '斗六门', '琅峤', '山朝社', '蛤仔难', '卑南觅', '内山',
    '五千九百三十三石八斗', '四千六百四十五石三斗', '七千七百八两零',
    '未邀裁减', '一岁所出共', '二万余金',
    '殆非人类', '若亦人也', '异其人，何必异其性',
]
for t in TAGS:
    if norm(t) not in lib:
        fails.append(f'[标签库本缺] {t}')
    if norm(t) not in pt:
        fails.append(f'[标签页面缺] {t}')
print(f'标签名物词 {len(TAGS)} 条 双侧核验')

# 3 排版红线
if re.search(r'[—–]', raw):
    fails.append('[禁长划线] 页面含 — 或 –')
chunks = [c for c in re.split(r'<[^>]+>|\n', raw) if '·' in c]
for c in chunks:
    if c.count('·') > 1:
        fails.append(f'[·限用] 一行多·: {c.strip()[:40]}')
pua = [c for c in set(raw) if 0xE000 <= ord(c) <= 0xF8FF]
if pua:
    fails.append(f'[零PUA] {pua}')
print(f'红线检查：长划线 / ·（{len(chunks)} 行含·，均不超1） / PUA')

# 4 零外部依赖
if re.search(r'<link|<script[^>]+src|@import|url\(', raw):
    fails.append('[外部依赖] 发现外链资源')
print('零外部依赖检查')

# 5 要素：字数自述 / 篇号 / 页脚三件套 / title
need = ['86557', '第二百一十篇', '殆知阁古代文献简体库',
        'github.com/robertsong2000/daizhigev20',
        '脚本核验通过', '不代表编者立场', '<title>台海使槎录 · 殆知阁导读</title>',
        '番歌三十三首', '六考十三区段', '黄叔璥', '康熙六十一年']
for t in need:
    if t not in raw:
        fails.append(f'[缺要素] {t}')
print('要素检查：字数自述 / 篇号 / 页脚三件套 / title')

if fails:
    print('\nFAIL')
    for f in fails:
        print(' ', f)
    sys.exit(1)
print('\nALL PASS')
