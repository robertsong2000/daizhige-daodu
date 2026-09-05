#!/usr/bin/env python3
"""红线自检：页面所有引文逐字比对库内文件；长划线；每行·计数；外部依赖；编号联动。"""
import re, unicodedata, sys

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/wobian-shilue.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/倭变事略.txt"
MULU = "/home/robertsong/workspace/claude/daizhige-daodu/mulu.html"
REPO = "https://github.com/robertsong2000/daizhige-daodu"

PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】●■◇　\b]")

def norm(s):
    return PUNCT.sub("", unicodedata.normalize("NFKC", s))

body = norm(open(SRC, encoding="utf-8").read())
html = open(HTML, encoding="utf-8").read()
ok = True

# 1. 引文比对：.q 块（精确 class）+ 所有「」对 + 诗行 + 散文白名单
blocks = re.findall(r'<div class="q">(.*?)</div>', html, re.S)
bracketed = re.findall(r"「([^」]*)」", html)
poem = re.findall(r'<div class="v">(.*?)</div>', html, re.S)
EXTRA = [
    "海上兵与倭交锋之始也",
    "衣冠失职书生",
    "徐海、王直、毛烈等并皆华人，可信矣。",
    "城守民贫者，日给米二升，夜给烛五枝，夜半给饼五枚",
    "余每夜巡逻，绕城走七匝，天始辨曙。",
    "以妇人将兵，颇有纪律，秋毫无犯。",
    "数请出战",
    "固守为上",
    "郁郁不得志",
    "佳人不易得，汝弃吾当取之。",
    "毋更作孽。",
    "当服何罪！",
    "不战而屈人之兵",
    "纪验讫。",
    "掠奸索食，不灭于贼。",
    "至有自相杀伤者。",
    "乘金碧舆",
    "即汪五峰",
    "死者约三千七百有奇",
    "杀害数千人，荡民产数万家",
    "斩获二千余级",
]
quotes = [(f"q块{i}", b) for i, b in enumerate(blocks, 1)] + \
         [(f"「」{i}", b) for i, b in enumerate(bracketed, 1)] + \
         [(f"诗{i}", b) for i, b in enumerate(poem, 1)] + \
         [(f"补{i}", b) for i, b in enumerate(EXTRA, 1)]
for tag, q in quotes:
    q = re.sub(r"<[^>]+>", "", q)
    frags = [f for f in re.split(r"……|\.\.\.", q) if norm(f)]
    for f in frags:
        if norm(f) not in body:
            ok = False
            print(f"FAIL 引文[{tag}]: {f}")
print(f"引文比对：{len(quotes)} 处（q块{len(blocks)} + 「」{len(bracketed)} + 诗{len(poem)} + 补{len(EXTRA)}） "
      + ("全部通过" if ok else "存在失败"))

# 2. 长划线
for ch, name in [("—", "—(em)"), ("–", "–(en)"), ("−", "−(minus)")]:
    if ch in html:
        ok = False
        print(f"FAIL 禁用字符 {name}")

# 3. 每行 · 最多 1 个
for ln, line in enumerate(html.splitlines(), 1):
    if line.count("·") > 1:
        ok = False
        print(f"FAIL 第{ln}行 · 超限: {line.strip()[:60]}")

# 4. 无外部依赖（仓库自身链接豁免）
if re.search(r'https?://|<link|src="http', html.replace(REPO, "")):
    ok = False
    print("FAIL 存在外部链接/资源引用")

# 5. 编号联动：页脚自标编号 vs mulu 现状
m = re.search(r'殆知阁导读 之(一百[零一二三四五六七八九十]*|[零一二三四五六七八九十]+),倭变事略', html)
if not m:
    ok = False
    print("FAIL 页脚编号格式未找到")
elif "NNN" in html:
    print("提示：页内编号仍为占位 NNN，commit 前必须落号")
else:
    mulu = open(MULU, encoding="utf-8").read()
    nos = [int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', mulu)]
    def cn2int(s):
        digits = {"零":0,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
        base = 0
        if s.startswith("一百"):
            base = 100
            s = s[2:]
        elif s.startswith("二百") or s.startswith("三百"):
            base = digits[s[0]] * 100
            s = s[2:]
        if "十" not in s: return base + digits.get(s, -1)
        a, _, b = s.partition("十")
        left = digits.get(a, 1) if a else 1
        right = digits.get(b, 0) if b else 0
        return base + left * 10 + right
    n = cn2int(m.group(1))
    nxt = max(nos) + 1
    if n != nxt:
        ok = False
        print(f"FAIL 页脚编号 {n} != mulu 下一号 {nxt}")
    else:
        print(f"编号联动：页脚 {n} == mulu 下一号 {nxt}，通过")

print("结果：" + ("PASS 全部红线通过" if ok else "未通过"))
sys.exit(0 if ok else 1)
