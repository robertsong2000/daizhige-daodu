#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_baoyue.py 保越录页面核验"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/baoyue-lu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/传记/保越录.txt'
NO   = 131

raw_html = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF:
            out.append(ch)
    return ''.join(out)

lib_n = norm(lib)

fails, warns = [], []

# ---------- 1. 页面 .q 收集（html.parser 栈配平） ----------
VOID = {'br','img','meta','link','hr','input','source','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.qdepth=0; self.buf=[]; self.qs=[]
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class') or ''
        if tag in VOID: return
        isq = 'q' in cls.split()
        skip = 'from' in cls.split()   # from: 出处签，内容不入引文
        self.stack.append((tag, isq, skip))
        if isq:
            self.qdepth = len(self.stack)
            self.buf = []
    def handle_endtag(self, tag):
        if tag in VOID: return
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0]==tag:
                was_q = self.stack[i][1]
                del self.stack[i:]
                if was_q:
                    self.qs.append(''.join(self.buf))
                    self.buf=[]
                    self.qdepth=0
                    for t,qq,_sk in self.stack:
                        if qq:
                            self.qdepth = len(self.stack)+1
                            break
                break
    def handle_data(self, data):
        if not self.qdepth: return
        for t,_q,sk in self.stack[self.qdepth-1:]:
            if sk: return
        self.buf.append(data)
qc=QC(); qc.feed(raw_html)
page_qs=[norm(t) for t in qc.qs if norm(t)]
print(f'[i] 页面 .q 收集 {len(qc.qs)} 块，非空 {len(page_qs)} 块')

