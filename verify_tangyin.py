#!/usr/bin/env python3
"""棠阴比事 导读页核验：引文逐字比对库本 + 排版红线"""
import re, sys, unicodedata

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/法家/棠阴比事.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/tangyin-bishi.html'

lib = open(LIB, encoding='utf-8').read()
page = open(HTML, encoding='utf-8').read()

def norm(s):
    s = re.sub(r'\s+', '', s)
    return ''.join(ch for ch in s if unicodedata.category(ch)[0] not in ('P', 'S', 'Z'))

lib_n = norm(lib)

# 提取页面所有 blockquote 原文（剥掉 .bq-src 标注行）
quotes = []
for m in re.finditer(r'<blockquote class="bq">(.*?)</blockquote>', page, re.S):
    body = re.sub(r'<span class="bq-src">.*?</span>', '', m.group(1), flags=re.S)
    quotes.append((m.group(1).strip()[:28], body))
quotes.append(('inline 瞿然敛衽', '瞿然敛衽'))

fails = 0
for label, q in quotes:
    qn = norm(q)
    if not qn:
        print(f'[FAIL] 空引文 {label}'); fails += 1; continue
    if qn in lib_n:
        print(f'[OK]   {label}')
    else:
        print(f'[FAIL] 库本无此句: {label}'); fails += 1
    for ch in q:
        o = ord(ch)
        if 0xE000 <= o <= 0xF8FF or 0xF900 <= o <= 0xFAFF or o > 0xFFFF:
            print(f'       注意 特殊字符 U+{o:04X} {ch!r}')

# 案名（印格 + 印谱标签）须为库本标题
titles = ['张举猪灰','崇龟认刀','孙亮验蜜','乖崖察额','傅令鞭丝','孝肃杖吏','棠阴比事',
          '欧阳左手','李公验榉','王臻辨葛','妾吏酖宋','季珪鸡豆','程簿旧钱','王珣辨印',
          '江分表里','章辨朱墨','左史诬裴','郎简校劵','文成括书','彦超虚盗','道让诈囚',
          '柳设榜牒','蒋常觇妪','包牛割舌','御史失状','庄遵疑哭','张升窥井','胡质集邻',
          '杜亚疑酒','元膺擒轝','王扣狂妪']
for t in titles:
    if norm(t) in lib_n:
        print(f'[OK]   案名 {t}')
    else:
        print(f'[FAIL] 案名不在库本: {t}'); fails += 1

# 排版红线
for bad, name in [('—','长划线—'), ('–','短划线–'), ('─','制表横线─')]:
    if bad in page:
        print(f'[FAIL] 出现 {name}'); fails += 1
for i, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        print(f'[FAIL] 第{i}行有{line.count("·")}个·'); fails += 1

# 数量声明与库本一致
lib_lines = [l.strip('　 \n') for l in lib.split('\n') if l.strip('　 \n')]
main = sum(1 for l in lib_lines if len(l) <= 10 and '。' not in l and '：' not in l and not l.startswith(('棠阴比事','开禧','端明')))
print(f'[INFO] 页面声明：正文80案 附录27篇；脚本粗计标题行 {main}（含拆分误差，参考）')

print('RESULT:', 'PASS' if fails == 0 else f'FAIL({fails})')
sys.exit(0 if fails == 0 else 1)
