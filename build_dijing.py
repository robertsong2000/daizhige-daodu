#!/usr/bin/env python3
# 帝京岁时纪胜导读页 builder：程序化切引 + 反扫核验
import re, sys
from html.parser import HTMLParser

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/帝京岁时纪胜.txt'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/dijing-suishijisheng.html'
src = open(SRC, encoding='utf-8').read()

PUA = re.compile('[-\U00020000-\U0003ffff]')
PUNCT = '，。、；：？！…—–·「」『』（）()《》〈〉【】〔〕%※：;,"\'！？。…〈〉＜＞＜＞〔〕〖〗〔〕□◆○●◎★☆①②③④⑤⑥⑦⑧⑨⑩・“”‘’'
def norm(s):
    s = PUA.sub('', s)
    s = re.sub(r'\s+', '', s)
    return ''.join(ch for ch in s if ch not in PUNCT)

srcn = norm(src)

def cut(a, b=None):
    ia = src.find(a)
    assert ia >= 0, 'start miss: ' + a
    if b is None: b = a
    ib = src.find(b, ia)
    assert ib >= 0, 'end miss: ' + b
    return src[ia:ib + len(b)]

Q = {}
def q(name, a, b=None):
    Q[name] = cut(a, b)

# ---- 自序 ----
q('xu1', '晨入夜出，负星而趁瞑', '可涉笔札')
q('xu2', '惟是皇都品汇万方', '岂可茫无记述')
q('xu3', '而谬以促笔短裁', '仪文之盛')
# ---- 目录墙 ----
q('muluall', '正月　元旦', '岁暮杂务 皇都品汇')
# ---- 元日 市声 ----
q('baozhu', '除夕之次', '彻夜无停')
q('maisheng1', '更间有下庙之博浪鼓声', '卖合菜细粉声')
q('maisheng2', '与爆竹之声', '良可听也')
q('xinxi', '路遇亲友', '新禧纳福')
q('zouqianjia', '俗说谓新正拜节', '极一时之胜也矣')
q('liulichang', '每于新正元旦至十六日', '宝玩填街')
# ---- 上元 烟火 ----
q('jinwubujin', '而城市张灯', '金吾不禁')
q('zouqiao', '元夕妇女群游', '识宜男也')
q('yanhuo1', '其爆竹有双响震天雷', '名色')
q('dilaoshu', '其不响不起盘旋地上者', '水老鼠')
q('didijin', '滴滴金，梨花香', '哄姑娘')
# ---- 月令折屏 ----
q('xingdeng', '初八日传为诸星下界', '百有八盏为率')
q('yanjiu', '考元大宗师长春真人邱处机赴元太祖召', '全活不下三万人')
q('tiancang', '念五日为填仓节', '名曰填仓')
q('yinlong', '乡民用灰自门外蜿蜒布入宅厨', '呼为引龙过')
q('zhanaotou', '小儿辈懒学', '曰占鳌头')
q('huazhao', '十二日传为花王诞日', '曰花朝')
q('zhiyuan', '清明扫墓', '施放较胜')
q('dailiu', '清明日摘新柳佩带', '来生变黄狗')
q('fengtai', '而京师丰台', '日万余茎')
q('tianxian', '每岁之四月朔至十八日', '素称最胜')
q('duanyang', '五月朔，家家悬朱符', '宜夏避恶')
q('nvrierjie', '已嫁之女亦各归宁', '为女儿节')
q('xionghuang', '午前细切蒲根', '以避虫毒')
q('lengtao', '京师于是日家家俱食冷淘面', '天下无比')
q('wuyuehan', '有钱难买五月旱', '吃饱饭')
q('yuxiang', '銮仪卫驯象所', '环聚如堵')
q('shanglian', '都人结侣携觞，酌酒赏花', '遍集其下')
q('qiqiao', '幼女以盂水曝日下', '卜女之巧')
q('xishuai', '都人好畜蟋蟀', '为市易之')
q('qiusheng', '金风渐起', '此城阙之秋声也')
q('yuebing', '十五日祭月', '团圆月饼也')
q('caitu', '京师以黄沙土作白玉兔', '市而易之')
q('denggao', '重阳日，北城居人多于', '弥陀塔登高')
q('tata', '法藏寺弥陀塔独空', '乐作天上矣')
q('ciqing', '都人结伴呼从', '谓菊花水可以却疾')
q('anchun', '膏粱子弟好斗鹌鹑', '千金角胜')
q('nvjie2', '有女之家', '又为女儿节云')
q('hanyi', '晚夕缄书冥楮', '曰送寒衣')
q('guoguo', '偶于稠人广座之中', '自得之甚')
q('baitadeng', '岁之十月廿五日', '恍如星斗')
q('tuochuang', '以木作床', '名曰拖床')
q('liubing', '冰上滑擦者', '名曰溜冰')
q('cuju', '金海冰上做蹙鞠之戏', '以得者为胜')
q('sizao', '廿三日更尽时', '悬挂天灯')
q('xilata', '二十七，洗疚疾', '洗邋遢')
q('diubai', '将一年食余药饵', '名丢百病')
# ---- 中元 河灯 ----
q('shuqianji', '使小内监持荷叶燃烛其中', '随波上下')
q('guapideng', '镂瓜皮，掏莲蓬', '各具一质')
# ---- 皇都品汇 ----
q('fengnian', '丰年为瑞', '聚千方之玉帛')
q('sunhuzi', '孙胡子', '滚元宵')
q('wangmazi', '王麻子', '三代钢针')
q('wuweishen', '至若饮食佳品', '尽在都门')
q('layuesanfen', '腊月诸物价昂', '贵三分之谚')
# ---- 尾屏 消寒 ----
q('xiaohantu', '至日数九', '曰九九消寒之图')
q('meilianlian', '试看图中梅黑黑', '草青青')
q('shu9a', '一九二九', '相逢不出手')
q('shu9b', '三九四九', '冰上走')
q('shu9c', '五九四十五', '穷汉街前舞')
q('shu9d', '七九六十三', '着衣单')
q('shousui', '高烧银烛', '以兆延年')

for k, v in Q.items():
    vn = norm(v)
    assert vn in srcn, 'quote not verbatim: ' + k
    assert vn, 'empty quote: ' + k

