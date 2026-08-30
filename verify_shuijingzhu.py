# -*- coding: utf-8 -*-
# 引文核验 + 卷次定位 + 排版红线检查
import re, sys

HTML = "shuijingzhu.html"
CORP = {
    "sjz": "../daizhige-simplified/史藏/地理/水经注.txt",
    "bs":  "../daizhige-simplified/史藏/正史/北史.txt",
    "ws":  "../daizhige-simplified/史藏/正史/魏书.txt",
}

def norm(s):
    return re.sub(r"[^0-9A-Za-z一-鿿𠀀-𪛟]", "", s)

corp_lines = {k: open(v, encoding="utf-8").read().splitlines() for k, v in CORP.items()}
corp_norm = {k: norm("\n".join(ls)) for k, ls in corp_lines.items()}

html = open(HTML, encoding="utf-8").read()

# 1. q 标签引文
qs = re.findall(r"<q>(.*?)</q>", html, re.S)
# 2. 「」行内引文
inline = re.findall(r"「(.*?)」", html, re.S)
# 3. 库本档案残留行（全角空格显示，按去空白比对）
scar = re.search(r"<code>(.*?)</code>", html, re.S).group(1)

fails = 0
print("== <q> 引文核验 ==")
for q in qs:
    n = norm(q)
    hit = [k for k, c in corp_norm.items() if n in c]
    tag = "PASS " + ("+".join(hit) if hit else "")
    if not hit: fails += 1
    print(f"[{'FAIL' if not hit else 'PASS'}|{'+'.join(hit) if hit else '???'}] {q[:34]}")

print("== 「」行内引文核验 ==")
for q in inline:
    n = norm(q)
    hit = [k for k, c in corp_norm.items() if n in c]
    if not hit: fails += 1
    print(f"[{'FAIL' if not hit else 'PASS'}|{'+'.join(hit) if hit else '???'}] {q[:34]}")

print("== 库本档案残留行核验 ==")
n = norm(scar)
hit = n in corp_norm["sjz"]
print(f"[{'PASS' if hit else 'FAIL'}] scar line")
if not hit: fails += 1

# 卷次定位：sjz 引文按行号向上找最近的 卷/○ 题（qs 下标按页面顺序）
print("== 卷次定位 ==")
juan_of = []
cur_j = cur_t = None
for i, line in enumerate(corp_lines["sjz"]):
    if re.match(r"^卷", line): cur_j = line.strip()
    if re.match(r"^○", line): cur_t = line.strip()
    juan_of.append((cur_j, cur_t))
EXPECT = {4: "卷一", 5: "卷一", 6: "卷四", 7: "卷十六", 8: "卷三十四", 9: "卷三十四", 10: "卷三十四", 11: "卷三十四", 12: "卷四十"}
for idx, expect in EXPECT.items():
    q = qs[idx]
    n = norm(q)
    i = next((i for i, line in enumerate(corp_lines["sjz"]) if n and n in norm(line)), None)
    if i is None:
        print(f"[FAIL] 定位失败: {q[:20]}"); fails += 1; continue
    j, t = juan_of[i]
    ok = (j == expect)
    if not ok: fails += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {expect} vs {j} {t} : {q[:20]}")

# 排版红线：无长划线；每行 · 至多 1
print("== 排版红线 ==")
for ch, name in [("—", "长划线—"), ("–", "en-dash–"), ("‒", "figure-dash"), ("―", "horizontal bar")]:
    if ch in html:
        print(f"[FAIL] 发现 {name}"); fails += 1
bad = [(i+1, l) for i, l in enumerate(html.splitlines()) if l.count("·") > 1]
if bad:
    for ln, l in bad: print(f"[FAIL] 第{ln}行含{2}个·: {l[:60]}")
    fails += 1
else:
    print("[PASS] 无长划线；每行 · 至多 1")

# mulu 编号连续性在另一脚本处理
print("FAILS:", fails)
sys.exit(1 if fails else 0)
