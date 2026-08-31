#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""金佗稡编 导读页核验：引文双侧逐字 + 「」反扫 + 排版红线 + 机数断言"""
import re, sys, html
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/jintuo-cuibian.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/传记/金佗稡编.txt'

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8', errors='replace').read()
FAIL = []

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch.isspace():
            continue
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

# ---------- 1. 收集页面 .q（html.parser 栈配平，VOID 不入栈） ----------
VOID = {'br','img','meta','link','hr','input','source','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.qs=[]; self.cur=None; self.qdepth=0
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        if tag == 'q': pass
        a = dict(attrs)
        cls = a.get('class','') or ''
        isq = 'q' in cls.split()
        if isq:
            self.qdepth = len(self.stack)  # depth AFTER outer stack, before pushing q itself
            self.cur = []
        self.stack.append((tag, isq))
    def handle_startendtag(self, tag, attrs): pass
    def handle_endtag(self, tag):
        if tag in VOID: return
        if not self.stack: return
        t, isq = self.stack.pop()
        if isq:
            if len(self.stack) < self.qdepth or True:
                pass
            self.qs.append(''.join(self.cur or []))
            self.cur = None
    def handle_data(self, d):
        if self.cur is not None:
            # 回溯最近 q 祖先：直接收（cur 只在 q 开启后非 None）
            self.cur.append(d)

# 页面 .q 集合（含嵌套子标签文本，但内层独立 .q 会单独成块）
collect = QC(); collect.feed(page)
qtexts = [q for q in collect.qs if q.strip()]
# 内层 q 会产生独立小串，另收全部文本兜底
class TC(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip=0; self.buf=[]
    def handle_starttag(self, tag, attrs):
        if tag in ('style','script'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('style','script'): self.skip = max(0,self.skip-1)
    def handle_data(self, d):
        if not self.skip: self.buf.append(d)
tc = TC(); tc.feed(page)
ALLTEXT = ''.join(tc.buf)

def q_in_page(qn):
    nq = norm(qn)
    for q in qtexts:
        if nq and nq in norm(q):
            return True
    return False

# ---------- 2. QUOTES：双侧断言 ----------
QUOTES = [
 '援淮西召赴行在除枢宻副使赐金带鱼袋银绢鞍马等带本职按阅御前军还兵柄还两镇节充万寿观使奉朝请',
 '证张宪事殁',
 '是编为辨其祖岳飞之寃而作珂别业在嘉兴金佗坊故以名书稡编成于嘉定戊寅续编成于绍定戊子',
 '珂试守檇李之明年始刻家世吁天之书于郡塾即汉制佩章之义稡五编为一名之曰金佗',
 '金人再犯东京敌方在境难以召卿逺来面议今遣李若虚前去就卿商量凡今日可以乗机御敌之事卿可一一筹画措置先入急递奏来据事势莫须重兵持守轻兵择利其施设之方则委任卿朕不可以遥度也',
 '金人过河侵犯东京复来占据已割旧疆卿素蕴忠义想深愤激凡对境事宜可以乘机取胜结约招纳等事可悉从便措置',
 '其宸翰拾遗中舞剑赋乃唐乔潭之作因高宗御书以赐故亦载焉',
 '桧曰飞子云与张宪书不明其事体莫须有',
 '唯枢宻使韩世忠不平狱成诣桧诘其实桧曰飞子云与张宪书不明其事体莫须有世忠曰相公言莫须有何以服天下因力争桧竟不纳',
 '洪皓时在敌中驰蜡书还奏以为敌所大畏服不敢以名呼者唯先臣号之为岳爷爷',
 '将帅闻其死皆酌酒相贺曰和议自此坚矣',
 '尔朝夕以和请而岳飞方为河北图且杀吾壻不可以不报必杀岳飞而后和可成也',
 '一日而奉金书字牌者十有二先臣嗟惋至泣东向再拜曰臣十年之力废于一旦非臣不称职权臣秦桧实误陛下也',
 '我等顶香盆运粮草以迎官军敌人悉知之今日相公去此某等不遗噍类矣',
 '自古未有权臣在内而大将能立功于外者',
 '毋恐第证一句语言今日便出先唯唯',
 '先臣之忤张俊也以亷忤秦桧也以忠',
 '此所以不免也时以为名言',
 '何铸薛仁辅以不愿推鞫而逐',
 '李若朴何彦猷以辨其非辜而罢',
 '韩世忠以莫须有三字何以服天下为问而夺之柄',
 '最后而刘允升以布衣叩阍而坐极典矣',
 '以布衣而抗卿相甘蹈大僇而公议之喙卒不得而钳也',
 '吁天辨诬者记秦桧等之鍜链诬陷每事引当时记载之文',
 '呜呼书既焚矣是果有书乎此不待臣之辨也',
 '天下之不可泯没者惟其理之正也',
 '伸屈有时而不同荣辱既久而自判',
 '皇上再见圜丘之嗣岁珂吁天之书始成浮九江自春徂夏以四月哉生明抵行在所',
 '越四日庚子再拜北阙下奉书付登闻匦吏以入又八日戊申诏出下两省',
 '乃以鄂为请癸未制可',
 '天定录者则飞经昭雪之后朝廷复爵褒封谥议诸事也',
 '天定别录者岳云岳雷岳霖岳甫岳琛等辨诬复官告制劄及给还田宅诸制',
 '即人心之天以合天理之天则名编之意盖在此而不在彼也',
 '开禧元年十二月癸丑朔承奉郎监镇江府户部大军仓岳珂序',
 '不敢以名呼者唯先臣号之为岳爷爷'.replace('唯先臣号之为岳爷爷','唯先臣号之为岳爷爷'),  # 甲本
 '不敢以名呼者唯飞至号之为父',
 '百氏昭忠录者飞厯阵战功及厯官政绩经编于国史及宋人刘光祖等所作碑刻行实黄元振等所编事迹以次彚叙者也',
 '王年三十九为秦桧所陷而殁后追复元官谥武穆封鄂王建庙鄂州赐号忠烈',
 '其版旧刋之嘉禾岁久版脱坏无存其文藏诸民间者又遗阙而无全书',
 '西湖书院岳氏故第也宜序而藏诸至正二十三年三月甲子',
 '时髙宗为太上皇犹及见之',
 '吾意其北望旧京必恨不诛秦桧以谢天下呜呼已无及矣',
 '光武知人明见万里髙宗举国听于权臣',
 '朱仙镇之捷岳飞之功大',
]
# 页面上出现的引文串（去重后逐一验证）
seen = []
for q in QUOTES:
    if q in seen: continue
    seen.append(q)
for q in seen:
    inlib = norm(q) in norm(lib)
    inpage = q_in_page(q)
    if not inlib: FAIL.append(f'库本无: {q[:24]}…')
    if not inpage: FAIL.append(f'页面.q无: {q[:24]}…')
print(f'[1] 引文双侧 {len(seen)} 条：{"PASS" if not FAIL else "FAIL"}')

# ---------- 3. 「」反扫：页面上所有「」内容必须库内有（剥标签后） ----------
bad = []
for m in re.finditer(r'「([^「」]{2,60})」', ALLTEXT):
    s = m.group(1)
    if re.search(r'[a-zA-Z0-9]', s):  # 含数字/字母的说明性引号跳过
        continue
    if norm(s) and norm(s) not in norm(lib):
        bad.append(s)
if bad:
    FAIL.append(f'「」反扫失败 {len(bad)} 条: ' + ' ／ '.join(bad[:6]))
print(f'[2] 「」反扫：{"PASS" if not bad else "FAIL"}')

# ---------- 4. 排版红线 ----------
red = []
page_nostyle = re.sub(r'<style[\s\S]*?</style>','',page)
page_nostyle = re.sub(r'<script[\s\S]*?</script>','',page_nostyle)
if '—' in page_nostyle: red.append('长划线—')
if '–' in page_nostyle: red.append('短划线–')
for i, line in enumerate(page_nostyle.split('\n'), 1):
    if line.count('·') > 1:
        red.append(f'行{i} · 超限')
bad_w = re.findall(r'[a-zA-Z]{4,}', re.sub(r'<[^>]*>','',page_nostyle))
allow = {'Songti','Noto','Serif','SimSun','serif','Menlo','Consolas','PingFang','github','robertsong','daizhigev'}
stray = [w for w in bad_w if w not in allow]
if stray: red.append(f'英文残留: {stray[:6]}')
if red: FAIL.extend(red)
print(f'[3] 排版红线：{"PASS" if not red else "FAIL"}')

# ---------- 5. 机数断言（库本侧） ----------
def n(*pats):
    return [lib.count(p) for p in pats]
cnt_checks = [
    ('莫须', 9), ('金字牌', 14), ('班师', 42), ('御札', 131), ('宸翰', 21),
    ('先臣', 965), ('呜呼', 54), ('寃', 69), ('风波', 0), ('登闻匦', 2),
    ('岳爷爷', 7), ('金佗', 154),
]
for w, exp in cnt_checks:
    got = lib.count(w)
    if got != exp:
        FAIL.append(f'计数 {w}: 库本 {got} ≠ 页面口径 {exp}')
print(f'[4] 库本词频 {len(cnt_checks)} 项：{"PASS" if all(lib.count(w)==e for w,e in cnt_checks) else "FAIL"}')

# 汉字数
han = len([c for c in lib if '㐀'<=c<='鿿' or '\U00020000'<=c<='\U0002ffff'])
if han != 258640: FAIL.append(f'汉字数 {han} ≠ 258640')
tot = len(lib)
if tot != 266940: FAIL.append(f'全帙字符 {tot} ≠ 266940')
print(f'[5] 全帙 {tot} 字符 / 汉字 {han}：{"PASS" if han==258640 and tot==266940 else "FAIL"}')

# 提要自报结构：宸翰3+行实6+家集10+吁天5+通叙1+天定3=28；摭遗1+丝纶11+别录4+昭忠14=30
for frag, lab in [('高宗宸翰三巻鄂王行实编年六巻鄂王家集十巻吁天辨诬五巻天定录三巻','稡编五编'),
                  ('行实六巻吁天辨诬五巻通叙一巻','贴黄通叙一'),
                  ('宸翰摭遗一巻','摭遗一'),('信录十一巻','丝纶十一'),('天定别录四巻','别录四'),('百氏昭忠录十四巻','昭忠十四')]:
    if frag not in lib: FAIL.append(f'提要结构缺: {lab}')
if 3+6+10+5+1+3 != 28 or 1+11+4+14 != 30: FAIL.append('卷数算术')
print('[6] 提要自报结构 28＋30：PASS' if not any('提要结构' in f or '卷数' in f for f in FAIL) else '[6] FAIL')

# 昭忠录卷头：14 卷，12 有号 2 无号（行首全角缩进剥除）
heads = [l.strip() for l in lib.split('\n') if re.match(r'^百氏昭忠录([巻卷][一二三四五六七八九十]+)?$', l.strip())]
withno = len([h for h in heads if h == '百氏昭忠录'])
if not (len(heads) == 14 and withno == 2):
    FAIL.append(f'昭忠录卷头: 共{len(heads)} 无号{withno}')
print(f'[7] 昭忠录卷头 14（无号 2）：{"PASS" if len(heads)==14 and withno==2 else "FAIL"}')

# 五辨篇名
for t in ['建储辨','淮西辨','山阳辨','张宪辨','承楚辨']:
    if lib.count(t) < 1: FAIL.append(f'辨目缺 {t}')
print('[8] 吁天辨诬五目：PASS' if not any('辨目' in f for f in FAIL) else '[8] FAIL')

# 行实编年十一年一行 50 字
line50 = '援淮西召赴行在除枢宻副使赐金带鱼袋银绢鞍马等带本职按阅御前军还兵柄还两镇节充万寿观使奉朝请证张宪事殁'
if len(line50) != 50 or lib.count(line50) != 1:
    FAIL.append(f'十一年一行: {len(line50)}字 x{lib.count(line50)}')
print(f'[9] 绍兴十一年编年一行恰50字：{"PASS" if len(line50)==50 and lib.count(line50)==1 else "FAIL"}')

# 页面自身断言：序号、卷号、页脚
for s in ['之一百三十九','卷七十九','昭雪','github.com/robertsong2000/daizhigev20','时代局限提醒','逐字核验']:
    if s not in page: FAIL.append(f'页面缺: {s}')
# 落款推算自检：开禧元年=1205（1205-1142=63）
if 1205-1142 != 63: FAIL.append('六十三年算术')
print(f'[10] 页面要素+算术：{"PASS" if not any("页面缺" in f or "算术" in f for f in FAIL) else "FAIL"}')

# ---------- 汇总 ----------
print('=' * 46)
if FAIL:
    print('FAIL', len(FAIL), '项')
    for f in FAIL: print(' ✗', f)
    sys.exit(1)
print('ALL PASS')
