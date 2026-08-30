# -*- coding: utf-8 -*-
# 蟹谱 导读页核验：引文逐字对库 + 排版红线 + 机数断言
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/xie-pu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/蟹谱.txt'
ZHIZHAI = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/目录/直斋书录解题.txt'
SONGSHI = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/正史/宋史.txt'

VOID = {'meta','link','br','img','hr','input','area','base','col','embed','source','track','wbr'}

def norm(t):
    out=[]
    for ch in t:
        o=ord(ch)
        if 0x3400<=o<=0x9FFF or 0x20000<=o<=0x3FFFF:
            out.append(ch)
        elif ch.isascii() and ch.isalnum():
            out.append(ch)
    return ''.join(out)

class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.quotes=[]; self.cur=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        cls=(a.get('class') or '').split()
        d={'tag':tag,'classes':cls,'datasrc':a.get('data-src'),'qtext':[]}
        self.stack.append(d)
        if self.cur is None and 'q' in cls:
            self.cur=d
    def handle_startendtag(self,tag,attrs):
        if tag not in VOID:
            self.handle_starttag(tag,attrs); self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag:
                closed=self.stack[i:]
                del self.stack[i:]
                if self.cur in closed:
                    txt=''.join(self.cur['qtext'])
                    self.quotes.append({'text':txt,'datasrc':self.cur['datasrc'],
                                        'classes':self.cur['classes']})
                    self.cur=None
                break
    def handle_data(self,data):
        if self.cur is not None:
            self.cur['qtext'].append(data)

html=open(PAGE,encoding='utf-8').read()
body=html[html.find('<body'):]
body=body[:body.find('</html>')]
# strip style/script contents for text scans
vis=re.sub(r'<style[\s\S]*?</style>','',body)
vis=re.sub(r'<script[\s\S]*?</script>','',vis)

p=QC(); p.feed(body)
fails=[]

libs={
 'main': norm(open(LIB,encoding='utf-8').read()),
 'zhizhai': norm(open(ZHIZHAI,encoding='utf-8').read()),
 'songshi': norm(open(SONGSHI,encoding='utf-8').read()),
}
raws={
 'main': open(LIB,encoding='utf-8').read(),
 'zhizhai': open(ZHIZHAI,encoding='utf-8').read(),
 'songshi': open(SONGSHI,encoding='utf-8').read(),
}
raws['main']=re.sub(r'\s','',raws['main'])

# ---------- 1. sweep: every .q must hit its source ----------
main_hits=0
for i,qd in enumerate(p.quotes,1):
    n=norm(qd['text'])
    if len(n)<2:
        fails.append(f'Q{i:02d} too short: {qd["text"][:24]!r}'); continue
    src=qd['datasrc'] or 'main'
    if n not in libs[src]:
        fails.append(f'Q{i:02d} MISS[{src}]: {qd["text"][:40]!r}')
    else:
        if src=='main': main_hits+=1
print(f'[sweep] .q spans={len(p.quotes)}  main-source hits={main_hits}')
if len(p.quotes)<30: fails.append(f'quote count {len(p.quotes)} < 30')

# ---------- 2. 「」反扫: quoted fragments outside .q ----------
qtexts=[norm(q['text']) for q in p.quotes]
bare=[]
for m in re.finditer(r'「([^「」]{1,60})」',vis):
    frag=m.group(1); n=norm(frag)
    if len(n)>=6 and not any(n in qt for qt in qtexts):
        bare.append(frag)
if bare:
    fails.append('bare quotes: '+repr(bare[:8]))
print(f'[bare] fragments>=6 outside .q: {len(bare)}')

# ---------- 3. layout red lines ----------
vis2=re.sub(r'<!--[^>]*-->','',vis)
plain=re.sub(r'<[^>]+>','',vis2)
if '—' in plain or '–' in plain: fails.append('em/en dash found')
for ln,line in enumerate(plain.split('\n'),1):
    if line.count('·')>1: fails.append(f'line {ln} has {line.count("·")} middot')
