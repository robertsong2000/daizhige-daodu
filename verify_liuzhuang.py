#!/usr/bin/env python3
"""核验 liuzhuang-xiangfa.html：引文逐字比对库内文件 + 明史跨库辅证 + 排版红线。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'liuzhuang-xiangfa.html'
SRC_BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/易藏/术数/柳庄相法.txt'
SRC_MINGSI = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/正史/明史.txt'
VOID = {'br', 'meta', 'link', 'img', 'hr', 'input', 'wbr'}

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

class QCollector(HTMLParser):
    """收集全部 class 含 q 的 span/div 文本（回溯最近 q 祖先，VOID 不入栈）。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []       # (tag, is_q, buf)
        self.found = []       # (text, data_src)
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        cls = dict(attrs).get('class', '') or ''
        is_q = 'q' in cls.split()
        src = dict(attrs).get('data-src', '')
        self.stack.append([tag, is_q, src, []])
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                node = self.stack.pop(i)
                text = ''.join(node[3])
                if node[1]:
                    self.found.append((text, node[2]))
                if self.stack:
                    self.stack[-1][3].append(text)
                break
    def handle_data(self, data):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][1]:
                self.stack[i][3].append(data)
                return

def main():
    html_raw = open(PAGE, encoding='utf-8').read()
    book = open(SRC_BOOK, encoding='utf-8').read()
    mingsi = open(SRC_MINGSI, encoding='utf-8').read()
    nbook, nms = norm(book), norm(mingsi)
    errors, warns = [], []

    # ---- 红线：长划线与每行·计数 ----
    for ch, name in [('—', '——(U+2014)'), ('–', '–(U+2013)')]:
        if ch in html_raw:
            errors.append(f'红线：页面出现 {name}')
    style_end = html_raw.find('</style>')
    for ln, line in enumerate(html_raw[style_end:].split('\n'), 1):
        if line.count('·') > 1:
            errors.append(f'红线：第{ln}行有 {line.count("·")} 个 ·')

    # ---- 引文收集 ----
    col = QCollector()
    body = html_raw[html_raw.find('<body'):]
    col.feed(body)
    qs = [(norm(t), s) for t, s in col.found if norm(t)]
    print(f'页面 .q 计数（norm 后非空）: {len(qs)}')
    if len(qs) != 47:
        warns.append(f'.q 数量 {len(qs)} ≠ 预期 47，请确认是否有新增引文未申报')

    for i, (qn, src) in enumerate(qs, 1):
        srcname = '明史' if src == 'ms' else '柳庄相法'
        hay = nms if src == 'ms' else nbook
        if qn not in hay:
            errors.append(f'引文{i:02d} [{srcname}] 页面有而库本无: {qn[:42]}...')
        if src == 'ms' and qn in nbook:
            warns.append(f'引文{i:02d} 标注明史但库本也有（两书同文，可接受）: {qn[:24]}')

    # ---- 「」提及反扫（≥6 字须在源内） ----
    text_only = re.sub(r'<[^>]+>', '', body)
    for m in re.finditer('「([^」]+)」', text_only):
        c = norm(m.group(1))
        if len(c) >= 6 and c not in nbook and c not in nms:
            errors.append(f'「」提及不在任何源内: {c}')

    # ---- 库本机数 ----
    checks = [
        ('曰 计数', book.count('曰'), 216), ('日 计数', book.count('日'), 0),
        ('诗曰 计数', book.count('诗曰'), 32), ('书云 计数', book.count('书云'), 71),
        ('一世禄重问', book.count('一世禄好则不如何说'), 2),
    ]
    for name, got, want in checks:
        if got != want:
            errors.append(f'{name}: {got} ≠ 期望 {want}')
        else:
            print(f'机数 {name} = {got} ✓')

    C = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
    def cn(s):
        if '十' in s:
            a, b = s.split('十')
            return (C[a] if a else 1) * 10 + (C[b] if b else 0)
        return C[s]
    book_end = book.find('中册、永乐百问')
    heads = [cn(h) for h in re.findall(r'\n([一二三四五六七八九十]{1,4})、', book[:book_end])]
    if len(heads) == 94 and max(heads) == 95 and 76 not in heads:
        print('机数 上册 94 节缺七十六 ✓')
    else:
        errors.append(f'上册节号异常: {len(heads)} 节 max {max(heads)}')
    qn_nums = [cn(h) for h in re.findall(r'\n([一二三四五六七八九十]{1,4})、', book[book_end:book.find('下册')])]
    if sorted(qn_nums) == list(range(1, 75)):
        print('机数 永乐百问 一至七十四无缺 ✓')
    else:
        errors.append('永乐百问条号有缺')
    seg12 = book[book.find('七十三、十二宫'):book.find('七十四、十八上贵')]
    pal = ['命宫','财帛宫','兄弟宫','田宅宫','男女宫','奴仆宫','妻妾宫','疾厄宫','迁移宫','官禄宫','福德宫','相貌宫']
    pos = [seg12.find(p + '。') if seg12.find(p + '。') >= 0 else seg12.find(p) for p in pal]
    if all(p >= 0 for p in pos) and pos == sorted(pos):
        print('机数 十二宫 按序在位 ✓')
    else:
        errors.append('十二宫缺失或乱序')

    # ---- 页面结构 ----
    if body.count('class="plaque"') == 9 and body.count('plaque king') == 1:
        print('结构 卫士九人 + 燕王一枚 ✓')
    else:
        errors.append('卫士名牌数量不符（应 9+1）')
    if body.count('class="item"') == 4:
        print('结构 永乐百问四卡 ✓')
    if body.count('class="tome"') == 3:
        print('结构 天地人三册 ✓')
    ms_n = body.count('data-src="ms"')
    if ms_n != 18:
        warns.append(f'明史跨库引文 {ms_n} 处 ≠ 预期 18')
    else:
        print(f'结构 明史跨库引文 {ms_n} 处 ✓')
    for frag in ['殆知阁简体库', '引文经核验', '时代的局限', '之一百零七', '柳庄相法']:
        if frag not in html_raw:
            errors.append(f'页脚/版面缺关键串: {frag}')
    for bad in ['questions', 'instrument', 'designer']:
        if bad in html_raw:
            errors.append(f'英文残留: {bad}')

    print()
    for w in warns:
        print('警告:', w)
    if errors:
        print(f'\n✗ {len(errors)} 项失败')
        for e in errors:
            print('  ✗', e)
        sys.exit(1)
    print(f'\n✓ 全部通过：{len(qs)} 条引文双侧逐字命中 + 红线 + 机数 + 结构')

if __name__ == '__main__':
    main()
