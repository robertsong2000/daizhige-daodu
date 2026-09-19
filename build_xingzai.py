#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""行在阳秋导读页构建：全部 <q> 引文自库本锚点切片生成，零誊写。"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'daizhige-simplified', '史藏', '志存记录', '行在阳秋.txt')
TPL = os.path.join(HERE, 'xingzai-yangqiu.tpl.html')
OUT = os.path.join(HERE, 'xingzai-yangqiu.html')

# key: (start_anchor, end_anchor or None)
SLICES = {
    'janguo':   ('永明王监国肇庆', '以明年为永历元年'),
    'yingli':   ('谓天下不可一日无君', '乃迎桂嗣王至肇庆立之'),
    'tangwang': ('唐王自立于广东', '改元绍武'),
    'haikou':   ('唐王兵伪降', '人马尽陷，兵大溃'),
    'd0q':      ('上即皇帝位于肇庆', None),
    'shuizhan': ('我兵水陆', '可上下扼也'),
    'd4q':      ('改武岗为奉天府', None),
    'd5q':      ('朝官星散', '不复存上下纲纪'),
    'd6q':      ('文武诸臣皆微服而行', None),
    'd7q':      ('今日江', '住桂以出楚'),
    'd12q':     ('驾离滇都', '传幸永昌'),
    'd13q':     ('出沐国公印相对', '乃信'),
    'd14q':     ('构草房十大间', '每日百余兵守护'),
    'd15q':     ('令人奉上居滇', '严兵防守'),
    'wenchang': ('乘虚数十骑冲入文昌门', '城中大惊'),
    'yingxian': ('琏矢无虚发', '应弦而毙者半'),
    'xiaohao':  ('琏曰：枵号奈何', '士益乐用命'),
    'xiyang':   ('式耜与琏分门婴守', '用西洋铳击中胡骑'),
    'yiguan':   ('式耜衣冠危坐署中', None),
    'tongchang': ('泅水过江入桂林', '愿与式耜同殉国'),
    'yisheng':  ('事已至此', '夫复何言'),
    'sisishi':  ('我二人多活了四十日', '今日事毕矣'),
    'sisuo':    ('今日得死所矣', None),
    'jue1':     ('从容待死与城亡', None),
    'jue2':     ('头丝犹带满天香', None),
    'leiting':  ('雷霆冬发', '征在公也'),
    'zhijiu':   ('置酒楼船', '梧州系龙洲之上下'),
    'shuidian': ('起恒手书', '挂小牌于御舟前'),
    'shuidianzi': ('「水殿」', None),
    'minyao':   ('汉宫秋也', '昭阳愁也'),
    'buluo':    ('上饮至中宵', '有败报也'),
    'jiangshu': ('东宫问杨在曰', '在不能对'),
    'chumian':  ('能主入缅者', '必能主乎出缅'),
    'zhibao':   ('掷皇帝之宝', '命掌玺太监李国用碎之'),
    'mensheng': ('你们要收门生', '特把朕作人情耳'),
    'jiajiao':  ('朕已航闽', '都与截杀'),
    'xibao1':   ('毕竟衣冠文物好看', None),
    'xibao2':   ('于天曰：如此', '代为疏请'),
    'qinwang':  ('金堡以祖制无有', '阻之'),
    'jiqi':     ('可望密遣人击起恒于邓州之滨', '几殆'),
    'huoxin':   ('包藏祸心', '贻祸封疆'),
    'wuzhenyu': ('除赐辅臣吴贞毓死外', None),
    'youde':    ('定国偏师轻骑', '有德自刎'),
    'jiaoshui': ('十九日战于交水', '可望奔溃'),
    'liewu':    ('后随出猎', '被射死'),
    'zhoushui1': ('我王初立', '请去吃咒水'),
    'bing3000': ('缅酋以兵三千围所扎处', None),
    'zhoushui2': ('尔等大汉', '即乱枪杀死'),
    'tianbo':   ('有沐天波', '各伤缅兵数人而死'),
    'laian1':   ('有银与你', None),
    'laian2':   ('抵腰假作取银', '刺伤缅兵而死'),
    'quan':     ('太后年老', '将谁为依'),
    'yilou':    ('大小二百四十余人', '声闻里外'),
    'jiujie':   ('缅酋将天波至城上', '以示城外'),
    'luobai':   ('王及诸将士皆下马罗拜', '声振天地'),
    'jiquan':   ('遂大剿孟坑城外', '鸡犬不留而去'),
    'taiqu':    ('数蛮子将上连杌子抬去', None),
    'beisheng': ('太后等悲声震天', None),
    'namian':   ('上南面坐', '达旦'),
    'gu':       ('固然', '有太后在'),
    'shierling': ('朕本北京人', '尔能任之乎'),
    'ou1':      ('初甚倨傲', '见上长揖'),
    'ou2':      ('三桂噤不敢对', None),
    'ou3':      ('始称名应诏', None),
    'ou4':      ('色加死灰', '汗流浃背'),
    'ou5':      ('自后', '不复敢见'),
    'gongyi1':  ('此吾君也', '南北皆然'),
    'gongyi2':  ('上勉饮三爵', '遂触地而死'),
    'zhenzhu':  ('此真主也', None),
    'qiebian':  ('满、汉诸大臣皆割辫而起', None),
    'gongxian': ('以弓弦绞于市', None),
    'taizi':    ('黠贼', '乃至此耶'),
    'fengmai':  ('是日，天大昏黑', '人影不见'),
    'zhisha':   ('三桂使人炙尸扬灰', '传赐诸将'),
    'liri':     ('命造历日', None),
    'cong':     ('从邓凯请也', None),
    'dengkai':  ('不受，为僧去', None),
    'jingxian': ('晋王李定国薨于景线', None),
    'longyu':   ('而龙驭宾天', '辛丑三月十八日也'),
    'kaoyi':    ('此云壬寅', '未知何据'),
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
        frag = frag.strip()
        html = html.replace(token, '<q>%s</q>' % frag)

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
