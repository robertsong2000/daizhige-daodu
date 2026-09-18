#!/usr/bin/env python3
"""build canluanlu.html: slice quotes verbatim from the daizhige file, inject into tpl."""
import sys, re

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/传记/骖鸾录.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/canluanlu.tpl.html'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/canluanlu.html'

PIAOHAO = sys.argv[1] if len(sys.argv) > 1 else '454'
JUANHAO = sys.argv[2] if len(sys.argv) > 2 else '三百三十三'

s = open(SRC, encoding='utf-8').read()

def cut(a, b):
    i = s.find(a)
    assert i >= 0, 'start not found: ' + a
    j = s.find(b, i)
    assert j >= 0, 'end not found: ' + b
    return s[i:j + len(b)]

def cut_last(a, b):
    i = s.rfind(a)
    assert i >= 0, 'start not found: ' + a
    j = s.find(b, i)
    assert j >= 0, 'end not found: ' + b
    return s[i:j + len(b)]

Q = {
 'Q1A1': cut_last('逺胜登仙去', '逺胜登仙去'),
 'Q1A2': cut_last('飞鸾不暇骖', '飞鸾不暇骖'),
 'Q1B':  cut('其曰“骖鸾”者', '语也。'),
 'Q27':  cut('其辨元结', '忠厚之旨。'),
 'Q4':   cut('雪满千山', '未必过此。'),
 'Q5':   cut('扫雪坐平石上', '境过清矣。'),
 'Q6':   cut('薄宦区区如此', '岂惟愧羊裘公。'),
 'Q6B':  cut('后十年以括苍假守被召', '复自和三篇。'),
 'Q7':   cut('休宁山中宜杉', '故取之难穷。'),
 'Q8':   cut('盖一木出山或不直百钱', '费使之。'),
 'Q9B':  cut('严之官吏方曰', '不为州矣”。'),
 'Q10':  cut('其故基甚侈', '罢久矣。'),
 'Q11':  cut('名为盗区', '不可过。'),
 'Q13':  cut('吾行四方，见园池多矣', '非甲而何？'),
 'Q14':  cut('岭阪上皆禾田', '名“梯田”。'),
 'Q15':  cut('岭阪上皆禾田', '名“梯田”。'),
 'Q16':  cut_last('庙有杨氏称吴时加封司徒竹册', '文称宝大元年。'),
 'Q18':  cut('譬如上寿父母之前', '非奉觞时可及。'),
 'Q26':  cut('善恶自有史册', '不当含讥。'),
 'Q28':  cut('甫入桂林界', '指似夸叹。'),
 'Q29':  cut('道上时见鲜血之点', '然亦怪何其多也。'),
 'Q30':  cut('忽悟此必食槟榔者所唾', '徐究之果然。'),
 'Q31':  cut('入严关两山之间', '限岭南北。'),
 'Q32':  cut('蒸水自邵阳来', '绕其右'),
 'Q33':  cut('夜分大雪', '亦竒赏也。'),
 'Q35':  cut('湘江岸小山坡陀其来无穷', '荒凉相属耳。'),
 'Q36':  cut('自婺至衢，皆砖街', '泥涂之忧。'),
 'Q37':  cut('自入常山至此', '浙西之所乏也。'),
 'Q38':  cut('自吴至桂三千里', '皆夷坦，无大山'),
 'Q39':  cut_last('若其风土之详', '焉。'),
 'Q40':  cut('比登一小岭', '湖南界矣。'),
 'Q41':  cut('环皆市区', '盗贼亡命多隐其间'),
 'Q42':  cut('君今过岭入厉土', '安否问？'),
 'Q43':  cut('参天带水，翠羽黄甘', '之语'),
 'Q44':  cut('烦君净洗南来眼', '胜北州”。'),
 'Q12':  cut('夜遣从卒', '以安众。'),
 'Q34':  cut('帅司亟遣众工模搨', '用摸本更画'),
}
# 泊牌引文，序号对应 stations[].q（0=无）
PAI = {
 1:'Q2P', 2:'Q3P', 3:'Q4P', 4:'Q36', 5:'Q37', 6:'Q11',
 7:'Q10', 8:'Q13', 9:'Q40', 10:'Q35', 11:'Q34', 12:'Q32',
 13:'Q18', 14:'Q39',
}
# 泊牌引文实际切片（P 系列避免与正文占位冲突）
PAISLICE = {
 'Q2P': cut('夜登垂虹', '遂泊桥下。'),
 'Q3P': cut('分路时，心目刲断', '信然。'),
 'Q4P': cut('雪满千山', '不胜清绝。'),
}
PAI = {
 1:'Q2P', 2:'Q3P', 3:'Q42', 4:'Q36', 5:'Q37', 6:'Q11',
 7:'Q10', 8:'Q13', 9:'Q40', 10:'Q35', 11:'Q34',
 12:'Q32', 13:'Q18', 14:'Q39',
}