print('[redline] dashes & middot: clean' if not any('dash' in f or 'middot' in f for f in fails) else '[redline] FAIL')

# ---------- 4. library stats ----------
lib=open(LIB,encoding='utf-8').read()
no_ws=re.sub(r'\s','',lib)
han=sum(1 for c in lib if 0x3400<=ord(c)<=0x9FFF or 0x20000<=ord(c)<=0x2FFFF)
assert len(lib)==6989, len(lib)
assert len(no_ws)==6310, len(no_ws)
assert han==5133, han
for w,cnt in [('蟹',156),('呉',9),('吴',0),('蟹王',1),('横行',4),('□',30),('〈',30),('嘉佑',4)]:
    got=lib.count(w)
    if got!=cnt: fails.append(f'lib count {w}={got} expect {cnt}')
print(f'[lib] 6989/6310/5133 counts ok; 蟹156 呉9 吴0 蟹王1 横行4 □30 〈30 嘉佑4')

# ---------- 5. entry-name wall vs library ----------
lines=[l.strip() for l in lib.split('\n')]
def listline(key):
    for l in lines:
        if l.startswith(key) and '　' in l:
            return [x for x in l.split('　') if x]
    raise KeyError(key)
up=listline('离象'); down=listline('孝报')
assert len(up)==42, len(up)
assert len(down)==24, len(down)
chips=re.findall(r'<span class="chip[^"]*">([^<]+)<sup>(\d+)</sup></span>',body)
assert len(chips)==66, len(chips)
names=[c[0] for c in chips]
if names!=up+down:
    for k,(a,b) in enumerate(zip(names,up+down)):
        if a!=b: fails.append(f'chip#{k+1} page={a!r} lib={b!r}'); break
    fails.append('chip wall mismatch')
nos=[int(c[1]) for c in chips]
if nos!=list(range(1,67)): fails.append('chip numbering broken')
hot=re.findall(r'<span class="chip hot">([^<]+)<sup>',body)
want_hot={'左持','蟚蜝','输芒','孝报','殊类','贪化','泉比','食品','兵权','白蟹'}
if set(hot)!=want_hot or len(hot)!=10:
    fails.append(f'hot chips {sorted(hot)}')
print(f'[wall] 42+24 chips all match library order; hot={len(hot)}')

# ---------- 6. 提要 internal discrepancies ----------
t0=lib.find('《蟹谱》二卷'); tiyao=lib[t0:lib.find('卷上',t0)]
assert '贪花' in tiyao and '贪化' in lib, '提要/正文 贪花贪化'
assert '食莨' in lib and '食茛' in lib, '食莨/食茛'
assert '肱字自翼' in lib, '提要自翼'
print('[text] 贪花/贪化 食莨/食茛 自翼 variants confirmed in library')

# ---------- 7. cross-lib sources ----------
zz=raws['zhizhai'].replace('\n','')
if '称怪山傅肱子翼撰' not in zz or '嘉祐四年序' not in zz: fails.append('直斋 evidence missing')
if '蟹略' not in zz or '高似孙续古撰' not in zz: fails.append('直斋 蟹略 missing')
ss=raws['songshi']
if '赵概罢知徐州' not in re.sub(r'\s','',ss): fails.append('宋史 赵概 missing')
print('[crosslib] 直斋 蟹谱条+蟹略条, 宋史 赵概罢知徐州: present')

# ---------- 8. page self-claims ----------
for token in ['6,989','6,310','5,133','<b>42</b> 目','<b>24</b> 目','之一百零五','引文已与库内文件逐字核验','时代局限','github.com/robertsong2000/daizhigev20']:
    if token not in body: fails.append(f'page claim missing: {token!r}')
print('[claims] page numbers & footer tokens present')

print('='*46)
if fails:
    print('FAIL', len(fails))
    for f in fails: print(' -',f)
    sys.exit(1)
print('ALL PASS', f'({len(p.quotes)} .q spans, 66 chips, redlines clean)')
