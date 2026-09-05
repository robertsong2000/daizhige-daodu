#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_benshishi.py 本事诗导读页核验"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/benshi-shi.html'
MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
CORPUS = '/home/robertsong/workspace/claude/daizhige-simplified/诗藏/诗话/本事诗.txt'

fails = []
def chk(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)

def norm(s):
    s = ''.join(ch for ch in s if ch.isalnum() or '一' <= ch <= '鿿')
    return s

raw = open(PAGE, encoding='utf-8').read()
corpus_raw = open(CORPUS, encoding='utf-8').read()
corpus_norm = norm(corpus_raw)

# ---------- 收集器：q / div.verse / div.csq / div.jz 为引文；code 单列；i 内为出处注；style/script 剥离 ----------
class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = None          # style/script
        self.stack = []           # (kind, tag, parts)
        self.quotes = []
        self.codes = []
        self.body = []            # 页面可见文本（剥标签）
    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.skip = tag
            return
        if self.skip:
            return
        cls = (dict(attrs).get('class') or '').split()
        kind = None
        if tag == 'q':
            kind = 'quote'
        elif tag == 'code':
            kind = 'code'
        elif tag == 'i':
            kind = 'skipnote'
        elif tag == 'div' and ({'verse', 'csq'} & set(cls)):
            kind = 'quote'
        else:
            return          # br、b、span 等不压栈，数据穿透给下层捕获
        self.stack.append((kind, tag, []))
    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip:
                self.skip = None
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][1] == tag:
                kind, _, parts = self.stack.pop(i)
                text = ''.join(parts)
                if kind == 'quote':
                    self.quotes.append(text)
                elif kind == 'code':
                    self.codes.append(text)
                break
    def handle_data(self, data):
        if self.skip:
            return
        self.body.append(data)
        if self.stack:
            top = self.stack[-1]
            if top[0] == 'quote':
                top[2].append(data)
            elif top[0] == 'code':
                top[2].append(data)

c = Collector()
c.feed(raw)
quotes, codes, body_text = c.quotes, c.codes, ''.join(c.body)
page_norm = norm(body_text)

chk(len(quotes) >= 40, f'收集引文块数非零且充足：{len(quotes)} 块')
chk(len(codes) == 2, f'code 校字记录目数 = {len(codes)}')

# ---------- 逐条引文双侧：在库本 + 在页面 ----------
bad = [q for q in quotes if norm(q) not in corpus_norm]
chk(not bad, f'全部引文块命中库本（失败 {len(bad)}）')
for q in bad[:5]:
    print('   未命中：', q[:60])
bad2 = [q for q in quotes if norm(q) not in page_norm]
chk(not bad2, '全部引文块均来自页面自身（收集器自洽）')

