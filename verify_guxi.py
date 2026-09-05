#!/usr/bin/env python3
# 引文核验：姑溪词溪堂词.txt 双侧逐字（库本命中 + 页面反扫），去标点空白，异体照录比对
import re, sys

LIB = 'daizhige-simplified/诗藏/词集/姑溪词溪堂词.txt'
PAGE = 'daizhige-daodu/guxi-ci.html'

FOLD = {'嬾': '懒', '逰': '游', '聼': '听', '栁': '柳', '隂': '阴', '眺': '朓'}

def norm(s):
    s = ''.join(ch for ch in s if '一' <= ch <= '鿿')
    for a, b in FOLD.items():
        s = s.replace(a, b)
    return s

lib = norm(open(LIB, encoding='utf-8').read())
raw = open(PAGE, encoding='utf-8').read()
body = raw.split('<body>', 1)[1]
page = norm(re.sub(r'<[^>]+>', '', body))

quotes = [
    '我住长江头君住长江尾日日思君不见君共饮长江水',
    '此水几时休此恨何时已只愿君心似我心定不负相思意',
    '端叔赵郡人辟为中山幕府因代范忠宣作遗表得罪编置当涂即家焉自号姑溪居士',
    '之仪以尺牍擅名而其词亦工小令尤清婉峭蒨殆不减秦观',
    '独恨归来已晚半生孤负渔竿',
    '十年南北感征鸿恨应同苦重重',
    '聴杨妹琴',
    '为杨妹作',
    '与黄鲁直于当涂花园石洞聼杨妹弹履霜操鲁直有词因次韵',
    '其和陈瓘贺铸黄庭坚诸词皆列原作于前而巳词居后唱和并载',
    '牛渚天门险限南北七雄豪占',
    '天堑休论险尽远目与天俱占',
    '一弄醒心弦情在两山斜叠弹到古人愁处有真珠承睫',
    '相见两无言愁恨又还千叠别有恼人深处在懵腾双睫',
    '中多次韵小令更长于淡语景语情语如鸳衾半拥空床月又如步嬾恰寻床卧看逰丝到地长又如时时浸手心头熨受尽无人知处凉即置之片玉漱玉集中莫能伯仲',
    '至若我住长江头君住长江尾日日思君不见君共饮长江水直是古乐府俊语矣叔阳不列之南渡诸家得无遗珠之恨耶',
    '花庵词选未经采入有遗珠之叹',
    '不知黄升所录皆南渡以后之人故曰中兴以来绝妙词之仪时代在前晋殊未考',
    '尝过黄州杏花村馆题江神子一阕于驿壁过者必索笔于驿卒卒苦之因以泥涂焉',
    '杏花村馆酒旗风水溶溶飏残红野渡舟横杨栁绿隂浓',
    '凡四十调共八十有八阕',
]

fail = 0
for q in quotes:
    nq = norm(q)
    in_lib = nq in lib
    in_page = nq in page
    tag = 'OK ' if (in_lib and in_page) else 'FAIL'
    if not (in_lib and in_page):
        fail += 1
    print(f'{tag} 库本={"√" if in_lib else "×"} 页面={"√" if in_page else "×"} {q[:34]}')

# 红线
for dash in ('—', '–'):
    if dash in raw:
        print(f'红线: 页面含长划线 {dash!r}'); fail += 1
for i, line in enumerate(raw.split('\n'), 1):
    if line.count('·') > 1:
        print(f'红线: 第{i}行 · 超限'); fail += 1
for need in ('殆知阁简体库', '逐字核对', '时代局限'):
    if need not in raw:
        print(f'红线: 页脚缺 {need}'); fail += 1
if 'github.com' not in raw:
    print('红线: 页脚缺仓库链接'); fail += 1

print(f'\n引文 {len(quotes)} 组，失败 {fail} 处')
sys.exit(1 if fail else 0)
