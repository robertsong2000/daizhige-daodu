#!/usr/bin/env python3
"""方言语引文核验：页面所有「」引文与库内文件去标点+异体字归一后逐字比对。"""
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/儒藏/小学/方言.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/fangyan.html'

# 异体字/库本讹字归一
VARIANT = {
    '𬨎': '輶', '蔵': '藏', '扵': '于', '髙': '高', '徃': '往',
    '畧': '略', '寛': '宽', '荅': '答', '鐡': '铁', '軰': '辈',
}

def norm(s: str) -> str:
    for k, v in VARIANT.items():
        s = s.replace(k, v)
    return re.sub(r'[^\w]', '', s)

src = norm(open(SRC, encoding='utf-8').read())
page = re.sub(r'<[^>]+>', '', open(PAGE, encoding='utf-8').read())  # 去标签

quotes = re.findall(r'「([^」]+)」', page)
extra = ['神明焕然顿还旧观', '往凡语也', '病不斟']  # 未加引号的直引点

fails, checked = [], 0
for q in quotes:
    nq = norm(q)
    checked += 1
    if nq not in src:
        fails.append(q)

for q in extra:
    checked += 1
    if norm(q) not in src:
        fails.append('[直引点]' + q)

print(f'核对引文 {checked} 条，通过 {checked - len(fails)} 条，失败 {len(fails)} 条')
for q in fails:
    print('FAIL:', q)
sys.exit(1 if fails else 0)
