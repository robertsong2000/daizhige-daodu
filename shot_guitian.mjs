import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/guitian-lu.html');
await p.waitForTimeout(400);

await p.click('#bootL');
await p.waitForTimeout(250);
await p.click('#bootR');
await p.waitForTimeout(350);
await p.click('#oilplay');
await p.waitForTimeout(400);

const h = await p.evaluate(() => document.body.scrollHeight);
console.log('page height', h);

let n = 0;
for (let y = 0; y < h; y += 900) {
  await p.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await p.waitForTimeout(180);
  await p.screenshot({ path: `/tmp/gt_${String(n).padStart(2, '0')}.png` });
  n++;
}
console.log('shots', n);
console.log('js errors:', errors.length ? errors.join(' | ') : 'none');
await b.close();
