#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""池北偶谈导读页核验：
1. 每个 <q> 的可见文本（剥内层标签）去标点归一后必须是库本子串；
2. 白话反扫：页面全部非 q 可见文本的六字滑窗不得命中库本；
3. 硬性排版：不得出现长划线；每行 · 最多一个。
"""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, 'chibei-outan.html')
SRC = os.path.join(HERE, '..', 'daizhige-simplified', '史藏', '志存记录', '池北偶谈.txt')

PUNCT = re.compile(r'[\s\W_a-zA-Z0-9]+', re.UNICODE)

def norm(s):
    return PUNCT.sub('', s)

def main():
    html = open(HTML, encoding='utf-8').read()
    src = norm(open(SRC, encoding='utf-8').read())
    fails = 0

    qs = re.findall(r'<q[\s\S]*?</q>', html)
    if not qs:
        print('FAIL: 页面没有任何 <q>'); return 1
    for q in qs:
        txt = norm(re.sub(r'<[^>]+>', '', q))
        if not txt:
            print(f'FAIL: 空 q: {q[:60]}'); fails += 1; continue
        if txt not in src:
            print(f'FAIL: q 不在库本: {txt[:50]}'); fails += 1
    print(f'q 通道: {len(qs)} 条, 失败 {fails}')

    body = re.sub(r'<script[\s\S]*?</script>', '', html)
    body = re.sub(r'<style[\s\S]*?</style>', '', body)
    body = re.sub(r'<q[\s\S]*?</q>', '\n', body)
    body = re.sub(r'<[^>]+>', '', body)
    plain = norm(body)
    hits = []
    for i in range(len(plain) - 5):
        w = plain[i:i + 6]
        if w in src:
            hits.append(w)
    if hits:
        print(f'FAIL: 白话反扫命中 {len(hits)} 处:')
        seen = set()
        for w in hits:
            if w not in seen:
                seen.add(w)
                idx = plain.find(w)
                print(f'  [{w}] 上下文: …{plain[max(0, idx - 10):idx + 16]}…')
        fails += len(hits)
    else:
        print('白话反扫: 六字窗零撞')

    if '—' in html or '–' in html:
        print('FAIL: 出现长划线'); fails += 1
    else:
        print('长划线: 无')

    dotbad = 0
    for line in html.split('\n'):
        if line.count('·') > 1:
            print(f'FAIL: 一行多个·: {line.strip()[:60]}'); dotbad += 1
    if not dotbad:
        print('间隔号: 每行至多一个')
    fails += dotbad

    print('RESULT:', 'PASS' if fails == 0 else f'FAIL x{fails}')
    return 0 if fails == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
