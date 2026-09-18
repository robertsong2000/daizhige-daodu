#!/usr/bin/env python3
# mulu.html 发布：条目文案窗检查 + 三锚更新 + 卷330块插入 + 连续性断言
import re, sys

MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/帝京岁时纪胜.txt'
src = open(SRC, encoding='utf-8').read()
PUA = re.compile('[--\U00020000-\U0003ffff]')
PUNCT = '，。、；：？！…—–·「」『』（）()《》〈〉【】〔〕%※：;,"\'！？。…〈〉＜＞＜＞〔〕〖〗〔〕□◆○●◎★☆①②③④⑤⑥⑦⑧⑨⑩・“”‘’'
def norm(s):
    s = PUA.sub('', s)
    s = re.sub(r'\s+', '', s)
    return ''.join(ch for ch in s if ch not in PUNCT)
srcn = norm(src)
WHITELIST = {'帝京岁时纪胜'}

DESC = '乾隆间北京人潘荣陛把帝都一年拆成十二个月来记：元日爆竹底下的叫卖、上元的烟火名色、中元满河的灯、冬至起九九八十一瓣的消寒素梅，岁末再附一篇把全城铺面数到头的皇都品汇。本卷收〈帝京岁时纪胜〉导读一篇，做成走马灯壳：首屏灯影走马点灯显名钤熙朝景物印，元日市声墙五声点亮与爆竹相和，烟火名色六枚点放开满天，十二折月令屏逐折展读原句，中元河灯放满一河点亮灯名，皇都品汇点匾看老字号来历，尾屏九九消寒图染瓣至春深钤印。引文经脚本与库内文件去标点、归一逐字比对通过（六十六处，白话反扫六字窗零撞）。'
TI = '乾隆间大兴潘荣陛撰，字在廷，据史藏地理库本，去空白约一万九千四百字，一卷：自序、目录、正文按月分折，自元日、燕九、清明、端阳、七夕、中元、中秋、重阳、冬至数九直至岁暮祀灶守岁逐节立目，末以皇都品汇一篇骈列全城铺户，书末附今人考略。书眼＝按月记账的一座城：别人记节令只记仪典，他连爆竹声缝里的四种叫卖都记，走桥摸钉、占鳌头、丢百病、听谶语，全是日子本身的动静。名场面：元夜妇女过桥摸门钉祈子；白云观燕九节记邱真人应元太祖之召，一心以止杀为言，活人不下三万，与本系列第二十七篇遥遥相扣；丰台芍药日售万茎而惜无好事者图而谱之；城南法藏寺塔高十丈，八面每窗一佛，共五十八佛各舍一灯，上元夜僧众点灯绕塔奏乐；乾隆间宫中中元放荷叶灯数千盏浮在水上；九九消寒图画素梅八十一瓣，每天染一瓣，染完恰是深春。可看的细节：烟火有双响震天雷与地老鼠、金盆捞月与叠落金钱诸名色，街头叫卖滴滴金儿歌；中秋以黄沙土作白玉兔，即兔儿爷前身；夏至家家冷淘面，谚语说冬至吃馄饨夏至吃面；腊月的水土要贵上三分；皇都品汇报出王麻子钢针、孙胡子扁食、马思远元宵一批老字号。版式＝走马灯壳：首屏灯影走马点灯显名钤熙朝景物印；元日市声墙五声点亮与爆竹相和；上元烟火名色六枚点放开满天出滴滴金谣；十二折月令屏逐折展读三十六节原句；中元河灯放满一河点亮四种灯名；皇都品汇五匾点看字号来历；尾屏九九消寒图八十一瓣逐瓣染至春深钤春深印，数九歌逐九点亮。校字记：库本讹字照录，前奇百状之前为千字之讹，联镰飞鞚疑为联镳之讹；■〈〉式造字记号与扩展区字照录不入引。时代局限：香会赛神、禁忌谶纬与男尊女卑皆乾隆年间观念现场，照录立此存照，不代今人立论。引文经脚本与库内文件去标点、归一逐字比对通过（六十六处，白话反扫六字窗零撞）。'

