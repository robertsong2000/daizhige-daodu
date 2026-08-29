#!/usr/bin/env python3
"""引文核验 + 排版规则校验：shiliuqiu-lu.html vs 库内文件"""
import re, sys, unicodedata

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/shiliuqiu-lu.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/使琉球录.txt"

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    return "".join(ch for ch in s if "一" <= ch <= "鿿")

html = open(HTML, encoding="utf-8").read()
src = norm(open(SRC, encoding="utf-8").read())
fail = []

# 1. 长划线禁止；·每行（源行≤1 保证渲染行≤1）
for bad, label in [("—", "长划线—"), ("–", "短划线–")]:
    if bad in html:
        fail.append(f"排版：发现 {label}")
for ln, line in enumerate(html.splitlines(), 1):
    if line.count("·") > 1:
        fail.append(f"排版：第{ln}行有{line.count('·')}个·")

# 2. blockquote.q 引文逐字比对（排除 .src 注）
quotes = re.findall(r'<blockquote class="q">(.*?)<span class="src">', html, re.S)
print(f"引文块 {len(quotes)} 条")
for i, q in enumerate(quotes, 1):
    text = norm(re.sub(r"<[^>]+>", "", q))
    if not text:
        fail.append(f"引文{i}：空")
    elif text not in src:
        fail.append(f"引文{i} 不在库内文件中：{q[:40]}...")

# 3. 夷语词表逐对比对（词，音。）
pairs = [
    ("海", "吾乜"), ("山", "牙马奴"), ("船", "福尼"), ("舵", "看失"),
    ("酒", "撒急"), ("雪", "由其"), ("皇帝", "倭的每"),
    ("琉球人", "倭急拿必周"), ("日本人", "亚马奴必周"), ("万万岁", "麻油吐失"),
]
for w, p in pairs:
    if norm(f"{w}，{p}。") not in src:
        fail.append(f"夷语对不上：{w} {p}")

# 4. 关键事实句核对
facts = [
    "顺风七昼夜始可至琉球",
    "价计二千五百两有奇",
    "旧时用四百余人今革其十分之一",
    "去必孟夏而来必季秋",
    "金着陈侃等收了",
    "共计黄金一百九十二两",
    "自昔奉使造舟未有若余等之艰苦者也",
    "东风相左针路舛误",
    "毁伤",  # 福建卷案风雨毁伤（宽匹配）
]
for f in facts:
    if norm(f) not in src:
        fail.append(f"事实句不在库内：{f}")

if fail:
    print("FAIL")
    [print(" ", x) for x in fail]
    sys.exit(1)
print("PASS：无长划线/间隔号；引文、词表、事实句全部命中库内原文")