# ---------- 2. EXPECTED 清单 ----------
EXPECTED = [
 # 提要
 '凡攻三月卒不能下乃还',
 '是录称士诚兵曰我军称珍曰公殆士诚未亡时绍兴人所纪',
 '其中称明为大军及太祖髙皇帝字则疑士诚亡后明人传钞所改耳',
 '绍兴自是以后独保守八年及至正二十六年始归于明',
 '珍亦至是年湖州之败乃降于徐达虽初事非主晚节不终而在绍兴则不为无功矣',
 '大海攻绍兴挫衂及其纵兵淫掠发宋陵墓诸恶迹明史皆不载',
 '所录张正防妻韩氏女池奴冯道二妻抗节事明史亦皆不书尤足补史传之遗',
 '故录之以备参考焉',
 # 卷首布防
 '至正十八年冬十一月戊戍浙江等处行枢密院副使吕公珍来镇绍兴',
 '越民思之如失怙恃公至祭而哭之拜其母于家中',
 '遂命增濠各广五丈深二丈繇是排栅沮水益固而战船往来俱得便利',
 '乃督城外居民悉迁城中毁居宇近城者清野以待之',
 '公与将校议曰敌势逺来利在速战而城外多水非用武之地',
 '以寡御众以逸待劳观其动静与之持久此吾志也',
 # 兵临
 '丁卯自诸暨分三路',
 '一出枫桥古博岭天章木栅至亭山',
 '一出江灶暨于茅洋漓渚至戴旗山',
 '一出街亭象路铸石岭平水至九里',
 '公叱之曰汝是谁我舍命大王也语未毕公挥攩杈已中其頥遂擒以还',
 '一城之命悬于公愿无轻出',
 '大军初至其势方锐吾不身先士卒以挫其锋谁肯出力',
 '大军见公铠甲輙引去',
 '城上观者杂于卒伍中耳目既熟皆恬然不复忧惧市井作息无异平日',
 # 内应之夜
 '大军扬言城中民约我举火为内应是夜三更城东北上民有火炬',
 '公曰吾不负民民岂负我耶',
 '总管焦徳昭请以二皷击四皷休击三皷及使人察市巷居皆安寝如常至夜不复语由是大军间不能入',
 # 禁钟
 '先是城中鸣禁钟以声疾徐知大军缓急然未甞击也',
 '是日民俱骇惧或又击钟公怒命止之戒后勿击仍禁民登城观望自后交战民皆不知',
 # 城中
 '谓食肉者吃菜食饭者餟粥又禁米不许出郭',
 '乃俾上户五日中户三日下户二日得便轮日相代单丁老弱者免',
 '漕杭州粮一万石',
 '后因艰澁',
 '运嘉兴米十万石',
 '以盐换米二万石',
 # 名册
 '大军发掘冢墓自理宗慈献夫人以下至官庶坟墓无不发金玉宝器捆载而去',
 '其尸或敛之以水银面皆如生',
 '庐屋尽毁恐被汚辱',
 '共缢死',
 '女不敢哭解尸于地自投崖下而死',
 '昼匿山中夜归守尸旁寻亦饿死',
 '二妇度不能脱乃共往大军营愿首饰衣服',
 '皆投井而死',
 '吾愿杀不为妻也',
 '潘氏曰我行不乱且吾夫方死不忍暴弃遗骸愿将焚化随去庶绝吾念否则有死而已',
 '烟焰方炽潘氏临哭之遂投火而死',
 # 王冕
 '郡人王冕字元章负气偃蹇居九里山中大兵至民皆避兵入城冕独不入',
 '自言善能韬畧兵书得不死',
 '请定官额陈设攻取方畧上大悦即命授以重任',
 '复治攻城器具又定决水之策画图本以示诸将',
 '大军自右堰之败人马散亡甚众颇咎王冕由此疎之',
 # 风与火
 '时溽暑郁蒸疫疠大作大军首将祈祷南镇不应乃毁其像仆碑石',
 '万户宋之杰擒之以还乃胡大海义子请以金银马匹来赎不许',
 '大军将蔡元帅铠甲坐胡床指挥其众我军以火筒射而仆之大军径舁之还寨',
 '是夜大军以板屋竹牌聨比布列架木为栅庇身栅上去越月城不数尺',
 '我军以火箭烧其竹牌板屋',
 '大军以四舟编聨而行上积枯薪乗风纵火直趋城门',
 '暴风忽起飞石扬沙尘埃蔽面人马不能正立大军将旗俱折器械铺舍纵横散乱白昼晦防',
 # 遁营
 '或前者已去后者不知或烹而未炊或炊而未食资装器械委顿原野',
 '骑回顾曰汝不知兵也耶赶人不可赶上倪昶曰休走好男子骑曰今日好男子被吕家赶散汝毋追我',
 '所掠民间妇女纷纭田野公命入城中聚大善寺给以衣食听还完聚',
 '掩瘗尸骸之暴露者',
 '城外望见城中常有紫云覆防',
 # 城全之后
 '民岳宗唐元夀等建公生祠于卧龙山之西麓',
 '公讳珍字国宝安丰人系出故宋保相之后',
 '绍兴城池坚固民心易附于保全不足为功',
 '故珍愿就贬降以示不忘诸暨且使将士知珍之罪',
 # coda + 散引
 '公坐城上见居民出观大军寨曰民患大军攻城三月余矣',
 '太祖髙皇帝',
 '我军',
]
STRUCT = [  # 页面以数据呈现、须在库本存在的串
 '部长统御长御长统社长社长统保长保长统甲首',
 '巴尔斯布哈','米文选','顾得兴','元信','胡大有','周元','田希仁','丁兴祖','包王','刘宣',
 '铸石岭','亭山','陵家山','中堰','右堰','迎恩门','常禧门','植利门','稽山门','五瑞门','都泗门','昌安门',
]

# ---------- 3. 双侧断言 ----------
for e in EXPECTED:
    en = norm(e)
    if en not in lib_n:
        fails.append(f'EXPECTED 不在库本: {e}')
    if not any(en in pq for pq in page_qs):
        fails.append(f'EXPECTED 未载于页面 .q: {e}')
for s in STRUCT:
    if norm(s) not in lib_n:
        fails.append(f'STRUCT 不在库本: {s}')
    if norm(s) not in norm(re.sub(r'<[^>]+>','',raw_html)):
        fails.append(f'STRUCT 未见于页面: {s}')
