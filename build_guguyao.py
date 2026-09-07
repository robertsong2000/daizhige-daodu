# -*- coding: utf-8 -*-
"""格古要论导读页构建：引文单源注入，逐条对库断言后生成 gegu-yaolun.html"""
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/格古要论.txt'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/gegu-yaolun.html'

NO = '222'            # 篇号（发布前随 mulu 实况改）
NO_HAN = '二百二十二'

def norm(s):
    s = re.sub(r'\s+', '', s)
    s = re.sub('[-]', '', s)
    s = s.replace('囗', '')
    return s

def han(n):
    d = '零一二三四五六七八九'
    if n < 10: return d[n]
    if n < 20: return '十' + (d[n % 10] if n % 10 else '')
    if n < 100:
        return d[n // 10] + '十' + (d[n % 10] if n % 10 else '')
    return str(n)

raw = open(LIB, encoding='utf-8').read()
flat = norm(raw)
ws = ''.join(raw.split())
print('库本去空白 %d 字' % len(ws))

Q = {
 # 序
 'qx_pre':  '先子贞隠处士平生好古博雅素蓄古法帖名画古琴旧砚彛鼎尊壶之属置之斋阁以为珍玩其售之者往来尤多',
 'qx_eye':  '凡见一物必遍阅图谱究其来歴格其优劣别其是否而后已',
 'qx_aim':  '因取古铜器书画异物分高下辨真赝举其要略书而成编析门分类目之曰格古要论以示世之好事者',
 'qx_date': '洪武二十年三月望日云间曹昭明仲序',
 # 提要
 'qtj_13':     '凡分十三门曰古铜器曰古画曰古墨迹曰古碑法帖曰古琴曰古砚曰珍竒曰金铁曰古窑器曰古漆器曰锦绮曰异木曰异石',
 'qtj_fenshu': '每门又各分数目多者三四十条少者亦五六条',
 'qtj_zhong':  '故其书颇为赏鉴家所重',
 'qtj_lang':   '郎瑛七修类稿尝议其琴论后当入古笙管淳化帖后当收谱系一卷珍寳门欠楚母绿圣銕异石类欠大理仙姑异木欠伽蓝香古铜中欠布刀等钱古纸欠藏经纸',
 'qtj_defend1':'其书不过自抒闻见以为后来考古之资',
 'qtj_defend2':'要未可以一二事之偶未赅备遽訾其脱漏也',
 # 古铜器
 'qt_rust':    '铜器入土千年色纯青如翠',
 'qt_rust2':   '入水千年色纯绿如囗皮皆莹润如玉',
 'qy_weixiu':  '用酽醋调防砂末匀傅新铜器上成蜡茶色或漆色或绿色',
 'qy_zhusha':  '伪朱砂斑以漆调朱为之',
 'qt_fakebone':'然俱在外不能入骨最易辨也',
 'qt_yang':    '但有阳识者决非三代器也',
 'qt_censer':  '上古无香焚萧艾尚气臭而已故无香炉今所用者皆古之祭器鼎彛之属非香炉也',
 'qt_flower':  '古铜器入土年久受土气深用以养花花色鲜明如枝头开速而谢迟则就瓶结实陶器亦然',
 'qt_bixie':   '古铜器多能辟祟人家宜寳之',
 'qt_bixie2':  '葢山精木魅之能为祟者以歴年多尔三代钟鼎彛器歴年又过之所以能辟祟',
 'qt_mirror':  '其十二时镜能应时自鸣此古灵异器也',
 # 古画
 'qp_liufa':   '画有六法一曰气韵生动二曰骨法用笔三曰应物象形四曰随类傅彩五曰经营位置六曰传模移冩六法精论万古不移',
 'qp_sanpin':  '人莫窥其巧者谓之神品笔墨超绝传染得冝意趣有余者谓之妙品得其形似不失规矩者谓之能品',
 'qp_sanbing': '画有三病皆系用笔一曰版二曰刻三曰结',
 'qp_shifu':   '赵子昂问钱舜举曰如何是士夫画',
 'qp_star':    '董源李成近代人耳所画犹稀如星凤况晋唐名贤真迹其可得见之哉',
 'qp_silk':    '古画绢色淡黑自有一种古香可爱',
 'qp_crack':   '古绢自然破者必有鲫鱼口须连三四丝不直裂伪作者则否其绢亦新',
 'qp_nameless':'无名人画有甚佳者今人以无名命为有名不可胜数如见牛即戴嵩见马即韩干尤为可笑',
 'qp_ma':      '或峭峰直上而不见其顶或绝壁直下而不见其脚',
 'qp_wangwei': '画袁安卧雪圗有雪里芭蕉',
 # 古墨迹·古碑法帖
 'qm_xiangta':  '响榻伪墨迹用纸加碑帖上向明处以游丝笔圏却字画填以浓墨谓之响榻然圏隠隠犹存其字亦无精彩',
 'qm_xiaocheng':'唐萧诚伪为古帖示李邕曰右军真迹邕欣然曰是真物诚以实告邕复视曰细看亦未能好',
 'qm_paper':    '古墨迹纸色必表古而里新赝作者用古纸浸汁染之则表里俱透微揭视之乃见矣',
 'qm_chunhua':  '宋太宗捜访古人墨迹于淳化中命侍书王着用枣木板摹刻十卷于秘阁',
 'qm_chunhua2': '用澄心堂纸李庭珪墨拓打手揩之而不汚',
 'qm_monk':     '清凉本洪武初因寺入官其石留天界寺住持僧金西白盗去后事发其僧系狱死石遂不知所在',
 # 古琴
 'qz_duan':   '古琴以断纹为证不歴数百年不断',
 'qz_shefu':  '有蛇腹断其纹横截琴面相去或寸许或寸半',
 'qz_xiwen':  '有细纹断如髪千百条',
 'qz_meihua': '又有梅花断其纹如梅花头此最为古',
 'qz_fake':   '用琴于冬日内晒或以猛火烘琴极热以雪罨激裂之然漆色还新',
 'qz_guan':   '宋时置官局制琴其琴俱有定式长短大小如一故曰官琴但有不如式者俱是野斵',
 'qz_float':  '桐木置之水上阳面浮隂必沉反复不易',
 # 古砚
 'qy_duan':   '色黑如漆细润如玉有眼眼中有晕',
 'qy_silent': '皆扣之无声磨墨亦无声',
 'qy_sound':  '扣之磨墨皆有声',
 'qy_wuyan':  '古云无眼不成端其眼有活眼泪眼死眼活眼胜泪眼泪眼胜死眼',
 'qy_bing':   '又云眼多石中有病',
 'qy_tao':    '洮河绿石色绿如蓝润如玉发墨不减端溪下嵒出临洮大河深水底甚难得',
 'qy_she':    '色淡青黑无纹细润如玉水湿微紫',
 # 珍竒
 'qb_suju':    '白玉其色如酥者最贵',
 'qb_suju2':   '但飡色【即饭汤色】油色及有雪花者皆次之',
 'qb_shigu':   '白玉上有红如血谓之血古又谓之尸古最佳',
 'qb_yu':      '利刀刮不动温润而泽',
 'qb_guanzi':  '雪白罐子玉系北方用药于罐子内烧成者若无气眼者与真玉相似',
 'qb_shi':     '好者与真玉相似虽刀刮不动终有石性不温润',
 'qb_glass':   '其用药烧者入手轻有气眼',
 'qb_crystal': '古云千年氷化为水晶',
 'qb_agate':   '古云玛瑙无红一世穷',
 'qb_rhinostrip':'凡犀带多有角地上贴好犀作面夹成一片者可验底面花儿大小逺近更于侧向寻合缝处可见真伪',
 'qb_rhino':   '用汤煮软攅打端正者不是生犀',
 'qb_amber':   '此物于皮肤上揩热用纸片些少离寸许则自然飞起假者以羊角染色为之',
 'qb_gongqiu': '尝有象牙圎毬儿一个中直通一窍内车数重皆可转动故谓之鬼功毬',
 # 金铁
 'qj_seven':       '其色七青八黄九紫十赤以赤色为足色金也',
 'qj_zhayao':      '然只在外也',
 'qj_flowersilver':'足色者成锭面有金花次者绿花又次者黒花故谓之花银',
 'qj_bintie':      '古云识铁强如识金',
 # 古窰器
 'qk_chai':     '出北地世传柴世宗时烧者故谓之柴窰',
 'qk_chai2':    '天青色滋润细媚有细纹',
 'qk_ru':       '淡青色有蟹爪纹者真无纹者尤好土脉滋媚薄甚亦难得',
 'qk_guan':     '紫口铁足',
 'qk_guanfake': '伪者皆龙泉烧者无纹路',
 'qk_ding':     '外有泪痕者是真划花者最佳素者亦好绣花者次之',
 'qk_dingshi':  '东坡诗云定州花瓷琢红玉',
 'qk_shiyu':    '凡窰器茅篾骨出者价轻【损曰茅路曰篾无油水曰骨出此卖骨董市语也】',
 'qk_huo':      '卖骨董者称为新定器好事者以重价收之尤为可笑',
 'qk_dashi':    '以铜作身用药烧成五色花者',
 'qk_dashi2':   '又谓之鬼国窰',
 # 古漆器·锦绮
 'qq_tihong':  '剔红器无新旧但看朱厚色鲜红而坚重者为好',
 'qq_duihong': '假剔红用灰团起外面用朱漆漆之故曰堆红',
 'qn_kesi':    '其配色如傅粉',
 'qn_huohuan': '如染汚垢腻入火烧则洁白',
 # 异木·异石
 'qo_lingbi':    '其色黑如漆间有细白纹如玉',
 'qo_lingbi2':   '有卧砂不起峰亦无岩岫佳者如卧牛菡萏蟠螭扣之声清如玉快刀刮不动',
 'qo_lingbifake':'假者多以太湖石染色为之刀刮成屑',
 'qo_shouxiang': '此石能收香斋间有之香烟终日不散',
 'qo_yingshi':   '如铜鑛声倒生岩下',
 'qo_taihu':     '先雕寘急水中舂撞乆之如天成或用烟薰色黑',
 'qo_yong':      '以手摸之坳垤可验',
 'qo_touchstone':'出蜀中江水内纯黑色细润者佳',
}

bad = [k for k, v in Q.items() if norm(v) not in flat]
if bad:
    print('引文未命中库本：', bad); sys.exit(1)
print('引文 %d 条全部命中库本' % len(Q))

for k in Q:
    Q[k] = Q[k].replace('【', '<span class="zg">【').replace('】', '】</span>')

TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>格古要论 · 殆知阁导读</title>
<style>
  :root {
    --ink: #191917;
    --ink2: #201f1d;
    --paper: #e8e4dc;
    --dim: #a39e93;
    --faint: #6e6a61;
    --st: #5f9270;
    --st-soft: rgba(95,146,112,0.14);
    --red: #c0453c;
    --hairline: rgba(232,228,220,0.12);
    --hairline2: rgba(232,228,220,0.22);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    background: var(--ink); color: var(--paper);
    font-family: "Songti SC", "Noto Serif SC", "Source Han Serif SC", "SimSun", serif;
    line-height: 1.95; -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }
  .mono { font-family: "SF Mono", Menlo, Consolas, monospace; }
  .wrap { max-width: 1000px; margin: 0 auto; padding: 0 26px; }
  a { color: var(--st); }
  q { quotes: none; }
  q::before { content: "「"; color: var(--st); }
  q::after { content: "」"; color: var(--st); }
  .zg { color: var(--dim); font-size: 0.85em; }
  small.note { display: block; color: var(--dim); font-size: 0.86em; margin-top: 6px; }

  /* 首屏：戥秤 */
  .hero { position: relative; padding: 88px 0 30px; overflow: hidden; }
  .kicker { position: absolute; top: 26px; left: 0; font-size: 13px; letter-spacing: 3px; color: var(--faint); }
  .no-chip { position: absolute; top: 26px; right: 0; font-size: 13px; color: var(--dim);
    border: 1px solid var(--hairline2); padding: 3px 12px; border-radius: 20px; }
  .no-chip b { color: var(--st); }
  .beam-stage { position: relative; height: 290px; max-width: 760px; margin: 0 auto; }
  .beam-group { position: absolute; inset: 0; transform-origin: 50% 0; animation: sway 7s ease-in-out infinite alternate; }
  @keyframes sway { from { transform: rotate(0.6deg); } to { transform: rotate(-0.6deg); } }
  .pivline { position: absolute; left: 30%; top: 0; width: 1px; height: 26px; background: var(--faint); }
  .pivot { position: absolute; left: 30%; top: 18px; transform: translateX(-50%); width: 0; height: 0;
    border-left: 11px solid transparent; border-right: 11px solid transparent; border-bottom: 20px solid var(--faint); }
  .beam { position: absolute; left: 30%; top: 44px; width: 560px; height: 9px; transform: translateX(-50%);
    background: linear-gradient(90deg, #37342f, #5a554c 45%, #37342f); border-radius: 5px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.5); }
  .beam i { position: absolute; top: 50%; width: 4px; height: 4px; margin-top: -2px; border-radius: 50%;
    background: var(--st); box-shadow: 0 0 4px rgba(95,146,112,0.7); }
  .hookL, .hookR { position: absolute; top: 50px; width: 1px; height: 46px; background: var(--faint); }
  .tag { position: absolute; top: 96px; width: 54px; height: 54px; background: var(--paper); color: var(--ink);
    display: grid; place-items: center; font-size: 26px; border-radius: 3px;
    box-shadow: 0 6px 14px rgba(0,0,0,0.45); }
  .tag::before { content: ""; position: absolute; top: 5px; left: 50%; transform: translateX(-50%);
    width: 6px; height: 6px; border-radius: 50%; background: var(--ink); }
  .tag-real { left: calc(30% - 148px); transform: rotate(-5deg); }
  .tag-fake { left: calc(30% - 66px); transform: rotate(4deg); color: var(--red); }
  .seal { position: absolute; top: 92px; left: calc(30% + 246px); writing-mode: vertical-rl;
    border: 2px solid var(--red); color: var(--red); font-size: 17px; letter-spacing: 4px;
    padding: 9px 5px; border-radius: 4px; transform: rotate(6deg); background: rgba(192,69,60,0.07); }
  .hero-grid { max-width: 900px; margin: 6px auto 0; display: grid; grid-template-columns: 90px 150px 1fr; gap: 26px; align-items: end; }
  .vmeta { writing-mode: vertical-rl; color: var(--dim); font-size: 14px; letter-spacing: 4px;
    height: 220px; display: flex; flex-direction: column; gap: 16px; margin: 0 auto; }
  .vtitle { writing-mode: vertical-rl; font-size: 62px; font-weight: 700; letter-spacing: 14px;
    height: 360px; line-height: 1.2; margin: 0 auto; color: var(--paper); }
  .hero-copy { padding-bottom: 14px; }
  .hero-line { font-size: 25px; letter-spacing: 6px; color: var(--st); margin-bottom: 12px; }
  .hero-sub { color: var(--dim); font-size: 15.5px; max-width: 560px; }
  .hero-cite { margin-top: 16px; font-size: 17px; }
  .hero-hint { text-align: center; color: var(--faint); font-size: 13px; letter-spacing: 4px; margin-top: 8px; }

  /* 账头（十三门导条） */
  .ledger { position: sticky; top: 0; z-index: 60; background: var(--paper); color: var(--ink);
    box-shadow: 0 4px 14px rgba(0,0,0,0.4); }
  .ledger .wrap { display: flex; gap: 4px; align-items: center; overflow-x: auto; padding: 9px 26px; }
  .chip { flex: 0 0 auto; font-size: 13.5px; padding: 2px 11px; border-radius: 15px; color: #3c3a34;
    text-decoration: none; letter-spacing: 1px; white-space: nowrap; }
  .chip:hover { background: var(--st-soft); color: #2c4a37; }
  .chip.top { color: var(--red); font-weight: 700; }

  /* 门块通用 */
  main { padding-bottom: 20px; }
  .sec { padding: 64px 0 8px; scroll-margin-top: 56px; }
  .sec-head { display: flex; align-items: baseline; gap: 16px; margin-bottom: 8px; flex-wrap: wrap; }
  .door { flex: 0 0 auto; background: var(--paper); color: var(--ink); font-size: 13px;
    padding: 3px 10px; border-radius: 2px; letter-spacing: 2px; box-shadow: 2px 2px 0 rgba(0,0,0,0.35); }
  .sec-head h2 { font-size: 27px; letter-spacing: 5px; font-weight: 700; }
  .sec-head .en { color: var(--faint); font-size: 13.5px; letter-spacing: 2px; }
  .sec-lead { color: var(--dim); max-width: 780px; margin-bottom: 26px; font-size: 15.5px; }
  .et { padding: 20px 0 18px; border-top: 1px solid var(--hairline); }
  .et h3 { font-size: 18.5px; letter-spacing: 3px; margin-bottom: 8px; }
  .et h3 em { font-style: normal; color: var(--st); font-size: 13px; letter-spacing: 2px; margin-left: 10px; }
  .et p { font-size: 15.5px; color: #d8d4ca; max-width: 800px; }
  .et q { display: block; margin: 10px 0 4px; font-size: 16.5px; line-height: 2.05; }
  .et q.inl { display: inline; }
  .duo { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 16px 0 4px; }
  .cell { border: 1px solid var(--hairline2); border-radius: 6px; padding: 14px 16px; background: var(--ink2); }
  .cell.real { border-top: 3px solid var(--st); }
  .cell.fake { border-top: 3px solid var(--red); }
  .cell b { display: block; font-size: 14px; letter-spacing: 3px; margin-bottom: 6px; }
  .cell.real b { color: var(--st); }
  .cell.fake b { color: var(--red); }
  .cell p { font-size: 14.5px; color: #cfcabf; }
  .cell q { font-size: 15px; display: block; margin-top: 8px; }

  /* 缘起 */
  .yuan p { font-size: 16px; color: #d8d4ca; max-width: 800px; margin-bottom: 14px; }
  .luokuan { text-align: right; color: var(--dim); font-size: 15px; margin-top: 4px; }
  .tiyao { border-left: 3px solid var(--st); padding: 4px 0 4px 18px; margin: 24px 0; max-width: 820px; }
  .tiyao p { font-size: 15px; color: var(--dim); }
  .tiyao q { display: block; font-size: 16px; color: var(--paper); margin-top: 8px; }

  /* 掌眼六路 */
  .lu-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .lu-card { border: 1px solid var(--hairline2); border-radius: 8px; background: var(--ink2); padding: 20px 20px 14px; }
  .lu-glyph { width: 58px; height: 58px; border-radius: 50%; border: 1.5px solid var(--st); color: var(--st);
    display: grid; place-items: center; font-size: 30px; margin-bottom: 12px; background: var(--st-soft); }
  .lu-card h3 { font-size: 18px; letter-spacing: 3px; }
  .lu-card h3 small { color: var(--faint); font-size: 12.5px; letter-spacing: 2px; margin-left: 8px; }
  .lu-card ul { list-style: none; margin-top: 10px; }
  .lu-card li { font-size: 14.5px; color: #cfcabf; padding: 5px 0; border-top: 1px dashed var(--hairline); }
  .lu-card li b { color: var(--paper); font-weight: 600; }

  /* 断纹演示 */
  .duan-demo { border: 1px solid var(--hairline2); border-radius: 8px; background: #211f1c; padding: 22px; margin: 18px 0 8px; }
  .lacq { position: relative; height: 210px; border-radius: 6px; overflow: hidden;
    background: linear-gradient(160deg, #2e2a25, #262320 60%, #2b2721);
    box-shadow: inset 0 0 40px rgba(0,0,0,0.55); }
  .lacq .mold { position: absolute; inset: 0; transition: opacity 0.5s; }
  .m-shefu { background: repeating-linear-gradient(180deg, transparent 0 52px, rgba(232,228,220,0.30) 52px 55px, transparent 55px 78px); }
  .m-xiwen { background: repeating-linear-gradient(180deg, transparent 0 7px, rgba(232,228,220,0.16) 7px 8px); }
  .m-meihua { background-image:
    radial-gradient(circle at 18% 30%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 24% 27%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 21% 38%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 27% 35%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 16% 36%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 21% 32%, rgba(232,228,220,0.5) 0 4px, transparent 5px),
    radial-gradient(circle at 68% 62%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 74% 59%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 71% 70%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 77% 67%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 66% 68%, rgba(232,228,220,0.34) 0 3px, transparent 4px),
    radial-gradient(circle at 71% 64%, rgba(232,228,220,0.5) 0 4px, transparent 5px),
    radial-gradient(circle at 42% 80%, rgba(232,228,220,0.28) 0 2.5px, transparent 4px),
    radial-gradient(circle at 86% 18%, rgba(232,228,220,0.28) 0 2.5px, transparent 4px); }
  .m-fake { background:
    linear-gradient(73deg, transparent 31%, rgba(192,69,60,0.5) 31.3% 31.8%, transparent 32.1%),
    linear-gradient(112deg, transparent 55%, rgba(192,69,60,0.42) 55.3% 55.7%, transparent 56%),
    linear-gradient(64deg, transparent 72%, rgba(192,69,60,0.5) 72.3% 72.8%, transparent 73.1%),
    linear-gradient(129deg, transparent 18%, rgba(192,69,60,0.4) 18.3% 18.7%, transparent 19%),
    linear-gradient(94deg, transparent 84%, rgba(192,69,60,0.45) 84.3% 84.8%, transparent 85.1%),
    linear-gradient(160deg, #2e2a25, #262320 60%, #2b2721); }
  .lacq.fake .mold[data-m="fake"] { opacity: 1 !important; }
  .lacq-cap { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; align-items: center; }
  .dc-btn { flex: 0 0 auto; font-size: 13.5px; letter-spacing: 2px; padding: 4px 14px; border-radius: 16px;
    border: 1px solid var(--hairline2); color: var(--dim); background: transparent; cursor: pointer;
    font-family: inherit; }
  .dc-btn.on { border-color: var(--st); color: var(--st); background: var(--st-soft); }
  .dc-btn.warn.on { border-color: var(--red); color: #d98a84; background: rgba(192,69,60,0.1); }
  .dc-note { font-size: 13.5px; color: var(--faint); }
  .fake-reveal { display: none; margin-top: 14px; font-size: 15.5px; }
  .fake-reveal.show { display: block; }

  /* 眼品 */
  .eye-row { display: flex; gap: 26px; align-items: flex-end; flex-wrap: wrap; margin: 18px 0 6px; }
  .eye { text-align: center; }
  .eye i { display: block; width: 74px; height: 74px; border-radius: 50%; margin: 0 auto 8px;
    border: 1px solid var(--hairline2);
    background: radial-gradient(circle at 38% 34%, #efe9dd 0 7%, #c9b489 8% 26%, #7a5c30 27% 46%, #3d3021 47%, #241f18 60%); }
  .eye.tear i { background: radial-gradient(circle at 38% 34%, rgba(232,228,220,0.5) 0 6%, #a99372 7% 24%, #5c4a2c 25% 44%, #241f18 58%);
    filter: saturate(0.75); }
  .eye.dead i { background: radial-gradient(circle, #55504a 0 30%, #35322d 31% 55%, #26241f 56%);
    filter: grayscale(0.4); }
  .eye span { font-size: 14.5px; letter-spacing: 3px; color: var(--paper); display: block; }
  .eye small { color: var(--faint); font-size: 12.5px; }
  .eye-arrow { color: var(--faint); font-size: 20px; padding-bottom: 30px; }

  /* 金色阶 */
  .gold-scale { margin: 20px 0 6px; }
  .gs-bar { height: 20px; border-radius: 10px; overflow: hidden; display: flex;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.5); }
  .gs-bar span { flex: 1; }
  .gs1 { background: linear-gradient(180deg, #5d7d90, #48626f); }
  .gs2 { background: linear-gradient(180deg, #d0ab4f, #b08c33); }
  .gs3 { background: linear-gradient(180deg, #92719f, #71537d); }
  .gs4 { background: linear-gradient(180deg, #c05348, #96352e); }
  .gs-labels { display: flex; margin-top: 8px; }
  .gs-labels span { flex: 1; text-align: center; font-size: 14.5px; letter-spacing: 2px; }
  .gs-labels b { display: block; color: var(--dim); font-size: 12.5px; font-weight: 400; }
  .silver-dots { display: flex; gap: 26px; margin-top: 14px; flex-wrap: wrap; }
  .silver-dots span { font-size: 14.5px; color: #cfcabf; display: flex; align-items: center; gap: 8px; }
  .silver-dots i { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }

  /* 市语与冷笑 */
  .market { background: var(--paper); color: var(--ink); border-radius: 8px; padding: 20px 24px; margin: 18px 0;
    box-shadow: 3px 4px 0 rgba(0,0,0,0.35); transform: rotate(-0.4deg); overflow: hidden; }
  .market b { letter-spacing: 3px; font-size: 16px; }
  .market .mtag { float: right; background: var(--red); color: #f3ece0; font-size: 12px; letter-spacing: 2px;
    padding: 2px 9px; border-radius: 12px; transform: rotate(3deg); }
  .market q { color: #33302a; margin-top: 8px; display: block; font-size: 16px; }
  .market q::before, .market q::after { color: var(--red); }
  .market .zg { color: #6e6a61; }
  .laugh-duo { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 18px; }
  .laugh { border-top: 3px double var(--st); padding-top: 12px; }
  .laugh p { font-size: 14.5px; color: var(--dim); }
  .laugh q { display: block; margin-top: 8px; font-size: 15.5px; }

  /* 奇技格 */
  .qiji { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .qi-card { border: 1px solid var(--hairline2); border-radius: 8px; background: var(--ink2); padding: 22px; text-align: center; }
  .qi-card h3 { font-size: 18px; letter-spacing: 4px; margin-bottom: 10px; }
  .orb { width: 150px; height: 150px; margin: 8px auto; }
  .orb circle { fill: none; stroke: var(--st); }
  .orb .o1 { stroke-width: 2.5; opacity: 0.95; }
  .orb .o2 { stroke-width: 1.6; opacity: 0.75; stroke-dasharray: 3 5; }
  .orb .o3 { stroke-width: 1.2; opacity: 0.6; }
  .orb .o4 { stroke-width: 1; opacity: 0.5; }
  .spin1, .spin2 { transform-origin: 75px 75px; }
  .spin1 { animation: rot 26s linear infinite; }
  .spin2 { animation: rotR 18s linear infinite; }
  @keyframes rot { to { transform: rotate(360deg); } }
  @keyframes rotR { to { transform: rotate(-360deg); } }
  @media (prefers-reduced-motion: reduce) {
    .beam-group, .spin1, .spin2 { animation: none; }
  }
  .amber-scene { position: relative; height: 150px; margin: 8px auto; max-width: 240px; }
  .amber-stone { position: absolute; left: 84px; bottom: 12px; width: 52px; height: 40px; border-radius: 12px;
    background: linear-gradient(145deg, #d99a3e, #a3651f 70%);
    box-shadow: inset -4px -6px 10px rgba(0,0,0,0.35), 0 4px 10px rgba(217,154,62,0.25); }
  .paper-bit { position: absolute; left: 108px; bottom: 108px; width: 26px; height: 34px; background: var(--paper);
    border-radius: 2px; transform: rotate(-14deg); box-shadow: 0 3px 8px rgba(0,0,0,0.4); }
  .paper-bit::after { content: ""; position: absolute; left: 11px; top: -20px; border: 6px solid transparent;
    border-bottom-color: var(--dim); }
  .amber-line { position: absolute; left: 119px; bottom: 46px; width: 1px; height: 56px;
    background: repeating-linear-gradient(180deg, var(--faint) 0 4px, transparent 4px 8px); }
  .qi-card q { display: block; margin-top: 12px; font-size: 15.5px; text-align: left; }
  .qi-card p { font-size: 14px; color: var(--dim); margin-top: 8px; text-align: left; }

  /* 校字记 + 尾声 */
  .jiaoz { background: var(--paper); color: var(--ink); border-radius: 8px; padding: 24px 26px; margin: 34px 0 8px; }
  .jiaoz h3 { letter-spacing: 4px; font-size: 17px; margin-bottom: 10px; color: #3c3a34; }
  .jiaoz ul { margin-left: 4px; }
  .jiaoz li { margin-left: 18px; font-size: 14.5px; line-height: 1.9; color: #45423b; }
  .gap-duo { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 16px; margin-top: 22px; }
  .gap-list { background: var(--ink2); border: 1px dashed var(--hairline2); border-radius: 8px; padding: 20px 22px; }
  .gap-list h4, .reply h4 { font-size: 15px; letter-spacing: 3px; margin-bottom: 10px; color: var(--dim); }
  .gap-list ul { margin-left: 4px; }
  .gap-list li { margin-left: 18px; font-size: 14.5px; color: #cfcabf; padding: 3px 0; }
  .gap-list q { display: block; font-size: 15.5px; margin-bottom: 8px; }
  .reply { background: var(--ink2); border: 1px solid var(--hairline2); border-radius: 8px; padding: 20px 22px; }
  .reply q { display: block; font-size: 16px; margin: 10px 0; }
  .reply p { font-size: 14.5px; color: var(--dim); }
  .reply q.inl { display: inline; }
  .ends { margin-top: 30px; font-size: 16px; color: #d8d4ca; max-width: 800px; }
  .ends b { color: var(--st); }

  /* 页脚 */
  footer { border-top: 1px solid var(--hairline); margin-top: 60px; padding: 30px 0 44px;
    color: var(--faint); font-size: 13.5px; line-height: 2; }
  footer a { color: var(--dim); }
  footer .fin { display: block; margin-top: 10px; color: var(--dim); letter-spacing: 2px; }

  @media (max-width: 760px) {
    .kicker { display: none; }
    .beam-stage { height: 220px; transform: scale(0.62); transform-origin: 50% 0; width: 120%; margin-left: -10%; }
    .hero-grid { display: block; }
    .vmeta { writing-mode: horizontal-tb; height: auto; flex-direction: row; gap: 14px;
      font-size: 12px; justify-content: center; margin: 0 0 4px; }
    .vtitle { writing-mode: horizontal-tb; height: auto; font-size: 46px; letter-spacing: 14px;
      line-height: 1.3; text-align: center; margin: 0 0 10px; }
    .hero-copy { text-align: center; }
    .hero-sub { margin: 0 auto; }
    .lu-grid { grid-template-columns: 1fr; }
    .duo, .laugh-duo, .qiji, .gap-duo { grid-template-columns: 1fr; }
    .eye-arrow { display: none; }
  }
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <div class="kicker">殆知阁导读 · 子藏笔记 杂家类杂品之属</div>
    <div class="no-chip">之{{NO_HAN}} · <b class="mono">{{NO}}</b></div>
    <div class="beam-stage" aria-hidden="true">
      <div class="beam-group">
        <div class="pivline"></div><div class="pivot"></div>
        <div class="beam">
          <i style="left:6%"></i><i style="left:11%"></i><i style="left:16%"></i><i style="left:21%"></i>
          <i style="left:26%"></i><i style="left:31%"></i><i style="left:37%"></i><i style="left:43%"></i>
          <i style="left:49%"></i><i style="left:56%"></i><i style="left:63%"></i><i style="left:71%"></i>
          <i style="left:80%"></i>
        </div>
        <div class="hookL" style="left:calc(30% - 280px)"></div>
        <div class="hookR" style="left:calc(30% - 39px)"></div>
        <div class="tag tag-real">真</div>
        <div class="tag tag-fake">伪</div>
        <div class="seal">辨真赝</div>
      </div>
    </div>
    <div class="hero-grid">
      <div class="vmeta"><span>明 云间人 曹昭明仲 撰</span><span>据子藏笔记本</span></div>
      <h1 class="vtitle">格古要论</h1>
      <div class="hero-copy">
        <p class="hero-line">分高下 · 辨真赝</p>
        <p class="hero-sub">一部为古物定高下真赝的私家手册：铜锈要问入骨不入骨，绢断要看鲫鱼口，断纹要等数百年，金以赤色为足。今天鉴宝行当里的每一句口诀，差不多都能在这本小书里找到最早的家法。</p>
        <p class="hero-cite"><q>{{qx_eye}}</q></p>
      </div>
    </div>
    <p class="hero-hint">杆上十三星，一门一颗，往下过手</p>
  </div>
</header>

<nav class="ledger">
  <div class="wrap">
    <a class="chip top" href="#top">卷首</a>
    <a class="chip" href="#qi">缘起</a>
    <a class="chip" href="#du">掌眼六路</a>
    <a class="chip" href="#tong">古铜器</a>
    <a class="chip" href="#hua">古画</a>
    <a class="chip" href="#tie">墨迹碑帖</a>
    <a class="chip" href="#qin">古琴</a>
    <a class="chip" href="#yan">古砚</a>
    <a class="chip" href="#yu">珍竒</a>
    <a class="chip" href="#jin">金铁</a>
    <a class="chip" href="#yao">古窰器</a>
    <a class="chip" href="#qi2">漆器锦绮</a>
    <a class="chip" href="#shi2">异木异石</a>
    <a class="chip" href="#qiji">奇技</a>
    <a class="chip" href="#wei">尾声</a>
  </div>
</nav>

<main class="wrap" id="top">

  <!-- 缘起 -->
  <section class="sec yuan" id="qi">
    <div class="sec-head"><span class="door">卷首</span><h2>缘起</h2><span class="en">松江曹家，三代蓄古</span></div>
    <p>松江曹家是一座老宅子里的收藏世家。</p>
    <q>{{qx_pre}}</q>
    <p>来卖古物的贩子踏破门槛。少年曹昭跟在父亲身边，见一件东西就翻一遍图谱，把来历、优劣、真假三件事问清楚才肯罢手，一直到老。看得多了，他发现当时的纨绔子弟也在学清玩，可惜心虽好而眼不识货，于是把家学整理成编：</p>
    <q>{{qx_aim}}</q>
    <p class="luokuan"><q class="inl">{{qx_date}}</q></p>
    <div class="tiyao">
      <p>一百多年后，《四库全书》把它收进子部杂家类杂品之属，馆臣提要里点了一遍它的骨架：</p>
      <q>{{qtj_13}}</q>
      <q>{{qtj_fenshu}}</q>
      <small class="note">十三门就是杆上十三颗星。下面先看全书的读法，再按门过手。</small>
    </div>
  </section>

  <!-- 掌眼六路 -->
  <section class="sec" id="du">
    <div class="sec-head"><span class="door">读法</span><h2>掌眼六路</h2><span class="en">把八十多条家法归拢成六个动作</span></div>
    <p class="sec-lead">曹昭不大讲玄理，讲办法。把十三门里所有辨伪的路数拆开，无非六路：用眼睛看色与纹，用耳朵听声，用手去揭、去刮、去摸，用水试沉浮显隐，用火烧看变化，用药物看它做不做得出来。</p>
    <div class="lu-grid">
      <div class="lu-card">
        <div class="lu-glyph">目</div>
        <h3>目验<small>看锈看纹看断口</small></h3>
        <ul>
          <li><b>铜锈入骨</b>，伪锈浮在外表</li>
          <li><b>汝窑蟹爪纹</b>，官窑紫口铁足</li>
          <li><b>定窑泪痕</b>，划花最佳</li>
          <li><b>绢断鲫鱼口</b>，伪画裂口笔直</li>
          <li><b>端砚色黑如漆</b>，眼中有晕</li>
        </ul>
      </div>
      <div class="lu-card">
        <div class="lu-glyph">耳</div>
        <h3>耳验<small>敲一敲听一听</small></h3>
        <ul>
          <li><b>端溪下岩</b>扣之无声，上岩有声</li>
          <li><b>英石</b>声如铜矿</li>
          <li><b>灵壁石</b>声清如玉</li>
        </ul>
      </div>
      <div class="lu-card">
        <div class="lu-glyph">手</div>
        <h3>手验<small>揭刮摸掂</small></h3>
        <ul>
          <li><b>揭纸</b>，古墨迹表古而里新</li>
          <li><b>刮石</b>，假灵壁刀刮成屑</li>
          <li><b>摸石</b>，永石刀刻的花手摸得出坳垤</li>
          <li><b>掂玻璃</b>，药烧的入手轻</li>
        </ul>
      </div>
      <div class="lu-card">
        <div class="lu-glyph">水</div>
        <h3>水试<small>泡一泡见真章</small></h3>
        <ul>
          <li><b>琴材浮沉</b>，桐木阳面浮阴面沉</li>
          <li><b>歙砚水湿微紫</b>，干了就看不到</li>
          <li><b>太湖石</b>雕完丢急水里撞，撞成天成样</li>
        </ul>
      </div>
      <div class="lu-card">
        <div class="lu-glyph">火</div>
        <h3>火试<small>烧一烧见变化</small></h3>
        <ul>
          <li><b>金刚钻</b>烧红浸醋，假的酥碎</li>
          <li><b>火浣布</b>弄脏了进火一烧就白</li>
          <li><b>伪断纹</b>猛火烘极热，拿雪一激就裂（见琴席）</li>
        </ul>
      </div>
      <div class="lu-card">
        <div class="lu-glyph">药</div>
        <h3>药试<small>做旧全靠药</small></h3>
        <ul>
          <li><b>伪铜锈</b>，醋调硇砂抹新铜</li>
          <li><b>伪朱砂斑</b>，漆调朱画上去</li>
          <li><b>染古纸</b>，药水一浸表里全透</li>
          <li><b>罐子玉</b>，药罐里烧出来的白玉</li>
        </ul>
      </div>
    </div>
  </section>

  <!-- 古铜器 -->
  <section class="sec" id="tong">
    <div class="sec-head"><span class="door">门一</span><h2>古铜器论</h2><span class="en">锈入骨者为真</span></div>
    <p class="sec-lead">开卷第一门是全书鉴定学的总纲：铜器的皮色是岁月长出来的，长在骨头里；做旧做出来的皮，只浮在面上。</p>
    <div class="et">
      <h3>古铜色<em>入土与入水</em></h3>
      <q>{{qt_rust}}{{qt_rust2}}</q>
      <small class="note">囗为库本未成字空位（私用区一处），通行本或作瓜皮，见文末校字记。</small>
      <p>反过来，土蚀穿剥处像蜗篆一样自然；有斧凿痕的，就是伪品。而三等最贵的皮色，是蜡茶色、黑漆色与朱砂斑。</p>
    </div>
    <div class="et">
      <h3>伪古铜<em>醋与漆的手艺</em></h3>
      <p>怎么做旧，曹昭写得像老师傅带徒弟：</p>
      <q>{{qy_weixiu}}</q>
      <q>{{qy_zhusha}}</q>
      <q>{{qt_fakebone}}</q>
      <p>防砂以醋调之傅铜，稻草烧烟薰，新布擦光，这套配方流传了几百年。判据也只有一句：全浮在外面，进不了骨头。</p>
    </div>
    <div class="et">
      <h3>古铜款识<em>阳识断代</em></h3>
      <p>三代器用阴识，字凹进去；汉代起用阳识，字凸出来，因为阴识难铸、阳识易成。于是一条铁律立住了：</p>
      <q>{{qt_yang}}</q>
    </div>
    <div class="et">
      <h3>古香炉<em>一场器物考古</em></h3>
      <p>宋元以来把鼎彝当香炉供，曹昭说搞错了：上古烧的是萧艾，求的是气味不求烟，所以根本没有香炉。今人用的香炉，其实是古人的祭器；真正的香炉从汉代的博山炉才开始。一句冷知识，把一屋子香案翻了案。</p>
      <q>{{qt_censer}}</q>
    </div>
    <div class="et">
      <h3>古瓶养花<em>意外的实用贴</em></h3>
      <p>手册里也夹着生活小贴士：入土年久的铜器受土气深，拿来插花，花色鲜明得像还在枝头，开得快谢得慢，甚至能在瓶里结实。</p>
      <q>{{qt_flower}}</q>
    </div>
    <div class="et">
      <h3>古器辟邪<em>库本的另一面</em></h3>
      <p>这一门末尾也留着古人的信仰：铜器能镇宅，甚至说十二时镜能到点自鸣，是古灵异器。科学骨架的书里长着这样一节，不必替古人删去。</p>
      <q>{{qt_bixie}}{{qt_bixie2}}{{qt_mirror}}</q>
    </div>
  </section>

  <!-- 古画 -->
  <section class="sec" id="hua">
    <div class="sec-head"><span class="door">门二</span><h2>古画论</h2><span class="en">气韵居首，绢断为证</span></div>
    <p class="sec-lead">古画门先立品第，再教断代，最后教打假：六法三品是理论骨架，鲫鱼口是化验单。</p>
    <div class="et">
      <h3>六法三品<em>万古不移</em></h3>
      <q>{{qp_liufa}}</q>
      <p>六法之中，气韵居首，也只有它学不来：生而知之，巧密与岁月都换不来。于是分三品：</p>
      <q>{{qp_sanpin}}</q>
      <p>用笔的毛病也有名单，一共三种，全出在腕上：版是腕弱笔痴，刻是运笔迟疑妄生圭角，结是欲行不行，似物凝碍。</p>
      <q>{{qp_sanbing}}</q>
    </div>
    <div class="et">
      <h3>真迹难存<em>稀如星凤</em></h3>
      <p>为什么假画多？曹昭先算了存世账：</p>
      <q>{{qp_star}}</q>
      <p>纸绢本身脆，舒卷就损，聚在富贵之家，一场水火丧乱就举群失之。所以市面上流通的，多半要靠下面这招辨一辨。</p>
    </div>
    <div class="et">
      <h3>古画绢色<em>鲫鱼口化验单</em></h3>
      <p>真古画有年代给的包浆：</p>
      <q>{{qp_silk}}</q>
      <p>做旧的用香烟熏、灶脂煎汁染，色黄而无神。最硬的一条是裂口的形状：</p>
      <q>{{qp_crack}}</q>
      <p>自然老化的绢裂成鲫鱼口，一个裂口连着三四根丝，丝是斜的；人工撕的裂口笔直，绢也是新的。这条至今仍是书画鉴定的基本功。</p>
    </div>
    <div class="et">
      <h3>无名人画<em>两声冷笑之一</em></h3>
      <p>骨董摊上最不缺的是点名挂姓：</p>
      <q>{{qp_nameless}}</q>
      <p>见牛就是戴嵩，见马就是韩干，给无名画安名款的冲动，六百年前就被他嘲笑过了。</p>
    </div>
    <div class="et">
      <h3>马逺画<em>边角之境的出处</em></h3>
      <p>马一角的美术史名词，源头就是这几句：</p>
      <q>{{qp_ma}}</q>
      <p>峭峰不见顶，绝壁不见脚，孤舟泛月只剩一人。后人管这叫马一角，曹昭记下了它最初的样子。</p>
    </div>
    <div class="et">
      <h3>王维画<em>雪里芭蕉</em></h3>
      <p>画史著名公案也在册：王维画袁安卧雪图，雪地里长着芭蕉。张彦远说他画到兴头不问四时，桃杏芙蓉和莲花可以同作一景。</p>
      <q>{{qp_wangwei}}</q>
      <p>另有赵孟頫问钱选何为士夫画的一段对话，库本答句前疑脱一字（通行作戾家画也），照录存疑。</p>
      <q>{{qp_shifu}}</q>
    </div>
  </section>

  <!-- 古墨迹·古碑法帖 -->
  <section class="sec" id="tie">
    <div class="sec-head"><span class="door">门三·四</span><h2>古墨迹 古碑法帖</h2><span class="en">纸是最后的证人</span></div>
    <p class="sec-lead">帖学两门合并来看：一教看笔，一教看纸；碑帖部分则是一份宋刻丛帖清单，从淳化祖本一路点到元明翻刻。</p>
    <div class="et">
      <h3>响榻<em>伪墨迹工艺</em></h3>
      <q>{{qm_xiangta}}</q>
      <p>把纸蒙在碑帖上对着光描一圈再填浓墨，就是响榻。破绽：圈痕隐隐还在，字也没有精彩。</p>
    </div>
    <div class="et">
      <h3>古帖难辨<em>李邕走眼记</em></h3>
      <p>连李邕这样的大家都栽过：萧诚造假帖骗他，说是 <q class="inl">右军真迹</q>，李邕欣然说是真物；萧诚坦白后，李邕再看：</p>
      <q>{{qm_xiaocheng}}</q>
      <p>曹昭记下这桩公案，结论只有八个字：古人墨迹，未易辨也。此事出唐人记载，属通行故事，库外随文申报。</p>
    </div>
    <div class="et">
      <h3>古墨迹纸色<em>表古里新</em></h3>
      <p>这是全书最漂亮的一条物证：真古纸的旧，只在表面。</p>
      <q>{{qm_paper}}</q>
      <p>染出来的假旧，表里俱透；真传世的旧，揭开背面还是新的。一张纸的两面，隔开真伪。</p>
    </div>
    <div class="et">
      <h3>淳化阁帖<em>枣木板祖本</em></h3>
      <q>{{qm_chunhua}}</q>
      <p>法帖之祖刻在枣木板上，<q class="inl">{{qm_chunhua2}}</q>，只赐亲王大臣，人间罕得。</p>
    </div>
    <div class="et">
      <h3>兰亭帖<em>被僧人盗走的石头</em></h3>
      <p>兰亭诸本里，定武居首，清凉本次之。定武石刻建炎南渡后不知存亡；清凉本的结局像一桩案子：</p>
      <q>{{qm_monk}}</q>
      <p>洪武初年，天界寺住持金西白把石头盗走，事发系狱而死，石头从此不见。兰亭的传说，一直续写到曹昭的时代。</p>
    </div>
  </section>

  <!-- 古琴 -->
  <section class="sec" id="qin">
    <div class="sec-head"><span class="door">门五</span><h2>古琴论</h2><span class="en">断纹是琴的年轮</span></div>
    <p class="sec-lead">琴是十三门里最有实验室气质的一门：漆面裂开的纹路就是年轮，曹昭给纹路分了等级，还演示了怎么做假。</p>
    <div class="et">
      <h3>断纹琴<em>三等纹路</em></h3>
      <q>{{qz_duan}}</q>
      <p>不满几百年不裂，裂了才配称古琴。断纹分等：</p>
      <q>{{qz_shefu}}{{qz_xiwen}}</q>
      <q>{{qz_meihua}}</q>
      <p>蛇腹断横截琴面，一条隔一寸上下；细纹断千百条如发；最古的是梅花断，纹开成梅花头。</p>
    </div>
    <div class="duan-demo">
      <div class="lacq" id="lacq">
        <div class="mold m-shefu" data-m="shefu"></div>
        <div class="mold m-xiwen" data-m="xiwen" style="opacity:0"></div>
        <div class="mold m-meihua" data-m="meihua" style="opacity:0"></div>
        <div class="mold m-fake" data-m="fake" style="opacity:0"></div>
      </div>
      <div class="lacq-cap">
        <button class="dc-btn on" data-m="shefu">蛇腹断</button>
        <button class="dc-btn" data-m="xiwen">细纹断</button>
        <button class="dc-btn" data-m="meihua">梅花断</button>
        <button class="dc-btn warn" data-m="fake">伪断纹：冬日晒，猛火烘，雪罨激</button>
        <span class="dc-note">点一枚看纹样，点伪断纹看造假</span>
      </div>
      <div class="fake-reveal" id="fakereveal">
        <q>{{qz_fake}}</q>
        <p>裂是裂开了，但漆色还新。造假能催出裂纹，催不出三百年。</p>
      </div>
    </div>
    <div class="et">
      <h3>唐宋琴<em>官琴与野斵</em></h3>
      <p>唐代雷文、张越两家制琴最有名。宋代置官局制琴，规矩就大了：</p>
      <q>{{qz_guan}}</q>
      <p>尺寸统一的叫官琴，不合式的都是野斵。一句行话，分开了官窑与民窑。</p>
    </div>
    <div class="et">
      <h3>古琴阴阳材<em>水上浮沉</em></h3>
      <p>琴面用阳材，向日那面；琴底用阴材，背日那面。辨认办法最物理不过：不论新旧，桐木放水上，</p>
      <q>{{qz_float}}</q>
      <p>阳材琴早上浊傍晚清，晴浊雨清；阴材琴正相反。一张琴的早晚音色，取决于那块木头当年朝着太阳还是背着太阳。</p>
    </div>
  </section>

  <!-- 古砚 -->
  <section class="sec" id="yan">
    <div class="sec-head"><span class="door">门六</span><h2>古砚论</h2><span class="en">无眼不成端</span></div>
    <p class="sec-lead">砚门是一场产地分级学：端溪下岩封顶，歙溪龙尾紧随，洮河深水底里的绿石管保发墨。辨认全靠色、声、水三相。</p>
    <div class="et">
      <h3>端溪下岩<em>色黑如漆</em></h3>
      <q>{{qy_duan}}</q>
      <p>六七枚石眼相连，排成星斗。庆历年间这一坑就采竭了，所以后世所见，多半要打个问号。最贵的一等石，扣上去没有声音：</p>
      <q>{{qy_silent}}</q>
      <p>反观上岩石，<q class="inl">{{qy_sound}}</q>，久用就光得像镜面。听声即分高下。</p>
    </div>
    <div class="et">
      <h3>歙溪洮河<em>两块名石</em></h3>
      <p>歙溪龙尾的旧坑石：</p>
      <q>{{qy_she}}</q>
      <p>水一湿，淡青黑里透出紫色，隐隐还有白纹排成山水星月；干了就什么都看不见。南唐开坑，到北宋取尽。另一块传说中的石头在临洮大河的深水底：</p>
      <q>{{qy_tao}}</q>
      <p>绿如蓝，润如玉，发墨不输端溪下岩。曹昭补了一句大实话：甚难得。市面上叫洮石的，多半是别处的石头磨的。</p>
    </div>
    <div class="et">
      <h3>眼品<em>眼分三等</em></h3>
      <p>端石以眼为贵，眼又分三等，一等压一等：</p>
      <div class="eye-row">
        <div class="eye"><i></i><span>活眼</span><small>最胜</small></div>
        <div class="eye-arrow">胜</div>
        <div class="eye tear"><i></i><span>泪眼</span><small>次之</small></div>
        <div class="eye-arrow">胜</div>
        <div class="eye dead"><i></i><span>死眼</span><small>又次之</small></div>
      </div>
      <q>{{qy_wuyan}}</q>
      <p>但曹昭紧接着记下另一句行话，替买家留了个心眼：</p>
      <q>{{qy_bing}}</q>
      <p>贵眼又怕眼多，一块石头的身世，全在两句话的张力里。</p>
    </div>
  </section>

  <!-- 珍竒 -->
  <section class="sec" id="yu">
    <div class="sec-head"><span class="door">门七</span><h2>珍竒论</h2><span class="en">玉宝犀珀的化验单</span></div>
    <p class="sec-lead">珍竒门是全书的珠宝柜台：玉分九色，琥珀会静电，犀角看合缝，玻璃看气眼。曹昭验宝，条条落到手感上。</p>
    <div class="et">
      <h3>玉器<em>九色与如酥</em></h3>
      <q>{{qb_suju}}{{qb_suju2}}</q>
      <p>白玉以色如酥为最贵，库本自注：飡色即饭汤色。老玉还要看皮：<q class="inl">{{qb_shigu}}</q>，土古是洗不掉的一重黄土。玉出自西域的于阗，<q class="inl">{{qb_yu}}</q>，是这一门的天花板。</p>
    </div>
    <div class="et">
      <h3>假玉两种<em>药烧与石性</em></h3>
      <div class="duo">
        <div class="cell fake"><b>罐子玉</b><p>北方用药在罐子里烧成，没有气眼的，几乎乱真：</p><q>{{qb_guanzi}}</q><p>但比真玉多了蝇脚纹，久了不润，而且极脆。</p></div>
        <div class="cell fake"><b>石类玉</b><p>茅山石、水石，冷得发白，好的也能乱真：</p><q>{{qb_shi}}</q><p>刮是刮不动，可终究有石性，不温不润，宜细验。</p></div>
      </div>
      <p>玻璃（库本作玻瓈）同理：真者器皿多碾雨点花，<q class="inl">{{qb_glass}}</q>，入手轻，与琉璃相似。</p>
    </div>
    <div class="et">
      <h3>俗谚两签<em>行话里的价值表</em></h3>
      <q>{{qb_crystal}}</q>
      <q>{{qb_agate}}</q>
      <p>一句讲年头，一句讲成色，宝石行情被两句话说完。琥珀更有趣，那是一种会飞的宝石，见奇技格。</p>
    </div>
    <div class="et">
      <h3>犀角<em>贴面与合缝</em></h3>
      <p>犀角带造假，用的是木器贴皮的老手艺：</p>
      <q>{{qb_rhinostrip}}</q>
      <p>好犀贴在角地上夹成一片，底面花纹对不上，侧面还能找到合缝。至于煮软了再攅打端正的，<q class="inl">{{qb_rhino}}</q>，生犀的纹路骗不了行家。</p>
    </div>
  </section>

  <!-- 金铁 -->
  <section class="sec" id="jin">
    <div class="sec-head"><span class="door">门八</span><h2>金铁论</h2><span class="en">颜色即仪器</span></div>
    <p class="sec-lead">金银的成色，曹昭给了一套色谱。没有化验仪器，颜色就是仪器。</p>
    <div class="et">
      <h3>金<em>足色色谱</em></h3>
      <q>{{qj_seven}}</q>
      <div class="gold-scale">
        <div class="gs-bar"><span class="gs1"></span><span class="gs2"></span><span class="gs3"></span><span class="gs4"></span></div>
        <div class="gs-labels">
          <span>七青<b>七成金发青</b></span>
          <span>八黄<b>八成金发黄</b></span>
          <span>九紫<b>九成金发紫</b></span>
          <span>十赤<b>足色金发赤</b></span>
        </div>
      </div>
      <p>成色不够的，掺了银的石试色青，火烧不黑；和了红铜的，试石有声而落屑。假金还要过一道药：</p>
      <q>{{qj_zhayao}}</q>
      <p>燔硝绿矾盐煎水刷金，烘出焦色再洗净，不黄再刷。刷得再黄，只在外头。</p>
    </div>
    <div class="et">
      <h3>银<em>花银三级</em></h3>
      <q>{{qj_flowersilver}}</q>
      <div class="silver-dots">
        <span><i style="background:#e6c34a"></i>金花，足色</span>
        <span><i style="background:#7fae7f"></i>绿花，次之</span>
        <span><i style="background:#4a4a48"></i>黑花，又次之</span>
      </div>
      <p>锭面有金花的才配叫花银。面有黑斑而不光泽的，里头必有黑铅。造假的花银，用密陀僧做。</p>
    </div>
    <div class="et">
      <h3>镔铁<em>花纹自现</em></h3>
      <p>西蕃镔铁面上自带旋螺花与芝麻雪花两种纹，刀剑打磨光净后，金丝矾一矾花纹就现，价钱贵过银子。曹昭借行家的话收尾：</p>
      <q>{{qj_bintie}}</q>
    </div>
  </section>

  <!-- 古窰器 -->
  <section class="sec" id="yao">
    <div class="sec-head"><span class="door">门九</span><h2>古窰器论</h2><span class="en">蟹爪纹与泪痕</span></div>
    <p class="sec-lead">古窑器门是后世谈瓷绕不开的一页：柴、汝、官、定这些名字在这里并排出现，判词个个具体。</p>
    <div class="et">
      <h3>柴窰<em>传说级</em></h3>
      <q>{{qk_chai}}</q>
      <q>{{qk_chai2}}</q>
      <p>柴世宗时烧的，天青，滋润细媚，多足粗黄土，近世少见。两字天青，是后世无数仿品追赶的影子。</p>
    </div>
    <div class="duo">
      <div class="cell real"><b>汝窰</b><p>淡青色，宋时烧：</p><q>{{qk_ru}}</q><p>有蟹爪纹的为真，没有纹的反而更好。土脉滋媚，薄得很，也难得。</p></div>
      <div class="cell real"><b>官窰</b><p>宋修内司烧，土脉细润，色青带粉红，浓淡不一：</p><q>{{qk_guan}}</q><p>伪的都出自龙泉，破绽：<q class="inl">{{qk_guanfake}}</q></p></div>
    </div>
    <div class="et">
      <h3>古定器<em>泪痕与花瓷</em></h3>
      <q>{{qk_ding}}</q>
      <p>定窑白瓷，以有泪痕的为真，划花最佳，素也好，绣花次之。宣和政和间的窑最好，还出紫定、墨定，色黑如漆。苏东坡的诗作证：</p>
      <q>{{qk_dingshi}}</q>
    </div>
    <div class="et">
      <h3>卖骨董市语<em>行话入书</em></h3>
      <div class="market">
        <span class="mtag">库本自注</span>
        <b>骨董行的行话，曹昭原样收进书里，还自带注释：</b>
        <q>{{qk_shiyu}}</q>
      </div>
      <p>窑器有毛病的，行里叫茅、篾、骨出：损了叫茅，路纹叫篾，没有油水叫骨出。连黑话都注明词义，这是一部手册的自我修养。</p>
    </div>
    <div class="et">
      <h3>霍器<em>两声冷笑之二</em></h3>
      <p>霍州金匠彭君宝仿古定烧折腰样，整齐得很，叫彭窰。土脉细白的与定相似，就是滑口欠滋润，极脆，不甚值钱。于是一幕熟悉的戏上演：</p>
      <q>{{qk_huo}}</q>
      <p>仿品被当成新定器，好事者重价收之。六百年前曹昭就笑过的局，今天还在拍场上演。</p>
    </div>
    <div class="et">
      <h3>大食窰<em>鬼国窰</em></h3>
      <q>{{qk_dashi}}</q>
      <p>铜作胎，用药烧出五色花，与拂郎嵌是一路货，即今天所说的掐丝珐琅。曹昭的评语不太客气：只好放进妇人闺阁，不算文房清玩，<q class="inl">{{qk_dashi2}}</q>。文人的偏见，也给一件工艺留下了名字。</p>
    </div>
  </section>

  <!-- 古漆器·锦绮 -->
  <section class="sec" id="qi2">
    <div class="sec-head"><span class="door">门十·十一</span><h2>古漆器 锦绮</h2><span class="en">看朱厚，试火烧</span></div>
    <div class="et">
      <h3>剔红<em>一句总纲</em></h3>
      <q>{{qq_tihong}}</q>
      <p>剔红不分新旧，只看朱漆厚不厚、色鲜不鲜、胎子重不重。宋朝内府的剔红，底下多是金银素胎；元末西塘的张成、杨茂两家最得名。</p>
    </div>
    <div class="et">
      <h3>堆红<em>假剔红</em></h3>
      <q>{{qq_duihong}}</q>
      <p>灰团堆起个样子，外面罩朱漆，所以叫堆红，又叫罩红。与铜器的锈、纸色的旧一个道理：真的长在里头，假的罩在外头。</p>
    </div>
    <div class="et">
      <h3>火浣布<em>进火一烧就白</em></h3>
      <p>锦绮门里录着一件西域奇货：布弄脏了不要洗，</p>
      <q>{{qn_huohuan}}</q>
      <p>所谓火浣布，即石棉织物，库本火防毛三字形讹（见校字记）。又一等刻丝，宋时旧织，<q class="inl">{{qn_kesi}}</q>，配色像傅粉一样匀净，又称颜色作。</p>
    </div>
  </section>

  <!-- 异木·异石 -->
  <section class="sec" id="shi2">
    <div class="sec-head"><span class="door">门十二·十三</span><h2>异木 异石</h2><span class="en">案头清玩的产地表</span></div>
    <div class="et">
      <h3>灵壁石<em>收香的石头</em></h3>
      <p>灵壁县深山里掘出来的黑石头，形状好的像卧牛、菡萏、蟠螭：</p>
      <q>{{qo_lingbi}}{{qo_lingbi2}}</q>
      <p>曹昭还记了一桩玄事：<q class="inl">{{qo_shouxiang}}</q>。假的呢，多拿太湖石染色，刀刮就成屑。</p>
      <q>{{qo_lingbifake}}</q>
    </div>
    <div class="et">
      <h3>太湖石<em>流水线天成</em></h3>
      <p>苏州太湖石，出水的那道工序听着就不像天然的：</p>
      <q>{{qo_taihu}}</q>
      <p>先雕好，丢进急水里冲撞得久了，如同天成，或者拿烟薰黑。古人造景与造假的边界，本来就在同一道工序上。</p>
    </div>
    <div class="et">
      <h3>英石<em>叩之如铜</em></h3>
      <p>英石倒生岩下，以锯取之，底平而起峰，几案间的奇玩。敲起来是另一路声音：</p>
      <q>{{qo_yingshi}}</q>
    </div>
    <div class="et">
      <h3>永石<em>手摸坳垤</em></h3>
      <p>永州石不坚，好的面上有山水、日月、人物之像，多是刀刮成的，不是自然长出来的。验法：<q class="inl">{{qo_yong}}</q>。指腹比眼睛诚实。</p>
    </div>
    <div class="et">
      <h3>试金石<em>门名的回声</em></h3>
      <p>异石门收尾是一块黑色小石头：</p>
      <q>{{qo_touchstone}}</q>
      <p>试金石磨金辨色，用盐洗去，湿地上放一会，胡桃油一揩，还能再用，宜常用袋盛之。整本格古要论，就是骨董行的试金石。</p>
    </div>
  </section>

  <!-- 奇技格 -->
  <section class="sec" id="qiji">
    <div class="sec-head"><span class="door">附录</span><h2>奇技格</h2><span class="en">两条差点被当成传说的记录</span></div>
    <div class="qiji">
      <div class="qi-card">
        <h3>鬼功毬</h3>
        <svg class="orb" viewBox="0 0 150 150" aria-hidden="true">
          <circle class="o1" cx="75" cy="75" r="70"/>
          <g class="spin1">
            <circle class="o2" cx="75" cy="75" r="52"/>
            <circle class="o3" cx="75" cy="75" r="36"/>
          </g>
          <g class="spin2">
            <circle class="o3" cx="75" cy="75" r="20"/>
            <circle class="o4" cx="75" cy="75" r="8"/>
          </g>
        </svg>
        <q>{{qb_gongqiu}}</q>
        <p>一整块象牙，中心通一窍，里面车出数层，层层都能转。鬼工球后来成了广州牙雕的绝艺，曹昭记下的这条是它最早的文字身影之一，还补了一句：或云出自宋内院。</p>
      </div>
      <div class="qi-card">
        <h3>琥珀飞纸</h3>
        <div class="amber-scene" aria-hidden="true">
          <div class="paper-bit"></div>
          <div class="amber-line"></div>
          <div class="amber-stone"></div>
        </div>
        <q>{{qb_amber}}</q>
        <p>布上摩擦生热，纸片离一寸自然飞起。这是静电吸纸的最早中文记录之一，两千多年前泰勒斯玩过同一招；而假琥珀以羊角染色，热了一试便知。真伪与物理，在一条词条里相遇。</p>
      </div>
    </div>
  </section>

  <!-- 尾声 -->
  <section class="sec" id="wei">
    <div class="sec-head"><span class="door">卷尾</span><h2>缺口单与回批</h2><span class="en">后人挑刺，四库回护</span></div>
    <p class="sec-lead">一部手册最好的命运，是有人拿放大镜挑毛病。明人郎瑛在七修类稿里给曹昭开了一张补货单，乾隆年间的四库馆臣替他回了批。</p>
    <div class="gap-duo">
      <div class="gap-list">
        <h4>郎瑛的缺口单</h4>
        <q>{{qtj_lang}}</q>
        <ul>
          <li>琴论后面补笙管</li>
          <li>淳化帖后收谱系一卷</li>
          <li>珍宝门补祖母绿、圣铁</li>
          <li>异石补大理、仙姑</li>
          <li>异木补伽蓝香</li>
          <li>古铜补布刀等钱</li>
          <li>古纸补藏经纸</li>
          <li>珍奇后再设羽皮一类</li>
          <li>文房器物也该谈一谈</li>
        </ul>
      </div>
      <div class="reply">
        <h4>四库馆臣的回批</h4>
        <q>{{qtj_defend1}}</q>
        <q>{{qtj_defend2}}</q>
        <p>这话乍听有理，馆臣先让半步，再顶回去：不能拿一两件事没写到，就说人家脱漏。结束语是<q class="inl">{{qtj_zhong}}</q>。</p>
      </div>
    </div>
    <p class="ends">从洪武二十年到今天，六百多年：曹昭的十三门裂变成整个古玩行当，鲫鱼口与蟹爪纹成了通用语，那套金色谱还在秤上。这本小书没有一条现代意义的科学结论，但它立下了一个行当的基本姿势：<b>先看东西，再谈价钱；凡说真，拿出证据。</b></p>
    <div class="jiaoz">
      <h3>校字记（库本讹字与空位申报）</h3>
      <ul>
        <li>射赫云画有六法：射赫通行作谢赫，形近而讹。</li>
        <li>伪古铜条防砂末：防砂不成词，通行作硇砂（卤砂），以醋调之傅铜做锈是旧法。</li>
        <li>火浣布条火防毛织者：防毛字讹，所指即不燃之毛。</li>
        <li>铜色条色纯绿如囗皮：囗为库本未成字空位（私用区一处），通行或作瓜皮，存疑不论。</li>
        <li>士夫画条钱选答句作家画也：家上疑脱一字，通行作戾家画也。</li>
        <li>提要内类书囗事体例有殊：囗为库本未成字空位（私用区一处），本页未引此句。</li>
      </ul>
    </div>
    <div class="jiaoz" style="margin-top:14px">
      <h3>时代局限提醒</h3>
      <ul>
        <li>古器辟邪、十二时镜应时自鸣、灵壁收香等，属古人信仰与博物传闻，读时自辨。</li>
        <li>火浣布即石棉织物，石棉尘有害健康，切勿效仿试验。</li>
        <li>犀角、象牙、玳瑁、鹤顶、珊瑚等物，今多在保护之列，本书只作历史文献读。</li>
        <li>大食、回回、倭、鞑靼、髙丽、于阗等皆当时称谓，今已不用。</li>
      </ul>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    文本来源：殆知阁简体库 子藏笔记《格古要论》（去空白一万二千三百七十九字），页面无外部依赖。<br>
    本篇引文{{QCOUNT}}条已与库内文件逐字核验（去空白比对，私用区空位与囗互删），实测数据以库本正文与四库提要为准。<br>
    所录工艺与观念皆十四世纪之物，其见识与局限同在，今人读之当自辨之。<br>
    <a href="https://github.com/robertsong2000/daizhige-daodu">github.com/robertsong2000/daizhige-daodu</a> · 系列总目见 <a href="mulu.html">mulu.html</a>
    <span class="fin">之{{NO_HAN}} 格古要论 · 2026 年 9 月</span>
  </div>
</footer>

<script>
(function(){
  var lacq=document.getElementById('lacq');
  var btns=document.querySelectorAll('.dc-btn');
  var fr=document.getElementById('fakereveal');
  function show(m){
    lacq.classList.toggle('fake', m==='fake');
    document.querySelectorAll('.mold').forEach(function(d){
      d.style.opacity = (d.dataset.m===m) ? 1 : 0;
    });
    btns.forEach(function(b){ b.classList.toggle('on', b.dataset.m===m); });
    if(m==='fake'){ fr.classList.add('show'); } else { fr.classList.remove('show'); }
  }
  btns.forEach(function(b){
    b.addEventListener('click', function(){ show(b.dataset.m); });
  });
  show('shefu');
})();
</script>
</body>
</html>
'''

html = TEMPLATE
for k, v in Q.items():
    html = html.replace('{{%s}}' % k, v)
html = html.replace('{{NO}}', NO).replace('{{NO_HAN}}', NO_HAN).replace('{{QCOUNT}}', han(len(Q)))
left = re.findall(r'\{\{\w+\}\}', html)
if left:
    print('未替换占位符：', left); sys.exit(1)
for i, line in enumerate(html.splitlines(), 1):
    if '—' in line or '–' in line:
        print('发现长划线 L%d：%s' % (i, line[:60])); sys.exit(1)
    if line.count('·') > 1:
        print('一行多· L%d：%s' % (i, line[:80])); sys.exit(1)
open(OUT, 'w', encoding='utf-8').write(html)
print('已写出', OUT, len(html), '字节')
