# -*- coding: utf-8 -*-
"""复辟录 导读页核验：引文双侧、反扫、红线、机数。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'fubi-lu.html'
LIB  = '../daizhige-simplified/史藏/志存记录/复辟录.txt'

lib = open(LIB, encoding='utf8').read()
page = open(PAGE, encoding='utf8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

NL, NP = norm(lib), norm(page)
fail = []

# ---------- 1. 页面 .q 收集（栈配平，VOID 跳过，q 祖先回溯） ----------
VOID = {'meta','link','br','hr','img','input','source','wbr','area','base','col','embed','track'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.qstack, self.cur, self.out = [], [], None, []
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        cls = dict(attrs).get('class') or ''
        qs = 'q' in cls.split()
        self.stack.append(tag)
        if self.cur is not None:
            self.qstack.append(self.cur)
        elif qs:
            self.cur = []          # 重置，防上个引文残留
            self.qstack.append(self.cur)
        elif self.qstack:
            self.cur = self.qstack[-1]
    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if self.qstack:
            ended = self.cur is self.qstack[-1]
            self.qstack.pop()
            if ended:
                self.out.append(''.join(self.cur))
                self.cur = self.qstack[-1] if self.qstack else None
    def handle_data(self, d):
        if self.cur is not None:
            self.cur.append(d)

qc = QC(); qc.feed(page)
collected = [norm(x) for x in qc.out if norm(x)]
print(f'[收集] .q 共 {len(qc.out)} 块，归一后非空 {len(collected)} 块')

QUOTES = [
 "太监兴安自内出，问曰：“若皆何官？”",
 "兴安以指作十字，谓病之笃不过是日耳。",
 "若皆朝廷大臣，耳目不能为社稷计，日日徒问安耳。",
 "我更一字，乃更建字为择字。",
 "待正月十七日早朝，请择元良一节难准。",
 "天下者，太祖、太宗之天下，传之于宣宗、陛下、宣宗之子、宣宗之孙，以祖父之天下传之于孙，此万古不易之常法。",
 "因姓氏众，字画多讹，至十六日晡时方完。",
 "十七日四鼓时，众集于朝，人人谨待上出，以期事济。",
 "顷之，南城呼噪震地，群臣失色。须臾，鸣钟鼓，上皇御极矣。",
 "于是朝野欢腾，以为复见太平，本遂不进。",
 "迎立之迹无实可验，乃曰：“谋而未成。”",
 "此社稷功也，虽然彬老矣，无能为也，盍图之徐元玉。",
 "太上皇帝昔者出狩，非以游畋，为赤子故耳。",
 "有贞乃升屋览，步乾象，亟下附靰等耳言：“时在今夕，不可失。”",
 "事成，社会稷之福；不成，家族之祸矣。归人不归鬼。",
 "夜四鼓，开长安门，纳兵近千人，宿卫官军惊愕不知所为。",
 "锁讫，有贞取钥投水窦，并靰等莫知之。",
 "数十人举撞城门，又令勇士逾垣入，与外兵合毁垣。垣坏门启，城中黯无灯火。",
 "烛下独出，问曰：“尔等何为？”众俯伏合声：“请陛下登位。”",
 "兵士惊惧不能举。有贞等助挽以前，掖上皇登辇，有贞等又自挽以行。",
 "时天色晦冥",
 "忽天色昭朗，星月辉光",
 "景皇帝闻钟鼓声，问左右云：“于谦耶？”左右对曰：“太上皇帝。”",
 "景皇帝曰：“哥哥做，好！”",
 "哥哥做，好！",
 "弟弟好矣，吃粥矣，事固无预弟弟，小人坏之耳。”诸臣默然。",
 "吃粥矣",
 "尔等何为？",
 "于谦耶？",
 "必须捏个异故，方显得吾辈功高。",
 "王文、于谦已遣人赍金牌敕符，取襄王世子去矣。",
 "所以诛戮者多非其罪。",
 "论法本当凌迟，从轻决了罢。",
 "这厮每图危宗社的情理，穷凶极恶，本当族灭，如今体上天好生之德，都从轻处治了。",
 "恁都察院便出榜，晓谕多人每知道。",
 "腾居南城，今既七年，心已忘天下",
 "当时赵太祖陈桥之变，史不称其谋反，尔等若助我至此，我职非尔为之而何？”众皆股战。",
 "时者难得而易失也，恐时一失，不可复得。",
 "这厮不是干此事底。",
 "一人砍予一刀，又打一刀背，曹钦适至，见予不忍杀，连呼尊长。",
 "提杲头示予，曰：“诚为此人激变，不得已也。”",
 "就与我写本进入。",
 "予拉翱同行，门缝投进。",
 "一日，递报陈都御史将至，邑人并惊信，文渊因自经死。未几，至者乃广东陈副使便道过家耳。",
 "上恻然曰：“卿言是。朕以弟妇少年，不宜存内，初不计其母子之命。”",
 "于是冒升职者四千人尽首改正，人心皆快。",
 "瑄乃身为目见，故谨录于斯，以彰国史之公，以备修史者采焉。",
 "身为目见",
 "议立东宫事，具奏不允。",
 "上再不可，吾等皆免冠叩头，辞职乞还田里。",
 "亨复遭烈祸，益见天道这好还也。",
]

# ---------- 2. 引文双侧断言 ----------
miss_lib = miss_page = 0
for q in QUOTES:
    qn = norm(q)
    if qn not in NL:
        miss_lib += 1; fail.append(f'库本无：{q[:26]}')
    if not any(qn in c for c in collected):
        miss_page += 1; fail.append(f'页面 .q 未载：{q[:26]}')
print(f'[引文] 期望 {len(QUOTES)} 条：库本缺 {miss_lib}，页面缺 {miss_page}')

# ---------- 3. 全量反扫：页面每块 .q 都必须是库内子串 ----------
sweep_bad = [c for c in collected if c not in NL]
if sweep_bad:
    for c in sweep_bad[:5]: fail.append(f'.q 非库内子串：{c[:30]}')
print(f'[反扫] .q→库本 不命中 {len(sweep_bad)} 块')

# ---------- 4. 「」反扫（剔除 style/script） ----------
body = re.sub(r'<style[\s\S]*?</style>', '', page)
body = re.sub(r'<script[\s\S]*?</script>', '', body)
for m in re.finditer(r'「([^」]*)」', body):
    if norm(m.group(1)) not in NL:
        fail.append(f'「」反扫不命中：{m.group(1)[:30]}')
print(f'[「」反扫] 完成，不命中 {sum(1 for m in re.finditer(r"「([^」]*)」", body) if norm(m.group(1)) not in NL)} 处')

# ---------- 5. 排版红线 ----------
for bad, name in [('—', '长划线'), ('–', '短划线')]:
    if bad in body: fail.append(f'红线：出现{name}')
dot_lines = [ln for ln in body.split('\n') if ln.count('·') > 1]
if dot_lines: fail.append(f'红线：{len(dot_lines)} 行出现多个 ·')
print(f'[红线] 长短划线 0，多 · 行 {len(dot_lines)}')

# ---------- 6. 机数 ----------
exp = {
    '全文': len(lib), '去空白': len(re.sub(r'\s', '', lib)),
    '汉字': len(re.findall(r'[㐀-鿿]', lib)),
}
if exp['去空白'] != 7359: fail.append(f"去空白 {exp['去空白']} != 7359")
if exp['汉字'] != 6085: fail.append(f"汉字 {exp['汉字']} != 6085")
stanzas = len([s for s in re.split(r'\n\s*\n', lib) if s.strip()])
if stanzas != 20: fail.append(f'段数 {stanzas} != 20')
for w, n in [('天道好还', 2), ('这好还', 1), ('于谦', 16), ('石亨', 14), ('徐有贞', 8),
             ('南城', 8), ('圣旨', 6), ('四鼓', 3), ('二鼓', 1), ('三鼓', 1), ('这厮', 5),
             ('水窦', 1), ('归人不归鬼', 1), ('乾象', 1), ('呼噪', 1), ('哥哥', 1),
             ('十七日', 6), ('辇', 2)]:
    c = lib.count(w)
    if c != n: fail.append(f'库本「{w}」{c} != {n}')
for s in ['于谦十六见', '石亨十四见', '南城八见', '圣旨六见', '四鼓三见', '这厮五见',
          '七千三百五十九', '六千零八十五', '二十段']:
    if s not in page: fail.append(f'页面缺实测句：{s}')
print('[机数] 库本与页面实测句断言完成')

# ---------- 7. 生僻字与标题 ----------
for ch in page:
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF or o >= 0x20000:
        fail.append(f'页面含私用/扩展区字符 U+{o:X}')
if '之一百一十六' not in page: fail.append('页面缺自编号 之一百一十六')
print('[杂项] 生僻字与自编号检查完成')

# ---------- 结果 ----------
if fail:
    print('\n== FAIL ==')
    for f in fail: print(' -', f)
    sys.exit(1)
print(f'\n== PASS ==  .q {len(collected)} 块 / 期望 {len(QUOTES)} 条 / 引文·反扫·红线·机数全过')