for i,pq in enumerate(page_qs):
    if pq not in lib_n:
        fails.append(f'页面 .q#{i} 不在库本: {pq[:40]}')

# 查重（同一期望串不应指向多个不同块）
seen={}
for e in EXPECTED:
    en=norm(e)
    hits=sum(1 for pq in page_qs if en in pq)
    if hits==0: continue
    # 长引文出现于多块或短串重复过多给警告
    if len(en)>=8 and hits>1:
        warns.append(f'EXPECTED 复现于 {hits} 块: {e}')

# ---------- 4. 「」反扫 ----------
body = re.sub(r'<style.*?</style>','',raw_html,flags=re.S)
body = re.sub(r'<script.*?</script>','',body,flags=re.S)
body = re.sub(r'<[^>]+>','',body)
for m in re.finditer(r'「([^」]*)」', body):
    t=norm(m.group(1))
    if t and t not in lib_n:
        fails.append(f'「」反扫不匹配: {m.group(1)}')

# ---------- 5. 排版红线 ----------
if '—' in raw_html or '–' in raw_html:
    fails.append('红线: 存在长划线')
for ln,line in enumerate(raw_html.split('\n'),1):
    if line.count('·')>1:
        fails.append(f'红线: 第{ln}行有 {line.count("·")} 枚 ·')
# 英文残留（剥标签后）
tokens=set(t.lower() for t in re.findall(r'[A-Za-z]{2,}', body))
ALLOW={'github','com','robertsong','daizhigev'}
bad=tokens-ALLOW
if bad:
    fails.append(f'红线: 英文残留 {bad}')

# ---------- 6. 机数断言 ----------
ns=re.sub(r'\s','',lib)
n_all=len(lib); n_ns=len(ns)
n_han=len(norm(lib))
def pg(s): return s in raw_html
checks=[
 (f'全帙 {n_all:,} 字', f'{n_all:,}'),
 (f'去空白 {n_ns:,}', f'{n_ns:,}'),
 (f'汉字 {n_han:,}', f'{n_han:,}'),
 ('大军 169', '169'), ('我军 41', '41'),
 ('【阙】11 见', '【阙】11 见'),
 ('防 25 见', '25 见'),
 ('私有区 4 见', '4 见'),
 ('库本 13 见(常禧)','库本 13 见'),('库本 10 见(稽山)','库本 10 见'),
 ('库本 5 见','库本 5 见'),('库本 4 见(迎恩)','库本 4 见'),
 ('库本 3 见(植利)','库本 3 见'),('库本 1 见(都泗)','库本 1 见'),
 ('包玉两见','包玉两见'),
 ('五月段时序申报','插在四月癸亥以下各日之前'),
 ('序号 131','之一百三十一'),
]
for label,needle in checks:
    if not pg(needle):
        fails.append(f'机数: 页面缺 [{needle}]（{label}）')
# 库本侧
m=[('我军',41),('大军',169),('【阙】',11)]
for w,c in m:
    if ns.count(w)!=c: fails.append(f'机数: 库本 {w} 计数 {ns.count(w)}≠{c}')
if ns.count('包王')!=1 or ns.count('包玉')!=2:
    fails.append('机数: 包王/包玉计数不符')
if lib.find('夏五月') > lib.find('四月癸亥'):
    fails.append('机数: 五月应在四月之前（库本错位前提不成立）')
if f'导读之{["零","一"][0]}' : pass  # noop
if norm('殆知阁') not in norm(re.sub(r'<[^>]+>','',raw_html)):
    fails.append('机数: 页面缺 殆知阁 字样')

# ---------- 汇总 ----------
print(f'[i] 引文核验 {len(EXPECTED)} 条期望 + {len(STRUCT)} 条结构；页面 .q {len(page_qs)} 块')
for w in warns: print('[warn]', w)
if fails:
    print(f'\n✗ FAIL {len(fails)} 项')
    for f in fails: print('  -', f)
    sys.exit(1)
print('\n✓ ALL PASS')
