const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve('/home/robertsong/workspace/claude/daizhige-daodu', 'guitian-shihua.html'));
  await page.waitForTimeout(500);
  await page.evaluate(() => document.getElementById('chen').scrollIntoView());
  await page.waitForTimeout(900);
  await page.click('#thump');
  await page.waitForTimeout(1500);
  const el = await page.$('.vpoem');
  await el.screenshot({ path: '/home/robertsong/workspace/claude/daizhige-daodu/shot_gt_zoom_poem.png' });
  const el2 = await page.$('.chenyan');
  await el2.screenshot({ path: '/home/robertsong/workspace/claude/daizhige-daodu/shot_gt_zoom_chen.png' });
  await browser.close();
})();
