#!/usr/bin/env python3
"""剑侠传自检：页面所有「」引文与 .q 块逐字比对库内文件；长划线；每行·计数；外链豁免仓库域名。"""
import re, unicodedata, sys

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/jianxia-zhuan.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/剑侠传.txt"
REPO = "https://github.com/robertsong2000/daizhige-daodu"

VAR = {"掲": "揭", "頺": "颓", "頽": "颓", "髙": "高", "竒": "奇", "渉": "涉",
       "姸": "妍", "郄": "却", "欵": "款", "寛": "宽", "眞": "真", "兎": "兔",
       "冩": "写", "浄": "净", "児": "儿", "巻": "卷", "歴": "历", "畧": "略",
       "襍": "杂", "癈": "废"}
PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】●■　]")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VAR.get(c, c) for c in s)
    return PUNCT.sub("", s)

body = norm(open(SRC, encoding="utf-8").read())
html = open(HTML, encoding="utf-8").read()

ok = True

# 1. 引文比对：所有 .q 块 + 所有「」对 + 页面上未加括号的 verbatim 短句（EXTRA）
blocks = re.findall(r'<div class="q">(.*?)</div>', html, re.S)
bracketed = re.findall(r"「([^」]*)」", html)
EXTRA = [
    "自此无复有人见隐娘矣。",
    "因伪醉离席，遂亡所在。",
    "一品悔惧，每夕多以家童持剑戟自卫。",
    "只须一条绳",
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

# 2. 长划线 / en-dash / 繁体残留
for ch, name in [("—", "—(em)"), ("–", "–(en)"), ("−", "−(minus)")]:
    if ch in html:
        ok = False
        print(f"FAIL 禁用字符 {name}")
for ch, name in [("給", "給(繁)"), ("裏", "裏(繁)"), ("於", "於(繁)"), ("爲", "爲(繁)")]:
    if ch in html:
        ok = False
        print(f"FAIL 繁体残留 {name}")

# 3. 每行 · 最多 1 个（按渲染行近似：HTML 源文件行）
for ln, line in enumerate(html.splitlines(), 1):
    if line.count("·") > 1:
        ok = False
        print(f"FAIL 第{ln}行 · 超限: {line.strip()[:60]}")

# 4. 无外部依赖（仓库自身链接豁免）
if re.search(r'https?://|<link|src="http', html.replace(REPO, "")):
    ok = False
    print("FAIL 存在外部链接/资源引用")

# 5. 结构断言：33 张小榜、到案表 5 行、自标 159、mulu 关键字
ties = re.findall(r'<div class="tie[ "]', html)
if len(ties) != 34:  # 33 张榜 + 1 张说明卡
    ok = False
    print(f"FAIL 小榜数量 {len(ties)} != 34")
rows = re.findall(r"<tr><td>", html)
if len(rows) != 5:
    ok = False
    print(f"FAIL 到案表行数 {len(rows)} != 5")
for kw in ["之一百六十一", "殆知阁导读之一百六十一", "弇州山人王世贞辑", "三十三人，到案者一"]:
    if kw not in html:
        ok = False
        print(f"FAIL 缺少关键字 {kw}")
nums = {"一": 1, "四": 4, "十七": 17, "十": 10}
cells = re.findall(r'<td class="wu">([^<]*)</td>', html)
if [c for c in cells] != ["一", "四", "十七", "十", "一"]:
    ok = False
    print(f"FAIL 到案表人数列 {cells}")

print("结果：" + ("PASS 全部红线通过" if ok else "未通过"))
sys.exit(0 if ok else 1)
