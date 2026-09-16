#!/usr/bin/env python3
# insert chan-shu entry into mulu.html with dynamic numbering and assertions
import re

MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/chan-shu.html'

CN = '〇零一二三四五六七八九十百千壹貳贰叁肆伍陆柒捌玖拾佰仟万'

def num2cn(x):
    cn = ['零','一','二','三','四','五','六','七','八','九']
    u = ['', '十', '百', '千']
    strs = []
    i = 0
    while x > 0:
        strs.append((x % 10, i)); x //= 10; i += 1
    res = ''
    for digit, pos in reversed(strs):
        if digit == 0:
            if not res.endswith('零') and pos < 3:
                res += '零'
        else:
            res += cn[digit] + u[pos]
    res = res.rstrip('零')
    if res.startswith('一十'):
        res = res[1:]
    return res

def vseal_cn(x):
    D = '零壹贰叁肆伍陆柒捌玖'
    s = D[x // 100] + '佰' if x >= 100 else ''
    r = x % 100
    if r >= 10:
        t = r // 10
        s += ('壹拾' if t == 1 else D[t] + '拾')
    if r % 10:
        s += D[r % 10]
    return s

def cn2num2(s):
    d = {'零': 0, '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
         '壹': 1, '贰': 2, '貳': 2, '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9}
    u = {'十': 10, '拾': 10, '百': 100, '佰': 100, '千': 1000, '仟': 1000}
    total, seg = 0, 0
    for ch in s:
        if ch in d:
            seg = d[ch]
        elif ch in u:
            total += (seg or 1) * u[ch]
            seg = 0
    return total + seg

mulu = open(MULU, encoding='utf-8').read()
assert 'chan-shu.html' not in mulu, 'page already linked'
assert '>无位</h2>' not in mulu and '· 无位<' not in mulu, 'vol name taken'

nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
assert sorted(nos) == list(range(1, max(nos) + 1)), 'pre-insert numbering not continuous'
n = max(nos) + 1
seals = re.findall(r'class="vseal"[^>]*>([' + CN + r']+)</div>', mulu)
vmax = max(cn2num2(s) for s in seals)
v = vmax + 1
print('entry no =', n, '| vol =', v)
assert v == vmax + 1, (v, vmax, n)
VOL_CN = vseal_cn(v)
JUAN_CN = num2cn(v)
assert f'<h2>卷{JUAN_CN} · ' not in mulu, f'juan {v} taken'

TI = ('唐罗隐撰，据子藏笔记库本，去空白一万四千八百七十一字，五卷六十篇，卷首无序，末附谗书重序，'
'库本录清人枚庵校本夹注六十四处，间有缺字方框，另有四目有题无文。'
'书眼＝一本自己认下恶名的书：作者本名罗横，应进士举十次落第，史称十上不第，遂改名隐，把集子径直题作谗书；'
'重序自辩，君子有其位则执大柄以定是非，无其位则着私而疏善恶，斯所以警当世而诫将来也；'
'英雄之言把偷玉帛与偷家国的说辞并排，牵于寒饿与救彼涂炭各是一套剧本，西刘则曰居宜如是，楚籍则曰可取而代，'
'末句峻宇逸游不为人所窥者鲜也；说天鸡一篇库本原阙、清人据唐文粹补七十三字，真天鸡冠距不举毛羽不彰而伺晨先鸣，'
'彩错铦利者峨冠俯步饮啄而已，道之坏也有是夫；越妇言替朱买臣休妻翻案，她以匡国致君为己任、以安民济物为心期质问故夫，'
'矜于一妇人则可矣，乃闭气而死，死于清醒不死于羞愧；汉武山呼把万岁声记在灾异册，'
'由是万岁之声发于感寤，东封之呼不得以为祥，而为英主之不幸；拾甲子年事记邯郸歌女新声三策不用、自缢、刘氏族灭，'
'谋及媍人者必亡，而新声之言惜其不用，篇名拾字来自固拾于编简；圣人理乱替孔子算账，穷仲尼于乱也，故庙之于后。'
'版式＝闱中出刺壳：首屏贡院号舍木栅灯影，十闱窗逐一点亮十次黜落，点名毕罗横改名条浮出、无位之言朱印砸下；'
'左缘八格刺签轨随文推进；说天鸡做成SVG斗鸡场，使之斗一声天鸡啼、日出口升、彩衣者伏地；'
'英雄之言做成措辞解码表加刘项对白双牌；越妇言竖排一纸绝笔自右展读，闭气句朱线下划；'
'山呼局每呼一声咎条渐满，祥字三呼后裂成咎字；新声案做成案卷，三策各钤不用朱印，结局名列逆党；'
'五卷六十篇谗谱五列排开，原阙四目以墨钉记；尾屏有位无位双柱竖排大字，鲁迅小品文的危机按语收梢，钤诫将来印。'
'校字记：隠媍磰皆库本原形照录，木偶人条狞□勇态、市赋条贤愚并□缺字照存，说天鸡七十三字系唐文粹辑补。'
'引文经脚本与库内文件去标点归一逐字比对通过（二十八处，白话反扫六字窗零撞）。')

DESC = ('一本书自己认下了最难听的名字。'
'本卷收〈谗书〉导读一篇，页面做成一座夜号舍：十闱窗点满十次落榜，改名条浮出朱印砸下；'
'一只不肯装的天鸡应声而啼，英雄的说辞并排解码，一封竖读绝笔替休妻翻案，'
'万岁声三呼之后裂成凶兆，歌女三策依次钤上不用，五卷六十刺终排成谱，有位无位双柱收梢。')

block = f'''
  <div class="vol" style="--vc: var(--c3)">
    <div class="wrap">
      <div class="vol-head">
        <div class="vseal" style="background: var(--c3); font-size: 15px">{VOL_CN}</div>
        <h2>卷{JUAN_CN} · 无位</h2>
        <div class="vsub">石青 · 子藏笔记</div>
      </div>
      <p class="vol-desc">{DESC}</p>
      <a class="entry" href="chan-shu.html">
        <span class="no mono">{n}</span>
        <span class="ti">谗书<small>{TI}</small></span>
        <span class="file mono">chan-shu.html</span>
      </a>
    </div>
  </div>

<footer class="page">'''

assert mulu.count('<footer class="page">') == 1
mulu = mulu.replace('<footer class="page">', block)

NCN = num2cn(n)
mulu = re.sub(r'[一二三四五六七八九十百零]+篇导读，2026 年 9 月编', f'{NCN}篇导读，2026 年 9 月编', mulu)

old_tail = '万杵卷问功，问穹卷叩天。</p>'
assert mulu.count(old_tail) == 1, mulu.count(old_tail)
mulu = mulu.replace(old_tail, '万杵卷问功，问穹卷叩天，无位卷出刺。</p>')

nos2 = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
assert sorted(nos2) == list(range(1, n + 1)), 'post-insert numbering broken'
assert f'>{n}</span>' in mulu and f'{NCN}篇导读' in mulu
open(MULU, 'w', encoding='utf-8').write(mulu)

page = open(PAGE, encoding='utf-8').read()
assert page.count('⟦NO⟧') == 3
page = page.replace('⟦NO⟧', str(n))
open(PAGE, 'w', encoding='utf-8').write(page)
print('inserted: entry', n, f'vol 卷{JUAN_CN}·无位, footer ->', NCN)
