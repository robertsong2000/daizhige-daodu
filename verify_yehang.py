#!/usr/bin/env python3
"""核验 yehang-chuan.html 中的引文是否与殆知阁库内《夜航船》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/类书/夜航船.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yehang-chuan.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

QUOTES = [
    # 序 · 船舱对话
    ("昔有一僧人，与一士子同宿夜航船。", "序 叙"),
    ("士子高谈阔论，僧畏慑，拳足而寝。", "序 叙"),
    ("僧人听其语有破绽，乃曰：", "序 叙"),
    ("请问相公，澹台灭明是一个人、两个人？", "序 僧问"),
    ("是两个人。", "序 士答"),
    ("这等尧舜是一个人、两个人？", "序 僧问"),
    ("自然是一个人！", "序 士答"),
    ("这等说起来，且待小僧伸伸脚。", "序 僧笑"),
    ("余所记载，皆眼前极肤浅之事，吾辈聊且记取，但勿使僧人伸脚则可已矣。", "题名引句"),
    ("故即命其名曰《夜航船》。", "身后 引句"),
    ("学问之富，真是两脚书厨，而其无益于文理考校，与彼目不识丁之人无以异也。", "两脚书厨"),
    ("古剑陶庵老人张岱书。", "序末署名"),
    # 序内散句（正文强调用）
    ("眼前极肤浅之事", "正文强调"),
    ("凡百工贱业", "正文强调"),
    ("不关于文理", "正文强调"),
    # 词条名
    ("司书鬼", "词条名"),
    ("耻与魑魅争光", "词条名"),
    ("迷楼", "词条名"),
    ("吐绶鸡", "词条名"),
    ("鸟社", "词条名"),
    ("物类相感", "词条名"),
    # 考校抽屉原文
    ("名曰长恩。除夕呼其名而祭之，鼠不敢啮，蠹鱼不生。", "司书鬼"),
    ("嵇中散灯下弹琴。有一人入室，初来时，面甚小，斯须转大，遂长丈余，颜色甚黑，单衣革带。嵇熟视良久，乃吹火灭，曰：“耻与魑魅争光！”", "耻与魑魅争光"),
    ("隋炀帝无日不治宫室，浙人项陛进新宫图，大悦，即日召有司庀材鸠工，经岁而就，帑藏为之一空。帝幸之，大喜曰：“使真仙游其中，亦当自迷也。”因署之曰“迷楼”。", "迷楼"),
    ("形状、毛色俱如大鸡。天睛淑景，颔下吐绶，方一尺，金碧晃曜，花纹如蜀锦，中有一字，乃篆文“寿”字，阴晦则不吐。一名“寿字鸡”，一名“锦带功曹”。", "吐绶鸡"),
    ("有鸟来为之耘，春拔草根，秋啄芜秽，谓之鸟社。县官禁民不得妄害此鸟，犯则无赦。", "鸟社"),
    ("磁石引针。琥珀摄芥。", "物类相感"),
    ("芽茶得盐，不苦而甜。", "物类相感"),
    ("柳絮经宿，即为浮萍。", "物类相感"),
]

text = norm(open(SRC, encoding="utf-8").read())
fail = 0
for q, where in QUOTES:
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:22] + ("…" if len(q) > 22 else ""))
    fail += 0 if ok else 1

# 页面引文块整体核验：.q span 与 <p class="q"> 段
html = open(PAGE, encoding="utf-8").read()
blocks = [re.sub(r"<[^>]+>", "", q) for q in re.findall(r'<span class="q">(.*?)</span>', html, re.S)]
blocks += [re.sub(r"<[^>]+>", "", q) for q in re.findall(r'<p class="q"[^>]*>(.*?)</p>', html, re.S)]
print(f"\n页面引文块 {len(blocks)} 个（.q span + p.q）：")
for b in blocks:
    b = b.strip()
    if len(norm(b)) < 2:
        continue
    ok = norm(b) in text
    print(("PASS" if ok else "FAIL"), b[:26])
    fail += 0 if ok else 1

# 排版规则：禁止长划线；每行 · 至多 1 个
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i)
        fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40])
        fail += 1

# 硬性视觉：墨底、纸白、宋体族、无外部依赖无脚本
checks = [
    ("#191917" in html, "墨底 #191917"),
    ("#e8e4dc" in html, "纸白 #e8e4dc"),
    ("Songti SC" in html, "宋体族"),
    ("href=\"http" not in html and "@import" not in html and "<script" not in html.lower(), "无外部依赖无脚本"),
]
for ok, name in checks:
    print(("PASS" if ok else "FAIL"), "视觉:", name)
    fail += 0 if ok else 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
