import json, re

SRC = '../daizhige-simplified/史藏/地理/台海使槎录.txt'
t = open(SRC, encoding='utf-8').read()

def pick(start, end):
    i = t.index(start)
    j = t.index(end, i) + len(end)
    return t[i:j]

QUOTES = {
    # 甲 针路
    'q_xu':        pick('凡禽鱼草木之细', '而后即安'),
    'q_feirenlei': pick('语言不通，袒裸盱雎', '殆非人类'),
    'q_zhenlu':    pick('放洋全以指南针为信', '曰针路。'),
    'q_xunzhen':   pick('由彭湖至台湾向巽方行', '仍回彭湖。'),
    'q_feng':      pick('台湾风信，与他海殊异', '为九降。'),
    'q_fengcao':   pick('土番识风草', '多节则多次。'),
    'q_lei':       pick('六月一雷止三台', '七月一雷九台来'),
    'q_heishui':   pick('自初三日登舟', '舟人大恐。'),
    'q_hudie':     pick('风中蝴蝶千百飞舞', '舟人以为不祥。'),
    'q_shuixian1': pick('惟有划水仙求登岸免死耳', '免死耳！'),
    'q_shuixian2': pick('众口齐作钲鼓声', '得不溺'),
    # 乙 六考矩阵 36 格
    'xj_jc':   pick('备酒豕邀请番众', '长数丈'),
    'xj_ys':   pick('一舂秫米使碎', '曰姑待'),
    'xj_yshi': pick('麻达走递公文', '瞬息数十里'),
    'xj_hs':   pick('婚姻名曰牵手', '不需媒妁'),
    'xj_sz':   pick('番死曰马歹', '殉之。'),
    'xj_qy':   pick('螺钱皆汉人磨砻而成', '各社皆然。'),
    'dwz_jc':  pick('架梯入室，极高耸宏敞', '门绘红毛人像。'),
    'dwz_ys':  pick('每年以黍熟时为节', '歌呼呜呜'),
    'dwz_yshi': pick('他里雾以上，多为大耳', '名曰马卓'),
    'dwz_hs':  pick('亦有不用定聘', '合意遂成夫妇'),
    'dwz_sz':  pick('父母死，服皂衣', '守丧三月'),
    'dwz_qy':  pick('出入必佩小刀', '击之即瘥'),
    'bx_jc':   pick('大小同居一室', '曰猫邻'),
    'bx_ys':   pick('半线以北，取海泥卤曝为盐', '以腌鱼虾'),
    'bx_yshi': pick('每年二月间力田之候', '曰包练'),
    'bx_hs':   pick('婚姻曰绵堵混', '或送糯饭'),
    'bx_sz':   pick('番死，老幼裹以草席', '呼为马邻'),
    'bx_qy':   pick('耕种捕鹿具', '竹筒为汲桶'),
    'dd_jc':   pick('猫雾拺诸社，凿山为壁', '俯首而行'),
    'dd_ys':   pick('舂为饼饵', '名都都'),
    'dd_yshi': pick('猫雾拺、岸里以下诸社', '止露两目'),
    'dd_hs':   pick('男以银锡约指赠女为定', '曰猫六'),
    'dd_sz':   pick('十二日后，请番神姊祈禳除服', '除服。'),
    'dd_qy':   pick('无升斗，以篾篮较准', '与汉人交易'),
    'bs_jc':   pick('惟娶妇赘婿', '另室而居'),
    'bs_ys':   pick('又蒸熟置罂缶中', '蒸其液为酒'),
    'bs_yshi': pick('麻达编五色篾', '以便奔走'),
    'bs_hs':   pick('娶妇先以海蛤数升为聘', '生鹿肉为定'),
    'bs_sz':   pick('番死，男女老幼皆裸体', '舁至山上'),
    'bs_qy':   pick('耕种犁耙诸器', '多仿汉人。'),
    'sds_jc':  pick('贮米另为小室', '名曰圭茅'),
    'sds_ys':  pick('又有香米倍长大', '不售也'),
    'sds_yshi': pick('性好洁', '或浴于溪'),
    'sds_hs':  pick('琴削竹为弓', '名曰突肉'),
    'sds_sz':  pick('挂蓝布旛竿', '通社闭户。'),
    'sds_qy':  pick('汲水用大葫芦', '曰大蒲仑'),
    # 番歌
    'sg_xingang': pick('马无艾几唎', '回来便相赠'),
    'sg_madou':   pick('唉加安吕燕', '心中欢喜难说'),
    'sg_wanli':   pick('朱连么吱匏里乞', '彼此便觉好看'),
    'sg_langqiao': pick('立孙呵网直', '得罪得罪'),
    # 丙 界与商
    'q_yifu':   pick('各社终身依妇以处', '有以也'),
    'q_sheka':  pick('郡县有财力者', '名曰社商'),
    'q_shegun': pick('利番人之愚', '贫则力不敢抗'),
    'q_aini':   pick('是举世所当哀矜者', '莫番若矣'),
    'q_yiren':  pick('噫！若亦人也', '何必异其性'),
    'q_zhong1': pick('向为番民鹿场麻地', '存什一于千百'),
    'q_zhong2': pick('土番膏血有几', '虽欲不穷得乎'),
    'q_jieshi': pick('竖石以限之', '越入者有禁'),
    'q_fanyi':  pick('问何故跣足', '可见人性皆同'),
    'q_dongfu': pick('因与道府约', '以滋扰累'),
    'q_fantong': pick('余劳以酒食', '或可渐易也'),
    'q_chenwen': pick('草鸡夜鸣', '太和千纪'),
    'q_chenjie': pick('识者曰：鸡', '为群盗也'),
    'q_chenwei': pick('六十年海氛', '异哉'),
}

norm = lambda s: re.sub(r'\s', '', s)
tn = norm(t)
bad = []
for k, v in QUOTES.items():
    nv = norm(v)
    if nv not in tn:
        bad.append(k)
    if '■' in v or '—' in v or '–' in v:
        bad.append(k + ' [PUA/长划线]')
    print(k, '|', v)
assert not bad, bad

json.dump(QUOTES, open('quotes_taihai.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('OK', len(QUOTES), 'quotes -> quotes_taihai.json')
