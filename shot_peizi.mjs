import { chromium } from 'playwright-core';
const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe });
const errors = [];
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
const URL = 'file:///home/robertsong/workspace/claude/daizhige-daodu/peizi-yulin.html';
await page.goto(URL);
await page.waitForTimeout(900);

const rep = await page.evaluate(() => ({
  overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  qCount: document.querySelectorAll('.q').length,
  bodyLen: document.body.innerText.length,
}));
console.log('report', JSON.stringify(rep));

await page.screenshot({ path: 'shot_pz_1_hero.png' });

// 传写互动：点满5次
await page.locator('#s1').scrollIntoViewIfNeeded();
await page.waitForTimeout(600);
for (let i = 0; i < 5; i++) { await page.click('#cxBtn'); await page.waitForTimeout(120); }
await page.waitForTimeout(600);
const cnt = await page.textContent('#cxCount');
console.log('counter after 5 clicks:', cnt.trim());
await page.evaluate(() => document.querySelector('.desk').scrollIntoView({ block: 'center' }));
await page.waitForTimeout(700);
await page.screenshot({ path: 'shot_pz_2_desk.png' });
await page.screenshot({ path: 'shot_pz_3_nine.png', fullPage: false });

// 幕二：废印
await page.evaluate(() => document.getElementById('s2').scrollIntoView());
await page.waitForTimeout(900);
await page.evaluate(() => document.querySelector('.fatalslip').scrollIntoView({ block: 'center' }));
await page.waitForTimeout(900);
await page.screenshot({ path: 'shot_pz_4_fei.png' });
await page.evaluate(() => document.getElementById('tl').scrollIntoView({ block: 'center' }));
await page.waitForTimeout(1100);
await page.screenshot({ path: 'shot_pz_5_tl.png' });

// 幕三：捞叶 装配中与装配完
await page.evaluate(() => document.getElementById('fisher').scrollIntoView({ block: 'center' }));
await page.waitForTimeout(400);
await page.screenshot({ path: 'shot_pz_6_fisher.png' });
await page.evaluate(() => window.scrollBy(0, 400));
await page.waitForTimeout(400);
await page.screenshot({ path: 'shot_pz_7_fisher_done.png' });
await page.evaluate(() => document.querySelector('.dus').scrollIntoView({ block: 'center' }));
await page.waitForTimeout(800);
await page.screenshot({ path: 'shot_pz_8_dus.png' });
await page.evaluate(() => document.querySelector('.coda').scrollIntoView());
await page.waitForTimeout(800);
await page.screenshot({ path: 'shot_pz_9_coda.png' });

// 每行·计数
const dots = await page.evaluate(() => {
  let bad = [];
  document.querySelectorAll('p, h1, h2, span, div, b, small').forEach(el => {
    if (el.children.length === 0 && (el.textContent.match(/·/g) || []).length > 1)
      bad.push(el.textContent.trim().slice(0, 30));
  });
  return bad;
});
console.log('multi-dot lines:', JSON.stringify(dots));
console.log('errors:', JSON.stringify(errors));
await browser.close();

// ---- mobile ----
const b2 = await chromium.launch({ executablePath: exe });
const m = await b2.newPage({ viewport: { width: 390, height: 844 } });
m.on('pageerror', e => errors.push('m pageerror: ' + e.message));
await m.goto(URL);
await m.waitForTimeout(900);
await m.screenshot({ path: 'shot_pz_m1_hero.png' });
await m.evaluate(() => document.getElementById('s1').scrollIntoView());
await m.waitForTimeout(600);
await m.screenshot({ path: 'shot_pz_m2_s1.png' });
await m.evaluate(() => document.getElementById('s3').scrollIntoView());
await m.waitForTimeout(800);
const mrep = await m.evaluate(() => ({
  overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
}));
console.log('mobile', JSON.stringify(mrep));
await m.screenshot({ path: 'shot_pz_m3_s3.png' });
await b2.close();
console.log('errors2:', JSON.stringify(errors));
