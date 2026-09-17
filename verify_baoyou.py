#!/usr/bin/env python3
# 引文核验：baoyou-dengkelu.html 对 库内文件 史藏/传记/宋宝祐四年登科录.txt
# 1) .q 引文与库本去标点、异体归一后逐字比对
# 2) 白话转述六字窗反向扫描
# 3) 禁用字符（长划线、en dash）检查
# 4) 顺带生成 quotes_baoyou.json（引文切片清单）
import json, re, sys
from html.parser import HTMLParser

PAGE = 'baoyou-dengkelu.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/传记/宋宝祐四年登科录.txt'

raw = open(SRC, encoding='utf-8').read()

def keep_cjk(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0xE000 <= o <= 0xF8FF:          # PUA 占位字
            out.append('\u25a1')
        elif (0x3400 <= o <= 0x4DBF or 0x4E00 <= o <= 0x9FFF
              or 0xF900 <= o <= 0xFAFF or 0x20000 <= o <= 0x2A6DF):
            out.append(ch)
    return ''.join(out)

flat = keep_cjk(re.sub(r'[\s\u3000]+', '', raw))

html = open(PAGE, encoding='utf-8').read()

# ---------- 3) 禁用字符 ----------
bad_chars = []
for name, pat in [('em dash —', '\u2014'), ('en dash –', '\u2013'),
                  ('horizontal bar ―', '\u2015')]:
    if pat in html:
        bad_chars.append(name)
if bad_chars:
    print('[FAIL] 禁用字符:', bad_chars); sys.exit(1)
print('[ok] 无长划线、en dash')

# ---------- 解析 HTML，收集 .q 与白话 ----------
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes = []      # (qid, text)
        self.prose = []       # 白话文本块
        self._q = None
        self._buf = []
        self._skip = 0        # script/style
        self._in_body = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'body': self._in_body = True
        if tag in ('script', 'style'): self._skip += 1
        if self._skip == 0 and self._in_body and 'q' in (a.get('class') or '').split():
            self._q = a.get('data-qid')
            self._buf = []
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self._skip = max(0, self._skip - 1)
        if self._q is not None and tag not in ('script', 'style'):
            self.quotes.append((self._q, ''.join(self._buf)))
            self._q = None
    def handle_data(self, d):
        if self._skip: return
        if not self._in_body: return
        if self._q is not None:
            self._buf.append(d)
        else:
            self.prose.append(d)

p = P(); p.feed(html)

# ---------- 1) 引文比对 ----------
fails = 0; uniq = 0
records = {}
for qid, text in p.quotes:
    norm = keep_cjk(re.sub(r'[\s\u3000]+', '', text))
    if not norm:
        print(f'[FAIL] {qid}: 引文为空'); fails += 1; continue
    c = flat.count(norm)
    records[qid] = {'display': text.strip(), 'run': norm, 'count': c, 'chars': len(norm)}
    if c < 1:
        print(f'[FAIL] {qid}: 未在库本命中 <<{norm[:40]}...>>'); fails += 1
    else:
        uniq += 1 if c == 1 else 0
print(f'[{"ok" if fails==0 else "FAIL"}] 引文 {len(p.quotes)} 条，比对通过 {len(p.quotes)-fails} 条（其中唯一命中 {uniq} 条）')
if fails: sys.exit(1)

# ---------- 2) 白话反扫 ----------
hits = []
for blk in p.prose:
    norm = keep_cjk(blk)
    for i in range(len(norm) - 5):
        w = norm[i:i+6]
        if w in flat and not set(w) <= {'□'}:
            hits.append((blk.strip()[:24], w))
if hits:
    print(f'[FAIL] 白话反扫命中 {len(hits)} 处：')
    for ctx, w in hits[:20]:
        print('   ', ctx, '<<', w, '>>')
    sys.exit(1)
print('[ok] 白话反扫六字窗零撞')

json.dump(records, open('quotes_baoyou.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'[ok] quotes_baoyou.json 已更新（{len(records)} 条）')
