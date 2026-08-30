#!/usr/bin/env python3
# verify_menggu.py — 蒙古秘史页核验：引文逐字比对 + 排版红线 + 机算数字
import re, json, sys, unicodedata

TXT = '../daizhige-simplified/集藏/演义/元朝秘史.txt'
PAGE = 'menggu-mishi.html'

def norm(x):
    return ''.join(ch for ch in x if ch.isalnum())

t = open(TXT, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()
ptext = re.sub(r'<[^>]+>', '', page)
Q = json.loads(r"""{
 "langlu": "当初元朝的人祖，是天生一个苍色的狼，与一个惨白色的鹿相配了，同渡过腾吉思名字的水，来到于斡难名字的河源头，不儿罕名字的山前住着，产了一个人，名字唤作巴塔赤罕。",
 "wujian": "春间，一日，他母亲阿阑豁阿煮着腊羊，将五个儿子唤来根前列坐着。每人与一只箭竿，教折折，各人都折折了。再将五只箭竿束在一处，教折折呵，五人轮着，都折不折。",
 "mutong": "您五个儿子，都是我一个肚皮里生的，如恰才五只箭竿一般，各自一只呵，任谁容易折折。您兄弟但同心呵，便如这五只箭竿束在一处，他人如何容易折得折！",
 "ying": "除影儿外无伴当，除尾子外无鞭子。",
 "she": "我死就死，您休将我别勒古台弃了。”",
 "panjiao": "说讫，盘脚坐着，等他的箭。帖木真两兄弟，自前自后，将别克帖儿射死了。",
 "yangwo": "又入斡难河水的溜道里仰卧着，身在水里，但露出面来。",
 "suoer": "正为你这般有见识了，所以上泰亦赤兀惕兄弟每妒害你。你谨慎，只那般卧着，我不告你。”",
 "huolian": "更与了一张弓、两只箭，不曾与他火镰，这般打发教去了。",
 "shisan": "成吉思被札木合推动，退着于斡难河哲列捏地面狭处屯札了。",
 "qiguo": "札木合于是回去，将赤那思地面有的大王每，教七十锅都煮了，又斫断捏兀歹察合安的头，马尾上拖着去了。",
 "zhebie0": "阔亦田地面对阵时，自岭上将我马项骨射断的，果是谁？",
 "zhebie1": "是我射来。如今皇帝教死呵，止污手掌般一块地。",
 "zhebie2": "但凡敌人害了人的事，他必隐讳了不说。如今你却不隐讳，可以做伴当。”",
 "zhebie3": "者别，军器之名也。",
 "liangyuan": "且我与你如车的两辕，一辕折了呵，牛拽不得；如车的两轮，一轮坏了呵，车行不得。",
 "zhixue": "王罕听了这言语，叹息着说：“帖木真儿子行，有不可离的道理！我已离了。”于是内心艰难，将刀刺破小指流血，就盛在小桦皮桶内，说：“我若见帖木真儿子害他呵，似这血般教刺着。”",
 "shaox": "只道达达每少，如何烧的火如星般多？",
 "xiannan": "眼上刺呵不转睛，腮上刺呵不躲避。",
 "jianguo": "至是虎儿年，于斡难河源头，建九脚白旄纛做皇帝，封功臣木合黎为国王",
 "qianhu": "整治达达百姓，除附马外，复授同开国有功者九十五人为千户。",
 "jiuci": "如今你的坐次，坐在众人之上，九次犯罪休罚。这西边直至金山，你做万户管者。”",
 "suoerh": "再教你子孙行，许他带弓箭，喝盏，九次犯罪休罚者。”",
 "suwei": "我的护卫散班等于各万户、千户、百户内，选一万人做者。",
 "tongguan": "金主闻知，迁都汴梁，其余金兵困饿，人皆相食。",
 "ashaganbu": "你气力既不能，不必做皇帝。”",
 "zhuima": "成吉思骑一匹红沙马，为野马所惊，成吉思坠马跌伤",
 "changsheng": "虽死呵，也去问他。长生天知者。",
 "jinjue": "教但凡进饮食时，须要提说：“唐兀惕尽绝了。”",
 "heilao": "黑老鸦会拿鸭子，奴婢能拿主人，皇帝安答必不差了。”",
 "che2": "我先曾教你做一只车辕，你分离去了。",
 "chan4": "自坐我父亲大位之后，添了四件勾当：一件平了金国，一件立了ㄢ赤，一件无水处教穿井，一件各城池内立探马赤镇守了；",
 "cha4": "一件听信妇人言语，取斡赤斤叔叔百姓的女子；一件将有忠义的朵豁勒忽因私恨阴害了；",
 "zhanma": "不是紧急事务，须要乘坐站马，不许沿百姓处经过。",
 "xiebi": "此书大聚会着，鼠儿年七月，于客鲁涟河阔迭额阿剌勒地面处下时，写毕了。"
}""")

fails = []
def chk(cond, msg):
    if not cond:
        fails.append(msg)

# 1. every quote: verbatim in txt (raw) and in page (norm), and page span norm == quote norm via substring
for k, v in Q.items():
    chk(v in t, 'QUOTE not raw in txt: ' + k)
    chk(norm(v) in norm(ptext), 'QUOTE not on page: ' + k)

# 2. every .q span must be norm-substring of txt
spans = re.findall(r'<span class="q"[^>]*>(.*?)</span>', page, re.S)
for i, sp in enumerate(spans):
    inner = norm(re.sub(r'<[^>]+>', '', sp))
    chk(inner != '' and inner in norm(t), '.q span #%d not in library: %s' % (i, inner[:24]))

# 3. redlines
chk('—' not in page and '–' not in page, 'em/en dash found')
for ln in page.split('\n'):
    b = re.sub(r'<[^>]+>', '', ln)
    chk(b.count('·') <= 1, 'line with >1 dot: ' + b[:60])
for ch in ['⺀', '⻵']:
    pass

# 4. machine counts
counts = {'成吉思': 222, '帖木真': 150, '安答': 29, '札木合': 95, '王罕': 103,
          '九次犯罪休罚': 3, '斡歌歹': 27, '斡歌夕': 1, '站赤': 2}
for w, c in counts.items():
    chk(t.count(w) == c, 'count ' + w + ': got %d want %d' % (t.count(w), c))
bopu = sum(1 for ch in t if 0x3105 <= ord(ch) <= 0x3129)
chk(bopu == 6, 'bopomofo count %d' % bopu)
chk(all(0xE000 > ord(c) or ord(c) > 0xF8FF for q in Q.values() for c in q), 'PUA leaked into quotes')

whole = len(re.sub(r'\s', '', t))
chk(whole == 48224, 'whole %d' % whole)
parts = re.split(r'(●卷[一二三四五六七八九十]+)', t)
vols = []
cur = None
for x in parts:
    if x.startswith('●卷'):
        cur = re.sub(r'\s', '', x[1:])
        vols.append([cur, ''])
    elif cur:
        vols[-1][1] += x
body = sum(len(re.sub(r'\s', '', b)) for _, b in vols)
chk(len(vols) == 15, 'vol count %d' % len(vols))
chk(body == 48166, 'body %d' % body)
chk(whole - body == 58, 'head+marks %d' % (whole - body))
per = [len(re.sub(r'\s', '', b)) for _, b in vols]
chk(per[0] == 5438 and per[-1] == 1058, 'per-vol ends %s' % per)

# page states its numbers
for frag in ['48,224', '48,166', '222', '95对103', '29']:
    chk(frag in ptext, 'page missing stat ' + frag)

print('.q spans checked:', len(spans))
print('quotes checked:', len(Q))
if fails:
    print('FAIL', len(fails))
    [print(' -', f) for f in fails]
    sys.exit(1)
print('ALL PASS')
