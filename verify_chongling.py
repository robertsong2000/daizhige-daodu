#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""崇陵传信录 页面核验：引文双侧逐字 + 「」反扫 + 红线 + 机数"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/chongling-chuanxin-lu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/崇陵传信录.txt'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF:
            out.append(ch)
    return ''.join(out)

libn = norm(lib)

# ---------- 1. 收集 .q 块 ----------
class QC(HTMLParser):
    VOID = {'br','img','meta','link','hr','input','area','base','col','embed','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, is_q)
        self.qdepth = 0
        self.skip_depth = 0      # eyetag/who/style/script 内容剥离
        self.skip_tag = None
        self.blocks = []
        self.cur = []
        self.in_style = 0
    def handle_starttag(self, tag, attrs):
        if self.in_style:
            return
        if tag in ('style','script'):
            self.in_style += 1
            return
        if self.skip_tag:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return
        cls = dict(attrs).get('class','') or ''
        is_q = 'q' in cls.split()
        if 'eyetag' in cls.split() or 'who' in cls.split():
            self.skip_tag = tag
            self.skip_depth = 1
            return
        if tag in self.VOID:
            return
        if is_q and self.qdepth == 0:
            self.qdepth = len(self.stack) + 1
            self.cur = []
        self.stack.append((tag, is_q))
    def handle_endtag(self, tag):
        if self.in_style:
            if tag in ('style','script'):
                self.in_style -= 1
            return
        if self.skip_tag:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    self.skip_tag = None
            return
        if tag in self.VOID:
            return
        # 配平：回退到同名标签
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if self.qdepth and len(self.stack) < self.qdepth:
            txt = ''.join(self.cur)
            if txt.strip():
                self.blocks.append(txt)
            self.qdepth = 0
            self.cur = []
    def handle_data(self, data):
        if self.in_style or self.skip_tag:
            return
        if self.qdepth:
            self.cur.append(data)

qc = QC()
qc.feed(page)
blocks = qc.blocks
fails = []
for i, b in enumerate(blocks):
    bn = norm(b)
    if not bn:
        fails.append(('EMPTY', i, b[:40])); continue
    if bn not in libn:
        fails.append(('BLOCK', i, b[:60]))
print(f'收集 .q 块 {len(blocks)} 枚；块级 MISS {len(fails)}')
for f in fails: print('  MISS', f)

# ---------- 2. 「」反扫（可见文本全部引号必须对库） ----------
vis = re.sub(r'<style[\s\S]*?</style>', '', page)
vis = re.sub(r'<script[\s\S]*?</script>', '', vis)
vis = re.sub(r'<[^>]+>', '', vis)
quotes = re.findall(r'「([^」]*)」', vis)
bad = [q for q in quotes if norm(q) and norm(q) not in libn]
print(f'「」反扫 {len(quotes)} 条；MISS {len(bad)}')
for q in bad: print('  MISS', q[:50])

# ---------- 3. EXPECTED 清单（页面+库本双侧） ----------
EXPECTED = [
 '毓鼎事先帝十九年，侍螭头，领阑台，所居皆史职。',
 '天颜戚戚，常若不愉，未尝一日展容舒气也。',
 '后之人稽光绪一朝事，所见者懿旨耳，上谕耳，奏疏耳。先帝一多病柔懦之主而已，庸讵知天挺英明，豁达大度，奋发欲有所为。',
 '大臣列传，则缀拾邸抄公牍，不得有所采访，申己意，盖太史南董之风坠地尽矣。',
 '弃臣民之后半月，冲主御法驾，升正殿，行即位礼。毓鼎侍班御座前，默思先帝生平遭际困厄，心酸鼻辛，欲制泪不禁涔涔被面矣。',
 '幼而提携，长而禁制，终于损其天年，无母子之亲，无夫妇、昆季之爱，无臣下侍从宴游暇豫之乐',
 '无恩私，无党议，可以告先帝而质鬼神。',
 '两宫之垂帘也，帝中坐，后蔽以纱幕，孝贞、孝钦左右对面坐。',
 '孝贞既崩，孝钦独坐于后。',
 '至戊戌训政，则太后与上并坐，若二君焉。',
 '迁上于南海瀛台，三面皆水，隆冬冰坚结',
 '传闻上常携小阉踏冰出，为门者所阻，于是有传匠凿冰之举。',
 '上常至一太监屋，几有书，取视之，《三国演义》也。阅数行掷去，长叹曰：',
 '朕并不如汉献帝也！',
 '上幼畏雷声，虽在书房，必投身翁师傅怀中。',
 '体气健实，三十四年无疾病，未尝一日辍朝',
 '《天禄琳琅》初集之书，向储颐和园，庚申毁于兵火。',
 '二公共出银十两，给守殿太监为扫除费。',
 '闻德宗以此书置案头，时展览，颐和驻跸，亦携以自随',
 '上首问翰林院藏书及《永乐大典》所存册数，又问近有新出金石否，谕毓鼎在家宜多看书，不可专习诗赋',
 '光绪庚子，兵攻使馆，翰林院后墙正界英馆，亦毁于火，《大典》散入英馆，焚毁遗失者过半。',
 '此亦书林一大掌故也。',
 '壬寅年闻广肆有《大典》十余册出售',
 '毓鼎急网求之，则已为捷足者所得，至今思之犹耿耿',
 '此如日月之食，何足为圣明之累耶？',
 '夜半忽急诏促入诊，踉跄至干清宫，则见帝颜色大变，痘疮溃陷，其气甚恶。',
 '卿暂忍耐，终有出头日也。',
 '慈禧侦后诣帝所，窃尾之。',
 '去履袜行，伏幕外听之',
 '揭幕入，牵后发以出，且行且痛抶之，传内廷备大杖。',
 '帝惊恐且悲，坠于地，昏晕移时始苏，痘遂变。',
 '遂于次年二月二十日吞金以殉。',
 '惠陵上仙，实系患痘，外传花柳毒者非也。',
 '凶信出，百官皆以为西圣也。',
 '吾姊妹相处久，无闲言，何必留此诏乎？',
 '立取火焚之。',
 '西佛爷食之甚美，不肯独用，特分呈东佛爷。',
 '启盒，拈一饼对使者尝之，以示感意',
 '旋即传太医，谓东圣骤痰。',
 '厥医未入宫，而凤驭上升矣。',
 '辛巳后，土木游宴之风始盛',
 '太后直抵上寝宫，尽括章疏，携之去。',
 '我抚养汝二十余年，乃听小人之言谋我乎！',
 '我无此意。',
 '痴儿今日无我，明日安有汝乎！',
 '凡已见官书及外间记载者，概略之，以此录非政纪也。',
 '每日造脉案药方，传示各衙门，人心汹惧。',
 '今日换皇上矣。',
 '传闻将有废立事信乎？',
 '迨诏下，乃立溥俊为大阿哥也。',
 '大阿哥素不悦学，有所喜二犬，次日即宣索入宫，识者早有以虑其不终。',
 '此疏若为太后见，言官祸且不测，朕当保全之。',
 '甲午之丧师，戊戌之变政，己亥之建储，庚子之义和团，名虽四事，实一贯相生，必知此而后可论十年之朝局。',
 '殿南向，上及太后背窗向北坐，枢臣礼亲王世铎、荣禄、王文韶、赵书翘跪御案旁，自南而北，若雁行',
 '臣顷见董福祥，欲请上旨，令其驱逐乱民。',
 '好！此即失人心第一法。',
 '皇太后信乱民，敌西洋，不知欲倚何人办此大事？',
 '我恃董福祥。',
 '董福祥第一即不可恃。',
 '汝何姓名？',
 '汝保人来！',
 '山东巡抚袁世凯，忠勇有胆识，可调入京镇压乱民。',
 '太后于祖谋之出，犹怒目送之。',
 '顷得洋人照会四条，一、指明一地，令中国皇帝居注；一、代收各省钱粮；一、代掌天下兵权。',
 '其一勒令皇太后归政，太后讳言之也',
 '有机密事告急！',
 '荣相绕屋行，彷徨终夜，黎明遽进御。',
 '故二十五日宣战诏，不及此事。',
 '今日衅开自彼，国亡在目前。若竟拱手让之，我死无面目见列圣。',
 '谓皇太后送祖宗三百年天下',
 '臣等愿效死力',
 '庙谟盖已预定，特藉盈廷集议，一以为左证，一以备分谤。',
 '更妥商量。',
 '皇帝放手，毋误事！',
 '端郡王所居势位，与醇贤亲王相同，尤当善处嫌疑之地。',
 '欲袭桓温枋头故智，多诛戮大臣，以示威而逼上',
 '下刑部一夕，未讯供，骈斩西市。有妇人宁家，亦陷其中，杂诛之，儿犹在抱也。',
 '是日风霾晦冥，见者冤痛。',
 '谓谋乱当有据，羸翁弱妇，非谋乱之人，优装玩具，非谋乱之物',
 '钦命义和团王大臣奉懿旨，闻户部尚书立山藏匿洋人，行踪诡秘，着该大臣查明办理。',
 '诏文荒诞鄙俚，官文书所不载，特录存之，以为此诏非出宫廷之证。',
 '余故悉着其实，备后世秉史笔者取材焉。',
 '冠裳寥落，仅成朝仪。',
 '东华门不启，群臣皆入神武门。',
 '两宫黎明仓皇乘民车出德胜门。甫出门，白旗遍城上矣。',
 '太后御夏衣，挽便髻，上御青绸衫，皇后及大阿哥随行，妃嫔罕从者。',
 '濒行，太后命崔阉自三所出珍妃（三所在景远门外），推堕井中。',
 '乃出妃尸于井。浅葬京西田村。',
 '金井一叶堕，凄凉瑶殿旁。残枝未零落，映日有辉光。沟水空流恨，霓裳与断肠。何如泽畔草，犹得宿鸳鸯。',
 '老仆于屋梁结两绳，一左一右，徐相就其左，既承颈犹以目视右结，意固在承煜。',
 '此汉奸，杀之犹轻，何恤？',
 '在宅做大坑，自瘗死，并老母幼子皆生葬土中',
 '吾不忍见白旗也！',
 '我不意犹能见尔等！',
 '诸臣辄先哭数声，若举哀焉，慈颜则稍霁矣。',
 '读诏讫，从容再拜，谢罪毕，阖户自经',
 '舒翘故健实，吞金不死，服洋药不死',
 '以桑皮纸浸烧酒闭口鼻，气始绝。',
 '门罅未阖，侍班窥见上正扶阉肩，以两足起落作势，舒筋骨为跪拜计。',
 '须臾忽奉懿旨：皇帝卧病在床，免率百官行礼，辍侍班。上闻之大恸。',
 '有谮上者，谓帝闻太后病，有喜色。',
 '我不能先尔死！',
 '请脉时，上以双手仰置御案，默不出一言，别纸书病状陈案间。',
 '入诊者佥云六脉平和无病也',
 '有大星从西北来掠屋檐过，其声如雷，尾长数十丈',
 '皇后始省上于寝宫，不知何时气绝矣',
 '盍先殓乎？',
 '上尊号曰崇陵。',
 '王室其遂微矣。',
 '吾立朝近四十年，识近属亲贵迨遍，异日御区宇、握大权者，皆出其中，察其器识，无一足当军国之重者。',
 '其言至是而信。',
 '吾子孙虽存一女子，亦必覆满洲！',
 '勤惠致赙三百两（或传二千两非也），将命者误送孝钦舟。',
 '吾姊妹他日倘得志，无忘此令也。',
 '妹亦为醇贤亲王福晋，诞德宗。',
 '帝崩之次日，太后乃崩。',
 '宣统三年辛亥四月湖滨旧史恽毓鼎',
 '他日陵谷变迁，函开心史，三十四年之朝局，庶有大明之一日乎？',
]
pgv = norm(vis)
e_bad = []
for q in EXPECTED:
    qn = norm(q)
    if qn not in libn: e_bad.append(('LIB', q[:40]))
    if qn not in pgv:  e_bad.append(('PAGE', q[:40]))
print(f'EXPECTED {len(EXPECTED)} 条；双侧 MISS {len(e_bad)}')
for t, q in e_bad: print(f'  MISS[{t}]', q)

# ---------- 4. 红线 ----------
lines = [l for l in vis.split('\n')]
dash = [l.strip() for l in lines if ('—' in l or '–' in l)]
mid2 = [l.strip() for l in lines if l.count('·') > 1]
print(f'红线：长划 {len(dash)} 行；一行多· {len(mid2)} 行')
for l in dash[:5]: print('  —', l[:60])
for l in mid2[:5]: print('  ··', l[:60])

# ---------- 5. 机数 ----------
cnts = {'毓鼎':23,'三十四年':4,'起居注':3,'井':6,'叶赫':6,'仪鸾殿':5,'吞金':3,'急诏':2,'夜半':2,
        '天颜戚戚':1,'汉献帝':1,'克食':1,'桐宫之举':1,'今日换皇上矣':1,'我不能先尔死':1,'白旗':2,
        '德胜门':1,'脉案':1,'紫微星堕':1,'名刺':1,'函开心史':1,'质鬼神':1}
c_bad = [(k, lib.count(k), v) for k, v in cnts.items() if lib.count(k) != v]
print('机数与库本不符:', c_bad if c_bad else '无')
body = re.sub(r'\s','',lib)
hans = sum(1 for c in lib if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x2FFFF)
assert len(lib) == 16204, len(lib)
assert len(body) == 16115, len(body)
assert hans == 13576, hans
assert len([p for p in lib.split('\n') if p.strip()]) == 39
for s in ['16,204','16,115','13,576','三十九段','二十三见','之一百三十七','卷七十八','直庐']:
    assert s in page, s
pua = [c for c in page if 0xE000 <= ord(c) <= 0xF8FF]
ext = [c for c in re.sub(r'<style[\s\S]*?</style>','',page) if 0x20000 <= ord(c) <= 0x2FFFF]
print('PUA/扩展区字符:', len(pua), len(ext))
ok = not fails and not bad and not e_bad and not dash and not mid2 and not c_bad and not pua and not ext
print('RESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
