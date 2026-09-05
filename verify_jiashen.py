#!/usr/bin/env python3
"""核验 jiashen-chuanxinlu.html 所有引文与库内原文逐字一致(去标点+归一)"""
import re, sys, unicodedata

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/甲申传信录.txt"
HTML = "/home/robertsong/workspace/claude/daizhige-daodu/jiashen-chuanxinlu.html"

VARIANT = {"沈": "沉", "偪": "逼", "彊": "强", "壻": "婿", "歎": "叹", "汏": "汰"}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VARIANT.get(c, c) for c in s)
    return re.sub(r"[^一-鿿㐀-䶿\U00020000-\U0003ffff]", "", s)

lib = norm(open(LIB, encoding="utf-8").read())
html = open(HTML, encoding="utf-8").read()

# ── 1. 页面 <quote> 块主体:取 .who 之后到 .src 之前的文本 ──
quotes = re.findall(r'<span class="who">[^<]*</span>\s*(.*?)\s*<span class="src">', html, re.S)

# ── 2. src 标注与正文中的短语引用 ──
snippets = [
    "数癸未仲秋入都，迄甲申之变，其所见闻者，具述其略，至于政治纪纲，职在太史，非野陋之所及。",
    "上曰：『卿言可致数十万，何乃云无及』？永固曰：『暇日人易集，今事急，人心尽乱，虽一卒亦难致也』。",
    "邦曜曰：『如此，我亦从君行』。元璐曰：『诚如是，再加一盏，与君共之』。更与邦曜对酌三盏。",
    "伟先悬右，耿悬左。耿曰：『虽颠沛，不可失序』。乃解绳重整，正左右而死。",
    "自成谓诸将曰：『何不助孤作好皇帝』？制将军曰：『皇帝之权归汝！拷掠之威归我，无烦言也』！",
    "宗敏夹讯藻德曰：『若居首辅，何以致乱』？藻德曰：『本是书生，不谙政事，兼之先帝无道，遂至于此』。宗敏曰：『汝以书生擢状元，不三年为首辅，崇祯有何负汝，诋为无道』！呼左右掌其嘴数十。",
    "凡六昼夜，夹脑至裂而毙",
    "今必从容研质，真伪自分。草草毕事，诚恐廷臣曰假，而百姓疑；京师曰假，而四方疑；一日曰假，而后世疑。众口难妨，信史可畏也。",
    "世受国恩，义不受辱",
    "明日此时，便非凡人",
    "此真太子，愿无伤",
    "若速还我太子",
    "刑部钱先生至，可献茶",
    "孤将与分治江南，不忍有弑君之名",
    "此假太子也",
    "芝兰当户，不得不锄",
    "吾会藏书楼又多一瑰宝",
    "一品一云，九品为九云",
    "其志在于淘物",
]

checks = [(q, "quote块") for q in quotes] + [(s, "短语") for s in snippets]

fail = 0
for text, kind in checks:
    t = norm(text)
    if not t:
        continue
    if t in lib:
        print(f"PASS {kind}: {text[:18]}... ({len(t)}字)")
    else:
        # 定位最长可匹配前缀帮助排查
        lo, hi = 0, len(t)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if t[:mid] in lib:
                lo = mid
            else:
                hi = mid - 1
        print(f"FAIL {kind}: {text[:30]}...")
        print(f"      连续匹配至第{lo}字: ...{t[max(0,lo-8):lo]}【{t[lo:lo+10]}】...")
        fail += 1

print(f"\n共 {len(checks)} 项, 失败 {fail}")
sys.exit(1 if fail else 0)
