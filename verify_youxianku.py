#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_youxianku.py — 游仙窟导读页核验
用法: python3 verify_youxianku.py
库根: /home/robertsong/workspace/claude/daizhige-simplified
"""
import re, sys
from html.parser import HTMLParser

LIB = "/home/robertsong/workspace/claude/daizhige-simplified"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/youxian-ku.html"

SOURCES = {
    "main": LIB + "/子藏/笔记/游仙窟.txt",
    "水经注": LIB + "/史藏/地理/水经注.txt",
    "旧唐书": LIB + "/史藏/正史/旧唐书.txt",
    "新唐书": LIB + "/史藏/正史/新唐书.txt",
    "日本访书志": LIB + "/史藏/目录/日本访书志.txt",
    "思无邪小记": LIB + "/子藏/笔记/思无邪小记.txt",
}

QUOTES = {
"q1": ("main","若夫积石山者，在乎金城西南，河所经也。《书》云：“导河积石，至于龙门。”即此山是也。"),
"q2": ("main","古老相传云：“此是神仙窟也；人踪罕及，鸟路才通，每有香果琼枝，天衣锡钵，自然浮出，不知从何而至。”"),
"q3": ("main","承闻此处有神仙之窟宅，故来祗候。山川阻隔，疲顿异常，欲投娘子，片时停歇；赐惠交情，幸垂听许！"),
"q4": ("main","儿家堂舍贱陋，供给单疏，只恐不堪，终无吝惜。"),
"q5": ("main","自隐多姿则，欺他独自眠。故故将纤手，时时弄小弦。"),
"q6": ("main","面非他舍面，心是自家心；何处关天事，辛苦漫追寻！"),
"q7": ("main","敛笑偷残靥，含羞露半唇，一眉犹叵耐，双眼定伤人。"),
"q8": ("main","好是他家好，人非着意人，何须漫相弄，几许费精神！"),
"q9": ("main","无情明月，故故临窗；多事春风，时时动帐。愁人对此，将何自堪！"),
"q10": ("main","向来剧戏相弄，真成欲逼人。"),
"q11": ("main","向见称扬，谓言虚假，谁知对面，却是神仙。此是神仙窟也！"),
"q12": ("main","向见诗篇，谓言凡俗，今逢玉貌，更胜文章。此是文章窟也！"),
"q13": ("main","儿是清河崔公之末孙，适弘农杨府君之长子。即成大礼，随父住于河西。蜀生狡猾，屡侵边境，兄及夫主，弃笔从戎，身死寇场，茕魂莫返。儿年十七，死守一夫；嫂年十九，誓不再醮。"),
"q14": ("main","前被宾贡，已入甲科；后属搜扬，又蒙高第。奉敕授关内道小县尉，见宛河源道行军总管记室。"),
"q15": ("main","娘子既是主人母，少府须作主人公。"),
"q16": ("main","只恐张郎不能禁此事。"),
"q17": ("main","关关雎鸠，在河之洲。窈窕淑女，君子好仇。"),
"q18": ("main","折薪如之何？匪斧不克。娶妻如之何？匪媒不得。"),
"q19": ("main","女也不爽，士二其行。士也罔极，二三其德。"),
"q20": ("main","张郎心专，赋诗大有道理。俗谚曰：‘心欲专，凿石穿。’"),
"q21": ("main","下官不能赌酒，共娘子赌宿。"),
"q22": ("main","十娘输筹，则共下官卧一宿；下官输筹，则共十娘卧一宿。"),
"q23": ("main","汉骑驴则胡步行，胡步行则汉骑驴，总悉输他便点。"),
"q24": ("main","遮三不得一，觅两都卢失。"),
"q25": ("main","但问意如何，相知不在枣。"),
"q26": ("main","儿今正意密，不忍即分梨。"),
"q27": ("main","忽遇深恩，一生有杏。"),
"q28": ("main","当此之时，谁能忍柰！"),
"q29": ("main","自怜胶漆重，相思意不穷。可惜尖头物，终日在皮中。"),
"q30": ("main","数捺皮应缓，频磨快转多。渠今拔出后，空鞘欲如何！"),
"q31": ("main","旧来心肚热，无端强熨他。即今形势冷，谁肯重相磨！"),
"q32": ("main","摧毛任便点，爱色转须磨。所以研难竟，良由水太多。"),
"q33": ("main","眼多本自令渠爱，口少由来每被侵；无事风声彻他耳，教人气满自填心。"),
"q34": ("main","不是百兽率舞，乃是凤凰来仪。"),
"q35": ("main","不辞歌者苦，但伤知音稀。"),
"q36": ("main","问李树：如何意不同，应来主手里，翻入客怀中？"),
"q37": ("main","问蜂子：蜂子太无情，飞来蹈人面，欲似意相轻？"),
"q38": ("main","向来调谑，无处不佳；时既曛黄，且还房室。庶张郎共娘子安置。"),
"q39": ("main","少府谓言儿是九泉下人，明日在外谈道儿一钱不值。"),
"q40": ("main","谁知可憎病鹊，夜半惊人；薄媚狂鸡，三更唱晓。"),
"q41": ("main","所恨别易会难，去留乖隔，王事有限，不敢稽停。每一寻思，痛深骨髓。"),
"q42": ("main","凤锦行须赠，龙梭久绝声。自恨无机杼，何日见文成？"),
"q43": ("main","下官瞿然，破愁成笑。"),
"q44": ("main","好去。若因行李，时复相过。"),
"q45": ("main","他道愁胜死，儿言死胜愁。愁来百处痛，死去一时休。"),
"q46": ("main","可行至二三里，回头看数人，犹在旧处立。"),
"q47": ("main","望神仙兮不可见，普天地兮知余心；思神仙兮不可得，觅十娘兮断知闻"),
"q48": ("main","桂心已下，或脱银钗，落金钏，解帛子，施罗巾，皆白送张郎"),
"q49": ("main","别时终是别，春心不值春。羞见孤鸾影，悲看一骑尘。"),
"q50": ("main","两剑俄分匣，双凫忽异林。"),
"q51": ("main","若使人心密，莫惜马蹄穿。"),
"q54": ("main","此时经一去，谁知隔几年！双凫伤别绪，独鹤惨离弦。怨起移酲后，愁生落醉前。若使人心密，莫惜马蹄穿。"),
"q52": ("main","天涯地角知何处，玉体红颜难再遇！但令翅羽为人生，会些高飞共君去。"),
"q53": ("main","卞和山未斫，羊雍地不耕。自怜无玉子，何日见琼英？"),
"qs1": ("main","奉使河源"),
"qs2": ("main","十娘小名琼英"),
"qg1": ("main","聊将代左腕，长夜枕渠头。"),
"qg2": ("main","若道人心变，从渠照胆看。"),
"qg3": ("main","聊以当儿心，竟日承君足。"),
"qg4": ("main","希君掌中握，勿使恩情歇！"),
"qg5": ("main","裁为八幅被，时复一相思。"),
"qg6": ("main","莫言钗意小，可以挂渠冠。"),
"x1": ("新唐书","新罗、日本使至，必出金宝购其文。"),
"x2": ("旧唐书","张子之文如青钱，万简万中，未闻退时。"),
"x3": ("旧唐书","国有此人而不用，汉无能为也。"),
"x4": ("新唐书","浮艳少理致，其论著率诋诮芜猥，然大行一时，晚进莫不传记。"),
"x5": ("日本访书志","此书中土著录家皆未之及，首题“宁州襄乐县尉张文成作”。"),
"x6": ("日本访书志","嵯峨天皇书卷之中，撰得《游仙窟》，召纪传儒者，欲传受也。诸家皆无传，学士伊时深愁叹。"),
"x7": ("日本访书志","我幼少自吝受此书，年阑倦事，仅所学诵而已。"),
"x8": ("日本访书志","男女姓氏并同《会真记》，而情事稍疏，以骈丽之辞，写猥亵之状"),
"x9": ("水经注","彼羌目鬼曰唐述，复因名之为唐述山，指其堂密之居，谓之唐述窟。"),
"x10": ("水经注","河峡崖傍有二窟：一曰唐述窟，高四十丈。"),
"x11": ("水经注","时亮窟，高百丈，广二十丈，深三十丈，藏古书五卷"),
"x12": ("思无邪小记","此书原本藏日本图书馆，今尚存。"),
"x13": ("思无邪小记","《西厢记》、《红楼梦》、《绿野仙踪》、《游仙窟》，此中上也。"),
"x14": ("思无邪小记","序谓此书系自日本抄传者，内有张文成崔五嫂赠答之诗数章。"),
"x15": ("日本访书志","此书日本别有刻本，分为五卷"),
"x16": ("日本访书志","文保三年四月十四日授申圆禅庵序毕。文章生英房。"),
}

def norm(s):
    return "".join(ch for ch in s if 0x3400 <= ord(ch) <= 0x9FFF or 0x20000 <= ord(ch) <= 0x3FFFF)

LIBNORM = {}
def libnorm(key):
    if key not in LIBNORM:
        LIBNORM[key] = norm(open(SOURCES[key], encoding="utf-8").read())
    return LIBNORM[key]

class QCollector(HTMLParser):
    """收集 class 含 q 的元素全文与 data-src；同时剥掉 .who/.cap/.era/.src 叶子。"""
    STRIP = {"who", "cap", "era", "src", "hom", "arrow"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (class set, data-src, buf list)
        self.quote_blocks = []   # (text, data_src)
        self.all_text = []       # 页面可见文本（分块，用于「」反扫与红线）
        self.lines = [[]]        # 伪行：块级元素一行
    BLOCK = {"p","div","section","header","footer","h1","h2","h3","h4","span","b","em","td","li"}
    VOID = {"meta","link","br","hr","img","input","wbr","source"}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        if tag in self.VOID:
            if tag == "br":
                self.lines.append([])
            return
        entry = (cls, a.get("data-src"), [])
        self.stack.append(entry)
        if tag in self.BLOCK:
            self.lines.append([])
    def handle_endtag(self, tag):
        entry = self.stack.pop()
        cls, src, buf = entry
        if "q" in cls:
            text = "".join(buf)
            self.quote_blocks.append((text, src))
        if tag in self.BLOCK:
            self.lines.append([])
    def handle_data(self, data):
        # 回溯最近的 q 祖先
        qsrc = None
        for cls, src, buf in reversed(self.stack):
            if "q" in cls:
                strip_hit = any(s in cls for s in self.STRIP)
                if not strip_hit:
                    buf.append(data)
                qsrc = src
                break
            elif any(s in cls for s in self.STRIP):
                qsrc = "STRIPPED"
                break
        self.lines[-1].append(data)

def main():
    html = open(PAGE, encoding="utf-8").read()
    errs, warns = [], []
    ok = 0

    # ---------- 1. 库内基线：77 段引文逐字节唯一 ----------
    for qid, (src, qt) in QUOTES.items():
        raw = open(SOURCES[src], encoding="utf-8").read()
        n = raw.count(qt)
        if n != 1:
            errs.append(f"[基线] {qid} 在 {src} 命中 {n} 次")
    print(f"基线：{len(QUOTES)} 段引文库内唯一性 … {'OK' if not errs else 'FAIL'}")

    # ---------- 2. 页面 .q 全量对源 ----------
    c = QCollector(); c.feed(html)
    if len(c.stack) != 0:
        errs.append(f"[结构] 标签未配平，栈剩 {len(c.stack)}")
    pageq = []
    for text, src in c.quote_blocks:
        nq = norm(text)
        if not nq:
            continue
        pageq.append((nq, src))
    srcname = {v.split("/")[-1].replace(".txt",""): k for k, v in SOURCES.items()}
    for i, (nq, src) in enumerate(pageq):
        if src == "STRIPPED":
            continue
        key = "main"
        if src:
            key = src if src in SOURCES else None
            if key is None:
                errs.append(f"[.q {i}] data-src 未知：{src}")
                continue
        hay = libnorm(key)
        if nq not in hay:
            errs.append(f"[.q {i}] 不在 {key}：{nq[:30]}…")
        else:
            ok += 1
    print(f"页面 .q：{len(pageq)} 块逐字对源 … {'OK' if not [e for e in errs if e.startswith('[.q')] else 'FAIL'}")

    # ---------- 3. 「」反扫（非 .q 的直引内容） ----------
    text_all = "\n".join("".join(l) for l in c.lines)
    qnorms = [nq for nq, _ in pageq]
    quoted = re.findall(r"「([^「」]+)」", text_all)
    bad = 0
    for seg in quoted:
        ns = norm(seg)
        if not ns:
            continue
        if ns in qnorms or ns in qnorms and True:
            continue
        if any(ns in libnorm(k) for k in SOURCES):
            ok += 1
        else:
            errs.append(f"[「」] 库内未命中：{seg}")
            bad += 1
    print(f"「」反扫：{len(quoted)} 处 … {'OK' if not bad else 'FAIL'}")

    # ---------- 4. 红线 ----------
    if "—" in html or "–" in html:
        errs.append("[红线] 页面含长划线 —/–")
    for ln in c.lines:
        line = "".join(ln)
        if line.count("·") > 1:
            errs.append(f"[红线] 一行超过一个·：{line.strip()[:40]}")
    print("红线：长划线 / 每行·≤1 …", "OK" if not [e for e in errs if e.startswith("[红线]")] else "FAIL")

    # ---------- 5. 机数：库本口径 ----------
    main_raw = open(SOURCES["main"], encoding="utf-8").read()
    m = {
        "总字符": len(main_raw),
        "去空白": len(re.sub(r"\s", "", main_raw)),
        "咏曰": main_raw.count("咏曰"),
        "答咏": main_raw.count("答咏"),
        "报诗": main_raw.count("报诗"),
        "报咏": main_raw.count("报咏"),
        "笑": main_raw.count("笑"),
        "十娘": main_raw.count("十娘"),
        "下官": main_raw.count("下官"),
        "五嫂": main_raw.count("五嫂"),
        "张郎": main_raw.count("张郎"),
        "酒巡": main_raw.count("酒巡"),
        "缺字□": main_raw.count("□"),
        "半角逗号": main_raw.count(","),
    }
    expect = {"总字符": 11396, "去空白": 10719, "咏曰": 53, "答咏": 1, "报诗": 2, "报咏": 2,
              "笑": 32, "十娘": 110, "下官": 70, "五嫂": 68, "张郎": 15, "酒巡": 2,
              "缺字□": 8, "半角逗号": 2}
    for k, v in expect.items():
        if m[k] != v:
            errs.append(f"[机数] 库本 {k}={m[k]} 预期 {v}")
    # 页面显示值与机数一致
    page_checks = [
        ("10,719", m["去空白"]), ("笑 32", m["笑"]), ("酒巡 2", m["酒巡"]),
        ("十娘 110", m["十娘"]), ("下官 70", m["下官"]), ("五嫂 68", m["五嫂"]),
        ("张郎 15", m["张郎"]),
    ]
    for token, val in page_checks:
        if token.replace(",", "") not in text_all.replace(",", ""):
            errs.append(f"[机数] 页面缺少 {token}")
    if "58" not in text_all or "53＋答咏 1＋报诗曰 2＋报咏 2" not in text_all:
        errs.append("[机数] 页面诗回合算式缺失或不符")
    if m["咏曰"] + m["答咏"] + m["报诗"] + m["报咏"] != 58:
        errs.append(f"[机数] 诗回合复算 {m['咏曰']}+{m['答咏']}+{m['报诗']}+{m['报咏']} != 58")
    print(f"机数：库本口径 {len(m)} 项 + 页面回填 … {'OK' if not [e for e in errs if e.startswith('[机数]')] else 'FAIL'}")

    # ---------- 6. 收尾 ----------
    print(f"\n命中计：.q/「」通过 {ok} 项")
    if errs:
        print(f"\nFAIL：{len(errs)} 项")
        for e in errs:
            print("  ✗", e)
        sys.exit(1)
    print("\nALL PASS")

if __name__ == "__main__":
    main()
