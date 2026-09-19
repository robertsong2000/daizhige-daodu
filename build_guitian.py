#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归田诗话导读页构建：全部 <q> 引文自库本锚点切片生成，零誊写。"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'daizhige-simplified', '诗藏', '诗话', '归田诗话.txt')
TPL = os.path.join(HERE, 'guitian-shihua.tpl.html')
OUT = os.path.join(HERE, 'guitian-shihua.html')

SLICES = {
    'jie_zong':  ('诗虽能致祸，然亦能解患', None),
    'shao_shi':  ('宋宗窗下对谈高', '割烹何必用牛刀'),
    'shao_zeng': ('瞿君有子早能诗', '定应高折广寒枝'),
    'shao_nian': ('时予年始十四云', None),
    'ba_zhu':    ('入为国子助教', '升周府右长史'),
    'ba_zhi':    ('谓其坐辅导失职', '罪窜保安'),
    'ba_huan':   ('洪熙乙巳赦还', None),
    'xu_jishu':  ('因笔录其有关于诗道者', '目曰《归田诗话》'),
    'wei_shi':   ('万户伤心生野烟', '凝碧池边春天管弦'),
    'wei_mian':  ('及唐收复两京', '见此诗，得免'),
    'bai_shi':   ('邯郸四十万', '或冀一人生'),
    'dong_shi':  ('圣主如天万物春', '十口无归更累人'),
    'dong_chu':  ('神宗见而怜之', '黄州团练副使'),
    'zhe_1':     ('朔风吹沙目欲眯', '带束蓝袍靴露趾'),
    'zhe_2':     ('一声爆竹人尽靡', '明日春光万馀里'),
    'zhe_3':     ('里胥临门', '遂成诗谶'),
    'zhe_4':     ('在任以乏', '归骨西湖'),
    'zang_shi':  ('一去西川隔夜台', '只有存斋冒雨来'),
    'ling_shi':  ('予视先生犹大父行', '喜后进之有人也'),
    'hu_tong':   ('时三人与予同寓保安', '子昂死焉。悲夫'),
    'teng_song': ('见予每诵元遗山', '若不能堪者'),
    'teng_zu':   ('滕与予同庚', '未得解脱云'),
    'dao_nei':   ('予自遭难', '不意爱成永别'),
    'yi_1':      ('五日过居庸', '不洒离别间'),
    'yi_2':      ('生男莫作班定远', '一去紫台空珮环'),
    'ke_di':     ('及谪居塞外', '吟咏不废'),
    'ke_qiong':  ('世谓“诗必穷而后工”', '岂信然哉'),
    'ke_chou':   ('实足以丑奸臣', '而已哉'),
    'mu_cheng':  ('非先生以诚而得古人作诗之要', '评之当哉'),
    'ba_yin':    ('所谓诗祸', '不能悉其故矣'),
    'ouyang':    ('昔欧阳文忠公致仕后', '亦窃“归田”之号'),
    'xu_xi':     ('不觉欣然而喜', '堕泪者屡矣'),
    'xu_gt':     ('辍耕垅上', '地位虽殊，而心事则无异也'),
    'xu_gai':    ('知我者见此', '一慨云'),
    'xu_wei':    ('予久羁山后', '不复经理'),
}

def main():
    src = open(SRC, encoding='utf-8').read()
    html = open(TPL, encoding='utf-8').read()
    fails = 0

    for key, (s, e) in SLICES.items():
        token = '{{Q:%s}}' % key
        if token not in html:
            print('WARN: 模板未使用 token %s' % key)
            continue
        n = src.count(s)
        if n != 1:
            print('FAIL: 锚 %s（%s）出现 %d 次' % (key, s, n)); fails += 1; continue
        i = src.find(s)
        if e is None:
            frag = s
        else:
            j = src.find(e, i + len(s))
            if j < 0:
                print('FAIL: 终锚 %s 未找到（%s）' % (key, e)); fails += 1; continue
            frag = src[i:j + len(e)]
        html = html.replace(token, '<q>%s</q>' % frag.strip())

    leftover = html.count('{{Q:')
    if leftover:
        print('FAIL: 残留 token %d 个' % leftover); fails += 1

    if fails == 0:
        open(OUT, 'w', encoding='utf-8').write(html)
        print('BUILD OK: %s（%d 条引文切片）' % (os.path.basename(OUT), len(SLICES)))
    else:
        print('BUILD FAILED x%d' % fails)
    return 1 if fails else 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
