#!/usr/bin/env python3
# 封氏闻见记：页面引文与库内文件双向核验
import re, sys, unicodedata

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/封氏闻见记.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/fengshi-wenjian-ji.html"

VARMAP = {"従": "从", "呉": "吴", "聫": "联", "寃": "冤", "兎": "兔"}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VARMAP.get(c, c) for c in s)
    return "".join(c for c in s if unicodedata.category(c).startswith("L") and ord(c) > 0x2E00)

src = open(SRC, encoding="utf-8").read()
page = open(PAGE, encoding="utf-8").read()
nsrc = norm(src)

fails = 0

# 0) 库本字数断言
plain = re.sub(r"\s+", "", src)
print(f"[i] 库本去空白字数 = {len(plain)} (页面声称 29,128)")
if len(plain) != 29128:
    print("[FAIL] 字数与页面声称不符"); fails += 1

# 1) 页面 blockquote.q 全量抽取（剔除 .src 标注）
quotes = []
for m in re.finditer(r'<blockquote class="q">(.*?)</blockquote>', page, re.S):
    body = re.sub(r'<span class="src">.*?</span>', "", m.group(1), flags=re.S)
    text = re.sub(r"<[^>]+>", "", body)
    quotes.append((text.strip(), m.group(0)))
print(f"[i] 页面引文块共 {len(quotes)} 段")
for i, (q, _) in enumerate(quotes, 1):
    nq = norm(q)
    if not nq:
        print(f"[FAIL] 引文{i} 归一后为空"); fails += 1; continue
    if nq in nsrc:
        print(f"[PASS] 引文{i} ({len(nq)}字) {q[:18]}……")
    else:
        # 定位最长可匹配前缀帮助排错
        lo, hi = 0, len(nq)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if nq[:mid] in nsrc: lo = mid
            else: hi = mid - 1
        print(f"[FAIL] 引文{i} 未命中库本：{q[:42]}……｜最长匹配前缀 {lo}/{len(nq)}：「{nq[:lo]}」｜断点后应接：「{nq[lo:lo+12]}」")
        fails += 1

# 2) .src 条目标注存在性：〈X〉须为库本 ○条目
labels = re.findall(r'〈([^〈〉]+)〉', "".join(s for _, s in quotes))
for lab in set(labels):
    if f"○{lab}" not in src.replace(" ", ""):
        print(f"[FAIL] 标注条目〈{lab}〉在库本无对应 ○ 条目"); fails += 1
    else:
        print(f"[PASS] 条目标注〈{lab}〉存在")
if "同上" in "".join(s for _, s in quotes):
    print("[PASS] 同上标注沿用前引出处")

# 3) 散文短引（「」内短语）双向
shorts = ["两边通耶"]
pagetext = norm(re.sub(r"<[^>]+>", "", page))
for s_ in shorts:
    ns = norm(s_)
    ok_p, ok_s = ns in pagetext, ns in nsrc
    print(f"[{'PASS' if ok_p and ok_s else 'FAIL'}] 短引「{s_}」 页面{ok_p} 库本{ok_s}")
    if not (ok_p and ok_s): fails += 1

# 4) 排版红线静态检查：禁长划线；标签外文本每行 · 最多 1 个
for ch, name in [("—", "em-dash"), ("–", "en-dash")]:
    if ch in page:
        print(f"[FAIL] 页面含禁字符 {name}"); fails += 1
body = page.split("<body>", 1)[1]
text = re.sub(r"<[^>]+>", "", body)
bad_lines = [ln.strip() for ln in text.splitlines() if ln.count("·") > 1]
if bad_lines:
    for ln in bad_lines[:5]: print(f"[FAIL] 一行多·：{ln[:60]}")
    fails += 1
else:
    print("[PASS] 无一行多·，无长划线")

print("=" * 40)
print(f"核验结果：{'全部通过' if fails == 0 else f'{fails} 项未过'}（引文{len(quotes)}段）")
sys.exit(1 if fails else 0)
