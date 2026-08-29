#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_qingming.py — 名公书判清明集导读页核验
引文与库内文件逐字比对（去标点+去空白归一）+ 排版规则 + 计数断言
"""
import re, sys, unicodedata

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/qingming-ji.html"
SRC  = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/职官/名公书判清明集.txt"

SKIP = set('，。：；、！？「」『』（）〔〕《》〈〉·…　')

def norm(s: str) -> str:
    s = re.sub(r'<[^>]+>', '', s)
    return ''.join(ch for ch in s if ch not in SKIP and not ch.isspace())

fails = []
def check(cond, label):
    print(('PASS' if cond else 'FAIL'), label)
    if not cond:
        fails.append(label)

page = open(PAGE, encoding='utf-8').read()
src  = open(SRC, encoding='utf-8').read()
npage, nsrc = norm(page), norm(src)

# ---------- 1. 引文核验（页面引文必须是库内原文子串） ----------
QUOTES = [
 "律己以廉，抚民以仁，存心以公，莅事以勤。",
 "何谓十害？曰断狱不公，狱者，民之大命，岂可少有私曲。听讼不审，讼有实有虚，听之不审，则实者反虚，虚者反实矣，其可苟哉！",
 "在法：父母已亡，儿女分产，女合得男之半。遗腹之男，亦男也，周丙身后财产合作三分，遗腹子得二分，细乙娘得一分，如此分析，方合法意。",
 "天下岂有女婿中分妻家财产之理哉？",
 "死者可慰舐犊之念，生者可远兼并之嫌，纵有健讼，奚所容喙。",
 "能欺于人，而不能欺于天。",
 "彼其生尚不能自给其口腹，而衣食于人，其顽不灵，亦可想见，焉有既死之后，反能为生民捍大患，御大灾者哉！盖万万无是理。",
 "焚之庙中，使此等淫昏之鬼有所愧惧，榜之庙前，使世间蠢愚之人有所觉悟。",
 "两舟既散之后，赤龙舟却为李辛一、杨童所激，遂固舟求鬬，而舟道相遇，小人一朝之忿忘其身，刃石交下，赤龙舟偶以人多，舟覆，死者一十三人。",
 "张万二所伤两人，决脊杖二十，刺配三千里岭南恶州军，拘锁土牢，月具存亡申；余万一所伤一人，决脊二十，刺配三千里，拘锁土牢，永不放还。",
 "法令所载，昭如日星。奸民无状，輙敢冒犯。",
 "决脊杖十五，配一千里，以为霸渡害民者之戒。",
 "王震自号曰时运先生，亦须稍识义理。",
 "曩余校录永乐大典，于清字编见有清明集二卷者，皆宋以来名公书判，其原情定罚，比物引类，可谓曲尽矣。",
 "笥藏中秘，世所希遘覩也。吾师凤盘先生校永乐大典，自群集中表出之。",
 "自真文忠公申儆官吏，讫于惩恶",
 "税出于田，一岁一收，可使一岁至再税乎。",
]
src_n = norm(src)
for i, q in enumerate(QUOTES, 1):
    nq = norm(q)
    in_src = nq in src_n
    in_page = nq in npage
    check(in_src, f"引{i:02d} 库内有原文: {q[:18]}…")
    check(in_page, f"引{i:02d} 页面已收录: {q[:18]}…")

# ---------- 2. 排版规则 ----------
check('—' not in page, "无长划线 —")
check('–' not in page, "无半字线 –")
bad_dots = [ (i, l) for i, l in enumerate(page.splitlines(), 1) if l.count('·') > 1 ]
check(not bad_dots, f"每行·最多1个 (违例 {len(bad_dots)} 行)")
check('src="http' not in page and 'href="http' not in page and '@import' not in page and '<link' not in page, "无外部资源引用")

# ---------- 3. 实测计数断言 ----------
lines = src.splitlines()
body = "\n".join(lines[856:4129])          # 正文区：卷之一 至 附录一 之前
check(len(src) == 302839, f"库内本总字数 302839 (实测 {len(src)})")
check(len(body) == 257045, f"正文字数 257045 (实测 {len(body)})")

# 卷次结构：正文十四卷
vol_marks = [l for l in lines[856:4129] if re.fullmatch(r'名公书判清明集卷之[一二三四五六七八九十]+', l.strip())]
check(len(vol_marks) == 14, f"正文十四卷 (实测 {len(vol_marks)})")
gates = ['官吏门','赋役门','文事门','户婚门','人伦门','人品门','惩恶门']
check(all(g in body for g in gates), "七门名目俱在正文")

# 署名榜计数（页面显示值）
expect = {"胡石壁":76,"蔡久轩":71,"翁浩堂":28,"吴雨岩":25,"范西堂":24,
          "刘后村":22,"叶岩峰":14,"宋自牧":12,"方秋崖":9,"真西山":8}
for name, c in expect.items():
    real = body.count(name)
    check(real == c, f"署名计数 {name}={c} (实测 {real})")

# 名氏录：二十八家，起晦庵，讫臞轩
roster = [l.strip() for l in lines[4133:4162] if l.strip()]
check(len(roster) == 28, f"名氏录二十八家 (实测 {len(roster)})")
check(roster[0].startswith('晦庵') and roster[-1].startswith('臞轩'), "名氏录起于晦庵，讫于臞轩")
check(any('宋氏慈' in l for l in roster), "宋慈在名氏录")

# 析类目录合计：二十二类 117 条
bill_text = "".join(lines[4166:4189])
CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def cn2int(s):
    if s == '十': return 10
    if '十' in s:
        a, _, b = s.partition('十')
        return (CN.get(a,1))*10 + (CN.get(b,0) if b else 0)
    return CN[s]
total = sum(cn2int(s) for s in re.findall(r'([一二三四五六七八九十]+)条', bill_text))
nums = re.findall(r'([一二三四五六七八九十]+)条', bill_text)
check(len(nums) == 22, f"户婚门析类二十二类 (实测 {len(nums)})")
check(total == 117, f"析类合计 117 条 (实测 {total})")

# 页面计数呈现与实测一致
for c, cn in [(117,'一百一十七条'), (22,'二十二类'), (14,'十四卷'), (28,'二十八家')]:
    check(cn in page, f"页面载有 {cn}")
check('302,839' in page, "页面载有总字数")

print()
if fails:
    print(f"共 {len(fails)} 项未过："); [print(' -', f) for f in fails]; sys.exit(1)
print("全部通过")
