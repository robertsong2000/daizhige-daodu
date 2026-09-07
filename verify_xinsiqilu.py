#!/usr/bin/env python3
# 辛巳泣蕲录 导读页核验：引文双侧逐字 + 排版规则 + 库本字数
import re, sys

LIB = 'daizhige-simplified/史藏/志存记录/辛巳泣蕲录.txt'
PAGE = 'daizhige-daodu/xinsi-qilu.html'

lib = open(LIB, encoding='utf-8').read()
lib_ns = re.sub(r'\s+', '', lib)
han = lambda s: ''.join(re.findall(r'[一-鿿]', s))
lib_han = han(lib)

QUOTES = [
 "本州得报之后，人皆曰：“虏未必深入。”",
 "太守语寮属曰：“五关可恃否？”",
 "或者之议为不可恃，似闻尚有私小路，槎塞不尽。",
 "太守笑曰：“且看。”",
 "内点检得弓箭有七十万，弩箭有三十五万有奇。",
 "又点检有划车弩八十五座，箭约五万只",
 "点铁甲大小，共有五百副，兜鍪五百二十副，长枪五百条",
 "今守蕲春三载，两遇寇至，头颅七十，书生辈已两任边守，有何不得？",
 "入土之年，所欠惟一死耳。他无所恋。",
 "况诚之屡有丐祠之请，亦只是求一死所，万一寇至，只得与同官死守。",
 "出弩火药箭七千只，弓火药箭一万只，蒺藜火炮三千只，皮大炮二万只",
 "如黄土关只有百五十人，白沙关有三百人，大城关有百七十人，修缮关有二百五十人，木陡关有九十人",
 "上、下巴河百姓拥并奔窜，携孥挟子入本州城，哭声震天。",
 "奸细三名，已在吾掌握中矣。",
 "此正骑虎之势，宜急下脚手。不然，来日事变，我辈先为鱼肉矣。",
 "约二十四日用草鞋戳于枪头上为号，令番贼打入城中。",
 "独张奇之家有黑旗十余面，及有蕲黄、安庆、鄂州、兴国、武昌等城图",
 "虏贼拥众下山，直至下河渡，呼叫：“张奇八郎，如何不出来，莫误了我。”",
 "太守登城抚谕，又亲闻虏贼呼叫张奇八郎，始知所斩无愧。",
 "度其书，无过辱国之语，不必开看。",
 "金人拥众，皆以白布包头，前来西北团楼，号哭我城。",
 "彼哭我乐，又呼妓弟着红衣，动细乐于战棚上。",
 "钜自虏人围城，一家食素已半月矣。",
 "小儿子事斗尤虔，每夜朝礼诵经，亦只为一城生灵与骨肉之故。",
 "古法，候其近城，宜多热煎金汁浇灌其皮",
 "对楼焚尽，即飞申报捷。",
 "横流炮十有三座，每一炮继以一铁火炮，其声大如霹雳。",
 "其日对炮，市兵贾用因拽炮被金贼以铁火炮所伤头目，面霹碎不见一半。",
 "事已至此，守则亦死，出则亦死，不如与城俱亡。",
 "守边死，吾辈职也。",
 "今四围皆是贼垒，进退等死，当从死以求生。",
 "呼唤小儿二十余人，每名劳以百金、蒸饼一枚，贾勇擂鼓以激士卒。",
 "石炮之后，继以铁火炮，其形如匏状而口小，用生铁铸成，厚有二寸，震动城壁。",
 "董曰：“吾将家之后，中百十箭，此亦常事。”",
 "挽弓同诸军射贼。回身取箭间，左脾亦中一箭。",
 "与{容衣}情迫意切，未免望阙遥拜",
 "汝等宜以宗社为念。不然，则杀我而去，不妨。",
 "纵太守不认，钜出经总制库钱，兑支不妨。",
 "七名将校，八百四十九名长行，共支三万六千二百七十贯文",
 "而徐挥、常用等八百四十六人，弃城先遁",
 "但闻孙中厉声喝令诸军斗杀报答国家数声而已，其江士旺、孙中即为虏杀",
 "幸身衣军人绿布衫，杂在乱兵中。",
 "与{容衣}阖门一十五口，均与守、ヘ而下骨肉尽沦殁于贼手",
 "番贼攻围蕲州，前后二十有五日",
 "我不解便打破你城，是你大军自弃与我。且我明日十八日，也自要去了。",
 "朝廷差我策应黄州，即不曾策应蕲州。",
 "微笑不顾，径自渡江而去。",
 "既至高山，则云在松杨桥；至松杨桥，则云青蒿；至青蒿，则云在车坊；至车坊，则云在石龙坡；至石龙坡，则云在四祖山；至四祖山前，则云在太湖县",
 "故前乎援兵之未至，越二十有五日而城不陷者，实本州官寮民兵同守之力。",
 "妇人、女子各贾勇般石，与诸民兵相接击贼，渴不暇饮。",
 "太守寻乃就设厅，引剑自刎。",
 "遂设一室自焚，其时白袍犹未脱体，其子三将仕复同时就尽。",
 "我为国死，汝等可自求生。",
 "先遣其子女赴井，然后自投身于厅前井中",
 "于是相率投身于子城河内而死",
 "及蕲一破，应干库宇不留片瓦，惟此仓独存。今日饥民流归者，赖此存米，故得不死。",
 "一通判秦钜与男二人，将仕、婢仆五人，私仆三人，全家死难。",
 "一从政郎、司理赵与袭得脱性命，独存。",
 "李诚之、秦钜各特赠五官，更特赠秘阁修撰，仍各追赐紫章服",
 "今欲拟褒忠庙为额",
 "蕲州通判秦钜合拟封二字侯爵，今欲拟义烈侯",
 "蕲州知郡李诚之合拟封二字侯爵，今欲拟正节侯",
 "尔相阀之华，属承郡事，孤城岌岌，莫抗虏锋，能佐其长，服节守义，父子同陨，朕甚哀之。",
 "与{容衣}灾患余生，死不敢爱，呼天一鸣，以祈省览，且为它日之考证。",
 "自黄州分正军三万人来打蕲州",
 "具道虏人有左监军完颜鼎，有五万人马",
 "本州九里三十六步之城，共一千三百女头",
 "率厢禁军、民兵、市兵共有七百人，每人管女头两座",
]

