const { chromium } = require('/home/robertsong/workspace/construction-diorama/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell' });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + e.text()); });
  await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/tangshuang-pu.html');
  await page.waitForTimeout(3200);
  await page.screenshot({ path: '/tmp/ts_hero.png' });

  // S1 三折
  await page.click('#donkeyBtn');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/tmp/ts_donkey.png' });
  await page.click('#dealBtn');
  await page.waitForTimeout(700);
  await page.click('#statueBtn');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/tmp/ts_acts.png' });

  // S2 四色卡
  await page.click('.cane:nth-child(1)');
  await page.waitForTimeout(400);
  // S3 器用
  await page.click('.tool:nth-child(4)');
  await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/ts_cane_tool.png' });

  // S4 结霜：点四根竹梢 + 沥瓮
  await page.click('#st1'); await page.waitForTimeout(350);
  await page.click('#st1'); await page.waitForTimeout(350);
  await page.click('#st1'); await page.waitForTimeout(350);
  await page.click('#st2'); await page.waitForTimeout(200);
  await page.click('#st2'); await page.waitForTimeout(200);
  await page.click('#st2'); await page.waitForTimeout(200);
  await page.click('#st3'); await page.waitForTimeout(200);
  await page.click('#st3'); await page.waitForTimeout(200);
  await page.click('#st3'); await page.waitForTimeout(200);
  await page.click('#st4'); await page.waitForTimeout(200);
  await page.click('#st4'); await page.waitForTimeout(200);
  await page.click('#st4'); await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/ts_vat_full.png' });
  await page.click('#drainBtn');
  await page.waitForTimeout(1800);
  await page.screenshot({ path: '/tmp/ts_vat_drained.png' });

  // S5 翻转
  await page.click('#flipBtn');
  await page.waitForTimeout(900);
  await page.screenshot({ path: '/tmp/ts_flip.png' });

  // S6 开瓮
  await page.click('#openBtn');
  await page.waitForTimeout(700);
  await page.screenshot({ path: '/tmp/ts_fortune.png' });
  await page.click('#fortAgain');
  await page.waitForTimeout(700);

  // S7 + footer
  await page.screenshot({ path: '/tmp/ts_tail.png', fullPage: false });
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(900);
  await page.screenshot({ path: '/tmp/ts_footer.png' });

  // mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(800);
  await page.screenshot({ path: '/tmp/ts_mob.png' });

  console.log('ERRORS:', errors.length ? errors.join(' | ') : 'none');
  await browser.close();
})();
