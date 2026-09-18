const { chromium } = require('/home/robertsong/workspace/construction-diorama/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell' });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/duyang-zabian.html');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/dy_0_gate.png' });

  // 启封
  await page.click('#seal');
  await page.waitForTimeout(1100);
  await page.screenshot({ path: '/tmp/dy_1_juan.png' });

  // 切朝代签：德宗
  await page.click('button[data-r="de"]');
  await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/dy_2_de.png' });

  // 宣宗 + 宝异录
  await page.click('button[data-r="xuan"]');
  await page.waitForTimeout(300);
  await page.locator('.rarer').scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/dy_3_rarer.png' });

  // 神锦衾近火
  await page.click('#bfire');
  await page.waitForTimeout(900);
  await page.screenshot({ path: '/tmp/dy_4_fire.png' });
  await page.click('#bwet');

  // 同昌金册 + 九玉钗
  await page.locator('.golden').scrollIntoViewIfNeeded();
  await page.waitForTimeout(400);
  await page.click('#chai');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/dy_5_golden.png' });

  // 佛骨 + 尾屏
  await page.locator('.finale').scrollIntoViewIfNeeded();
  await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/dy_6_finale.png' });
  await page.locator('.vsign').scrollIntoViewIfNeeded();
  await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/dy_7_vsign.png' });

  // 移动端
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('.ledger').scrollIntoViewIfNeeded();
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/dy_8_mobile.png' });

  // 溢出检查
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log('overflow-x px:', overflow);
  console.log('errors:', errors.length ? errors : 'none');
  await browser.close();
})();
