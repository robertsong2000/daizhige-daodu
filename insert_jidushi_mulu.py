#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""insert_jidushi_mulu.py — commit 前一刻动态取号插入 mulu.html 并回填页面篇号"""
import re

MULU='mulu.html'; PAGE='jidushi.html'

VOL_DESC=('大都狱中，一卷杜诗是唯一的书。文天祥把杜甫五言裁成纸条，攒出二百首绝句，每题下按一段小序，记国亡身系的每一天；'
 '一百零五段小序有序可读，第一百三十四题自注诗阙，存目存序而无诗。本卷收〈文信国集杜诗〉导读一篇，从一扇狱窗开卷，'
 '二百首全谱按其自分卷次五段配色，点格读诗，末卷停在赴刑那年元旦写下的绝笔跋。引文经脚本与库内文件去标点、归一逐字比对通过（一千八百零一处，白话反扫六字窗零撞）。')

ENTRY_TI=('<small>宋文天祥撰，据集藏四库别集本，去空白约一万九千字，集杜甫五言句成五言绝句二百首，'
 '每题下系小序记事，一百零五题有序，第一百三十四徐榛题注诗阙存目无诗。书眼＝裁与拼：牢里唯一的书是杜集，'
 '他把五言裁成纸条攒成绝句，句下出处小签是这本书自带的引用格式；自序说日玩之不置但觉为吾诗忘其为子美诗也，'
 '卷次自分五段：首述其国次述其身次述其友次述其家而终以写本心。述国开卷即判词：三百年宗庙社稷为贾似道一人所破壊哀哉；'
 '将相弃国题下一夜两逃；厓山题记一字阵对长蛇阵，死溺者数万人；南海题存他手书拒降诗的原始记录，末句云人生自古谁无死留取丹心照汗青。'
 '述身是编年自传：舟中不食拟至庐陵得瞑目，镇江之脱靠杜浒一句且遁逃不获死未晩也，北上途中邳州门外哭母小祥，入狱第一题四句全借杜甫的眼睛看自己的牢房。'
 '述友十三传：金应葬城下、巩信中数箭死、邹防变姓名为卜者、邓光荐赴海被钩出、徐榛道病死而诗阙。'
 '述家点名式记骨肉：母薨妻陷六女尽殇长子夭。本心卷自道共二十九首杂然写其本心，恰有一句剪纸招我魂。'
 '版式＝狱窗裁句壳：首屏点裁句看四枚纸条从杜集飞入诗笺拼成开卷第一首，竖排书名升起钤文山诗史印；'
 '右缘装订绳五结随读点亮；二百首全谱六色可点，弹卡读小序与出处签；北行站牌线点站读诗；'
 '述友传签墙点签读传；家册九行点行展小序；本心站抽一句机与末页竖排绝笔跋钤千载心印；卷尾五签记书名、诗史之目、吴之振贬评、白字补文与落款之谜。'
 '校字记：防字七十余见系多个正字之讹照录，十八个生僻码位按上下文归一，不可考者以□存之。'
 '引文经脚本与库内文件去标点、归一逐字比对通过（一千八百零一处，白话反扫六字窗零撞）。</small>')

s=open(MULU,encoding='utf-8').read()
nos=[int(m) for m in re.findall(r'<span class="no mono">(\d+)</span>',s)]
n=max(nos)+1
def cn2int(t):
    lo='一二三四五六七八九'; up='壹贰叁肆伍陆柒捌玖'
    total=0;num=0
    for ch in t:
        if ch in lo: num=lo.index(ch)+1
        elif ch in up: num=up.index(ch)+1
        elif ch in '十拾': total+=(num or 1)*10; num=0
        elif ch in '百佰': total+=(num or 1)*100; num=0
    return total+num
seals=re.findall(r'class="vseal"[^>]*>([^<]+)</div>',s)
VAR={'貳':2,'弍':2,'叄':3,'參':3,'叁':3,'陸':6,'柒':7,'漆':7,'捌':8,'玖':9,'伍':5,'肆':4,'壹':1,'贰':2,'叁':3,'陆':6,
     '一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'零':0,'〇':0}
def parse_seal(t):
    total=0;num=0
    for ch in t:
        if ch in VAR: num=VAR[ch]
        elif ch in '十拾': total+=(num or 1)*10; num=0
        elif ch in '百佰': total+=(num or 1)*100; num=0
        else: return None
    return total+num
vals=[parse_seal(x) for x in seals]
vals=[x for x in vals if x]
vmax=max(vals); v=vmax+1
assert abs(v-(n-120))<=2, ('卷篇同步断言',v,n)
assert 'jidushi.html' not in s
assert '集杜' not in s and '文信国' not in s and '裁句' not in s
def n2cn(v):
    D='〇一二三四五六七八九'
    def u(x):
        if x<10:return D[x]
        if x==10:return '十'
        if x<20:return '十'+(D[x%10] if x%10 else '')
        if x<100:return D[x//10]+'十'+(D[x%10] if x%10 else '')
        return D[x//100]+'百'+(u(x%100) if x%100 else '')
    return u(v)
def n2cn_seal(v):
    D='〇壹贰叁肆伍陆柒捌玖'
    def u(x):
        if x<10:return D[x]
        if x==10:return '十'
        if x<20:return '十'+(D[x%10] if x%10 else '')
        if x<100:return D[x//10]+'十'+(D[x%10] if x%10 else '')
        return D[x//100]+'百'+(u(x%100) if x%100 else '')
    return u(v)
vcn=n2cn(v); vseal=n2cn_seal(v)
assert ('卷'+vcn+' ·') not in s

pg=open(PAGE,encoding='utf-8').read()
assert pg.count('第〇〇篇')==1
open(PAGE,'w',encoding='utf-8').write(pg.replace('第〇〇篇','第%d篇'%n))

old=n2cn(n-1)+'篇'; new=n2cn(n)+'篇'
assert s.count(old)==2, ('anchors',s.count(old))
s=s.replace(old,new)

vol=('\n  <div class="vol" style="--vc: var(--c3)">\n    <div class="wrap">\n      <div class="vol-head">\n'
 '        <div class="vseal" style="background: var(--c3)">'+vseal+'</div>\n'
 '        <h2>卷'+vcn+' · 裁句</h2>\n'
 '        <div class="vsub">石青 · 集藏别集</div>\n'
 '      </div>\n      <p class="vol-desc">'+VOL_DESC+'</p>\n'
 '      <a class="entry" href="jidushi.html">\n'
 '        <span class="no mono">%d</span>\n'%n+
 '        <span class="ti">'+ENTRY_TI+'\n'
 '        </span>\n        <span class="file mono">jidushi.html</span>\n      </a>\n    </div>\n  </div>\n\n')
idx=s.rindex('</footer>')
s=s[:idx]+vol+s[idx:]
open(MULU,'w',encoding='utf-8').write(s)

nos2=[int(m) for m in re.findall(r'<span class="no mono">(\d+)</span>',s)]
assert sorted(nos2)==list(range(1,len(nos2)+1)) and nos2[-1]==n
print('OK inserted 第%d篇 卷%s %s'%(n,vcn,vseal))
