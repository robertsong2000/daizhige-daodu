import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/yisi-riji.html');
await page.waitForTimeout(700);

// 结构断言
const cells = await page.locator('.cell').count();
const torn = await page.locator('.cell.torn').count();
const dot = await page.locator('.cell.dot').count();
console.log('cells:', cells, 'torn:', torn, 'dot:', dot);
if (cells !== 297) { console.log('FAIL cell count'); process.exit(1); }
if (torn !== 1) { console.log('FAIL torn'); process.exit(1); }

// 点击一格读全则
await page.click('.cell[data-i="100"]');
await page.waitForTimeout(200);
const rt = await page.locator('#reader .rt').textContent();
console.log('reader sample:', rt.slice(0, 40), 'len:', rt.length);
if (rt.length < 10) { console.log('FAIL reader'); process.exit(1); }

// 边款
const tally = await page.locator('#tally').textContent();
console.log('tally:', tally.trim().slice(0, 80));

// 首屏截图
await page.screenshot({ path: '/tmp/ys_00_hero.png' });

// 分屏下滚目检
const H = await page.evaluate(() => document.body.scrollHeight);
console.log('pageHeight:', H);
let n = 0;
for (let y = 0; y < H; y += 820) {
  await page.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(500);
  n++;
  await page.screenshot({ path: `/tmp/ys_s${String(n).padStart(2, '0')}.png` });
  if (n >= 12) break;
}

// 叶子点击(叶堆有过渡动画, 直接派发 click)
await page.evaluate(() => document.querySelector('#leaves').scrollIntoView({ block: 'center' }));
await page.waitForTimeout(400);
const leafTxt = await page.evaluate(() => {
  const l = document.querySelectorAll('#leaves .leaf')[2];
  l.click();
  return l.classList.contains('under');
});
await page.waitForTimeout(500);
const front = await page.evaluate(() => {
  const ls = [...document.querySelectorAll('#leaves .leaf')];
  return ls.findIndex(l => !l.classList.contains('under'));
});
console.log('leaf front index:', front);
if (front !== 2) { console.log('FAIL leaf click'); process.exit(1); }
await page.screenshot({ path: '/tmp/ys_leaf.png' });

// 溢出检查 1280 / 390
const ov1 = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
console.log('overflow1280:', ov1);
const p2 = await browser.newPage({ viewport: { width: 390, height: 844 } });
await p2.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/yisi-riji.html');
await p2.waitForTimeout(600);
const ov2 = await p2.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
console.log('overflow390:', ov2);
await p2.screenshot({ path: '/tmp/ys_m0.png' });
await p2.evaluate(() => document.getElementById('grid').scrollIntoView());
await p2.waitForTimeout(400);
await p2.screenshot({ path: '/tmp/ys_m1.png' });

console.log('console errors:', errors.length ? errors : 'none');
await browser.close();
if (errors.length || ov1 > 1 || ov2 > 1) { console.log('FAIL'); process.exit(1); }
console.log('HEADLESS PASS');