STATIONS = [
 ('乾道八年腊月','吴郡','泊姑苏馆待发。中书舍人外放静江府，举家登舟。',0),
 ('乾道八年腊月','垂虹','送客至松江，夜里同登长桥看月，主客都忘了赶路。',1),
 ('乾道八年腊月','震泽','故人来会。他记起去年北道之行半路病危，几乎不返。',0),
 ('乾道八年腊月','余杭','同行乳母病喘难进，托付给同乳的妹妹。临别一幕最见性情。',2),
 ('乾道八年腊月','富阳','弃舟登陆。亲友遮道泣送，都问岭南瘴气带没带药。',3),
 ('乾道八年腊月','桐庐','除夕夜开到桐庐，船头看雪看了一路。详见折一。',0),
 ('乾道九年正月','钓台','元正登台讲礼，扫雪坐石，第四次过严光钓台。详见折二。',0),
 ('乾道九年正月','严州','在浮桥边看木税，给一根杉木算了笔账。详见折三。',0),
 ('乾道九年正月','兰溪','旧日出名酒，近年酒坊归了漕司，酒味大不如前。',0),
 ('乾道九年正月','衢州','婺衢之间有砖街直路，原是两家结亲的富户凑钱修的。',4),
 ('乾道九年正月','玉山','入信州。沿途乔木清溪，倒把浙西比了下去。',5),
 ('乾道九年正月','余干','访琵琶洲，记下长沙人怕此洲吸干本地水气、远道来凿洲的传闻。',0),
 ('乾道九年闰正月','邬子','鄱阳湖尾有名的水盗出没地。大雪夜有人报盗船不远，他叫人在苇丛边烧船壮胆，稳住一船人。',6),
 ('乾道九年闰正月','南昌','登滕王阁。名楼基址犹在，楼上如今租给酒商。详见水程牌按语。',7),
 ('乾道九年闰正月','东湖','游东湖，访孺子亭许真君观，看镇蛟的铁柱。',0),
 ('乾道九年闰正月','芗林','雨中连游芗林盘园两座名园，听朋友把自家的石湖捧为东南第一。',8),
 ('乾道九年闰正月','仰山','访仰山，山腹见层层稻田直到顶。详见折四。',0),
 ('乾道九年闰正月','醴陵','翻过小岭眼前大亮，已入湖南界，驿屋号称两湖最雄。',9),
 ('乾道九年二月','湘江','开始沿湘江行船，六日早暮不停，两岸土山连绵不见秀色。',10),
 ('乾道九年二月','南岳','谒岳庙。记壁画的劫后余生：火灾后官府抢拓旧本，新庙照拓本重绘。',11),
 ('乾道九年二月','衡州','石鼓书院就在州治里。三水会流的地形，被他比作诸侯入朝会盟。',12),
 ('乾道九年二月','浯溪','停舟看中兴颂摩崖，题诗开骂战。详见折五。',13),
 ('乾道九年二月','愚溪','渡潇水寻柳州旧迹，钴鉧潭诸胜已埋进竹丛，无人说得出准处。',0),
 ('乾道九年二月','桂林界','石峰如排衙列队，官道血点成谜。详见折六。',0),
 ('乾道九年二月','八桂堂','泊桂林北城外别圃，一住十天，候交割。',0),
 ('乾道九年三月','桂林城','入城接印。行纪到此收笔，风土另写进桂海虞衡志。',14),
]

CN = ['一','二','三','四','五','六','七','八','九','十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','廿一','廿二','廿三','廿四','廿五','廿六']

def qhtml(tok):
    return '<span class="q">{{%s}}</span>' % tok

stations_html = []
for i, (era, place, note, qi) in enumerate(STATIONS):
    no = '第%s泊 · 共廿六泊' % CN[i]
    parts = ['<div class="qnote" data-i="%d">' % i,
             '<p class="no">%s</p>' % no,
             '<p class="pd">%s</p>' % era,
             '<h4 class="pl">%s</h4>' % place,
             '<p class="nt">%s</p>' % note]
    if qi:
        parts.append('<p>%s</p>' % qhtml(PAI[qi]))
    parts.append('</div>')
    stations_html.append('\n'.join(parts))

html = open(TPL, encoding='utf-8').read()
html = html.replace('{{STATIONS}}', '\n'.join(stations_html))
for k, v in Q.items():
    html = html.replace('{{%s}}' % k, v)
for k, v in PAISLICE.items():
    html = html.replace('{{%s}}' % k, v)
html = html.replace('{{PIAOHAO}}', PIAOHAO).replace('{{JUANHAO}}', JUANHAO)
assert '{{' not in html, 'unresolved placeholder: ' + html[html.find('{{'):html.find('{{') + 40]
open(OUT, 'w', encoding='utf-8').write(html)
nq = html.count('<span class="q">') + html.count('<span class="qv">')
print('built %s, piaohao=%s, juan=%s, q count=%d' % (OUT, PIAOHAO, JUANHAO, nq))