def e(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def qt(name, cls=''):
    c = (' class="' + cls + '"') if cls else ''
    return '<q' + c + '>' + e(Q[name]) + '</q>'

# 目录墙：全角空格保留，pre-wrap 展示
mulu_wall = '<div class="mulu-wall"><q>' + e(Q['muluall']) + '</q></div>'

# ---- 月令折屏 ----
PANELS = [
    ('正月', '孟春', '寅', [('星灯', 'xingdeng'), ('燕九', 'yanjiu'), ('填仓', 'tiancang')]),
    ('二月', '仲春', '卯', [('引龙过', 'yinlong'), ('占鳌头', 'zhanaotou'), ('花朝', 'huazhao')]),
    ('三月', '季春', '辰', [('纸鸢', 'zhiyuan'), ('戴柳', 'dailiu')]),
    ('四月', '孟夏', '巳', [('丰台芍药', 'fengtai'), ('天仙庙', 'tianxian')]),
    ('五月', '仲夏', '午', [('端阳', 'duanyang'), ('女儿节', 'nvrierjie'), ('雄黄', 'xionghuang'), ('冷淘面', 'lengtao'), ('旱谚', 'wuyuehan')]),
    ('六月', '季夏', '未', [('浴象', 'yuxiang'), ('赏莲', 'shanglian')]),
    ('七月', '孟秋', '申', [('乞巧', 'qiqiao'), ('蟋蟀', 'xishuai'), ('秋声', 'qiusheng')]),
    ('八月', '仲秋', '酉', [('祭月', 'yuebing'), ('彩兔', 'caitu')]),
    ('九月', '季秋', '戌', [('登高', 'denggao'), ('塔灯', 'tata'), ('辞青', 'ciqing'), ('斗鹌鹑', 'anchun'), ('又女儿节', 'nvjie2')]),
    ('十月', '孟冬', '亥', [('送寒衣', 'hanyi'), ('蝈蝈', 'guoguo'), ('白塔燃灯', 'baitadeng')]),
    ('十一月', '仲冬', '子', [('拖床', 'tuochuang'), ('滑擦', 'liubing'), ('蹙鞠', 'cuju')]),
    ('十二月', '季冬', '丑', [('祀灶', 'sizao'), ('丢百病', 'diubai'), ('洗邋遢', 'xilata')]),
]
SEACLS = ['s-sp', 's-sp', 's-sp', 's-su', 's-su', 's-su', 's-au', 's-au', 's-au', 's-wi', 's-wi', 's-wi']
panel_html = []
for i, (m, jie, zhi, items) in enumerate(PANELS):
    rows = ''.join(
        '<div class="prow"><b>' + n + '</b><div class="pqq">' + qt(k) + '</div></div>'
        for n, k in items)
    panel_html.append(
        '<div class="fold ' + SEACLS[i] + '"><button class="fh" type="button">'
        '<i class="zh mono">' + zhi + '</i><b>' + m + '</b>'
        '<span class="jj">' + jie + '</span><em class="cv">展</em></button>'
        '<div class="fb">' + rows + '</div></div>')

# ---- 市声墙 ----
SELLS = [
    ('拨浪鼓', 'xia1'), ('瓜子解闷', 'xia2'), ('江米白酒', 'xia3'),
    ('桂花头油', 'xia4'), ('合菜细粉', 'xia5'),
]
sell_html = ''.join(
    '<button class="sell" type="button" data-k="' + kid + '"><span class="sico ' + kid + '"></span>'
    '<b>' + n + '</b></button>' for n, kid in SELLS)

# ---- 烟火名色 ----
FIRE = [
    ('金盆捞月', 'f5'), ('双响震天雷', 'f1'), ('叠落金钱', 'f6'),
    ('地老鼠', 'f3'), ('升高三级浪', 'f2'), ('水老鼠', 'f4'),
]
fire_html = ''.join(
    '<button class="fcard" type="button" data-k="' + kid + '"><i class="fico ' + kid + '"></i>'
    '<b>' + n + '</b></button>' for n, kid in FIRE)

# ---- 皇都匾墙 ----
PLAQUE = [
    ('王麻子', '针铺', 'wangmazi'),
    ('孙胡子', '扁食', 'sunhuzi'),
    ('五味神', '都在都门', 'wuweishen'),
    ('丰年为瑞', '万国车书', 'fengnian'),
    ('水土贵三分', '岁暮之谚', 'layuesanfen'),
]
plaque_html = ''.join(
    '<button class="pai" type="button" data-k="' + k + '"><span class="ptop">' + t + '</span>'
    '<b>' + n + '</b><i class="pbot">' + d + '</i></button>'
    for (n, d, k), (t, _, _) in zip(PLAQUE, [('', '', '')] * len(PLAQUE)))

HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>帝京岁时纪胜 · 第肆佰伍拾贰篇</title>
<style>
:root{
  --mo:#191917; --mo2:#201f1c; --mo3:#26231d;
  --zhi:#e8e4dc; --dim:#8f887b; --line:#3a372f;
  --jin:#c9963f; --jin2:#a87c33; --zhu:#a8433c; --yue:#5e8fbb;
  --sp:#7d9a6d; --su:#5e8fbb; --au:#c07a3a; --wi:#7b8fa6;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--mo);color:var(--zhi);
  font-family:"Noto Serif CJK SC","Songti SC","STSong","SimSun",serif;
  line-height:1.9;font-size:16px}
.wrap{max-width:1080px;margin:0 auto;padding:0 26px}
.mono{font-family:"JetBrains Mono",Consolas,monospace}
q{quotes:none}
q,.qv{color:#d9d3c6}
.q{display:block;background:var(--mo2);border-left:3px solid var(--jin);
  padding:12px 18px;margin:10px 0;font-size:14.5px;line-height:2}
.kicker{display:flex;gap:18px;padding:20px 0 0;font-size:13px;
  color:var(--dim);letter-spacing:.16em}
.kicker b{color:var(--jin);font-weight:normal}
.kicker .right{margin-left:auto}
.rv{opacity:0;transform:translateY(22px);transition:opacity .8s,transform .8s}
.rv.on{opacity:1;transform:none}
h2.sec{font-size:clamp(24px,3.4vw,32px);font-weight:normal;letter-spacing:.2em;
  margin:0 0 6px}
h2.sec i{font-style:normal;color:var(--jin);font-size:.62em;letter-spacing:.3em;
  display:block;margin-bottom:6px}
.secintro{color:#b3ac9e;font-size:15px;max-width:660px;margin-bottom:26px}
section{padding:72px 0 26px}

/* ---------- hero 走马灯 ---------- */
.hero{position:relative;min-height:92vh;display:flex;align-items:center;
  overflow:hidden;border-bottom:1px solid var(--line);
  background:radial-gradient(ellipse 70% 50% at 50% 30%,#211f19,#191917 70%)}
.hero .wrap{width:100%;position:relative}
.lanst{position:relative;width:300px;height:380px;margin:0 auto}
.lan-cap{position:absolute;left:50%;transform:translateX(-50%);
  width:120px;height:16px;border-radius:8px;
  background:linear-gradient(var(--jin2),#6b5122)}
.lan-cap.top{top:0}
.lan-cap.bot{bottom:34px}
.lan-body{position:absolute;left:50%;top:16px;transform:translateX(-50%);
  width:240px;height:310px;border-radius:54px/70px;overflow:hidden;
  background:linear-gradient(180deg,#23201a,#1b1915);
  border:2px solid #3c352a;transition:box-shadow 1s}
.lit .lan-body{box-shadow:0 0 46px rgba(201,150,63,.24),inset 0 0 60px rgba(201,150,63,.13);
  border-color:#5c4d2c}
.lan-halo{position:absolute;inset:-40px;border-radius:50%;pointer-events:none;
  background:radial-gradient(ellipse at 50% 45%,rgba(201,150,63,.16),transparent 62%);
  opacity:0;transition:opacity 1.2s}
.lit .lan-halo{opacity:1}
.marow{position:absolute;top:96px;left:-100%;width:400%;height:120px;
  display:flex;align-items:flex-end;gap:44px;animation:pan 16s linear infinite;
  animation-play-state:paused}
.lit .marow{animation-play-state:running}
@keyframes pan{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.ma{flex:none;opacity:.22;transition:opacity 1.4s}
.lit .ma{opacity:.9}
.ma svg{display:block}
.lan-paper{position:absolute;inset:0;border-radius:54px/70px;pointer-events:none;
  background:repeating-linear-gradient(90deg,transparent 0 46px,rgba(232,228,220,.045) 46px 48px)}
.lan-flame{position:absolute;left:50%;bottom:44px;transform:translateX(-50%) scale(0);
  width:16px;height:26px;border-radius:50% 50% 50% 50%/62% 62% 38% 38%;
  background:radial-gradient(circle at 50% 72%,#ffe9b0 0%,#f2b04a 40%,#d0813c 78%,rgba(208,129,60,0) 100%);
  transition:transform .6s}
.lit .lan-flame{transform:translateX(-50%) scale(1);animation:flick 1.5s infinite}
@keyframes flick{0%,100%{height:26px;opacity:1}40%{height:22px;opacity:.86}70%{height:29px;opacity:.96}}
.lan-tassel{position:absolute;left:50%;bottom:0;transform:translateX(-50%);
  width:4px;height:34px;background:var(--zhu);border-radius:2px}
.lan-tassel::after{content:'';position:absolute;left:-5px;bottom:-8px;width:14px;height:14px;
  border-radius:50%;background:var(--zhu)}
.bigtitle{display:flex;gap:.06em;justify-content:center;margin-top:34px;
  font-size:clamp(46px,8.6vw,86px);letter-spacing:.1em;line-height:1.25}
.bigtitle .ch{position:relative;display:inline-block;color:#2e2b24;
  transition:color .7s ease var(--d,0s)}
.lit .bigtitle .ch{color:var(--zhi)}
.herosub{text-align:center;color:var(--dim);font-size:15px;letter-spacing:.2em;
  margin-top:18px;opacity:0;transition:opacity 1s .8s}
.lit .herosub{opacity:1}
.herosub b{color:var(--jin);font-weight:normal}
.herobtns{display:flex;gap:16px;justify-content:center;margin-top:24px}
.abtn{background:none;border:1px solid var(--jin);color:var(--jin);
  font-family:inherit;font-size:15px;letter-spacing:.34em;padding:10px 26px 10px 30px;
  cursor:pointer;transition:all .25s}
.abtn:hover{background:rgba(201,150,63,.12)}
.abtn:disabled{opacity:.32;cursor:default}
.heroseal{position:absolute;right:5%;top:14%;width:76px;height:76px;
  border:3px solid var(--zhu);color:var(--zhu);display:grid;place-items:center;
  font-size:24px;letter-spacing:2px;line-height:1.25;text-align:center;
  transform:rotate(8deg) scale(0);transition:transform .5s cubic-bezier(.2,1.6,.4,1) 1s;
  opacity:.92}
.lit .heroseal{transform:rotate(8deg) scale(1)}

/* ---------- 序 纸白 ---------- */
.paper{background:var(--zhi);color:#2b2925;border-top:1px solid #d5cfc2;
  border-bottom:1px solid #d5cfc2;padding:70px 0;margin-top:60px}
.paper h2.sec{color:#232019}
.paper h2.sec i{color:#8a6a2c}
.paper .secintro{color:#6b6557}
.paper .q{background:#f2eee4;border-left-color:#a87c33;color:#3a372f}
.xudesc{max-width:920px;font-size:15px;line-height:2.15;color:#4a463c}
.xudesc b{color:#8a6a2c;font-weight:normal}
.mulu-wall{border:1px solid #c9c2b2;background:#f2eee4;margin:26px 0 8px;max-width:920px}
.mulu-wall q{display:block;white-space:pre-wrap;line-height:2.2;
  padding:16px 20px;font-size:14px;color:#4a463c}
.mnote{font-size:12.5px;color:#8a8371;letter-spacing:.12em}

/* ---------- 元日市声 ---------- */
.noisewall{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;max-width:920px}
.sell{border:1px solid var(--line);background:var(--mo2);color:var(--zhi);
  font-family:inherit;cursor:pointer;padding:18px 8px 14px;display:flex;
  flex-direction:column;align-items:center;gap:10px;transition:all .3s}
.sell .sico{width:34px;height:34px;border-radius:50%;border:1px solid var(--line);
  position:relative;transition:all .3s}
.sell .sico::after{content:'';position:absolute;inset:9px;border-radius:50%;
  background:var(--line);transition:background .3s}
.sell.lit{border-color:var(--jin)}
.sell.lit .sico{border-color:var(--jin);box-shadow:0 0 18px rgba(201,150,63,.4)}
.sell.lit .sico::after{background:var(--jin)}
.sell b{font-weight:normal;font-size:14px;letter-spacing:.14em;color:#c9c2b4}
.sell.lit b{color:var(--zhi)}
.noiseline{display:flex;align-items:center;gap:14px;margin:22px 0 4px;flex-wrap:wrap}
.cbtn{background:none;border:1px solid var(--jin);color:var(--jin);
  font-family:inherit;font-size:14.5px;letter-spacing:.26em;padding:8px 20px 8px 24px;
  cursor:pointer;transition:background .25s}
.cbtn:hover{background:rgba(201,150,63,.12)}
.cbtn:disabled{opacity:.35;cursor:default}
.noisecount{font-size:14.5px;color:#b3ac9e}
.noisecount b{color:var(--jin);font-weight:normal;font-size:19px}
.echo{opacity:.25;transition:opacity 1s}
.echo.full{opacity:1}
.crackwall{height:4px;max-width:920px;margin-top:18px;background:#12110e;
  position:relative;overflow:hidden;border-radius:2px}
.crackwall i{position:absolute;top:0;bottom:0;width:3px;background:var(--jin);
  opacity:0}
.crackwall.boom i{animation:crack .5s ease-out}
@keyframes crack{0%{opacity:.95}100%{opacity:0}}

/* ---------- 上元烟火 ---------- */
.sky{position:relative;height:300px;max-width:920px;border:1px solid var(--line);
  background:linear-gradient(#14120e,#191713);overflow:hidden;margin-bottom:6px}
.sky .moon{position:absolute;right:8%;top:12%;width:44px;height:44px;border-radius:50%;
  background:radial-gradient(circle at 38% 34%,#efe9d8,#cfc7ad 68%,#b8ae8e);
  box-shadow:0 0 30px rgba(232,228,220,.18)}
.burst{position:absolute;width:6px;height:6px;border-radius:50%;
  background:#ffd98a;pointer-events:none}
.burst span{position:absolute;left:0;top:0;width:4px;height:4px;border-radius:50%;
  background:inherit;animation:spark 1.15s ease-out forwards}
@keyframes spark{0%{transform:translate(0,0) scale(1);opacity:1}
  100%{transform:translate(var(--dx),var(--dy)) scale(.2);opacity:0}}
.firegrid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;max-width:920px}
.fcard{border:1px solid var(--line);background:var(--mo2);color:var(--zhi);
  font-family:inherit;cursor:pointer;padding:16px 6px 12px;display:flex;
  flex-direction:column;align-items:center;gap:10px;transition:all .3s}
.fcard .fico{width:10px;height:10px;border-radius:50%;background:var(--line);transition:all .3s}
.fcard.hit{border-color:var(--jin)}
.fcard.hit .fico{background:var(--jin);box-shadow:0 0 16px rgba(201,150,63,.55)}
.fcard b{font-weight:normal;font-size:13.5px;letter-spacing:.08em;color:#c9c2b4}
.fcard.hit b{color:var(--zhi)}
.firenote{font-size:13px;color:var(--dim);letter-spacing:.12em;margin-top:10px}

/* ---------- 月令折屏 ---------- */
.foldwall{display:grid;grid-template-columns:repeat(4,1fr);gap:0;
  max-width:980px;border:1px solid var(--line);background:var(--mo2)}
.fold{border-right:1px solid var(--line);position:relative}
.fold:nth-child(4n){border-right:0}
.fold:nth-child(n+5){border-top:1px solid var(--line)}
.fold::before{content:'';position:absolute;left:0;top:0;bottom:0;width:10px;
  background:linear-gradient(90deg,rgba(0,0,0,.4),transparent);pointer-events:none}
.fh{width:100%;background:none;border:0;color:var(--zhi);font-family:inherit;
  cursor:pointer;padding:16px 12px 14px 22px;display:grid;
  grid-template-columns:auto 1fr auto;gap:8px;align-items:baseline;text-align:left}
.fh .zh{font-style:normal;font-size:12px;color:var(--dim);width:18px}
.fh b{font-weight:normal;font-size:17px;letter-spacing:.1em}
.fh .jj{font-size:12px;color:var(--dim);letter-spacing:.2em}
.fh .cv{font-style:normal;font-size:12px;color:var(--dim);transition:transform .3s}
.fold.open .fh .cv{transform:rotate(90deg)}
.s-sp .fh b{color:#a8bfa0}.s-su .fh b{color:#9ab4cf}
.s-au .fh b{color:#cf9a6a}.s-wi .fh b{color:#9daabb}
.fb{max-height:0;overflow:hidden;transition:max-height .55s ease}
.fold.open .fb{max-height:760px}
.prow{padding:2px 14px 12px 22px;border-top:1px dashed #2e2b24}
.prow b{display:block;font-weight:normal;font-size:13px;color:var(--dim);
  letter-spacing:.24em;padding:8px 0 0}
.prow .q{margin:6px 0 0;font-size:13.5px;padding:10px 14px}

/* ---------- 中元河灯 ---------- */
.river{position:relative;height:170px;max-width:920px;overflow:hidden;
  background:linear-gradient(#101318,#0d1013);border:1px solid var(--line)}
.river::after{content:'';position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent 0 26px,rgba(94,143,187,.05) 26px 27px)}
.hl{position:absolute;width:26px;height:14px;pointer-events:none;
  animation:drift linear forwards}
.hl .leaf{position:absolute;inset:0;background:#3d5c40;border-radius:60% 60% 60% 60%/100% 100% 30% 30%}
.hl .glow{position:absolute;left:8px;top:-7px;width:10px;height:10px;border-radius:50%;
  background:radial-gradient(circle,#ffe9b0,#d0813c 78%,rgba(208,129,60,0));
  box-shadow:0 0 12px rgba(255,220,140,.6)}
@keyframes drift{0%{transform:translateX(-40px)}100%{transform:translateX(980px)}}
.rivrow{display:flex;align-items:center;gap:14px;margin:16px 0 4px;flex-wrap:wrap}
.rivcount{font-size:14.5px;color:#b3ac9e}
.rivcount b{color:var(--yue);font-weight:normal;font-size:19px}
.lampnames{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}
.lampnames span{border:1px solid var(--line);color:var(--dim);font-size:13px;
  padding:4px 14px;letter-spacing:.16em;transition:all .4s}
.lampnames span.hit{border-color:var(--yue);color:var(--yue)}

/* ---------- 皇都品汇 ---------- */
.paiwall{display:flex;gap:18px;flex-wrap:wrap;justify-content:flex-start;max-width:920px}
.pai{width:128px;height:196px;background:linear-gradient(#2a251c,#221e16);
  border:1px solid #4a4232;border-radius:4px;font-family:inherit;cursor:pointer;
  color:var(--zhi);display:flex;flex-direction:column;align-items:center;
  justify-content:space-between;padding:16px 8px;transition:all .3s;position:relative}
.pai::before{content:'';position:absolute;inset:5px;border:1px solid #3c3526;
  border-radius:2px;pointer-events:none}
.pai b{font-size:19px;letter-spacing:.18em;writing-mode:vertical-rl;line-height:1.4;
  font-weight:normal}
.pai .ptop{font-size:11px;color:var(--dim);letter-spacing:.2em}
.pai .pbot{font-style:normal;font-size:11px;color:var(--dim);letter-spacing:.14em}
.pai.lit{border-color:var(--jin);box-shadow:0 0 22px rgba(201,150,63,.22)}
.pai.lit b{color:var(--jin)}
.paiq{max-width:920px}
.paiq .q{display:none}
.paiq .q.show{display:block}
.paihint{font-size:13px;color:var(--dim);letter-spacing:.14em;margin-top:12px}

/* ---------- 尾屏 消寒图 ---------- */
.tail{border-top:1px solid var(--line);margin-top:80px;padding:80px 0 90px;
  background:linear-gradient(180deg,var(--mo),#151412)}
.tailgrid{display:grid;grid-template-columns:auto 1fr;gap:56px;align-items:start}
.xht{flex:none}
.xht svg{display:block;width:min(430px,86vw);height:auto}
.petal{fill:#1d1b16;stroke:#4a4232;stroke-width:1;transition:fill 1.1s}
.petal.dyed{fill:var(--jin)}
.xhrow{display:flex;align-items:center;gap:16px;margin-top:18px;flex-wrap:wrap}
.xhcount{font-size:14.5px;color:#b3ac9e}
.xhcount b{color:var(--jin);font-weight:normal;font-size:20px}
.shuwall{display:grid;grid-template-columns:1fr;gap:6px}
.shuwall .q{margin:0;font-size:14px;opacity:.32;transition:opacity .8s}
.shuwall .q.hit{opacity:1;border-left-color:var(--zhu)}
.chun{width:92px;height:92px;border:3px solid var(--zhu);color:var(--zhu);
  display:grid;place-items:center;font-size:28px;letter-spacing:4px;margin-top:20px;
  transform:rotate(6deg) scale(0);opacity:.92;
  transition:transform .5s cubic-bezier(.2,1.6,.4,1)}
.chun.on{transform:rotate(6deg) scale(1)}
.chunline{font-size:15px;color:var(--dim);letter-spacing:.16em;opacity:0;transition:opacity 1s}
.chunline.on{opacity:1;color:var(--jin)}
.vq2{writing-mode:vertical-rl;font-size:clamp(20px,3vw,26px);letter-spacing:.4em;
  line-height:2.2;height:max-content;color:#cfc8ba;margin:6px auto 0}
.vq2 q{display:block}

footer{border-top:1px solid var(--line);padding:34px 0 46px;color:var(--dim);
  font-size:13.5px;line-height:2.05}
footer a{color:var(--jin);text-decoration:none}
footer .xiaoji{margin:8px 0}

@media (max-width:900px){
  .noisewall{grid-template-columns:repeat(3,1fr)}
  .foldwall{grid-template-columns:1fr 1fr}
  .fold:nth-child(2n){border-right:0}
  .fold:nth-child(4n){border-right:1px solid var(--line)}
  .fold:nth-child(2n){border-right:0}
  .firegrid{grid-template-columns:repeat(3,1fr)}
  .tailgrid{grid-template-columns:1fr}
}
@media (max-width:560px){
  .noisewall{grid-template-columns:repeat(2,1fr)}
  .foldwall{grid-template-columns:1fr}
  .firegrid{grid-template-columns:repeat(2,1fr)}
  .hero{min-height:80vh}
  .bigtitle{font-size:14vw}
}
</style>
</head>
<body>

<header>
  <div class="wrap">
    <div class="kicker"><span>殆知阁古代文献导读</span><b>第肆佰伍拾贰篇</b>
      <span class="right">史藏 · 地理之属</span></div>
  </div>
</header>

<div class="hero" id="hero">
  <div class="wrap">
    <div class="lanst">
      <div class="lan-halo"></div>
      <div class="lan-cap top"></div>
      <div class="lan-body">
        <div class="marow">
          <span class="ma"><svg width="72" height="104" viewBox="0 0 72 104"><path d="M30 8 L36 2 L42 8 L40 22 L52 30 L58 52 L48 56 L46 88 L54 100 L46 102 L38 90 L34 102 L26 100 L32 88 L28 56 L20 60 L14 40 L26 26 Z" fill="#0e0d0a"/></svg></span>
          <span class="ma"><svg width="86" height="96" viewBox="0 0 86 96"><path d="M10 60 L26 48 L48 46 L62 38 L74 40 L70 52 L78 58 L66 64 L58 60 L56 82 L64 92 L54 94 L46 84 L30 84 L26 94 L16 92 L24 82 L22 62 Z" fill="#0e0d0a"/><circle cx="70" cy="36" r="9" fill="#0e0d0a"/></svg></span>
          <span class="ma"><svg width="70" height="98" viewBox="0 0 70 98"><path d="M35 4 C50 4 58 16 58 28 C58 40 50 46 46 52 L52 92 L42 92 L36 68 L30 92 L20 92 L26 52 C20 46 12 40 12 28 C12 16 20 4 35 4 Z" fill="#0e0d0a"/></svg></span>
          <span class="ma"><svg width="88" height="90" viewBox="0 0 88 90"><path d="M6 58 C20 30 40 18 66 16 L82 10 L78 28 C84 46 76 64 58 70 L48 86 L40 74 L22 78 L26 64 Z" fill="#0e0d0a"/></svg></span>
          <span class="ma"><svg width="72" height="104" viewBox="0 0 72 104"><path d="M30 8 L36 2 L42 8 L40 22 L52 30 L58 52 L48 56 L46 88 L54 100 L46 102 L38 90 L34 102 L26 100 L32 88 L28 56 L20 60 L14 40 L26 26 Z" fill="#0e0d0a"/></svg></span>
          <span class="ma"><svg width="86" height="96" viewBox="0 0 86 96"><path d="M10 60 L26 48 L48 46 L62 38 L74 40 L70 52 L78 58 L66 64 L58 60 L56 82 L64 92 L54 94 L46 84 L30 84 L26 94 L16 92 L24 82 L22 62 Z" fill="#0e0d0a"/><circle cx="70" cy="36" r="9" fill="#0e0d0a"/></svg></span>
          <span class="ma"><svg width="70" height="98" viewBox="0 0 70 98"><path d="M35 4 C50 4 58 16 58 28 C58 40 50 46 46 52 L52 92 L42 92 L36 68 L30 92 L20 92 L26 52 C20 46 12 40 12 28 C12 16 20 4 35 4 Z" fill="#0e0d0a"/></svg></span>
          <span class="ma"><svg width="88" height="90" viewBox="0 0 88 90"><path d="M6 58 C20 30 40 18 66 16 L82 10 L78 28 C84 46 76 64 58 70 L48 86 L40 74 L22 78 L26 64 Z" fill="#0e0d0a"/></svg></span>
        </div>
        <div class="lan-paper"></div>
        <div class="lan-flame"></div>
      </div>
      <div class="lan-cap bot"></div>
      <div class="lan-tassel"></div>
    </div>
    <div class="bigtitle">
      <span class="ch" style="--d:.05s">帝</span><span class="ch" style="--d:.25s">京</span><span class="ch" style="--d:.45s">岁</span><span class="ch" style="--d:.65s">时</span><span class="ch" style="--d:.85s">纪</span><span class="ch" style="--d:1.05s">胜</span>
    </div>
    <p class="herosub">大兴潘荣陛撰于乾隆戊寅冬月 <b>一年十二月，按月记账</b></p>
    <div class="herobtns">
      <button class="abtn" id="btdian" type="button">点灯</button>
    </div>
    <div class="heroseal">熙朝<br>景物</div>
  </div>
</div>

<section class="rv paper">
  <div class="wrap">
    <h2 class="sec"><i>序灯</i>灯下自序</h2>
    <p class="secintro">作者潘荣陛，北京大兴人。雍正九年秋进宫当差，两年后调入史馆，得以遍看皇家藏书；后来分管宫阙工程的督销，白天黑夜连轴转。乾隆十一年冬他告老还乡，把经历过的事随手记下，攒成了几本小书。单说京城一年到头的节令风物，他觉得不该没人记，于是有了这一册。</p>
    <div class="xudesc">
      <div class="q" style="max-width:920px">@@Q:xu1@@</div>
      <p>入值史馆时他看到的，是整座帝都在过日子；笔下写的，是日子本身。自序里他给自己的定位极低，说自己不过是拿短小的笔记，录下街谈巷语：</p>
      <div class="q" style="max-width:920px">@@Q:xu3@@</div>
      <p>可紧接着那句不该没人记的实话，才是一书之眼：</p>
      <div class="q" style="max-width:920px">@@Q:xu2@@</div>
      <p class="mnote">全书正文一月一折，折里节令、景物、庙会、吃食、禁忌各有名目；岁末另附皇都品汇一节，把全城铺面数了个遍。</p>
    </div>
    <h2 class="sec" style="margin-top:34px"><i>目录</i>十二月折</h2>
    @@MULUWALL@@
    <p class="mnote">目录照录库本，全角空格为原式。</p>
  </div>
</section>

<section class="rv">
  <div class="wrap">
    <h2 class="sec"><i>元日</i>爆竹底下的叫卖</h2>
    <p class="secintro">大年初一夜里，鞭炮响成一片，可作者偏偏分神去听了鞭炮缝里的别种声音。他把四种叫卖声和拨浪鼓声一一记下，说它们和爆竹声混在一起，此起彼伏。逐个点亮这些声音，听听正月初一的都门街面。</p>
    <div class="q" style="max-width:920px">@@Q:baozhu@@</div>
    <div class="noisewall">@@SELLS@@</div>
    <div class="noiseline">
      <button class="cbtn" id="btboom" type="button">放爆竹</button>
      <span class="noisecount">已听 <b id="hearN">0</b> 声</span>
    </div>
    <div class="crackwall" id="crackwall"><i></i></div>
    <div class="q echo" id="echo1" style="max-width:920px">@@Q:maisheng1@@</div>
    <div class="q echo" id="echo2" style="max-width:920px">@@Q:maisheng2@@</div>
    <p style="color:#a59d8d;font-size:14px;margin-top:20px;max-width:920px">拜年的人怎么打招呼，他也录了实况：</p>
    <div class="q" style="max-width:920px">@@Q:xinxi@@</div>
    <p style="color:#a59d8d;font-size:14px;max-width:920px">然后是那句关于拜年的北京老话：</p>
    <div class="q" style="max-width:920px">@@Q:zouqianjia@@</div>
    <h2 class="sec" style="margin-top:40px"><i>厂甸</i>琉璃厂的年集</h2>
    <p class="secintro">新年头十六天，正阳门外变成一片书的集市。琉璃厂店一条，写尽了年节的买卖。</p>
    <div class="q" style="max-width:920px">@@Q:liulichang@@</div>
  </div>
</section>

<section class="rv">
  <div class="wrap">
    <h2 class="sec"><i>上元</i>烟火名色</h2>
    <p class="secintro">正月十三到十六，四夜灯不禁。妇女结队过桥摸门钉，家家放花。花炮有名有姓，作者一个个报了名字。点一枚名色，天上便开一朵。</p>
    <div class="q" style="max-width:920px">@@Q:jinwubujin@@</div>
    <div class="q" style="max-width:920px">@@Q:zouqiao@@</div>
    <div class="sky" id="sky"><div class="moon"></div></div>
    <div class="firegrid">@@FIRES@@</div>
    <p class="firenote" id="firenote"><span id="firedone"></span>已放 <span id="fireN">0</span> 枚 · 街头小车卖的另有俗名，还有一支卖烟火的儿歌</p>
    <div class="q" style="max-width:920px">@@Q:yanhuo1@@</div>
    <div class="q" style="max-width:920px">@@Q:dilaoshu@@</div>
    <div class="q" id="didi" style="max-width:920px;opacity:.25;transition:opacity 1s">@@Q:didijin@@</div>
  </div>
</section>

<section class="rv">
  <div class="wrap">
    <h2 class="sec"><i>月令</i>十二折屏</h2>
    <p class="secintro">全书正文就是一架十二折的屏风：每月一折，折里节令名目各有人有事。逐折展开，原句照录。</p>
    <div class="foldwall">@@FOLDS@@</div>
  </div>
</section>

<section class="rv">
  <div class="wrap">
    <h2 class="sec"><i>中元</i>河灯数千</h2>
    <p class="secintro">七月十五，先给水里的孤魂放灯。乾隆年间宫里办过一场最盛的：荷叶灯沿岸摆开数千盏，琉璃荷花灯随波上下，龙舟奏乐绕了一整圈才回。河里替他们再放一次。</p>
    <div class="river" id="river"></div>
    <div class="rivrow">
      <button class="cbtn" id="btfang" type="button">放河灯</button>
      <span class="rivcount">已放 <b id="fangN">0</b> 盏</span>
    </div>
    <div class="lampnames" id="lampnames"><span>荷叶灯</span><span>星星灯</span><span>瓜皮灯</span><span>莲蓬灯</span></div>
    <div class="q" style="max-width:920px">@@Q:shuqianji@@</div>
    <div class="q" style="max-width:920px">@@Q:guapideng@@</div>
  </div>
</section>

<section class="rv">
  <div class="wrap">
    <h2 class="sec"><i>岁末</i>皇都品汇</h2>
    <p class="secintro">全书最后压了一篇骈四俪六的铺面总账，从绸缎庄数到药铺、饭馆、香烛店，老字号报名点姓。点开牌匾，看各自的来历。</p>
    <div class="paiwall">@@PLAQUES@@</div>
    <div class="paiq" id="paiq">
      <div class="q" data-k="sunhuzi">@@Q:sunhuzi@@</div>
      <div class="q" data-k="wangmazi">@@Q:wangmazi@@</div>
      <div class="q" data-k="wuweishen">@@Q:wuweishen@@</div>
      <div class="q" data-k="fengnian">@@Q:fengnian@@</div>
      <div class="q" data-k="layuesanfen">@@Q:layuesanfen@@</div>
    </div>
    <p class="paihint">腊月的物价另有专谚，年末难买难卖，都在账里。</p>
  </div>
</section>

<div class="tail rv" id="tail">
  <div class="wrap">
    <h2 class="sec"><i>消寒</i>九九八十一瓣</h2>
    <p class="secintro">冬至起数，画一枝素梅，八十一瓣，每天染一瓣，瓣染尽就是深春。这是当年京师人家过冬的日历。替这枝梅花起染。</p>
    <div class="tailgrid">
      <div class="xht">
        @@PLUM@@
        <div class="xhrow">
          <button class="cbtn" id="btran" type="button">染一瓣</button>
          <button class="cbtn" id="btjiu" type="button">染九瓣</button>
          <span class="xhcount">已染 <b id="ranN">0</b> 瓣</span>
        </div>
        <div class="chunline" id="chunline">染到瓣尽，就是深春</div>
        <div class="chun" id="chun">春深</div>
      </div>
      <div class="shuwall">
        <div class="q">@@Q:xiaohantu@@</div>
        <div class="q" data-jiu="1">@@Q:shu9a@@</div>
        <div class="q" data-jiu="2">@@Q:shu9b@@</div>
        <div class="q" data-jiu="3">@@Q:shu9c@@</div>
        <div class="q" data-jiu="4">@@Q:shu9d@@</div>
        <div class="q">@@Q:meilianlian@@</div>
        <div class="q">@@Q:shousui@@</div>
      </div>
    </div>
    <div class="vq2" style="margin-top:44px"><q>试看图中梅黑黑 自然门外草青青</q></div>
  </div>
</div>

<footer>
  <div class="wrap">
    <p>本篇为殆知阁导读系列第452篇。文本来源：殆知阁简体库〈帝京岁时纪胜〉史藏地理库本（自序、目录、正文十二个月与皇都品汇，去空白约一万九千四百字）。仓库：<a href="https://github.com/rongyiwei/daizhige" target="_blank" rel="noopener">github.com/rongyiwei/daizhige</a>。</p>
    <p class="xiaoji">校字记：库本讹字照录，「前奇百状」之前为千字之讹，联镰飞鞚疑为联镳之讹；■〈〉式造字记号与𦶟、𬺓、𪲔等扩展区字照录不入引；目录冰床滑擦间顿号为原式。时代局限：书成于乾隆盛世笔底，香会赛神、禁忌宜忌、谶纬吉凶与男尊女卑皆两三百年前的观念现场，照录立此存照，不代今人立论；书末所附今人考语许它为清代头一部京师风俗志，属外缘事实不入引文。</p>
    <p>引文经脚本与库内文件去标点、归一逐字比对通过（@@NQ@@ 处，白话反扫六字窗零撞）。</p>
  </div>
</footer>

<script>
var io=new IntersectionObserver(function(es){es.forEach(function(e){
  if(e.isIntersecting){e.target.classList.add('on');io.unobserve(e.target)}})},{threshold:.12});
document.querySelectorAll('.rv').forEach(function(el){io.observe(el)});

var hero=document.getElementById('hero');
document.getElementById('btdian').addEventListener('click',function(){
  if(hero.classList.contains('lit'))return;
  hero.classList.add('lit');
  this.classList.add('done');this.disabled=true;this.textContent='已点';
});

var sells=document.querySelectorAll('.sell'),hearN=document.getElementById('hearN');
sells.forEach(function(b){
  b.addEventListener('click',function(){
    if(b.classList.contains('lit'))return;
    b.classList.add('lit');
    hearN.textContent=document.querySelectorAll('.sell.lit').length;
    if(hearN.textContent==='5'){
      document.getElementById('echo1').classList.add('full');
      document.getElementById('echo2').classList.add('full');
    }
  });
});
var cw=document.getElementById('crackwall');
document.getElementById('btboom').addEventListener('click',function(){
  cw.classList.remove('boom');void cw.offsetWidth;cw.classList.add('boom');
});

var sky=document.getElementById('sky'),fireN=document.getElementById('fireN');
document.querySelectorAll('.fcard').forEach(function(b){
  b.addEventListener('click',function(){
    var x=12+Math.random()*76,y=10+Math.random()*46;
    var bt=document.createElement('div');bt.className='burst';
    bt.style.left=x+'%';bt.style.top=y+'%';bt.style.background='#ffd98a';
    for(var i=0;i<14;i++){
      var s=document.createElement('span');
      var ang=Math.PI*2*i/14,r=34+Math.random()*30;
      s.style.setProperty('--dx',(Math.cos(ang)*r)+'px');
      s.style.setProperty('--dy',(Math.sin(ang)*r)+'px');
      if(i%3===0)s.style.background='#e86a4a';
      bt.appendChild(s);
    }
    sky.appendChild(bt);
    setTimeout(function(){sky.removeChild(bt)},1300);
    if(!b.classList.contains('hit')){
      b.classList.add('hit');
      var n=document.querySelectorAll('.fcard.hit').length;
      fireN.textContent=n;
      if(n===6){
        document.getElementById('didi').style.opacity=1;
        document.getElementById('firedone').textContent='六枚俱放 ';
      }
    }
  });
});

document.querySelectorAll('.fh').forEach(function(b){
  b.addEventListener('click',function(){b.parentElement.classList.toggle('open')});
});

var river=document.getElementById('river'),fangN=document.getElementById('fangN'),
    fanged=0;
document.getElementById('btfang').addEventListener('click',function(){
  for(var i=0;i<9;i++){
    var hl=document.createElement('div');hl.className='hl';
    hl.style.top=(12+Math.random()*70)+'%';
    var dur=5+Math.random()*4;
    hl.style.animationDuration=dur+'s';
    hl.innerHTML='<div class="leaf"></div><div class="glow"></div>';
    river.appendChild(hl);
    (function(node){setTimeout(function(){if(node.parentElement)node.parentElement.removeChild(node)},dur*1000)})(hl);
  }
  fanged=Math.min(108,fanged+9);
  fangN.textContent=fanged;
  var names=document.querySelectorAll('#lampnames span');
  for(var j=0;j<names.length;j++)names[j].classList.toggle('hit',fanged>=(j+1)*18);
});

document.querySelectorAll('.pai').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.paiq .q').forEach(function(qq){
      qq.classList.toggle('show',qq.getAttribute('data-k')===b.getAttribute('data-k'));
    });
  });
});

var petals=[].slice.call(document.querySelectorAll('.petal')),
    ranN=document.getElementById('ranN'),dyed=0;
function order(){return petals}
function paint(n){
  for(var i=0;i<petals.length;i++){
    petals[i].classList.toggle('dyed',i<n);
  }
  ranN.textContent=n;
  document.querySelectorAll('.shuwall .q[data-jiu]').forEach(function(qq){
    qq.classList.toggle('hit',n>=+(qq.getAttribute('data-jiu'))*9);
  });
  if(n>=81){
    document.getElementById('chunline').classList.add('on');
    document.getElementById('chun').classList.add('on');
    document.getElementById('btran').disabled=true;
    document.getElementById('btjiu').disabled=true;
  }
}
document.getElementById('btran').addEventListener('click',function(){
  if(dyed<81){dyed++;paint(dyed)}
});
document.getElementById('btjiu').addEventListener('click',function(){
  if(dyed<81){dyed=Math.min(81,dyed+9);paint(dyed)}
});
</script>
</body>
</html>
'''

# 素梅九花：三行三列，每花九瓣
import math
def plum_svg():
    out = ['<svg viewBox="0 0 460 330" aria-label="九九消寒图">']
    out.append('<path d="M20 310 C120 260 200 220 230 170 C260 220 340 260 440 310" fill="none" stroke="#3a342a" stroke-width="3"/>')
    for i in range(9):
        gx = 90 + (i % 3) * 140
        gy = 80 + (i // 3) * 100
        out.append('<g class="flower">')
        for p in range(9):
            a = math.radians(p * 40 - 90)
            px, py = gx + math.cos(a) * 20, gy + math.sin(a) * 20
            rot = p * 40
            out.append('<ellipse class="petal" data-f="%d" data-p="%d" cx="%.1f" cy="%.1f" rx="13" ry="7" transform="rotate(%.0f %.1f %.1f)"/>' % (i, p, px, py, rot, px, py))
        out.append('<circle cx="%d" cy="%d" r="7" fill="#3a342a"/>' % (gx, gy))
        out.append('</g>')
    out.append('</svg>')
    return ''.join(out)

html = (HTML.replace('@@SELLS@@', sell_html)
            .replace('@@FIRES@@', fire_html)
            .replace('@@FOLDS@@', '\n'.join(panel_html))
            .replace('@@PLAQUES@@', plaque_html)
            .replace('@@MULUWALL@@', mulu_wall)
            .replace('@@PLUM@@', plum_svg())
            .replace('@@NQ@@', str(len(Q) + 1)))  # 尾屏竖排一句也算引文
for k, v in Q.items():
    html = html.replace('@@Q:' + k + '@@', e(v))
assert '@@' not in html, 'unresolved token'

open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, len(html), 'bytes,', len(Q) + 1, 'quotes')

# ================= 反扫核验 =================
from html.parser import HTMLParser
VOID = {'br','img','input','meta','link','hr','area','base','col','embed','source','track','wbr'}

class Scan(HTMLParser):
    """栈式扫描：q 标签或 q/qv/qrow/q2/qbank 类的元素内部全部按引文计；
    文本归属最近的引文祖先，否则入白话。script/style 内容也入白话扫描。"""
    QUOTE_TAGS = {'q'}
    QUOTE_CLS = {'q', 'qv', 'qrow', 'q2', 'qbank'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.bai = []
        self.quotes = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'): self.skip += 1
        if tag in VOID: return
        cls = set((a.get('class') or '').split())
        quoted = tag in self.QUOTE_TAGS or bool(cls & self.QUOTE_CLS)
        self.stack.append([quoted, []])
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
        if tag in VOID: return
        if not self.stack: return
        quoted, buf = self.stack.pop()
        if quoted and buf:
            self.quotes.append(''.join(buf))
    def handle_data(self, d):
        if self.skip:
            self.bai.append(d); return
        for quoted, buf in reversed(self.stack):
            if quoted:
                buf.append(d); return
        self.bai.append(d)

s = Scan(); s.feed(html)

bad_q = []
for t in s.quotes:
    n = norm(t)
    if n and n not in srcn: bad_q.append(t[:40])
print('quotes parsed:', len(s.quotes), 'verbatim fails:', len(bad_q))
for b in bad_q: print('  FAIL:', b)

gram = set(srcn[i:i+6] for i in range(len(srcn) - 5))
bai = norm(''.join(s.bai))
WHITELIST = {'帝京岁时纪胜'}  # 书名六字本身即源串，按四百一十五篇先例入白名单
hits = []
for i in range(len(bai) - 5):
    w = bai[i:i+6]
    if w in gram and w not in WHITELIST:
        hits.append((i, w, bai[max(0,i-8):i+14]))
print('baihua 6-gram hits:', len(hits))
for i, w, ctx in hits[:24]:
    print('  HIT:', w, '…' + ctx + '…')

assert '—' not in html and '–' not in html, 'long dash!'
for ln, line in enumerate(html.split('\n'), 1):
    plain = re.sub(r'<[^>]+>', '', line)
    c = plain.count('·')
    assert c <= 1, f'line {ln} has {c} middots: {plain[:60]}'
print('typography ok')
if bad_q or hits:
    sys.exit(1)
print('ALL CHECKS PASS')