fails = []
for i, q in enumerate(QUOTES, 1):
    qns = re.sub(r'\s+', '', q)
    if qns not in lib_ns:
        if han(q) in lib_han:
            fails.append((i, 'LOOSE-ONLY(去标点可中)', q))
        else:
            j = han(q)[:10]
            pos = lib_han.find(j)
            ctx = lib_han[max(0,pos-5):pos+30] if pos >= 0 else '(全然找不到)'
            fails.append((i, f'MISS 库本近处:{ctx}', q))
print(f'引文 {len(QUOTES)} 条，严比对未过 {len(fails)} 条')
for i, why, q in fails:
    print(f'  [{i}] {why}\n      {q}')

n = len(re.sub(r'\s+', '', lib))
print(f'库本去空白 {n} 字（自述应为 25398：{"OK" if n == 25398 else "MISMATCH"}）')

if '--full' in sys.argv:
    html = open(PAGE, encoding='utf-8').read()
    qtags = re.findall(r'<q[^>]*>(.*?)</q>', html, re.S)
    page_quotes = [re.sub(r'<span class="src">.*?</span>', '', q, flags=re.S) for q in qtags]
    page_quotes = [re.sub(r'<[^>]+>', '', q) for q in page_quotes]
    miss = [q for q in page_quotes if re.sub(r'\s+', '', q) not in lib_ns]
    print(f'页内 <q> 引文 {len(page_quotes)} 条，未过 {len(miss)} 条')
    for q in miss:
        print('  MISS:', q[:60])
    # 排版规则
    assert '—' not in html and '–' not in html, '长划线'
    for li, line in enumerate(html.split('\n'), 1):
        c = line.count('·')
        assert c <= 1, f'行{li} 含·{c}个'
    for tag in ['div', 'section', 'q', 'footer', 'header', 'aside']:
        o, c = html.count(f'<{tag}'), html.count(f'</{tag}>')
        o = len(re.findall(f'<{tag}[ >]', html))
        assert o == c, f'标签不配平 {tag}: {o} vs {c}'
    assert 'http://' not in html and 'https://' not in html, '外部依赖'
    pu = [c for c in html if 0xE000 <= ord(c) <= 0xF8FF]
    assert not pu, f'PUA 泄入页面 {len(pu)}'
    assert '二十五日' in html and '二十五日' in lib, '自述核'
    foot = re.search(r'<footer.*?</footer>', html, re.S).group(0)
    for kw in ['殆知阁', '核验', '时代局限', 'github.com']:
        assert kw in foot, f'页脚缺 {kw}'
    # mulu 检查：编号连续、计数两处、新条目在册
    mulu = open('daizhige-daodu/mulu.html', encoding='utf-8').read()
    nums = [int(n) for n in re.findall(r'<span class="no mono">(\d+)</span>', mulu)]
    snums = sorted(set(nums))
    assert snums == list(range(1, len(snums) + 1)), 'mulu 编号不连续'
    assert nums[-1] == len(snums), '末号与篇数不一致'
    cn = '一二三四五六七八九十'
    def cnum(n):
        d = {1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'七',8:'八',9:'九'}
        def u99(m):
            if m <= 10: return '十' if m == 10 else d[m]
            if m < 20: return '十' + d[m % 10]
            a, b = divmod(m, 10)
            return d[a] + '十' + (d[b] if b else '')
        if n <= 99: return u99(n)
        c, r = divmod(n, 100)
        if r == 0: return d[c] + '百'
        suf = ('一十' + d[r % 10]) if 10 <= r < 20 else u99(r)
        return d[c] + '百' + (('零' if r < 10 else '') + suf)
    want = f'{cnum(len(nums))}篇导读'
    assert want in mulu, f'mulu 计数缺 {want}'
    assert 'xinsi-qilu.html' in mulu and '辛巳泣蕲录' in mulu, 'mulu 缺新条目'
    print(f'排版/页脚/依赖/mulu 检查全过（共 {len(nums)} 篇）')
