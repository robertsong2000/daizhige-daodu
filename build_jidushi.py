#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_jidushi.py — 注入 200 首全谱 qbank 与友传数据"""
import json, re

PAGE='/home/robertsong/workspace/claude/daizhige-daodu/jidushi.html'
POEMS='/tmp/jidu/poems.json'

PUA={'\U0002B3AC':'赣','\U0002543B':'碙','\uE638':'殓','\uE749':'眇','\uE805':'冥',
     '\uE867':'隉','\uE898':'瓜','\uEA1F':'弘','\uEA20':'玄','\uEB11':'□','\uEB9E':'徊',
     '\uEBB7':'□','\uEC46':'□','\uED3F':'眩','\uED70':'禩','\uEE98':'□','\uEEA1':'过',
     '\uEECA':'铉','\uF65F':'□','\uF81B':'□'}
def mp(t):
    for k,v in PUA.items(): t=t.replace(k,v)
    return t

def seg(n):
    if n<=52: return 'guo'
    if n<=104: return 'shen'
    if n<=138: return 'you'
    if n<=155: return 'jia'
    if n<=191: return 'xin'
    return 'shi'

poems=json.load(open(POEMS,encoding='utf-8'))
assert len(poems)==200

parts=[]
for p in poems:
    name=mp(p['name'])
    a=['<div class="qb-e" data-n="%d" data-name="%s" data-g="%s" data-que="%d">'%(p['n'],name,seg(p['n']),1 if p['que'] else 0)]
    if p['gx']:
        a.append('<span class="qb-gx qv">%s</span>'%mp(p['gx']))
    if p['que']:
        pass
    else:
        for txt,srcp in p['lines']:
            a.append('<span class="qb-l"><b class="qv">%s</b><i class="qv">%s</i></span>'%(mp(txt),mp(srcp)))
    a.append('</div>')
    parts.append(''.join(a))
qb='\n'.join(parts)

FRIENDS=[
 dict(name='金应',ti='承信郎路分，随身笔吏',no='第110首',qs=[
  '承信郎路分金应元备笔札使令性刚知义随勤王入京予陷敌左右星散惟应无叛去',
  '至通州以忧欝病死葬城下哀哉']),
 dict(name='张云',ti='吉州敢勇将官',no='第111首',qs=[
  '云不胜愤七月引所部袭敌于南栅门击杀甚众',
  '使能少忍当为吾用哀哉']),
 dict(name='吕武',ti='环卫官，太平人',no='第113首',qs=[
  '予陷冦应募随从北行其人劲烈靣折人触忌讳不避',
  '挺身冦寨化贼为兵']),
 dict(name='巩信',ti='团练使都统招谕使，荆湖老将',no='第114首',qs=[
  '信据险坚立不动中数箭死土人殓之如生']),
 dict(name='徐榛',ti='正将，温州人，此首诗阙',no='第134首',qs=[
  '予被执榛得脱自惠州来五羊愿从北行扶持患难备殚忠欵道病至丰城死焉']),
 dict(name='缪朝宗',ti='环卫官知梅州，淮人',no='第116首',qs=[
  '军府器械悉出其手空坑之败自经于山间哀哉']),
 dict(name='赵时赏',ti='督府参议官，宗室',no='第119首',qs=[
  '宗室有志气首宰旌德以一县抗敌数有功',
  '空坑之败走之吴溪寻被执于隆兴遇害哀哉']),
 dict(name='刘沐',ti='督府机宜，邻曲朋友',no='第120首',qs=[
  '凡江西忠义皆渊伯所号召昼夜酬应精力不倦',
  '遇害于隆兴长子同日刑次子贡元死空坑乱兵']),
 dict(name='刘子俊',ti='督府机宜，吾乡之杰',no='第129首',qs=[
  '越二十日而行府败民章被执莫知所终哀哉']),
 dict(name='萧资',ti='合门路钤，本书吏出身',no='第131首',qs=[
  '资于患难中扶持尽力',
  '潮阳移屯道遇冦资以病体被害哀哉']),
 dict(name='杜浒',ti='督府参谋官，游侠',no='第132至133首',qs=[
  '性刚猛为游侠京师予北行浒愿从镇江之脱浒之力也']),
 dict(name='邹防',ti='江西安抚副使，字凤叔',no='第127首',qs=[
  '慷慨有大志以豪侠行台郡间从予勤王',
  '宁都被执变姓名为卜者敌不知其为招讨使也']),
 dict(name='邓光荐',ti='礼部，字中甫',no='第137首',qs=[
  '中甫赴海敌舟防出之张元帅待以客礼与予俱出岭别于建康',
  '为管宁为陶潜不亦善乎']),
]

fjson=json.dumps(FRIENDS,ensure_ascii=False)
qb2='<div id="qb2" style="display:none">'+ ''.join(
    '<span class="qv2 qv">%s</span>'%q for f in FRIENDS for q in f['qs']) + '</div>'

s=open(PAGE,encoding='utf-8').read()
assert '<!--QB-->' in s and '/*FRIENDS*/' in s
s=s.replace('<!--QB-->', qb+'\n'+qb2)
s=s.replace('/*FRIENDS*/', fjson[1:-1])
open(PAGE,'w',encoding='utf-8').write(s)
print('injected: %d qb entries, %d friends' % (len(poems),len(FRIENDS)))
