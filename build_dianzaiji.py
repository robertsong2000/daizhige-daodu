#!/usr/bin/env python3
# build_dianzaiji.py：自库本锚点切片注入引文，零誊写
SRC='/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/滇载记.txt'
TPL='dianzaiji.tpl.html'
OUT='dianzaiji.html'

def norm(s):
    out=[]
    for ch in s:
        o=ord(ch)
        if (0x3400<=o<=0x9fff) or (0xf900<=o<=0xfaff) or ch.isdigit():
            out.append(ch)
    return ''.join(out)

src=open(SRC,encoding='utf-8').read()
nsrc=norm(src)

# (token, start_anchor, end_anchor)  end 为含尾；None 表示 start 即全串
QUOTES=[
 ('Q1','建松明为楼','五诏遂灭'),
 ('Q2','有妇曰沙壹','曰九隆族'),
 ('Q3','夷语谓诏为王',None),
 ('Q4','乃卜太和形胜','结于子午'),
 ('Q5','妻以宗女','中国之乐'),
 ('Q6','凤伽异及段俭魏','仅以身免'),
 ('Q7','刻碑国门之外','非得已也'),
 ('Q8','剑南留后李宓','全军没焉'),
 ('Q9','前后死者二十万人',None),
 ('Q10','皇帝所赐龟兹','在耳'),
 ('Q11a','冬时欲归来','高黎其上雪'),
 ('Q11b','夏秋欲归来','无柰穹甸热'),
 ('Q11c','春时欲归来','囊中资粮绝'),
 ('Q12','其山九峰','玉立万仞'),
 ('Q14','以王斧画大渡河曰','非吾有也'),
 ('Q15','云南三百年不通中国',None),
 ('Q16','饥摘野桃','青昔。”'),
 ('Q16b','青乃十二月','举义乎'),
 ('Q18','夫去首，为天，天子兆也',None),
 ('Q18b','玉瓶去耳为王，王者兆也',None),
 ('Q19','镜破则无影，无影则无敌矣',None),
 ('Q20','人从我江尾','尔国名大理'),
 ('Q21','段氏不振，国人推我','勿效尤也'),
 ('Q25','段氏自思平至兴智','三百五十年'),
 ('Q26','蒙氏自细奴罗至舜化真','三百十年'),
 ('Q27','亲莫若父母，宝莫若社稷',None),
 ('Q28','我父忌阿奴，愿与阿奴西归',None),
 ('Q29','明日，邀功东寺演梵','格杀之'),
 ('Q30','阿奴虽死，奴不负信黄泉也',None),
 ('Q31','吾家住在雁门深','欲随明月到苍山'),
 ('Q32','半纸功名百战身','点苍春'),
 ('Q34','杀虎子而还喂其虎母','其狙公'),
 ('Q35','待金马山换作点苍山','来矣'),
 ('Q36','我自束发','此旗所以识也'),
 ('Q37','余婴罪投裔','而不得也'),
 ('Q38','有《白古通玄峰年运志》其书','令其可读'),
 ('Q39','夫分隔之乱','今若此'),
 ('Q41','自世隆嗣立以来','为之虚耗'),
 ('Q42','遣其弟献图纳贡','复号南诏'),
 ('Q44','大理乃唐交绥之外国','余邦'),
 ('Q45','立上下二关','曰龙尾'),
 ('Q46','耕于巍山之麓','部众日盛'),
 ('Q47','因仲夏二十五日','祭先之期'),
 ('Q48','郑回说以大义','令复归唐'),
 ('Q51','复多征求','取夷州三十二'),
]

tpl=open(TPL,encoding='utf-8').read()
used=set()
for tok,st,en in QUOTES:
    i=src.find(st)
    assert i>=0, f'{tok} 起锚未找到: {st}'
    if en is None:
        q=st
    else:
        j=src.find(en,i)
        assert j>=0, f'{tok} 尾锚未找到: {en}'
        q=src[i:j+len(en)]
    n=norm(q)
    assert n in nsrc, f'{tok} 归一后不在库本'
    key='{{'+tok+'}}'
    assert key in tpl, f'{tok} 模板中无占位'
    used.add(key)
    tpl=tpl.replace(key,q)

leftover=[t for t in ('{{Q',) if t in tpl]
assert not leftover, f'模板残留占位: {[s for s in tpl.split("{{")[1:] if True][:3] if "{{" in tpl else []}'
import re
rem=re.findall(r'\{\{Q[0-9ab]+\}\}',tpl)
assert not rem, f'模板残留: {rem}'

strip=re.sub(r'\s','',re.sub(r'<[^>]+>','',src))
print(f'库本去标签去空白 {len(strip)} 字')
print(f'注入引文 {len(QUOTES)} 处')
open(OUT,'w',encoding='utf-8').write(tpl)
print(f'写出 {OUT}')
