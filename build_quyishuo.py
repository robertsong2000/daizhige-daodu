# -*- coding: utf-8 -*-
"""祛疑说导读页构建：引文全部程序化切片，零转写。"""
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/祛疑说.txt'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/quyishuo.html'

text = open(SRC, encoding='utf-8').read()

QUOTES = {
 'taiyao':   ('以平生笃好术数', '因作此而辨之'),
 'sanliu':   ('余皆考阴阳五行家言', '与黄白之说'),
 'luli':     ('余自緫角爱行持', '印几百颗'),
 'jiangli':  ('方知将吏只在身中', '神明不离方寸'),
 'duoshan':  ('而多所删削', '殊非储氏之旧'),
 't_shui':   ('咒水自沸', '咒水自沸'),
 'q_shui':   ('余旧见咒水者', '用手法助之耳'),
 'q_ying':   ('乃隐像于镜', '良可笑也'),
 't_jian':   ('叱剑斩鬼', '叱剑斩鬼'),
 'q_zhan':   ('毎置剑空室中', '流血满地'),
 'q_cao':    ('乃出示一草实', '水皆血色'),
 'q_xue':    ('血因形而生', '天下未有无形而有血者'),
 't_zao':    ('咒枣烟起', '咒枣自焦'),
 'q_zao':    ('乃知枣之烟者', '顷之自焦'),
 't_lu':     ('烧香召雷神', '钱入水即化'),
 'q_xiang':  ('以夜逰艾纳数药合而为香', '恍如雷神'),
 'q_qian':   ('乃用荸荠、水银杂草药数种', '钱入即化'),
 't_fu':     ('请封书僊', '请封书僊'),
 'q_feng':   ('其封愈多而牢', '惑而信者多矣'),
 'q_ma':     ('或以天麻子油书之', '不见其迹'),
 't_he':     ('呼鹤自至', '呼鹤自至'),
 'q_jiu':    ('其法用活雄鸠血书符', '其法用活雄鸠血书符'),
 'q_quan':   ('阅其咒语，尽从反犬', '遂不卒受其说'),
 't_fushe':  ('覆射', '覆射'),
 'q_shi':    ('惟一法用七言诗两首', '皆包罗而不遗'),
 'q_luo':    ('人但见其或击锣鼓', '寄幸于此也'),
 'q_shu':    ('取其箧中香末试烧', '蚊悉逺去'),
 'q_hehua':  ('来日叩之，微笑不答', '想亦荷花之须耳'),
 'q_gui_a':  ('夫鬼神者，本无形迹之可见', '谓之有则不可'),
 'q_gui_b':  ('非鬼神之显著者乎', '此谓之无则又不可'),
 'q_ju':     ('气聚则显然成象', '气散则泯然无迹'),
 'q_ling':   ('此非土木之灵', '乃人心之灵耳'),
 'q_xinju':  ('人心所聚，灵气之所聚也', '人心所聚，灵气之所聚也'),
 'q_yao':    ('乃取活蛇生鸦', '实助其妖孽耳'),
 'q_tai':    ('太史公言', '信哉斯言'),
 'q_16':     ('余为之断曰：大而紧者避之', '背于理者去之，如太岁一星'),
 'q_ge':     ('或有用汞以取银之体', '名曰隔窻取母'),
 'q_can':    ('如蚕室太阴', '可以略去'),
 'q_zhen':   ('不知金丹者，人之真阳', '岂徒以黄白为事'),
 'q_fu':     ('不思彼有是术', '又何待以传授资身也'),
 'q_kui':    ('凡水银入匮', '则水银为烟焰之归矣'),
 'q_yu':     ('或以金银为鼎器', '名曰玉女飜身'),
 'q_se':     ('然其体似银则色黄而体顽', '似铜则质润而色鲜'),
 'q_danfull':('彼嗜欲者，水竭于下', '百证俱见'),

 'q_sha':    ('用逺志、龙齿之类煅之', '则可以实脾气'),
 'q_shag':   ('随其佐使而见功', '无施不可'),
 'q_zhi':    ('故余特叙其术之大概', '正虑是也'),
 'q_duan':   ('不究端倪，皆非至当', '不究端倪，皆非至当'),
}

def slice_q(k):
    a, b = QUOTES[k]
    i = text.find(a)
    j = text.find(b)
    assert i >= 0 and j >= i, k
    s = text[i:j + len(b)]
    assert s not in ('',), k
    return s.strip()

html = open('/home/robertsong/workspace/claude/daizhige-daodu/quyishuo.tpl.html', encoding='utf-8').read()

def sub_q(m):
    return '<span class="q">' + slice_q(m.group(1)) + '</span>'

def sub_t(m):
    return slice_q(m.group(1))

html, n = re.subn(r'\{\{Q:([a-z_0-9]+)\}\}', sub_q, html)
html, nt = re.subn(r'\{\{T:([a-z_0-9]+)\}\}', sub_t, html)
missing = re.findall(r'\{\{[QT]:([a-z_0-9]+)\}\}', html)
assert not missing, missing
tpl_src = open('/home/robertsong/workspace/claude/daizhige-daodu/quyishuo.tpl.html', encoding='utf-8').read()
unused = [k for k in QUOTES if '{{Q:%s}}' % k not in tpl_src and '{{T:%s}}' % k not in tpl_src]
assert not unused, unused

open(OUT, 'w', encoding='utf-8').write(html)
print('wrote', OUT, '| quotes:', n, '| src chars(no ws):', len(re.sub(r'\s', '', text)))
