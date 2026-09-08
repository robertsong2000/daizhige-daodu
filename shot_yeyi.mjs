import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/yeyi.html');
await page.waitForTimeout(700);

// 首屏：夜与灯
await page.screenshot({ path: '/tmp/yy_01_night.png' });
// 点灯芯 → 天亮
await page.click('#night');
await page.waitForTimeout(2400);
await page.screenshot({ path: '/tmp/yy_02_dawn.png' });
await page.click('#night');
await page.waitForTimeout(400);

// 分屏下滚目检
const H = await page.evaluate(() => document.body.scrollHeight);
let n = 0;
for (let y = 620; y < H; y += 820) {
  await page.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(950);
  n++;
  await page.screenshot({ path: `/tmp/yy_s${String(n).padStart(2, '0')}.png` });
  if (n >= 12) break;
}
const qn = await page.evaluate(() => ({ h: document.body.scrollHeight, q: document.querySelectorAll('q').length }));
console.log('shots:', n + 2, 'pageHeight:', H, JSON.stringify(qn), 'errors:', errors.length ? errors : 'none');
await browser.close();
