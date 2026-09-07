import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/xiangxing-gongan.html');
await p.waitForTimeout(400);

// interactions: flip seal, draw a签, filter a chip
await p.click('#seal');
await p.click('#drawbtn');
await p.click('[data-cat="除害"]');
await p.waitForTimeout(300);
await p.click('.chip[data-cat=""]');

const h = await p.evaluate(() => document.body.scrollHeight);
console.log('page height', h);

// full page screenshots split by viewport
let n = 0;
for (let y = 0; y < h; y += 900) {
  await p.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await p.waitForTimeout(150);
  await p.screenshot({ path: `/tmp/xx_${String(n).padStart(2, '0')}.png` });
  n++;
}
console.log('shots', n);
await b.close();
