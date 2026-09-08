#!/usr/bin/env python3
import re, sys, unicodedata

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/佛藏/大藏经/续藏/古逸部/大目乾连冥间救母变文并图.txt"
HTML = "/home/robertsong/workspace/claude/daizhige-daodu/mulian-bianwen.html"

t = open(SRC, encoding="utf-8").read()
html = open(HTML, encoding="utf-8").read()

STRIP = "。，、；：？！·「」『』（）〔〕《》　 \t\r\n"
def norm(s):
    s = re.sub(r"<[^>]+>", "", s)
    return "".join(ch for ch in s if ch not in STRIP)

T = norm(t)
fails = []

# 1) .q 引文块
qs = re.findall(r'<blockquote class="q">(.*?)</blockquote>', html, re.S)
qs = [norm(q.split('<span class="src">')[0]) for q in qs]
# 2) qbank 注释
qb = re.search(r"<!-- qbank:(.*?)-->", html, re.S).group(1)
qbank = [norm(l) for l in qb.splitlines() if l.strip()]
# 3) colophon 题记
colo = norm(re.search(r'<p class="sig">(.*?)</p>', html, re.S).group(1))

checks = [("q块", qs), ("qbank", qbank), ("题记", [colo])]
for label, arr in checks:
    for q in arr:
        if not q: continue
        ok = q in T
        print(("OK  " if ok else "MISS"), label, q[:30])
        if not ok: fails.append((label, q))

# q 与 qbank 一致性
if sorted(qs + [colo]) != sorted(qbank):
    fails.append(("一致性", "q集合与qbank不完全对应"))

# 4) 排版规则
for i, line in enumerate(html.splitlines(), 1):
    if "—" in line or "–" in line:
        fails.append(("排版", f"L{i} 出现长划线")); print("排版FAIL L", i)
    if line.count("·") > 1:
        fails.append(("排版", f"L{i} · 超限")); print("排版FAIL L", i, line[:50])

# 5) 外部依赖
if re.search(r'https?://[^"]+\.(js|css|woff|ttf|png|jpg)', html):
    fails.append(("依赖", "存在外部静态资源")); print("依赖FAIL")

print()
if fails:
    print("FAIL", len(fails), "项"); sys.exit(1)
print(f"PASS：{len(qs)}条q + 题记共{len(qbank)+1}条引文逐字核验通过，排版规则通过，无外部依赖")
