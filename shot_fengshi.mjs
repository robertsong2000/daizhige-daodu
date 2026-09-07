import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/fengshi-wenjian-ji.html');
await p.waitForTimeout(400);

// interactions: open two 段子笺
await p.evaluate(() => document.querySelectorAll('#bu3 details')[0].setAttribute('open', ''));
await p.evaluate(() => document.querySelectorAll('#bu3 details')[3].setAttribute('open', ''));
await p.waitForTimeout(200);

const h = await p.evaluate(() => document.body.scrollHeight);
console.log('page height', h);

let n = 0;
for (let y = 0; y < h; y += 900) {
  await p.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await p.waitForTimeout(120);
  await p.screenshot({ path: `/tmp/fs_${String(n).padStart(2, '0')}.png` });
  n++;
}
console.log('shots', n);
await b.close();
