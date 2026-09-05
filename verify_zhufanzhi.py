#!/usr/bin/env python3
"""核验 zhufan-zhi.html 引文与殆知阁库内《诸蕃志》逐字一致，并查排版规则。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/诸蕃志.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/zhufan-zhi.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
full = norm(raw)
fail = 0

def check(q, where):
    global fail
    ok = norm(q) in full
    print(("PASS" if ok else "FAIL"), where, "|", q[:24] + ("…" if len(q) > 24 else ""))
    fail += 0 if ok else 1

# 手写引文底稿（含题记与正文散句）
MANUAL = [
    ("南对占城，西望真腊；东则千里长沙、万里石床，渺茫无际，天水一色。舟舶来往，惟以指南针为则；昼夜守视唯谨，毫厘之差，生死系焉。", "题记/海南 指南针"),
    ("然诸史外国列传，秉笔之人，皆未尝身历其地，即赵汝适「诸蕃志」之类，亦多得于市舶之口传。", "提要 口传"),
    ("番商贸易至，舶司视香之多少为殿最。", "乳香 殿最"),
    ("其国在海中，扼诸番舟车往来之咽喉。", "三佛齐 咽喉"),
    ("王系唐姓，服色饮食略与中国同", "交趾"),
    ("十取其二，外听交易", "占城 抽解"),
    ("于泉州为丙巳方", "阇婆 方位"),
    ("其王盆尼末换之前，谓之白衣大食", "大食 白衣"),
    ("乃佛麻霞勿所生之处", "麻嘉"),
    ("日食饭、面、烧饼、羊肉", "层拔 饮食"),
    ("一舟可容数千人", "木兰皮 巨舟"),
    ("其顶上有镜极大", "遏根陀 巨镜"),
    ("当泉州之东，舟行约五、六日程", "流求"),
    ("有进士、算学诸科，故号君子国", "新罗 君子国"),
    ("以「干文大宝」为文", "倭 铜钱"),
    ("其成片者，谓之梅花脑，以状似梅花也", "脑子 梅花脑"),
    ("番民以皮鞔躯，先用恶草作烟，迫逐群蜂飞散，随取其窠", "黄蜡 取蜡"),
    ("和香而真用龙涎焚之，一缕翠烟浮空，结而不散，座客可用一剪分烟缕。", "龙涎 翠烟"),
]
for q, where in MANUAL:
    check(q, where)

# 自动回验：页面所有 blockquote 引文块
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r'<blockquote class="(?:epi )?q"[^>]*>(.*?)</blockquote>', html, flags=re.S)
print(f"\n页面引文块 {len(blocks)} 个（blockquote）：")
for b in blocks:
    body = re.sub(r"<span[^>]*>.*?</span>", "", b, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body).strip()
    check(body, "页面块")

# 自动回验：正文散句引文 span.qi（剥去引号后比对）
qis = re.findall(r'<span class="qi">(.*?)</span>', html, flags=re.S)
print(f"\n正文散句引文 {len(qis)} 处（span.qi）：")
for q in qis:
    check(q, "散句")

# 字数口径：库内文件为三书合刊，诸蕃志部分 = 去掉第 429-525 行截断重复刊刻
lines = raw.split("\n")
canon = "\n".join(lines[0:428] + lines[526:735])
han = len(re.sub(r"[^一-鿿]", "", canon))
print(f"\n库内诸蕃志去重后汉字实测：{han}")
ok = han == 22607
print(("PASS" if ok else "FAIL"), "页面声称 22,607 汉字")
fail += 0 if ok else 1

# 排版规则：无长划线；每行·至多 1 个；无外部资源依赖
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1
for pat in ["<script src", "<link ", "@import", "url("]:
    if pat in html:
        print("FAIL 外部依赖：", pat); fail += 1

for k in ["殆知阁", "核验", "局限", "mulu.html", "daizhigev20", "22,607"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
