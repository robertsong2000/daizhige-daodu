#!/usr/bin/env python3
"""核验 ningguta-tuxiangzhi.html 引文与库内《宁古塔地方乡土志》逐字一致（去标点+异体归一，双向）。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/宁古塔地方乡土志.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/ningguta-tuxiangzhi.html"

VAR = {"煖": "暖", "鎗": "枪"}

def norm(s):
    s = re.sub(r"[^一-鿿]", "", s)
    return "".join(VAR.get(c, c) for c in s)

text = norm(open(SRC, encoding="utf-8").read())

QUOTES = [
    ("将前项采访志书事迹，饬造清册二本，迅速送省施行。", "卷首 咨"),
    ("在吉林省城东相距八百里，现筑土墙，高一丈二尺，周围五百八十五丈，东西南各一门。", "城池"),
    ("相距城南有虎儿哈河，今俗称牡丹江，康熙五年由旧城迁此，将军巴海监造。", "城池"),
    ("现有领催七十二名，前锋四十名，兵一千二百零八名。", "仕宦"),
    ("征收烧锅票课钱一万吊，按年分为春、秋二季收齐，备抵兵饷。", "田赋"),
    ("内有石佛一尊，高两丈余，后石首坠地，有石匠见之欲凿为碾，甫举锤，头忽痛，遂置之。是夕吴汉槎，钱德维等同感异梦，于是举石首凑法像，冶铁固之，故址建刹，至今重修，香火甚盛。", "古迹 石佛寺"),
    ("其形欲倒，历经工匠置之不动。", "古迹 石佛寺"),
    ("有红云一朵，降雨数点，闻有沥沥之声，众皆出视，其亭自正。", "古迹 石佛寺"),
    ("南至嘎哈里河，距城三百余里珲春界，北至阿穆阿兰河，距城三百余里三姓界，西至都林河，距城二百一十里吉林界，东至瑚布图卡伦，距城五百余里，东北至乌札库卡伦，距城八百余里；其迤东皆系俄界。", "疆域"),
    ("石面平如镜，洞穴大小不可数，或圆、或方、或六隅八隅，如井、如盆、如池、如口、如盂。", "古迹 德林石"),
    ("中有水泉澄然凝碧，夏无蚊虻，马鹿群嬉。", "古迹 德林石"),
    ("平甸车马行其上如闻空洞之声，石块或损，便有水从罅隙出，探之深不可测。", "古迹 德林石"),
    ("每至仲夏，日初出时，风平浪静，有巨鱼涌出波心，高约三丈，长十余丈，飞鸟不敢过其上，已午时始没。", "古迹 海眼"),
    ("湖水东注，水势汹溪，飞瀑蹑空，沸腾奔浪如雷吼，声闻数里，谓之响水。", "山川 吊水楼"),
    ("源出长白山，群流凑集至此，遂成巨浸，广五六里，长七十余里，湖中有三山。", "山川 镜泊湖"),
    ("相传为金时塞外之曲江。此泡向产莲花。", "山川 莲花泡"),
    ("此河出东珠，向年由吉林乌拉总管珠轩下派官往此捕打贡珠，并产达发哈鱼。", "山川 海兰河"),
    ("三丫五叶，背阳向阴。所来求找，椴树之下相寻。", "花之属 人参赞"),
    ("诸山皆有之。边外间有白质黑章者尤猛鸷，围中以激打枪手制之", "兽 虎"),
    ("国朝品官坐褥冬用皮，有定制，一品用狼，二品用獾，三品用貉，四品用山羊，五品以下用白羊皮，公、侯极品用虎豹皮。", "兽 狼"),
    ("近东北边者色黄，边外色紫黑，皮甚轻煖。打性人于雪天寻其迹而捕焉。", "兽 貂鼠"),
    ("宁古塔诸处有之。秋八月白海迎水入江，驱之不去、充积甚厚。土人竟有履鱼背而渡者，腹中子大如玉蜀黍，边地人取鱼炙干积之如粮。", "水族 大发哈鱼"),
    ("光绪十四年现查八旗户六千七百七十二户，披甲，闲散西丹男、妇等三万二千八百八十三口。", "户口"),
    ("民籍户一千七百五十三户，男、妇九千五百二十三名，口，官庄户八百九十五户，男，妇二千八百二十四名，口。", "户口"),
    ("东西南各一门", "城池（行内）"),
    ("现有领催七十二名，前锋四十名，兵一千二百零八名", "仕宦（行内）"),
]

fail = 0
print("== 页面引文清单 -> 库内文件 ==")
for q, tag in QUOTES:
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), f"[{tag}]", q[:30])
    fail += 0 if ok else 1

print("\n== 库内文件 -> 页面引文块（blockquote + .q 双向覆盖） ==")
html = open(PAGE, encoding="utf-8").read()
blocks = []
for m in re.finditer(r'<blockquote class="bq">(.*?)</blockquote>', html, re.S):
    body = re.sub(r'<span class="from">.*?</span>', "", m.group(1), flags=re.S)
    blocks.append(re.sub(r"<[^>]+>", "", body))
blocks.extend(re.sub(r"<[^>]+>", "", q) for q in re.findall(r'<span class="q">(.*?)</span>', html, re.S))
for b in blocks:
    b = b.strip()
    if len(norm(b)) < 4:
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

# 硬性视觉：墨底、纸白、宋体族、无外部资源
checks = [
    ("#191917" in html, "墨底 #191917"),
    ("#e8e4dc" in html, "纸白 #e8e4dc"),
    ("Songti SC" in html, "宋体族"),
    ("@import" not in html and "<link" not in html and 'url(http' not in html, "无外部字体样式"),
    ("<script src=" not in html and "<img" not in html and "src=\"http" not in html, "无外部脚本图片"),
]
for ok, name in checks:
    print(("PASS" if ok else "FAIL"), "视觉:", name)
    fail += 0 if ok else 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
