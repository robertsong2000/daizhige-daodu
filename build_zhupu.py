#!/usr/bin/env python3
# 竹谱详录导读页构建：锚点切片 -> token 注入，零誊写
import re

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/绘画/竹谱.txt'
TPL = 'zhupu-xianglu.tpl.html'
OUT = 'zhupu-xianglu.html'

Q = {
# 平生
'xu_danbo': ('予性澹泊', '于竹粗有知'),
'xu_youli': ('行役万余里', '无与寓目'),
'xu_shijiao': ('往岁仗国威灵', '区别品彚'),
'xu_nan': ('又十年始见文湖州', '得之如此其难也'),
'xu_chengshu': ('大德三年岁在乙亥', '蓟邱李衎仲宾父序'),
'cunwang': ('浙江鲍氏所', '载其完书'),
# 追真迹四幕
'mu1': ('予昔见人画竹', '如是者凡数十辈'),
'mu2': ('后得澹游先生所画', '遂愿学焉'),
'mu2b': ('或云黄华虽宗文', '宜异乎常人之为者'),
'mu3': ('邂逅友人王子庆', '曰非伪而何'),
'mu3b': ('明年四月重来', '欣然慰满平生矣'),
'mu3c': ('自是连得三本', '壹意师之'),
'mu4': ('独鲜于伯机父谓', '终非合作'),
# 胸中成竹
'cheng_zhu': ('文湖州授东坡诀云', '少纵则逝矣'),
'wu_shi': ('画竹之法一位置', '而后成竹'),
# 十病
'shi_bing': ('冲天撞地偏重偏轻', '断不可犯'),
# 竹态谱
'tai_cantou': ('如散生之竹竿下谓之蚕头', '谓之边或谓之鞭'),
'tai_weisun': ('边根出笋', '谓之蝉肚根'),
'tai_xiong': ('从根倒数上单节生枝者', '谓之雌竹'),
'tai_zuandigen': ('竹下插土者', '谓之钻地根'),
# 六品
'quande_intro': ('竹之为物非草非木', '故作全徳品'),
'quande_kui': ('筀竹出江浙河南北', '节叶枝干皆同'),
'yixing_intro': ('凡竹生于石则体坚而瘦硬', '故作异形品'),
'yixing_fang': ('方竹两浙江广处处有之', '以方为异矣'),
'yixing_wan': ('金海陵庶人完颜亮独喜作此', '每每画之'),
'yixing_jing': ('浄瓶竹江浙闽广俱有之', '宛如一瓶'),
'yise_intro': ('绿者竹之常色', '故作异色品'),
'yise_zi': ('紫竹出江浙两淮', '三年不斫四年死'),
'yise_yun': ('晕竹出湘全间', '殊可人意'),
'shenyi_intro': ('怪力乱神孔子所不语', '故作神异品'),
'shenyi_hualong': ('化龙竹后汉费长房', '顾见化为龙'),
'shenyi_laigong': ('莱公竹宋冦莱公凖', '号曰相公竹'),
'shenyi_she': ('射的竹小竹也', '暮北风后果然'),
'shenyi_xun': ('寻竹山海经云', '此处复见】'),
'sise_intro': ('古人有云物多相类而非', '故作似是而非竹品'),
'youming_intro': ('竹之比徳于君子者', '故作有名而非竹品'),
'youming_zong': ('椶榈竹两浙两广安南', '一如竹枝'),
# 墨竹谱
'mo1': ('墨竹位置一如画竹法', '便见枯荣'),
'mo2': ('生枝不应节', '方为成竹'),
'mo3': ('或叶如刀截', '不可胜言'),
'shuofu': ('撰墨竹谱【按说郛作管道升撰】', '作管道升撰】'),
# 尾屏
'coda1a': ('虚心劲节岁寒不变', '岁寒不变'),
'coda1b': ('是宜昔人特号以此君', '特号以此君'),
'coda2': ('画竹师李', '刻鹄类鹜'),
'coda3': ('求一艺之精', '信不易矣'),
}

t = open(SRC, encoding='utf-8').read()
slices = {}
for k, (a, b) in Q.items():
    assert t.count(a) == 1, f'{k}: start x{t.count(a)}'
    i = t.find(a)
    j = t.find(b, i)
    assert j >= 0, f'{k}: end missing'
    s = t[i:j + len(b)].strip()
    assert not re.search('[—–]', s), f'{k}: dash'
    s = ''.join('□' if 0xE000 <= ord(c) <= 0xF8FF else c for c in s)
    slices[k] = s

html = open(TPL, encoding='utf-8').read()
toks = set(re.findall(r'⟦([a-z0-9_]+)⟧', html))
missing = toks - set(slices)
unused = set(slices) - toks
assert not missing, f'missing tokens: {missing}'
for k, v in slices.items():
    html = html.replace('⟦' + k + '⟧', v)
assert '⟦' not in html, 'unreplaced token'
open(OUT, 'w', encoding='utf-8').write(html)
print(f'OK {OUT}: {len(slices)} slices injected, unused: {sorted(unused)}')
