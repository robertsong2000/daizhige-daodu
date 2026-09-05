#!/usr/bin/env python3
"""核验 bingta-yiyan.html 引文与殆知阁库内《病榻遗言》逐字一致，并查排版规则。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/病榻遗言.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/bingta-yiyan.html"

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

# 手写引文底稿（封面开卷、叙述散句、artifact 卡内引文）
MANUAL = [
    ("我祖宗二百年天下以至今日，国有长君，社稷之福，争奈东宫小里？", "封面 开卷第一声"),
    ("看吾疮尚未落痂也", "幕一 散句"),
    ("甚事不是内官坏了，先生你怎知道？", "幕一 散句"),
    ("连语数次，一语一顿足一握臣手", "幕一 散句"),
    ("遽不能起，有负先皇付托。东宫幼小，朕今付之卿等三臣同司礼监协心辅佐，遵守祖制，保固皇图", "幕一 揭帖"),
    ("拱读既恸", "幕一 散句"),
    ("事势必不可为", "幕一 散句"),
    ("而居正虽哭，乃面有喜色，扬扬得意", "幕一 揭帖"),
    ("不见张公意态耶？是诚何心？国家之祸，不知所终矣。", "幕一 揭帖"),
    ("着冯保掌司礼监印", "幕一 页脚行"),
    ("乃遗诏事宜耳", "幕一 散句"),
    ("待看，待看", "幕一 散句"),
    ("朕不豫，皇帝你做，一应礼仪自有该部题请而行，你要依三阁臣并司礼监辅导。进学修德，用贤使能，无事怠荒，保守帝业。", "对读卡 遗诏其二"),
    ("人心大骇，以为宦官安得受顾命", "对读卡"),
    ("然不知二遗诏者，皆居正所为", "对读卡"),
    ("若拨乱世，反之正", "幕二 散句"),
    ("堂堂之阵，正正之旗", "幕二 散句"),
    ("世所谓妖精者，张子其人也", "幕二 散句"),
    ("指鹿为马，无敢不言马者", "幕二 散句"),
    ("宁吾受人害", "幕二 散句"),
    ("吾有七子，当一日而死", "幕二 散句"),
    ("知道了，遵祖制", "幕二 散句"),
    ("今有大学士高拱专权擅政，把朝廷威福都强夺自专，通不许皇帝主管，不知他要何为？我母子三人惊惧不宁。高拱便著回籍闲住，不许停留。", "幕二 懿旨揭帖"),
    ("此旨词语通顺无滞，是谁为之", "幕二 页脚行"),
    ("觅一骡车载以行，道路之人见之多流涕者", "幕二 散句"),
    ("闻予去大惊，因呕血三日而死", "幕二 散句"),
    ("俗言又做师婆，又做鬼，吹笛捏眼，打鼓弄琵琶，三起三落任意搏，播弄君父于掌中乃至此也。", "幕二 揭帖"),
    ("此自有作用可借，以诛高氏灭口。", "幕三 密语揭帖"),
    ("以二剑一刀置王大臣怀袖中", "幕三 器物注"),
    ("汝只说是高阁老使汝来刺朝廷，我当与汝官做，永享富贵", "幕三 散句"),
    ("赏银二十两", "幕三 散句"),
    ("飞去河南新郑县拿高家人", "幕三 散句"),
    ("今厂中称主使者即是高老，万代恶名必归于公，将何自解？", "幕三 散句"),
    ("我为此事忧不如死", "幕三 散句"),
    ("意不回持", "幕三 散句"),
    ("才发君心，天已知，何须问我决嫌疑？愿子改图，从孝弟不愁，家室不相宜。", "签文卡"),
    ("所谋不善，何必祷神？宜决于心，改过自新。", "签文卡 解曰"),
    ("是你使我来，你岂不知，却又问我", "幕三 散句"),
    ("是你教我说来，我何曾认得高阁老", "幕三 散句"),
    ("那高胡子是正直忠臣，受顾命的，谁不知道那张蛮子夺他首相，故要杀他灭口。", "幕三 内廷揭帖"),
    ("年七十余", "幕三 页脚行"),
    ("然已中毒，哑不能言。至二十一日，三法司同审，更不问所以，王大臣亦无一言，当将处决了事。", "哑口段"),
    ("高老事几乎不免，我为他忧愁，昼夜不能寝食，吐血若干，须白了若干，今才救得下也。", "幕三 事后表演揭帖"),
    ("初时人亦惑之", "幕三 页脚行"),
    ("试待看之，必有信然者矣", "幕三 页脚行"),
    ("欲要宠则要宠，欲害人则害人", "对读盘后盘"),
]
for q, where in MANUAL:
    check(q, where)

# 自动回验：页面所有揭帖/开卷/签文 blockquote（剥去脚注后比对）
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r"<blockquote>(.*?)</blockquote>", html, flags=re.S)
print(f"\n页面 blockquote 引文块 {len(blocks)} 个：")
for b in blocks:
    b = re.sub(r"<footer[^>]*>.*?</footer>", "", b, flags=re.S)
    b = re.sub(r"<cite[^>]*>.*?</cite>", "", b, flags=re.S)
    body = re.sub(r"<[^>]+>", "", b).strip()
    body = re.sub(r"\s+", "", body).strip("「」")
    check(body, "页面块")

# 字数口径：库内全文汉字数
han = len(norm(raw))
print(f"\n库内汉字实测：{han}")
ok = han == 16080
print(("PASS" if ok else "FAIL"), "页面声称 16,080 汉字")
fail += 0 if ok else 1

# 荆人/居正分篇统计口径
i1, i2, i3 = raw.find("●顾命纪事"), raw.find("●矛盾原由"), raw.find("●毒害深谋")
chs = {"顾命": raw[i1:i2], "矛盾": raw[i2:i3], "毒害": raw[i3:]}
stats = {k: (v.count("荆人"), v.count("居正")) for k, v in chs.items()}
print("分篇统计（荆人，居正）：", stats)
for ok_, label in [
    (stats["顾命"][0] == 0, "荆人 0 于顾命篇"),
    (stats["矛盾"][0] == 81, "荆人 81 于矛盾篇"),
    (stats["毒害"][1] == 23, "居正 23 于毒害篇"),
]:
    print(("PASS" if ok_ else "FAIL"), label)
    fail += 0 if ok_ else 1

# 排版规则：无长划线；每行·至多 1 个；无外部资源依赖
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1
for pat in ["<script src", "<link ", "@import", "url("]:
    if pat in html:
        print("FAIL 外部依赖：", pat); fail += 1

for k in ["殆知阁", "核验", "局限", "mulu.html", "daizhigev20", "16,080"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
