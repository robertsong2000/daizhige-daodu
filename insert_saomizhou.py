#!/usr/bin/env python3
# dynamically pick next no/vol and insert 扫迷帚 into mulu.html, patch page numbers
import re, sys

MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/saomizhou.html'

mulu = open(MULU, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()

# ---- uniqueness checks ----
assert '扫迷帚' not in mulu, '扫迷帚 already in mulu!'
assert 'saomizhou.html' not in mulu, 'filename already used!'

# ---- current numbering ----
nos = [int(m) for m in re.findall(r'class="no mono">(\d+)<', mulu)]
n = max(nos) + 1
assert sorted(nos) == list(range(1, max(nos) + 1)), 'gap in existing nos!'

CN_D = {'零':0,'壹':1,'一':1,'贰':2,'两':2,'叁':3,'三':3,'肆':4,'四':4,'伍':5,'五':5,
        '陆':6,'六':6,'柒':7,'七':7,'捌':8,'八':8,'玖':9,'九':9}
CN_U = {'拾':10,'佰':100,'十':10,'百':100}

def cn2num(s):
    s = s.replace('貳', '贰').replace('參', '叁')
    total, cur = 0, 0
    for ch in s:
        if ch in CN_D:
            cur = CN_D[ch]
        elif ch in CN_U:
            u = CN_U[ch]
            if cur == 0:
                cur = 1
            total += cur * u
            cur = 0
        elif ch == '零':
            continue
    return total + cur

def num2cn(n):
    d = '零一二三四五六七八九'
    if n < 100:
        return ''.join(d[int(c)] for c in str(n))
    s = ''
    h, r = divmod(n, 100)
    s += d[h] + '百'
    if r == 0:
        return s
    if r < 10:
        return s + '零' + d[r]
    t, o = divmod(r, 10)
    return s + (d[t] + '十' if t else '十') + (d[o] if o else '')

vseals = re.findall(r'<div class="vseal"[^>]*>([^<]+)</div>', mulu)
vmax = max(cn2num(v) for v in vseals)
v = vmax + 1
h2vol = '卷' + num2cn(v)
assert h2vol + ' ·' not in mulu, h2vol + ' taken!'

FD = '零壹贰叁肆伍陆柒捌玖'

def formal(nn):
    h, t, o = nn // 100, nn // 10 % 10, nn % 10
    s = (FD[h] + '佰') if h else ''
    s += (FD[t] + '拾') if t else ('零' if h and o else '')
    s += FD[o] if o else ''
    return s

vseal = formal(v)
cn_no = num2cn(n)
print('target: no=%d vol=%s vseal=%s' % (n, h2vol, vseal))

# ---- vol block ----
BLOCK = '''  <div class="vol" style="--vc: var(--c1)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c1); font-size: 15px">%(vseal)s</div>
        <h2>%(h2)s · 醒迷</h2>
        <div class="vsub">朱砂 · 集藏破迷小说</div>
      </div>
      <p class="vol-desc">一把从未在正文里出现的扫帚，扫了整整二十四回：满街的香火、签筒、罗盘与符纸，一样一样拿到道理底下过秤。本卷收〈扫迷帚〉导读一篇，页面做成一条晚清夜街：点挥帚，大扫帚横扫六面幌子，幌子翻面露出破迷二字，竖排书名才显形；鬼会长卷二十二位挨个点验，验仙缸当众开盖，天师价目明码标榜，尾屏钤醒迷印收梢。</p>
      <a class="entry" href="saomizhou.html">
        <span class="no mono">%(n)s</span>
        <span class="ti">扫迷帚<small>清壮者撰，光绪间商务印书馆刊本，二十四回，去空白三万四千三百四十三字，清末破除迷信题材长篇白话小说的代表作。书眼＝书名里的帚在二十四回正文中从未出现，它就是书本身：主角卞至元号资生，吴江布衣，书案右首贴格言一纸，多读有用书少作无益事，救人莫如医惑世莫如巫，尽人事乃真君子诿天命必非丈夫；表弟杨德字心斋，镇江秀才，八股以外绝无事业，七月上浣买舟问难想把表兄驳倒，反被一路折服：命之说折于太上立命其次制命最下者听命，鬼神之说折于人死则譬诸灯灭形影俱息安得有鬼，讨替之说折于汝误才有今日我不误也，与豁达先生好大世界无遮无碍死去生来有何替代要走便走岂不爽快；第四回苏州盂兰会鬼队长卷，大头鬼小头鬼摸壁鬼无常鬼一路点到招摇撞骗鬼，压队焦面大王鬼摆来踱去全是官样，是鬼是官令人莫辨；元妙观瞎算命开口断人父母该打，半张布招传自异人应验如神与农人老拳同框；第八回茶肆里风水神佛对辩吵个平手，资生两案并结：郭璞为千古葬师之祖而不能保其身，日本不讲风水而国盛民安欧洲不讲风水而富强甲五洲；第九回学政拜青蛙，纳入盘中玻璃罩盖之舁蛙于彩舆中，衔牌执事开道蟒衣差官捧香，送的是那只蛙；第十一回英山柯女仙案，县尉顾某当众立言倘有灾祸吾当身任，开缸但见臭水满缸白骨数十根而已，是全书最硬的一次开验，可惜数年后父兄入狱服毒，迷信敛来的钱由穷人结账；第十七回一身百关，百日关千日关到罗汉关，明九暗九将军箭一箭三岁殇四箭十二岁难活，六十六阎王请吃肉被李翁一张梅红纸告示挡了一整年；第十四回妖道两案，地府需洋一百二十元可使尔子增寿三纪，粪汁一杯立时气绝，秀才提溺壶直灌道士头顶，从此癫疾竟好了，全书最解气的一把扫帚是一只溺壶；第二十二回张天师南游价目榜，上曰大真人府下曰民壮，符价自十二元至数十元不等，一醮三百金一忏四百金，捉妖示价千金起码限先三日缴银，瞻仰须费十四文为挂号金，杭人何某讨符洋砸价目虎头牌，闻天师甚狼狈云；第二十三回冲喜两案，敕勒术试刀血流如注疼痛异常落得终身残废，猫狗做亲双双交拜，其家因病而充喜反因充喜而得病以致于死；末回老儒王存中问难神道设教是古人救时的妙计，资生引有道之世其鬼不神作答，欲止渴而饮鸩欲疗疮而剜肉，双管齐下一边将迷信关头重重戡破一边大兴学堂，卷尾此后各事详载续编兹不复赘，续编始终没有来。版式＝夜街挥帚壳：首屏晚清夜街山墙灯笼，六面迷信行当幌子悬于绳上，点挥帚大扫帚横扫过街，幌子逐一翻面露出命不足凭符不疗病等破迷字样，竖排书名显形钤醒迷朱印；底部扫帚进度条随读横扫全街；格言九条纸条点击盖验字；辩局账三场问答竖签对谈；鬼会二十二位竖签横排点验计数；算命摊布招翻卡看瞎子两句话；验仙缸点开缸盖臭水白骨现形；关煞单黄纸与梅红纸告示；妖道案卷两开；天师价目黄榜四行含售后纠纷；尾屏老儒与资生对坐，钤醒迷大印收梢。校字记：治并镇煞之并疑为病讹照录，疾玻疗玻尫嬴等库本讹残诸条避引，□为库本阙字避引，决已不在之决库本原样照录。引文经脚本与库内文件去标点归一逐字比对通过（七十三处，白话反扫六字窗零撞）。</small></span>
        <span class="file mono">saomizhou.html</span>
      </a>
    </div>
  </div>

''' % dict(vseal=vseal, h2=h2vol, n=n)

anchor = '\n\n<footer class="page">'
assert mulu.count(anchor) == 1
mulu = mulu.replace(anchor, '\n\n' + BLOCK + '<footer class="page">')

# ---- count anchors (both; parallel sessions sometimes update only one) ----
anchors = re.findall(r'[零一二三四五六七八九十百]+篇导读', mulu)
assert len(anchors) == 2, 'count anchors: %d' % len(anchors)
mulu = re.sub(r'[零一二三四五六七八九十百]+篇导读', cn_no + '篇导读', mulu)

open(MULU, 'w', encoding='utf-8').write(mulu)

# ---- patch page numbers if shifted ----
mpage = re.search(r'导读 (\d+)', page)
page_n = int(mpage.group(1)) if mpage else n
if page_n != n:
    page = page.replace('导读 %d' % page_n, '导读 %d' % n)
    page = page.replace('第 %d 篇' % page_n, '第 %d 篇' % n)
    open(PAGE, 'w', encoding='utf-8').write(page)
    print('page numbers patched %d -> %d' % (page_n, n))

print('inserted: no=%d vol=%s(%d) counts=%s' % (n, h2vol, v, cn_no))
