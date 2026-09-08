import pkg from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.js';
const { chromium } = pkg;
const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errs = [];
page.on('pageerror', e => errs.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/minzhong-haicuo-shu.html');
await page.waitForTimeout(600);

// 行为断言
const checks = {};
checks.tabs = await page.locator('#tabs button').count();
checks.items_tab0 = await page.locator('#ceitem, .ceitem').count();
await page.click('#tabs button:nth-child(3)');
await page.waitForTimeout(200);
checks.items_tab2 = await page.locator('.ceitem').count();
await page.click('#tabs button:nth-child(1)');
// 展开一个按
await page.locator('.ceitem .row1').first().click();
await page.waitForTimeout(150);
checks.an_open = await page.locator('.ceitem .an.open').count();
checks.an_has_q = await page.locator('.ceitem .an.open q').count();
// 翻板
await page.locator('.kcard').first().click();
await page.waitForTimeout(300);
checks.flip = await page.locator('.kcard.flip').count();
// 淡入
await page.evaluate(() => window.scrollTo({ top: 999999, behavior: 'instant' }));
await page.waitForTimeout(700);
checks.fades_on = await page.locator('.fade.on').count();
checks.fades = await page.locator('.fade').count();
// 溢出检查：横向不得有滚动条
checks.hscroll = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
// 高度
checks.pageH = await page.evaluate(() => document.body.scrollHeight);
console.log(JSON.stringify(checks));
if (errs.length) { console.log('JS ERRORS:'); errs.forEach(e => console.log(e)); }

// 分屏截图
await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
await page.waitForTimeout(400);
const H = checks.pageH;
let idx = 0;
for (let y = 0; y < H; y += 850) {
  await page.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(250);
  await page.screenshot({ path: `/tmp/mz_${String(idx).padStart(2, '0')}.png` });
  idx++;
}
console.log('shots:', idx);
await browser.close();
