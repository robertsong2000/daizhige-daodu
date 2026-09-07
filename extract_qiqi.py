# -*- coding: utf-8 -*-
"""从库本提取《奇器图说》引文原文，逐字生成 quotes_qiqi.json"""
import json, re, sys

LIB = 'daizhige-simplified/艺藏/器物/奇器图说.txt'
raw = open(LIB, encoding='utf-8').read()
flat = re.sub(r'\s+', '', raw)

SPANS = [
    ('bookname',  '竒器图说译西庠文字', '此学本名原是力艺'),
    ('liyi',      '力艺重学也', '故独私号之曰重学云'),
    ('shicheng',  '相授之原有一大人名亚希黙得', '此皆力艺学中传授之人也'),
    ('eureka',    '偶悟而得者如一国王', '匠自服罪之类是也'),
    ('sizhi',     '思之思之又重思之', '鬼神将通之'),
    ('gen_a',     '此欵乃重学之根本', '诸法皆取用于此'),
    ('gen_b',     '有两系重是凖等者', '又为互相比例'),
    ('yong3',     '器之用有三', '以代人力'),
    ('liuqi',     '器之总类有六', '六藤线'),
    ('shuzhi',    '造物生物有数有度', '重则此力艺之重学也'),
    ('qizhong',   '以十分而举一分', '起五百斤也'),
    ('feilun',    '飞轮者已似无用', '人力必大胜矣'),
    ('shuichong_a', '此水铳可以灭火', '所难比其功用者也'),
    ('shuichong_b', '但有此器则五六人', '预阻未燃之火'),
    ('shuichong_c', '凡城邑村坊悉当置此', '尚广为传造焉'),
    ('che_a',     '其甲轮之所以能动者', '无重则反不能动也'),
    ('che_b',     '总之无木牛之名', '可行三里'),
    ('hu_ming',   '流光难追', '寸隂是珍'),
    ('hu_zhi',    '向曽制一具在都中', '谅其匪妄也'),
    ('daigeng_a', '一人坐一架手挽其橛', '足敌两牛'),
    ('daigeng_b', '此余在计部观政时', '并记之若此'),
    ('daigeng_c', '向余在计部观政时', '先得我心之同然矣'),
    ('tiyao_a',   '征泾阳人天启壬戌进士', '故名曰重又谓之力艺'),
    ('tiyao_b',   '其第一卷之首有表性言', '寸有所长自宜节取'),
    ('tiyao_c',   '诸噐图说凡图十一', '亦具有思致云'),
    ('deyan',     '是重学也最确当', '最确当而无差'),
    ('fengwei',   '此盖西海金四表先生所传', '不无小补云'),
    ('heming',    '冽彼下泉', '谁其长此禾黍'),
]

out = {}
for name, a, b in SPANS:
    i, j = flat.find(a), flat.find(b)
    if i < 0 or j < 0:
        print(f'FAIL miss {name}: a={i} b={j}'); sys.exit(1)
    j = j + len(b)
    if j <= i:
        print(f'FAIL order {name}'); sys.exit(1)
    out[name] = flat[i:j]

json.dump(out, open('daizhige-daodu/quotes_qiqi.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# 统计
nostrip = re.sub(r'\s+', '', raw)
print('库本总字符', len(raw), '去空白', len(nostrip))
for kw in ['欵', '圗缺', '六十一条', '九十二条', '第□']:
    print(kw, raw.count(kw))
q1 = list(re.finditer(r'第[一二三四五六七八九十]+欵', raw))
vol2 = raw.find('竒器图说卷二')
vol3 = raw.find('竒器图说卷三')
n1 = len([m for m in q1 if m.start() < vol2])
n2 = len([m for m in q1 if vol2 < m.start() < vol3])
print('卷一欵标', n1, '卷二欵标', n2)
print('提取', len(out), '段，全部锚点命中')