# ---------- 期望清单 ----------
EXPECTED = [
    '诗者，情动于中而形于言。故怨思悲愁，常多感慨。抒怀佳作，讽刺雅言，着于群书，虽盈厨溢阁，其间触事兴咏，尤所钟情。不有发挥，孰明厥义？因采为《本事诗》，凡七题，犹四始也。',
    '时光启二年十一月，大驾在褒中，前尚书司勋郎中赐紫金鱼袋孟棨序。',
    '有苍头卖半镜者，大高其价，人皆笑之。',
    '镜与人俱去，镜归人不归。无复嫦娥影，空留明月辉。',
    '今日何迁次，新官对旧官。笑啼俱不敢，方验作人难。',
    '沙场征戍客，寒苦若为眠。战袍经手作，知落阿谁边？畜意多添线，含情更着绵。今生已过也，结取后身缘。',
    '有作者勿隐，吾不罪汝。',
    '我与汝结今身缘。',
    '今生已过也',
    '一入深宫里，年年不见春。聊题一片叶，寄与有情人。',
    '花落深宫莺亦悲，上阳宫女断肠时。帝城不禁东流水，叶上题诗欲寄谁？',
    '一叶题诗出禁城，谁人酬和独含情？自嗟不及波中叶，荡漾乘春取次行。',
    '大丈夫相遇杯酒间，一言道合，尚相许以死，况一妇人，何足辞也！',
    '章台柳，章台柳，往日青青今在否？纵使长条似旧垂，亦应攀折他人手。',
    '杨柳枝，芳菲节，可恨年年赠离别。一叶随风忽报秋，纵使君来岂堪折？',
    '幸不辱命。',
    '此我往日所为也，而俊复能之！',
    '沙咤利宜赐绢二千匹，柳氏却归韩翃。',
    '春城无处不飞花，寒食东风御柳斜。日暮汉宫传蜡烛，轻烟散入五侯家。',
    '与此韩翃。',
    '司空见惯浑闲事，断尽江南刺史肠。',
    '?鬌，字亦作低堕，并上声，《古今注》言即坠马之遗传也。',
    '去年今日此门中，人面桃花相映红。人面秖今何处去？桃花依旧笑春风。',
    '门墙如故，而已锁扃之。',
    '某在斯，某在斯。',
    '须臾开目，半日复活矣。',
    '紫陌红尘拂面来，无人不道看花回。玄都观里桃千树，尽是刘郎去后栽。',
    '唯兔葵燕麦，动摇于春风耳。',
    '百亩庭中半是苔，桃花净尽菜花开。种桃道士归何处？前度刘郎今独来。',
    '以俟后再游',
    '樱桃樊素口，杨柳小蛮腰。',
    '一树春风万万枝，嫩于金色软于丝。永丰坊里东南角，尽日无人属阿谁？',
    '花时同醉破春愁，醉折花枝当酒筹。忽忆故人天际去，计程今日到梁州。',
    '梦君兄弟曲江头，也向慈恩院里游。驿吏唤人排马去，忽惊身在古梁州。',
    '千里神交，合若符契',
    '号为「谪仙」，解金龟换酒，与倾尽醉。',
    '此诗可以泣鬼神矣。',
    '饭颗山头逢杜甫，头戴笠子日卓午。借问何来太瘦生，总为从前作诗苦。',
    '故当时号为「诗史」。',
    '破却千家作一池，不栽桃李种蔷薇。蔷薇花落秋风后，荆棘满庭君始知。',
    '由是人皆恶其侮慢不逊，故卒不得第，抱憾而终。',
    '楼观沧海日，门听浙江潮',
    '此骆宾王也。',
    '僧所赠句，乃为一篇之警策。',
    '今年花落颜色改，明年花开复谁在？',
    '其不祥欤',
    '年年岁岁花相似，岁岁年年人不同。',
    '夜来双月满，曙后一星孤。',
    '人始悟其自谶也',
    '卜筑郊原古，青山唯四邻。',
    '忽然逢着贼，骑猪向南窜。',
    '骑猪者，是夹豕走也。',
    '火树银花合，星桥铁锁开。暗尘随马去，明月逐人来。',
    '无银花合',
    '子诗虽无「银花合」，还有「金铜钉」。',
    '今同丁令威',
    '回波尔时栲栳，怕妇也是大好。外边祇有裴谈，内里无过李老。',
]
for e in EXPECTED:
    chk(norm(e) in corpus_norm, f'期望在库本：{e[:18]}…')
    chk(any(norm(e) in norm(q) for q in quotes), f'期望上页：{e[:18]}…')

# 裸引（加粗叙述，无引号）
BARE = ['鹫岭郁岧峣，龙宫隐寂寥', '明日尚此路还，愿更一来取别', '殆无遗事']
for b in BARE:
    chk(norm(b) in corpus_norm and norm(b) in page_norm, f'裸引双侧：{b}')

# 校字记 code：异文一条须不在库本，讹词条须在库本
chk(len(codes) == 2 and norm('断尽苏州刺史肠') not in corpus_norm and any('断尽苏州刺史肠' in x for x in codes),
    '校字记异文（苏州）照录且确认非库本')
