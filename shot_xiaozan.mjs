import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';
const path = '/home/robertsong/workspace/claude/daizhige-daodu/xiaozan.html';
(async () => {
  const browser = await chromium.launch({
    executablePath: '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell',
    args: ['--no-sandbox']
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto('file://' + path, { waitUntil: 'load' });
  await page.screenshot({ path: '/tmp/xz_hero.png' });
  // 吹灯暗场
  await page.click('#lampBtn');
  await page.waitForTimeout(900);
  await page.screenshot({ path: '/tmp/xz_dark.png' });
  await page.click('#lampBtn');
  await page.waitForTimeout(900);
  // 逐屏截图
  const h = await page.evaluate(() => document.body.scrollHeight);
  let i = 0;
  for (let y = 900; y < h; y += 850) {
    await page.evaluate(yy => window.scrollTo({ top: yy, behavior: 'instant' }), y);
    await page.waitForTimeout(250);
    await page.screenshot({ path: `/tmp/xz_s${++i}.png` });
    if (i >= 7) break;
  }
  console.log('height', h, 'shots', i);
  await browser.close();
})();
