#!/usr/bin/env python3
"""红线自检：页面所有「」引文逐字比对库内文件；长划线；每行·计数。"""
import re, unicodedata, sys

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/yanlan-xiaopu.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/燕兰小谱.txt"
REPO = "https://github.com/robertsong2000/daizhige-daodu"

VAR = {"掲": "揭", "頺": "颓", "頽": "颓", "髙": "高", "竒": "奇", "渉": "涉",
       "姸": "妍", "郄": "却", "欵": "款", "寛": "宽", "眞": "真", "兎": "兔",
       "冩": "写", "浄": "净", "児": "儿", "巻": "卷", "歴": "历", "畧": "略"}
PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】●■　]")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VAR.get(c, c) for c in s)
    return PUNCT.sub("", s)

body = norm(open(SRC, encoding="utf-8").read())
html = open(HTML, encoding="utf-8").read()

ok = True

# 1. 引文比对：所有 .q 块 + 所有「」对 + 页面上未加括号的verbatim短句（EXTRA）
blocks = re.findall(r'<div class="q">(.*?)</div>', html, re.S)
bracketed = re.findall(r"「([^」]*)」", html)
EXTRA = [
    "雅花列部，协正变于风人；正杂分编，配阴阳于易象。",
    "舞榭歌台，都供水天之闲话。",
    "银官戏法、桂官画兰、万官弹琴，时称三妙。",
    "陈、王、二刘，时称四美，以冠花部，允协舆情。",
    "乐技至此愈降愈下矣",
    "今虽复演，与银官分部，改名永庆，然较前则杀去声矣。",
    "既而以《滚楼》一剧名动京城，观者日至千余，六大班顿为之减色。",
    "时乎！时乎！藏器以待可也。",
]
quotes = [(f"q块{i}", b) for i, b in enumerate(blocks, 1)] + \
         [(f"「」{i}", b) for i, b in enumerate(bracketed, 1)] + \
         [(f"补{i}", b) for i, b in enumerate(EXTRA, 1)]
for tag, q in quotes:
    frags = [f for f in re.split(r"……|\.\.\.", q) if norm(f)]
    for f in frags:
        if norm(f) not in body:
            ok = False
            print(f"FAIL 引文[{tag}]: {f}")
print(f"引文比对：{len(quotes)} 处（q块{len(blocks)} + 「」{len(bracketed)} + 补{len(EXTRA)}） "
      + ("全部通过" if ok else "存在失败"))

# 2. 长划线 / en-dash
for ch, name in [("—", "—(em)"), ("–", "–(en)"), ("−", "−(minus)")]:
    if ch in html:
        ok = False
        print(f"FAIL 禁用字符 {name}")

# 3. 每行 · 最多 1 个（按渲染行近似：HTML 源文件行）
for ln, line in enumerate(html.splitlines(), 1):
    if line.count("·") > 1:
        ok = False
        print(f"FAIL 第{ln}行 · 超限: {line.strip()[:60]}")

# 4. 无外部依赖（仓库自身链接豁免）
if re.search(r'https?://|<link|src="http', html.replace(REPO, "")):
    ok = False
    print("FAIL 存在外部链接/资源引用")

print("结果：" + ("PASS 全部红线通过" if ok else "未通过"))
sys.exit(0 if ok else 1)