for label, txt in (('desc', DESC), ('ti', TI)):
    n = norm(txt)
    gram = set(srcn[i:i+6] for i in range(len(srcn) - 5))
    hits = [n[i:i+6] for i in range(len(n) - 5) if n[i:i+6] in gram and n[i:i+6] not in WHITELIST]
    if hits:
        for h in hits[:20]:
            print('MULU-TEXT HIT [' + label + ']:', h, '…' + n[max(0, n.find(h) - 8):n.find(h) + 14] + '…')
        sys.exit(1)
print('mulu text windows: 0')

html = open(MULU, encoding='utf-8').read()

# ---- 前置断言：并行状态实测 ----
n450_before = html.count('四百五十')
assert 'dijing-suishijisheng.html' not in html, 'file link taken'
assert '卷三百三十一 ·' not in html, '卷331 taken'
assert 'dijing-suishijisheng.html' not in html, 'file link taken'
nos = sorted(set(int(x) for x in re.findall(r'class="no mono">(\d+)</span>', html)))
assert nos == list(range(1, max(nos) + 1)), 'entry numbers not continuous: ' + str(nos[-5:])
assert max(nos) == 451, 'max entry is %d, expected 451' % max(nos)

# ---- 三锚更新 ----
lines = html.split('\n')
for i, ln in enumerate(lines):
    if '<div class="kicker">' in ln and '导读合订' in ln:
        assert '四百五十一' in ln, 'kicker anchor stale differently: ' + ln[:80]
        lines[i] = ln.replace('四百五十一', '四百五十二')
    elif '<p class="sub">' in ln:
        assert '四百五十一篇短文' in ln, 'sub anchor: ' + ln[:60]
        assert '三百二十九卷分编' in ln, 'sub vol count: ' + ln[:80]
        ln2 = ln.replace('四百五十一篇', '四百五十二篇').replace('三百二十九卷分编', '三百三十一卷分编')
        assert '炎火卷护苗。</p>' in ln2, 'sub tail: ' + ln2[-80:]
        ln2 = ln2.replace('炎火卷护苗。</p>', '炎火卷护苗，灯月卷放灯。</p>')
        lines[i] = ln2
    elif '篇导读，2026 年 9 月编' in ln:
        assert '四百五十一篇导读' in ln, 'footer anchor: ' + ln[:60]
        lines[i] = ln.replace('四百五十一篇导读', '四百五十二篇导读')
html = '\n'.join(lines)
assert html.count('四百五十二') == 3, 'anchor count: %d' % html.count('四百五十二')

# ---- 卷330块 ----
BLOCK = '''  <div class="vol" style="--vc: var(--c4)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c4)">叁百叁拾壹</div>
        <h2>卷三百三十一 · 灯月</h2>
        <div class="vsub">赭金 · 史藏地理</div>
      </div>
      <p class="vol-desc">@@DESC@@</p>
      <a class="entry" href="dijing-suishijisheng.html">
        <span class="no mono">452</span>
        <span class="ti">帝京岁时纪胜<small>@@TI@@</small></span>
        <span class="file mono">dijing-suishijisheng.html</span>
      </a>
    </div>
  </div>'''
BLOCK = BLOCK.replace('@@DESC@@', DESC).replace('@@TI@@', TI)
idx = html.find('\n</footer>')
assert idx > 0, 'footer not found'
html = html[:idx].rstrip() + '\n\n' + BLOCK + '\n</footer>' + html[idx + len('\n</footer>'):]

open(MULU, 'w', encoding='utf-8').write(html)

# ---- 后置断言 ----
html2 = open(MULU, encoding='utf-8').read()
nos2 = sorted(set(int(x) for x in re.findall(r'class="no mono">(\d+)</span>', html2)))
assert nos2 == list(range(1, 453)), 'numbers broken'
vols = re.findall(r'<h2>(卷[^<]*)</h2>', html2)
assert len(vols) == len(set(vols)), 'dup volume titles'
assert '卷三百三十一 · 灯月' in html2 and html2.count('灯月卷放灯') == 1
assert html2.count('dijing-suishijisheng.html') == 2
print('mulu updated: entries 1..451, vol330 ok, anchors ok')
