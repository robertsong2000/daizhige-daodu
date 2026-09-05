# -*- coding: utf-8 -*-
"""核验《陈氏香谱》导读引文：去标点、去空白、PUA 字符归一后，与库内文本逐字比对。"""
import re, sys
from quotes_chenshi import QUOTES

SRC = "../daizhige-simplified/艺藏/器物/陈氏香谱.txt"

# 库本 PUA 字符归一表（实测归纳：康熙讳"玄"及传、爇等字以私用区字符存储）
PUA = {
    "": "玄",
    "": "传",
    "": "爇",
}

def norm(s: str) -> str:
    for k, v in PUA.items():
        s = s.replace(k, v)
    s = re.sub(r"[\s　。，、；：！？「」『』（）《》〈〉·\.\,;:!?\[\]【】\"'“”‘’…\-—―～]", "", s)
    return s

book = norm(open(SRC, encoding="utf-8").read())
fails = []
for qid, q in QUOTES.items():
    n = norm(q)
    if n not in book:
        fails.append(qid)
        # 就近提示：找最长可匹配前缀
        lo, hi = 0, len(n)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if n[:mid] in book:
                lo = mid
            else:
                hi = mid - 1
        print(f"[FAIL] {qid}: 前{lo}字可匹配 / 共{len(n)}字")
        print(f"       停在: …{n[max(0,lo-12):lo]}◀{n[lo:lo+12]}…")
if fails:
    print(f"\n{len(fails)} 条未通过: {fails}")
    sys.exit(1)
print(f"全部 {len(QUOTES)} 条引文核验通过（源：{SRC}）")
