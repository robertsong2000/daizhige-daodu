import json, re

SRC = '../daizhige-simplified/史藏/志存记录/朝野佥载.txt'
t = open(SRC, encoding='utf-8').read()

def pick(start, end):
    i = t.index(start)
    j = t.index(end, i) + len(end)
    return t[i:j]

QUOTES = {
    'q_qianxing': pick('张文成曰：干封以前选人', '每岁常至五万。'),
    'q_xuanren':  pick('是以选人冗冗', '多于蚁聚。'),
    'q_xiezhi':   pick('獬豸岂识字', '罪人而已。'),
    'q_housizhi': pick('不用你书言笔语', '即与你孟青。'),
    'q_hou_zhu':  pick('白司马者，北邙山', '孟青棒也。'),
    'q_bang':     pick('兴乃榜门判曰', '咸悉无言。'),
    'q_museng':   pick('将作大匠杨务廉甚有巧思', '施者日盈数千矣。'),
    'q_muren':    pick('刻木为人，衣以缯彩', '皆能应节。'),
    'q_renyao1':  pick('苟牵绳一断', '则扑杀数十人。'),
    'q_renyao2':  pick('皆称杨务廉', '以破残百姓。'),
    'q_yao1':     pick('莫浪语', '三叔闻时笑杀人。'),
    'q_yao1_zhu': pick('阿婆者，则天也', '孝和为第三也。'),
    'q_yao2':     pick('张公吃酒李公醉', '李公醉。'),
    'q_yao2_zhu': pick('张公者，斥易之兄弟也', '言李氏大盛也。'),
    'q_lvzhu0':   pick('石家金谷重新声', '一代容颜为君尽。'),
    'q_lvzhu1':   pick('百年离恨在高楼', '一代容颜为君尽。'),
    'q_lvzhu2':   pick('碧玉读诗，饮泪不食', '投井而死。'),
    'q_wenchen1': pick('率更令张文成，枭晨鸣于庭树', '连唾之。'),
    'q_wenchen2': pick('急洒扫', '吾当改官。'),
    'q_ding':     pick('鼎今乞得即喜', '去菩萨远矣。'),
    'q_chen2':    pick('臣据玄象推算', '殆将歼尽。'),
    'q_chen1':    pick('天之所命', '虽求恐不可得。'),
    'q_feiqian_short': pick('当今之选', '非钱不行。'),
    'q_zhou':     pick('若违心负教', '横遭三豹。'),
}

out = {}
norm = lambda s: re.sub(r'\s', '', s)
tn = norm(t)
for k, v in QUOTES.items():
    out[k] = v
    print(k, '|', v)
    assert norm(v) in tn, k

json.dump(out, open('quotes_chaoye.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('OK', len(out), 'quotes -> quotes_chaoye.json')
