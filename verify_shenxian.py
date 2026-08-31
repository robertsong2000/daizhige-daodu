#!/usr/bin/env python3
# 神仙传 页面核验：引文逐字对库 + 排版红线 + 数据实测
import re, sys

PAGE = 'shenxian-zhuan.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/道藏/藏外/神仙传.txt'

page = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()

errs, warns = [], []
def chk(cond, msg):
    if not cond: errs.append(msg)

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch.isspace(): continue
        if (0x3000 <= o <= 0x303F) or (0xFF00 <= o <= 0xFFEF) \
           or ch in '「」『』“”‘’·，。、；：？！〈〉《》（）｛｝【】' \
           or (0x2018 <= o <= 0x201F) or ch in '、。':
            continue
        if o < 0x2E80 and not ch.isalnum(): continue
        out.append(ch)
    return ''.join(out)

# ---------- 正文提取（去标签） ----------
body = page[page.index('<body>'):]
text = re.sub(r'<style>.*?</style>', '', body, flags=re.S)
text = re.sub(r'<[^>]+>', '', text)
text = html_unescape = text.replace('&nbsp;', ' ')

# ---------- 引文逐字对库 ----------
quotes = re.findall(r'「([^」]+)」', text)
libn = norm(lib)
chk(len(quotes) >= 10, f'引文数 {len(quotes)} 少于 10，疑似解析失败')
for q in quotes:
    qn = norm(q)
    if not qn:
        errs.append(f'空引文：{q[:20]}')
        continue
    if qn not in libn:
        # 找出首个失配位置帮助定位
        lo, hi = 0, len(qn)
        pos = None
        for i in range(len(qn), 0, -1):
            if qn[:i] in libn:
                pos = i; break
        errs.append(f'引文不匹配（前{pos}/{len(qn)}字可匹配）：「{q[:42]}」')

# ---------- 排版红线 ----------
chk('—' not in page, '出现长划线 —')
chk('–' not in page, '出现短划线 –')
for i, ln in enumerate(page.split('\n'), 1):
    c = ln.count('·')
    chk(c <= 1, f'第{i}行含 {c} 个 ·')
chk(page.count('「') == page.count('」'), '「」不配对')
chk(page.count('『') == page.count('』'), '『』不配对')

# ---------- 页脚必备 ----------
for s in ['殆知阁简体库', 'github.com/robertsong2000/daizhigev20', '引文核验', '时代局限', '切勿模仿']:
    chk(s in page, f'缺少必备文案：{s}')

# ---------- 实测数据对账 ----------
vol_line = re.findall(r'<div class="tv">卷[一二三四五六七八九十]+</div><div class="tc">(\d+)</div>', page)
chk(len(vol_line) == 10, f'卷轨 {len(vol_line)} 枚 != 10')
chk(sum(map(int, vol_line)) == 84, f'卷轨合计 {sum(map(int, vol_line))} != 84（实测八十四传）')
chk('84' in norm(''.join(vol_line)) or sum(map(int, vol_line)) == 84, '卷轨数字异常')

n_cards = page.count('<article class="zuo">')
chk(n_cards == 8, f'证人席 {n_cards} 卡 != 8')

# ---------- 卷次归属抽查（竹签上的卷号与人名须在同一卷） ----------
anchor = {
    '魏伯阳': '卷二', '皇初平': '卷二', '王远': '卷三', '栾巴': '卷五',
    '淮南王': '卷六', '壶公': '卷九', '董奉': '卷十', '李意期': '卷十',
    '白石生': '卷一',
}
lib_vols = {}
cur = None
for ln in lib.split('\n'):
    s = ln.strip()
    if re.fullmatch(r'卷[一二三四五六七八九十]+', s):
        cur = s
    elif cur and s and re.fullmatch(r'[一-鿿]{2,5}', s):
        lib_vols.setdefault(s, cur)
for name, v in anchor.items():
    got = lib_vols.get(name)
    chk(got == v, f'卷次错配：{name} 标注{v}，库内实为{got}')

print(f'引文 {len(quotes)} 条，全部逐字比对' if not errs else '')
for e in errs: print('ERR', e)
for w in warns: print('WARN', w)
sys.exit(1 if errs else 0)