chk(any(norm('江淮剌史') in norm(x) for x in codes) and norm('江淮剌史') in corpus_norm,
    '校字记讹字条（江淮剌史）双侧命中')

# ---------- 「」『』反扫 ----------
singles = re.findall(r'「([^「」]*)」', body_text)
inners = re.findall(r'『([^『』]*)』', body_text)
chk(len(singles) + len(inners) > 0, f'引号反扫条数 = {len(singles)}+{len(inners)}')
badq = [s for s in singles + inners if norm(s) and norm(s) not in corpus_norm]
chk(not badq, f'「」『』内容全部命中库本（失败 {len(badq)}）')
for s in badq:
    print('   反扫未命中：', s)
chk(body_text.count('「') == body_text.count('」'), '「」配对')

# ---------- 红线 ----------
stripped = re.sub(r'<style>.*?</style>', '', raw, flags=re.S)
stripped = re.sub(r'<script>.*?</script>', '', stripped, flags=re.S)
chk('—' not in stripped and '–' not in stripped, '禁长划线 — –')
badmid = [(i, l.count('·')) for i, l in enumerate(stripped.split('\n')) if l.count('·') > 1]
chk(not badmid, f'每行 · ≤1（失败 {badmid}）')

hrefs = re.findall(r'href="([^"]+)"', raw)
badhref = [h for h in hrefs if not (h.startswith('#') or h == 'mulu.html')]
chk(not badhref, f'零外链（失败 {badhref}）')

words = set(re.findall(r'[A-Za-z][A-Za-z0-9_./]*', body_text))
allow = {'github.com/robertsong2000/daizhigev20', 'verify_benshishi.py', 'OCR'}
chk(words <= allow, f'英文白名单（多出 {words - allow}）')

# ---------- 机数 ----------
ns = re.sub(r'\s', '', corpus_raw)
chk(len(ns) == 10211, f'库本去空白字数实测 {len(ns)} == 10211')
chk('一万零二百一十一' in raw, '页脚机数（一万零二百一十一）在页')

lines = [l.strip() for l in corpus_raw.split('\n')]
headers = ['情感第一', '事感第二', '高逸第三', '怨愤第四', '征异第五', '征咎第六', '嘲戏第七']
idx = []
for h in headers:
    idx.append(max(i for i, l in enumerate(lines) if l == h))  # 取正文题头，跳过卷首目录行
counts = []
for k, i in enumerate(idx):
    j = idx[k + 1] if k + 1 < len(idx) else len(lines)
    counts.append(sum(1 for l in lines[i + 1:j] if l))
chk(counts == [12, 6, 3, 5, 5, 3, 7], f'七题实数 {counts} == [12,6,3,5,5,3,7]')
chk(sum(counts) == 41, f'四十一事合计 {sum(counts)}')
chk('事四十一' in raw, '页脚四十一事在页')
for lab in ['十二事', '六事', '三事', '五事', '七事']:
    chk(lab in raw, f'七题签计数 {lab} 在页')
chk('光启二年' in raw and '凡七题' in raw, '落款年份与七题语在页')

# ---------- 编号联动 ----------
chk('殆知阁导读 之一百九十 本事诗' in raw, 'title 自标 190')
chk('殆知阁导读 之一百九十' in raw, 'kicker 自标 190')
mulu = open(MULU, encoding='utf-8').read()
nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
entered = 'benshi-shi.html' in mulu
if entered:
    chk(190 in nos and max(nos) == 190, f'mulu 已入库且为最大号（max={max(nos)}）')
    chk('一百九十篇' in mulu, 'mulu 计数已改一百九十篇')
else:
    chk(max(nos) + 1 == 190, f'mulu 当前 max={max(nos)}，页面自标 190 预备顺延')

print()
print('======', 'ALL PASS' if not fails else f'{len(fails)} FAIL', '======')
sys.exit(1 if fails else 0)
