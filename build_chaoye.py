import json, re

tpl = open('chaoye-qinzai.tpl.html', encoding='utf-8').read()
qs = json.load(open('quotes_chaoye.json', encoding='utf-8'))

keys = set(re.findall(r'⟦(q:[a-z0-9_]+)⟧', tpl))
missing = [k for k in keys if k[2:] not in qs]
unused = [k for k in qs if 'q:' + k not in keys]
assert not missing, f'缺占位符对应引文: {missing}'
print(f'占位符 {len(keys)} 个, 引文池 {len(qs)} 条, 未用 {unused}')

html = tpl
for k, v in qs.items():
    html = html.replace('⟦q:' + k + '⟧', v)

left = re.findall(r'⟦[^⟧]+⟧', html)
assert not left, f'残留占位符: {left}'
assert '⟦' not in html

open('chaoye-qinzai.html', 'w', encoding='utf-8').write(html)
print('OK -> chaoye-qinzai.html', len(html), 'bytes')
