# -*- coding: utf-8 -*-
"""从库内《熬波图》源文件切片生成引文清单，保证逐字照录。
每个引文给 (起始锚, 结束锚)，锚必须逐字出现在源文件中，切片含两端。"""
SRC = "../daizhige-simplified/史藏/政书/熬波图.txt"

SPECS = [
    ("dewang",   "浙之西华亭东百里", "煮海作盐其来尚矣"),
    ("tuji",     "命工绘为长卷", "垂于无穷也"),
    ("tuofu",    "敬齐慨然属椿而言曰", "而成其美云"),
    ("chushi",   "出示其父所图草卷", "如示诸掌"),
    ("guan",     "今观斯图真可谓得其情备而详矣", "备而详矣"),
    ("luokuan",  "旹元统甲戌", "陈椿志"),
    ("tiyao_sf", "此书乃元统中", "后系以诗"),
    ("tiyao_ly", "亦楼璹耕织圗", "之流亚也"),
    ("tiyao_sm", "然作是圗者", "不知为谁"),
    ("tiyao_qt", "惟原缺五图", "不可复补"),
    ("zaoshuo",  "并海立官舍", "私鬻官有刑"),
    ("che12",    "谁家少妇急工程", "泥两脚"),
    ("tan20_j",  "夏日苦热赤日行天", "无敢闲惰"),
    ("tan20_s",  "草间终日眠婴孩", "馌妇从西来"),
    ("lian_a",   "管莲之法采石莲", "用四等卤分浸四处"),
    ("lian_b",   "后用一竹管盛此四等所浸莲子", "以别卤咸淡之等"),
    ("lian_d2",  "三分卤浸一分水", "三分卤浸一分水"),
    ("lian_d3",  "一半水一半卤", "一半水一半卤"),
    ("lian_d4",  "一分卤浸二分水", "一分卤浸二分水"),
    ("huixue",   "灰如命脉卤如血", "相流连"),
    ("chai_j1",  "春首柴苗方出", "谓之看青"),
    ("chai_j2",  "毎盐一引用柴百束", "用柴倍其数"),
    ("chai_j3",  "浙西为有官荡", "减五两"),
    ("chai_s",   "有钱可买邻塲柴", "守盐哭"),
    ("pan_j",    "浙东以竹编", "各随其宜"),
    ("pan_s",    "洪炉一鼓焰掀天", "九肋鼈"),
    ("jian_s",   "炎炎火窖去地三尺许", "流汗雨"),
    ("liao_s",   "人面如灰汗如血", "不得歇"),
    ("xue_s",    "正愁天上多苦雾", "有醎雪"),
    ("hun_s",    "死灰不复燃", "今日冷如水"),
    ("yun_s",    "散盐如积雪", "数百堆"),
    ("wuche",    "空车晚归去", "寒鸦"),
    ("jianfu",   "却恐风来一扫间", "扳担泣"),
    ("biancang", "多者万引", "五七千引"),
]

book = open(SRC, encoding="utf-8").read()

def slice_between(start, end):
    i = book.find(start)
    assert i >= 0, f"起始锚未找到: {start}"
    j = book.find(end, i)
    assert j >= 0, f"结束锚未找到: {end}"
    return book[i:j + len(end)]

out = []
for qid, a, b in SPECS:
    s = slice_between(a, b)
    out.append((qid, s))
    print(f"{qid}\t{s}")

with open("quotes_aobotu_slices.txt", "w", encoding="utf-8") as f:
    for qid, s in out:
        f.write(f"{qid}\t{s}\n")
print(f"\n{len(SPECS)} 条切片完成 → quotes_aobotu_slices.txt")
