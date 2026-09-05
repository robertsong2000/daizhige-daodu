#!/usr/bin/env python3
"""西征随笔自检：页面所有 .q 块与「」引文、mono 补充片段、名号与条目签逐字比对库内文件；长划线；每行·计数；外链豁免仓库域名。"""
import re, unicodedata, sys

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/xizheng-suibi.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/西征随笔.txt"
REPO = "github.com/robertsong2000/daizhige-daodu"

VAR = {"髙": "高", "竒": "奇", "眞": "真", "兎": "兔", "巻": "卷", "歴": "历",
       "畧": "略", "襍": "杂", "癈": "废", "浄": "净", "冩": "写"}
PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】●■　]")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VAR.get(c, c) for c in s)
    return PUNCT.sub("", s)

body = norm(open(SRC, encoding="utf-8").read())
html = open(HTML, encoding="utf-8").read()

ok = True

# 1. 引文比对：.q 块 + 「」对 + 未加括号的 verbatim 短句（EXTRA）
blocks = re.findall(r'<div class="q">(.*?)</div>', html, re.S)
bracketed = re.findall(r"「([^」]*)」", html)
EXTRA = [
    "二月初六日午，刻赵州大石桥旅次",
    "正供桁杨桎梏，至卖儿贴妇以偿",
    "飞飞儿、决云儿、紫云来、锦上花、风中花、梨花雪、桃花雪",
    "小诗六章，聊效巷祝衢歌",
    "大将军有揖客，顾不重耶？",
    "吏治之坏莫甚于陕西，数十年来，督抚藩臬皆以满州人为之，目不知书",
    "按此条见雍正五年三月戊戌谕旨所引",
    "三月十七日",
    "步光小传", "诙谐之语", "孤魅畏节妇", "妇人缠足", "记台吉女自缢事", "秦中凯歌十三首",
    "闪电光", "一堆雪", "神臂弓", "飞飞儿", "决云儿", "紫云来", "锦上花", "风中花", "梨花雪", "桃花雪",
    "长枪", "大刀",
]
quotes = [(f"q块{i}", b) for i, b in enumerate(blocks, 1)] + \
         [(f"「」{i}", b) for i, b in enumerate(bracketed, 1)] + \
         [(f"补{i}", b) for i, b in enumerate(EXTRA, 1)]
for tag, q in quotes:
    frags = [f for f in re.split(r"……|\.\.\.", q) if norm(f)]
    for f in frags:
        if norm(f) not in body:
            ok = False
            print(f"[引文FAIL] {tag}: {f[:60]}")

# 2. 长划线（em/en dash 禁用）
if re.search(r"[—–]", html):
    ok = False
    print("[排版FAIL] 含长划线")

# 3. 每行 · 最多 1 个（按渲染近似：HTML 文本行）
in_style = False
for i, line in enumerate(html.splitlines(), 1):
    s = line.strip()
    if s.startswith("<style>"): in_style = True; continue
    if s.startswith("</style>"): in_style = False; continue
    if in_style: continue
    text = re.sub(r"<[^>]+>", "", line)
    if text.count("·") > 1:
        ok = False
        print(f"[排版FAIL] 行{i} · 超限: {text.strip()[:60]}")

# 4. 外链仅豁免仓库域名
for m in re.findall(r'href="(http[^"]+)"', html):
    if REPO not in m:
        ok = False
        print(f"[外链FAIL] {m}")

# 5. 残留未闭合粗检：div 计数
if html.count("<div") != html.count("</div>"):
    ok = False
    print(f"[结构FAIL] div 不配对 {html.count('<div')} vs {html.count('</div>')}")

print("PASS" if ok else "FAIL", f"(.q {len(blocks)} 条, EXTRA {len(EXTRA)} 条)")
sys.exit(0 if ok else 1)
