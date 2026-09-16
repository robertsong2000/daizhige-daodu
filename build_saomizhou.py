#!/usr/bin/env python3
# build & verify saomizhou.html (339th+ daodu page)
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/扫迷帚.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/saomizhou.html'

src = open(LIB, encoding='utf-8').read()
J = re.sub(r'\s', '', src)
tpl = open(TPL, encoding='utf-8').read()

QUOTES = {
 'Q1':  ('阻碍中国进化的大害', '莫若迷信'),
 'Q2':  ('极狡黠之人而信命', '而又信前定'),
 'Q3':  ('造魔自迷', '作茧自缚'),
 'Q4':  ('虽学士大夫', '同一见识'),
 'Q5':  ('故欲救中国', '改革习俗入手'),
 'Q6':  ('最恨鬼神', '进化的蟊贼'),
 'Q7':  ('视西人之脚踏实地', '凭实验不凭虚境'),
 'G1':  ('多读有用书', '少作无益事'),
 'G2':  ('救人莫如医', '惑世莫如巫'),
 'G3':  ('做人当从阳面做起', '勿从阴面做起'),
 'G4':  ('光明世界', '断无幻境'),
 'G5':  ('世果有神仙', '秦皇汉武，可以不死'),
 'G6':  ('尽人事乃真君子', '诿天命必非丈夫'),
 'G7':  ('岂风水行于中', '不行于西'),
 'G8':  ('相由心生', '欺人之语'),
 'G9':  ('赛会迎神', '我视为昏暗世界'),
 'Z1':  ('僧道无缘', '男读女织'),
 'B1':  ('太上立命', '最下者听命'),
 'B2':  ('人死则譬诸灯灭', '安得有鬼'),
 'B3':  ('疑心生暗鬼', '由疑心生出来的'),
 'B4':  ('汝误才有今日', '我不误也'),
 'B5':  ('好大世界', '岂不爽快'),
 'B6':  ('命不足凭', '敬佩名论'),
 'B7':  ('八股以外', '绝无事业'),
 'B8':  ('方今格致日明', '谈鬼神之说者'),
 'B9':  ('命之一说', '贫富贵贱死生六字'),
 'B10': ('明有神', '载于古籍'),
 'B11': ('苏子瞻喜人谈鬼', '披荔带萝之辈'),
 'B12': ('苏城童稚', '连日被溺'),
 'GH1': ('如大头鬼', '招摇撞骗鬼'),
 'GH2': ('焦面大王鬼', '令人莫辨'),
 'GH3': ('万头攒动', '都道会来会来'),
 'F1':  ('推算星命', '到馆面陈'),
 'F2':  ('照你的八字', '他人做父母么'),
 'F3':  ('即有一二句道得准', '察言辨色得来的'),
 'F4':  ('尊造刑克重重', '荫下之福'),
 'F5':  ('我父母康健无恙', '你怎说此话咒他老人家'),
 'FS1': ('天下只有风水', '没有神佛'),
 'FS2': ('神佛是实有的', '作不得准的'),
 'FS3': ('郭璞为千古葬师之祖', '不能保其身'),
 'FS4': ('日本不讲风水', '富强甲五洲'),
 'FS6': ('纳入盘中', '舁蛙于彩舆中'),
 'Y1':  ('宜用两缸对合封固', '则躯可不朽'),
 'Y2':  ('倘有灾祸', '吾当身任'),
 'Y3':  ('早已揭开', '数十根而已'),
 'K1':  ('有百日关', '有罗汉关'),
 'K2':  ('一箭伤人则三岁殇', '十二岁难活'),
 'K3':  ('六十六阎王请吃肉', '六十六阎王请吃肉'),
 'K4':  ('自元旦始', '一概辞谢不到'),
 'K5':  ('明九者', '三十六岁等是也'),
 'K6':  ('据术士所言', '灾悔厄难之虞'),
 'D1':  ('地府需洋一百二十元', '增寿三纪'),
 'D2':  ('竟以粪汁一杯', '立时气绝'),
 'D3':  ('提溺壶直灌道士的头顶', '淋漓尽致'),
 'D4':  ('从此癫疾竟好了', '从此癫疾竟好了'),
 'T1':  ('上曰', '下曰『民壮』'),
 'T2':  ('出售财神', '五将等符'),
 'T3':  ('价目高下互殊', '自十二元至数十元不等'),
 'T4':  ('一醮三百金', '一忏四百金'),
 'T5':  ('张均示价千金起码', '为之捉妖'),
 'T6':  ('定期设坛召将', '限先三日缴银'),
 'T7':  ('须费十四文', '为挂号金'),
 'T8':  ('今既不中', '诳骗无疑'),
 'T9':  ('闻天师甚狼狈云', '闻天师甚狼狈云'),
 'C1':  ('听你自杀', '如何还能杀人'),
 'C2':  ('血流如注', '疼痛异常'),
 'C3':  ('更觅得猫一犬一', '名曰猫狗做亲'),
 'C4':  ('其家因病而充喜', '以致于死'),
 'W1':  ('神道设教', '救时的妙计'),
 'W2':  ('有道之世', '其鬼不神'),
 'W3':  ('神权两字', '二十世纪以后'),
 'W4':  ('欲止渴而饮鸩', '欲疗疮而剜肉'),
 'W5':  ('一边将迷信关头重重戡破', '一边大兴学堂'),
 'W6':  ('此后各事', '兹不复赘'),
}

