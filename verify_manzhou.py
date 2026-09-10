import re, sys

HTML = 'manzhou-jishen-jitian-dianli.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/政书/满洲祭神祭天典礼.txt'

ALT = {'幙':'幕','䌷':'绸','脗':'吻','𬊈':'燖'}

def norm(s):
    s = re.sub(r'【[^】]*】', '', s)
    out = []
    for ch in s:
        if ch in ALT:
            ch = ALT[ch]
        if ch.isspace():
            continue
        o = ord(ch)
        if o < 0x2000 or (0x3000 <= o <= 0x303f) or (0xff00 <= o <= 0xffef):
            continue
        out.append(ch)
    return ''.join(out)

lib = norm(open(LIB, encoding='utf-8').read())

html = open(HTML, encoding='utf-8').read()
qs = re.findall(r'<q class="qi">(.*?)</q>', html, re.S)
qs += re.findall(r'<div class="zan">\s*(.*?)\s*</div>', html, re.S)
assert len(qs) == 11, f'expect 11 q, got {len(qs)}'

fails = 0
for i, q in enumerate(qs, 1):
    body = norm(q)
    n = lib.count(body)
    ok = n >= 1
    print(f'q{i:02d} len={len(body):3d} hit={n} {"OK" if ok else "FAIL"}')
    if not ok:
        fails += 1
        for j in range(len(body), 8, -8):
            if lib.count(body[:j]) == 1:
                print('   first mismatch after:', repr(body[j:j+24]))
                break

print(f'\n{len(qs)-fails}/{len(qs)} passed')
sys.exit(1 if fails else 0)
