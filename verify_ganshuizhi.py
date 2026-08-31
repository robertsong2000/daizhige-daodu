#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_ganshuizhi.py — 海盐澉水志导读页核验"""
import re, sys
from html.parser import HTMLParser

PAGE='ganshui-zhi.html'
LIB='/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/海盐澉水志.txt'
SJZ='/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/水经注.txt'
NO=134

def norm(s):
    out=[]
    for c in s:
        o=ord(c)
        if 0x3400<=o<=0x9FFF or 0x20000<=o<=0x2FFFF:
            out.append(c)
    return ''.join(out)

lib=norm(open(LIB,encoding='utf-8').read())
libraw=open(LIB,encoding='utf-8').read()
sjz=norm(open(SJZ,encoding='utf-8').read())
html=open(PAGE,encoding='utf-8').read()

fails=[]
def chk(cond,msg):
    if not cond: fails.append(msg)

# ---------- 收集 .q（html.parser 栈配平，VOID 不入栈） ----------
VOID={'br','img','meta','link','hr','input','area','base','col','embed','source','track','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.qs=[]; self.cur=None; self.qdepth=None
    def handle_starttag(self,tag,attrs):
        if tag in VOID: return
        if self.cur is not None: self.cur.append(' ')
        cls=dict(attrs).get('class','') if tag=='span' or True else ''
        if tag not in VOID:
            self.stack.append(tag)
            if self.qdepth is None:
                cl=dict(attrs).get('class','') or ''
                if 'q' in cl.split():
                    self.qdepth=len(self.stack); self.cur=[]
    def handle_startendtag(self,tag,attrs):
        pass
    def handle_endtag(self,tag):
        if tag in VOID: return
        if self.stack and tag in self.stack:
            while self.stack:
                t=self.stack.pop()
                if t==tag: break
        if self.qdepth is not None and len(self.stack)<self.qdepth:
            self.qs.append(''.join(self.cur)); self.cur=None; self.qdepth=None
    def handle_data(self,d):
        if self.cur is not None: self.cur.append(d)
qc=QC(); qc.feed(html)
blocks=[norm(b) for b in qc.qs if norm(b)]
print(f'收集 .q 块：{len(qc.qs)} 块（有效 {len(blocks)}）')

# ---------- 期望引文：双侧断言 ----------
EXPECTED=[
"戸口约五千余主戸少而客户多往来不定口尤难记",
"此方不事田产无仓廪储蓄好侈靡喜楼阁惟招接海南诸货贩运浙西诸邦网罗海中诸物以养生",
"唐开元五年张廷珪奏置",
"东西一十二里南北五里",
"周围二里半绍兴间人民稀少今烟火阜繁生齿日众故不止此",
"水路西去海盐县四十里北去嘉兴县九十里陆路东去海盐县三十六里南去盐官县八十里",
"东至海岸边海界　西至六里堰近潮村界南至筿山邉海界　北至官草荡新浦桥界东南到葛母山界　西南到盐官灵泉乡界东北到秦驻山界　西北到鲍郎浦界",
"县之德政乡田肥税重惟石帆秦山二村在镇东海边多致陷没",
"葫芦山在镇西南四里四望绝在海中如葫芦出没之状潮生潮退葫芦自若",
"秦驻山在镇东北一十五里有始皇庙下有聚落有荒草荡俗为秦驻坞始皇东游曾住此山" ,
"山之下有造船塲山之巅立烽燧山之外捍大海秦始皇东游登山望海以其孤耸遥望如堵墙因名",
"右九山不种林木官给亭戸养草煎盐之所",
"西南一潮至浙江名曰上潭",
"自浙江一潮归泊黄湾又一潮到镇岸名曰下潭",
"虽在澉浦金山两军之间相去隔远夜暮缓急卒难应援",
"淳熙元年奉御笔命守臣赵善悉相视重濬",
"面阔三丈底阔二丈二尺深五丈市镇止有此渠",
"永安湖在镇西南五里周围一十二里元以民田为湖储水灌溉均其税于湖侧田上税虽重而田少旱四围皆山中间小堤春时游人竞渡行乐号为小西湖",
"淳祐九年六月大旱居民沿河私捺小堰至水通诸堰悉复毁去独此堰为居民私置车索邀求过往久为定例",
"此堰赘立委是为害",
"市舶塲在镇东海岸淳祐六年创市舶官十年置塲",
"水军寨在镇东海岸淳祐间拨许浦水军百人于长墙山下岁易一戍",
"客旅巨舟重贩者多于此泊入镇贸易复归解缆",
"客船不上岸者多在于此泊舟为埠头",
"有姓鲍者凿浦煑盐因名曰鲍郎者吴俗女夫之通称也",
"又按南史孙恩作乱海盐令鲍陋遣子嗣之追奔陷没于此",
"列灶九岁课三万五千六百石有奇",
"庚子岁大歉亭民相脔肉自捄九灶不烟幸活无几",
"复盐灶一所复盐丁四十余戸复盐额一万六千八十七石有奇",
"旧传白龙窟于此今客舟舣泊以待潮",
"石帆在灵潭右耸若帆挂有神现其上潮生帆不为减潮退帆不为增月霁则吐蚌珠隂晦则曜神火舟触必碎人莫能涉",
"白龙母塜在镇东南长墙山后丛棘中每岁秋间白龙来视母塜必然风雨大作",
"旧传沿海有三十六条沙岸九涂十八滩至黄盘山上岸去绍兴三十六里风清月白呌卖声相闻",
"始皇欲作桥渡海后海变洗荡沙岸仅存其一黄盘山邈在海中桥柱犹存",
"淳祐十年犹有于旁滩潮里得古井及小石桥大树根之类验井砖上字则知东晋时屯兵处",
"今田废为海尚存数家生聚于潮花鼓舞间",
"昔日有海商失期不返其妻登磐望夫泣殒化而为石因名",
"建炎间有白猿出入神马驱驰毛巡检梦神曰何不创岳祠",
"里人孟毅梦神呼曰吾闽中吴真君当食此方福祐斯民晨见海中有一神主浮海至岸",
"后闽商绘像传塑但祈疗病者甚验四方咸集遂成丛林",
"今俗讹而为吴越二大王兼塑二王像非也",
"疑其神未必为夫差乃俗之传讹也今吴越祠亦类此",
"东南财用大抵资煑海之饶海滨斥卤牢盆相望而闗市有征未能去也",
"询访昔之官守者得一十九人列其姓氏而刻之石",
"澉浦为镇人物繁阜不啻汉一大县",
"下令曰民旅交闗必欲其两平军民杂处必欲其两慎毋启讼毋伤和毋犯干有司",
"民病厉遣吏劳问给药散财更生者几千人旱闭籴赈粟千斛损价售之济囏食者又几千人",
"君名叔韶字仪甫四明人",
"此廨廼今日甘棠",
"雨旸时若戸口日繁民与军而相安商与贾而共悦俱曰澉川当由此而益盛矣",
"若夫序沿草之详细述建造之始末纪到满之月日自有大手笔在何幸拭目以观之",
"门辟三面如尾如足东首而犹垣之",
"美哉山河之固昔武侯语也余是取焉",
"先是胡君下车摩挲旧记仅二十四人",
"惟嘉定初元先正视镇事余先君考叙题名余叔祖实肇厥记",
"先君子昔领是镇兼鲍郎盐塲",
"哭之哀不如传之远也",
"君之来兮鹤自九臯驾以去兮渺天地而逍遥",
"是岁二月朔竹牕常棠记并书",
"竹窻常棠书",
"叙述简核纲目该备而八巻之书为页止四十有四",
"明韩邦竒撰朝邑县志言约事尽世以为绝特之作今观是编乃知其源出于此",
"绍定三年镇尹罗仪甫属余撰澉水志虽一时编集大畧而仪甫满去竟弗暇",
"间逾七八政粤岁既久订正尤详",
"因【阙】边孙君来此听讼优长遇事练熟虽镇塲废坏非畴曩比",
"爰割已俸售募镌行",
"是书不刋于镇税全盛之前乃刋于镇税雕弊之后甚可嘉已",
"元和郡县志丞相李吉甫所制也后三百余年待制张公始刻于襄阳",
"今余所编澉水志后二十七禩权镇孙君即镂于时阜",
"则是书之遇知音又不大可庆耶",
"古庙三间矮棘丛帝魂枉自气凌空早知今日容身窄前此阿房不作宫",
"一湾秋月浸香痕涤尽山前万古尘犹记当时老梳洗淡妆明镜照眉颦",
"恠他蟹舍蚝房地不是吟情住亦难",
"数尺短墙围昼寂半钩疎箔障春寒水生草满蛙鸣合日薄花阴鹤梦安",
"潮声自为诉不平谁念诗人愁欲老",
"倚湖松竹拥楼台景物招人得得来谁识我身非俗物洞门深锁不容开",
]
pagetext=norm(re.sub(r'<[^>]+>',' ',html))
for i,q in enumerate(EXPECTED,1):
    nq=norm(q)
    chk(nq in lib, f'E{i:02d} 库本无:{q[:24]}')
    chk(nq in pagetext, f'E{i:02d} 页面未载:{q[:24]}')
print(f'期望引文 {len(EXPECTED)} 条双侧断言：{"PASS" if not fails else "有 FAIL"}')

# 跨库水经注
SJZQ=["谷水于县出为澉浦，以通巨海。","光熙元年，有毛民三人，集于县，盖泛于风也。"]
for i,q in enumerate(SJZQ,1):
    nq=norm(q)
    chk(nq in sjz, f'S{i} 水经注无:{q[:16]}')
    chk(nq in pagetext, f'S{i} 页面未载:{q[:16]}')

# ---------- 反扫：每个 .q 块必须能在主库或水经注找到 ----------
miss=0
for b in blocks:
    nb=norm(b)
    if nb and nb not in lib and nb not in sjz:
        miss+=1; print('反扫 MISS 块:', b[:40])
chk(miss==0,'存在库外 .q 块')

# ---------- 引号反扫：页面所有「」内容去标签后须在库本 ----------
def strip_tags(s):
    s=re.sub(r'<[^>]+>','',s); return s
visible=strip_tags(re.sub(r'<(style|script)[^>]*>.*?</\1>','',html,flags=re.S))
for m in re.finditer(r'「([^」]+)」', visible):
    seg=norm(m.group(1))
    if seg and seg not in lib:
        chk(False, f'「」反扫 MISS:{m.group(1)[:24]}')

# ---------- 红线 ----------
for bad,name in [('—','长划线'),('–','短划线')]:
    chk(bad not in html, f'红线:{name}出现')
for i,line in enumerate(visible.split('\n'),1):
    c=line.count('·')
    chk(c<=1, f'红线:第{i}行·×{c}')
op,cl=visible.count('「'),visible.count('」')
chk(op==cl, f'红线:「」不配对 {op}/{cl}')
for w in ['TODO','FIXME','lorem','placeholder','certificate','injector']:
    chk(w not in html, f'红线:英文残留 {w}')

# ---------- 机数（全部现场重算） ----------
total=len(libraw); ns=len(re.sub(r'\s','',libraw))
hz=sum(1 for c in libraw if 0x3400<=ord(c)<=0x9FFF or 0x20000<=ord(c)<=0x2FFFF)
puas=[c for c in libraw if 0xE000<=ord(c)<=0xF8FF]
extb={c for c in libraw if 0x20000<=ord(c)<=0x2FFFF}
mens=re.findall(r'^　　(\S{1,3}门)$', libraw, re.M)
chk(len(mens)==15 and '地理门' in mens and '诗咏门' in mens, f'门名机算 {len(mens)}')
vols=set(re.findall(r'海盐澉水志巻([一二三四五六七八])', libraw))
chk(len(vols)==8, '卷号机算八卷')
chk(libraw[:libraw.find('乾隆四十六年十二月恭校上')].count('曰')==15,'提要曰数15')
r1=libraw[libraw.find('陈南美'):libraw.find('　　澉浦镇新剏廨舎记')].count('【')
r2=libraw[libraw.find('朱俊之【'):libraw.find('　　美固堂记')].count('【')
r3=libraw[libraw.find('朱　俯【'):libraw.find('　　还朝序')].count('【')
chk(r1==24,f'题名一碑24(实{r1})'); chk(r2==17,f'题名二碑17(实{r2})')
chk(r3+2==12 and r3==10,f'鲍郎碑单12人10注(实{r3})')
cnts={'□':libraw.count('□'),'【阙】':libraw.count('【阙】'),'巻':libraw.count('巻'),
 '塲':libraw.count('塲'),'防':libraw.count('防'),'呉':libraw.count('呉'),
 '寳':libraw.count('寳'),'廸':libraw.count('廸'),'竹牕':libraw.count('竹牕'),
 '竹窻':libraw.count('竹窻'),'廷珪':libraw.count('廷珪'),'庭珪':libraw.count('庭珪'),
 '上潭':libraw.count('上潭'),'下潭':libraw.count('下潭'),'望潮鱼':libraw.count('望潮鱼'),
 '禩':libraw.count('禩'),'呌':libraw.count('呌'),'恠':libraw.count('恠')}
exp={'□':12,'【阙】':2,'巻':20,'塲':39,'防':47,'呉':5,'寳':16,'廸':3,'竹牕':2,'竹窻':3,
 '廷珪':1,'庭珪':1,'上潭':1,'下潭':1,'望潮鱼':1,'禩':1,'呌':1,'恠':1}
for k,v in exp.items():
    chk(cnts[k]==v, f'机数 {k} 期望{v} 实{cnts[k]}')
chk(len(puas)==30 and len(set(puas))==14, f'PUA 30/14(实{len(puas)}/{len(set(puas))})')
chk(len(extb)==5 and sum(1 for c in libraw if 0x20000<=ord(c)<=0x2FFFF)==6,'ExtB 6见5种')
chk(1230+27==1257,'二十七禩算术')
# 页面口径数字
for s in ['13,596','12,234','12,066','一万二千零六十六','八卷十五门','十五门']:
    chk(s in html, f'页面缺口径:{s}')
chk('十四门' in html and '数岔' in html, '提要十四门公案未上页')
chk('之一百三十四' in html, '页内序号缺失')

# ---------- 结构 ----------
chk('viewBox' in html and '黄盘山' in html and '招寳塘' in html, 'hero舆图要素')
chk(html.count('class="voidc"')>=3, '残名虚框(史□/赵□夫/傅朋□)')
chk(html.count('<section')>=9, '分节数')
chk('<footer' in html and 'daizhigev20' in html and '逐字核验' in html and '时代局限' in html, '页脚四件')
# 虚框示缺
chk('lostbox' in html, '亭名首字虚框')

print()
if fails:
    print(f'FAIL {len(fails)} 项'); [print(' -',f) for f in fails]; sys.exit(1)
print(f'ALL PASS ｜ 引文{len(EXPECTED)}+跨库{len(SJZQ)} ｜ .q块{len(blocks)} ｜ 机数{len(exp)+8}组 ｜ 红线全过')
