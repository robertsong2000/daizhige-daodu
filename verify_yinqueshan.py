#!/usr/bin/env python3
# 银雀山汉墓竹简 导读页核验：引文逐字 + 排版红线 + mulu 编号
import re, sys

PAGE = 'yinqueshan-hanmu-zhujian.html'
LIB = '../daizhige-simplified/史藏/别史/银雀山汉墓竹简.txt'
MULU = 'mulu.html'

fails = []
def check(name, ok, detail=''):
    print(('PASS' if ok else 'FAIL'), name, detail)
    if not ok: fails.append(name)

page = open(PAGE, encoding='utf-8').read()
lib = open(LIB, encoding='utf-8').read()
flat = ''.join(lib.split())

# 1. 引文逐字（去空白保标点，<q> 内容必须是库本连续子串）
quotes = re.findall(r'<q[^>]*>(.*?)</q>', page, re.S)
check('引文数量>=8', len(quotes) >= 8, f'n={len(quotes)}')
for i, q in enumerate(quotes):
    t = ''.join(re.sub(r'<[^>]+>', '', q).split())
    ok = bool(t) and t in flat
    check(f'引文{i+1}逐字', ok, t[:34])

# 2. 禁长划线
check('无长划线', '—' not in page and '–' not in page)

# 3. 每行·至多 1 个（按块级文本行近似）
bad_dot = 0
for block in re.split(r'</(?:p|div|span|q|li|h1|h2|h3|td|th|small|figcaption|title)>|<br[^>]*>', page):
    if block.count('·') > 1:
        bad_dot += 1
check('每行·至多1个', bad_dot == 0, f'bad={bad_dot}')

# 4. 零外部依赖：无 src/@import/外链样式图片字体；仅允许页脚 github 文本与相对链接
check('无 src=、@import、<script、<img、link rel', not re.search(r'src=|@import|<script|<img|<link', page, re.I))

# 5. 无 PUA / 扩展区字
pua = [c for c in page if 0xE000 <= ord(c) <= 0xF8FF or 0x20000 <= ord(c) <= 0x3FFFF]
check('无PUA/扩展区字', not pua, f'n={len(pua)}')

# 6. 页脚三件套 + 字数自述
check('页脚三件套', all(k in page for k in ['文本来源', '引文核验', '时代局限']))
n = len(flat)
cn = '三万八千九百一十八'
check(f'库本去空白={n} 且页脚自述一致', n == 38918 and cn in page, str(n))

# 7. mulu：编号连续、无重号、计数两处一致、含本页条目
mulu = open(MULU, encoding='utf-8').read()
nums = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
check('mulu编号连续无重号', sorted(set(nums)) == list(range(1, len(nums) + 1)), f'n={len(nums)}')
check('mulu收本页', 'yinqueshan-hanmu-zhujian.html' in mulu)
check('mulu计数=条目数(kicker+页脚)',
      nums[-1] == len(nums) == 198
      and ('一百九十八篇导读合订' in mulu)
      and ('一百九十八篇导读，' in mulu))

# 8. 自检锚：卷一百一十七 存在且在本卷条目内
check('卷一百一十七·探方', '卷一百一十七 · 探方' in mulu)

print('---')
print('ALL PASS' if not fails else f'FAILED: {fails}')
sys.exit(1 if fails else 0)
