import { chromium } from 'playwright-core';
const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe });
const errors = [];
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/chuanya.html');
await page.waitForTimeout(400);

const report = await page.evaluate(() => {
  const r = {};
  r.title = document.title;
  r.overflowX = document.documentElement.scrollWidth > document.documentElement.clientWidth;
  r.qCount = document.querySelectorAll('q').length;
  r.nodeCount = document.querySelectorAll('.kk').length;
  r.slipArea = !!document.querySelector('#slips');
  return r;
});
console.log('静态:', JSON.stringify(report));

// 1. 夜行：点 8 次走完 + 复位
await page.click('#goBtn'); await page.waitForTimeout(1300);
const gear1 = await page.textContent('#gear');
for (let i = 0; i < 7; i++) { await page.click('#goBtn'); await page.waitForTimeout(120); }
const gearLast = await page.textContent('#gear');
await page.click('#goBtn');
const gearReset = await page.textContent('#roadTip');
console.log('夜行:', JSON.stringify({ gear1, gearLast, gearReset }));

// 2. 切口揭底
await page.click('.kk');
const kkOpen = await page.evaluate(() => document.querySelector('.kk').classList.contains('open'));
await page.click('.kk');
console.log('切口揭底开合:', kkOpen);

// 3. 三大法
await page.click('#pJie');
const jieOn = await page.evaluate(() => document.getElementById('pJie').classList.contains('on'));
await page.click('#pDing');
const dingOn = await page.evaluate(() => document.getElementById('pDing').classList.contains('on'));
console.log('三大法开关:', { jieOn, dingOn });

// 4. 囊中取方：抽满 12 + 复位
for (let i = 0; i < 12; i++) { await page.click('#drawBtn'); await page.waitForTimeout(60); }
const drawn = await page.evaluate(() => ({
  slips: document.querySelectorAll('.slip').length,
  cnt: document.getElementById('nangCount').textContent,
  fangHasQ: !!document.querySelector('#fang q')
}));
await page.click('#drawBtn');
const reset = await page.evaluate(() => ({
  slips: document.querySelectorAll('.slip').length,
  cnt: document.getElementById('nangCount').textContent
}));
console.log('囊中取方:', JSON.stringify({ drawn, reset }));

// 5. 书命线
await page.click('.node.crack');
const tqTxt = await page.textContent('#tq');
console.log('书命线:', tqTxt.slice(0, 40));

// 6. 溢出复查
const over2 = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
console.log('溢出复查:', over2);
console.log('JS错误:', errors.length ? errors : '无');

// 截图：分段
const H = await page.evaluate(() => document.body.scrollHeight);
console.log('页高:', H);
let n = 0;
for (let y = 0; y < H; y += 850) {
  await page.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(250);
  await page.screenshot({ path: `/tmp/chuanya_${String(n).padStart(2, '0')}.png` });
  n++;
}
console.log('截图', n, '张');
await browser.close();