def norm(s):
    return re.sub(r'[^0-9A-Za-z一-鿿]', '', s)

NJ = norm(J)

fails = []
for k, (a, b) in QUOTES.items():
    ia, ib = J.find(a), J.find(b)
    ca = J.count(a)
    if ca != 1 or ia < 0 or ib < 0:
        fails.append((k, 'anchor', a, ca)); continue
    if ib < ia:
        fails.append((k, 'order', a)); continue
    seg = J[ia:ib + len(b)]
    if norm(seg) not in NJ:
        fails.append((k, 'norm'))
    if k == 'GH1':
        items = seg.split('、')
        html = ''.join('<i class="gt">%s</i>' % it for it in items)
        tpl = tpl.replace('⟦%s⟧' % k, html)
    else:
        tpl = tpl.replace('⟦%s⟧' % k, seg)

n = sys.argv[1] if len(sys.argv) > 1 else '341'
tpl = tpl.replace('⟦N⟧', n)

leftover = re.findall(r'⟦[A-Z0-9]+⟧', tpl)
if leftover:
    fails.append(('tokens', leftover))

open(TPL, 'w', encoding='utf-8').write(tpl)

# ---- quote verify on assembled page (channel: div class starting with "q") ----
page = tpl
qblocks = re.findall(r'<div class="q[ "][^>]*>(.*?)</div>', page, re.S)
nok = 0
for i, q in enumerate(qblocks):
    q = re.sub(r'<span class="src">.*?</span>', '', q, flags=re.S)
    nq = norm(re.sub(r'<[^>]+>', '', q))
    if nq and nq in NJ:
        nok += 1
    elif nq:
        fails.append(('verify', i, nq[:30]))

# ---- anti-scan: baihua 6-char windows vs lib ----
body = re.sub(r'<script.*?</script>', '', page, flags=re.S)
body = re.sub(r'<div class="q[ "][^>]*>.*?</div>', '\n', body, flags=re.S)
body = re.sub(r'<(h1|h2|h3|h4|p|div|section|footer|button|main|body|title|i|span)\b', '\n<\\1', body)
attrs = re.findall(r'data-(?:bub|d|t)="([^"]*)"', body)
blocks = [norm(re.sub(r'<[^>]+>', '', b)) for b in body.split('\n')]
blocks += [norm(a) for a in attrs]
hits = []
for bi, b in enumerate(blocks):
    if len(b) < 6:
        continue
    for i in range(len(b) - 5):
        w = b[i:i + 6]
        if w in NJ:
            hits.append((bi, w, b[max(0, i - 8):i + 14]))

# ---- hard rules ----
dashes = [c for c in '—–' if c in tpl]
mids = [(ln + 1, ln.count('·')) for ln in tpl.split('\n') if ln.count('·') > 1]

print('stripped lib chars:', len(J))
print('quote channels:', len(qblocks), 'verified ok:', nok)
print('anti-scan windows hit:', len(hits))
for h in hits[:40]:
    print('  HIT blk%d [%s] ...%s...' % h)
print('dash violation:', dashes, '| multi-dot lines:', mids)
if fails:
    print('FAILS:')
    for f in fails:
        print('  ', f)
    sys.exit(1)
print('ALL GREEN' if not hits and not dashes and not mids else 'CHECK ABOVE')
