#!/usr/bin/env python3
"""红线自检：引文逐字比对库本；长划线；每行·计数；外部依赖；编号联动；本页结构断言。"""
import re, unicodedata, sys

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/qincao.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/艺藏/音乐/琴操.txt"
MULU = "/home/robertsong/workspace/claude/daizhige-daodu/mulu.html"
REPO = "https://github.com/robertsong2000/daizhige-daodu"

PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】　\b]")

def norm(s):
    return PUNCT.sub("", unicodedata.normalize("NFKC", s))

body = norm(open(SRC, encoding="utf-8").read())
html = open(HTML, encoding="utf-8").read()
ok = True

# 1. 引文比对：.q 块 + .v 诗块 + 所有「」对
blocks = re.findall(r'<div class="q">(.*?)</div>', html, re.S)
verses = [re.sub(r"<small>.*?</small>", "", v, flags=re.S)
          for v in re.findall(r'<div class="v">(.*?)</div>', html, re.S)]
bracketed = re.findall(r"「([^」]*)」", html)
quotes = [(f"q块{i}", b) for i, b in enumerate(blocks, 1)] + \
         [(f"诗{i}", b) for i, b in enumerate(verses, 1)] + \
         [(f"「」{i}", b) for i, b in enumerate(bracketed, 1)]
fail = 0
for tag, q in quotes:
    q = re.sub(r"<[^>]+>", "", q)
    frags = [f for f in re.split(r"……|\.\.\.", q) if norm(f)]
    for f in frags:
        if norm(f) not in body:
            ok = False; fail += 1
            print(f"FAIL 引文[{tag}]: {f}")
print(f"引文比对：{len(quotes)} 处（q块{len(blocks)} + 诗{len(verses)} + 「」{len(bracketed)}） "
      + ("全部通过" if fail == 0 else f"{fail} 处失败"))

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

# 5. 结构断言
def chk(cond, msg):
    global ok
    if not cond:
        ok = False
        print(f"FAIL 结构: {msg}")

chk(html.count('class="hui"') == 13, "首屏琴身徽位应为 13")
rows = re.findall(r'<span class="dots">(.*?)</span>', html, re.S)
chk(len(rows) == 13, f"徽位分节应为 13，实得 {len(rows)}")
for i, r in enumerate(rows, 1):
    chk(r.count("<b") == 13, f"第{i}节徽点数应为 13")
    chk(r.count('class="on"') == 1, f"第{i}节应有且仅有一个当前徽位")
chk(html.count('class="que"') == 5, "缺牌应为 5")
chk(len(re.findall(r'class="row"', html)) == 9, "曲终人亡账应为 9 行")
prose_zone = html.split("</style>", 1)[1]
stripped = re.sub(r"<[^>]+>", "", prose_zone)
words = re.findall(r"[A-Za-z]{3,}", stripped)
allow = {"DOCTYPE", "html", "class", "href", "https", "github", "com", "span", "small", "style",
         "zh", "CN", "UTF", "width", "device", "scale", "section", "footer", "main", "header", "id",
         "txt", "robertsong", "daizhige", "daodu"}
bad = [w for w in words if w not in allow]
chk(not bad, f"正文残留英文词: {bad}")

# 6. 编号联动：页脚自标 vs mulu 下一号
m = re.search(r'殆知阁导读 之(一百[零一二三四五六七八九十]*|[零一二三四五六七八九十]+),琴操', html)
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
        if "十" not in s: return base + digits.get(s, -1)
        a, _, b = s.partition("十")
        left = digits.get(a, 1) if a else 1
        right = digits.get(b, 0) if b else 0
        return base + left * 10 + right
    n = cn2int(m.group(1))
    nxt = max(nos) + 1
    if n == nxt:
        print(f"编号联动：页脚 {n} == mulu 下一号 {nxt}，通过")
    elif n == max(nos) and n in nos:
        print(f"编号联动：页脚 {n} 已入 mulu 且为当前最大号，通过（已发布态）")
    else:
        ok = False
        print(f"FAIL 页脚编号 {n} 既不等于 mulu 下一号 {nxt}，也未入库")

# 7. 编号三处一致（title / kicker / footer）
chk("之一百六十五" in re.search(r"<title>(.*?)</title>", html).group(1), "title 编号")
chk("第一百六十五篇" in html, "kicker 编号")

print("结果：" + ("PASS 全部红线通过" if ok else "未通过"))
sys.exit(0 if ok else 1)
