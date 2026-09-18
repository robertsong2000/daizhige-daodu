const { chromium } = require('/home/robertsong/workspace/claude/likec4-demo/node_modules/playwright-core');
(async () => {
  const browser = await chromium.launch({
    executablePath: '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell',
    args: ['--no-sandbox']
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text()); });
  await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/fengtianlu.html');
  await page.waitForTimeout(700);
  await page.screenshot({ path: '/tmp/ftl_1_hero.png' });
  await page.click('#wax');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: '/tmp/ftl_2_open.png' });
  await page.evaluate(() => document.querySelector('article.slip').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(900);
  await page.screenshot({ path: '/tmp/ftl_3_slip1.png' });
  // 保票翻面
  await page.click('#ticket');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/tmp/ftl_4_ticket.png' });
  // 夺笏
  await page.evaluate(() => document.getElementById('hudemo').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(800);
  await page.click('#hudemo');
  await page.waitForTimeout(1600);
  await page.screenshot({ path: '/tmp/ftl_5_hu.png' });
  // 云梯举火
  await page.evaluate(() => document.getElementById('lad').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(800);
  await page.click('#firebtn');
  await page.waitForTimeout(2200);
  await page.screenshot({ path: '/tmp/ftl_6_fire.png' });
  // 石刻
  await page.evaluate(() => document.getElementById('stone').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(800);
  await page.click('#stone');
  await page.waitForTimeout(1400);
  await page.screenshot({ path: '/tmp/ftl_7_stone.png' });
  // 紫荆复荣
  await page.evaluate(() => document.getElementById('treebox').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(800);
  await page.click('#bloombtn');
  await page.waitForTimeout(2200);
  await page.screenshot({ path: '/tmp/ftl_8_bloom.png' });
  // 尾屏
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(900);
  await page.screenshot({ path: '/tmp/ftl_9_tail.png' });

  // 移动端
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  m.on('pageerror', e => errors.push('MOBILE PAGEERROR: ' + e.message));
  await m.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/fengtianlu.html');
  await m.waitForTimeout(600);
  await m.screenshot({ path: '/tmp/ftl_m1_hero.png' });
  await m.evaluate(() => document.querySelectorAll('article.slip')[2].scrollIntoView({ block: 'center' }));
  await m.waitForTimeout(900);
  await m.screenshot({ path: '/tmp/ftl_m2_slip.png' });
  await m.evaluate(() => document.getElementById('treebox').scrollIntoView({ block: 'center' }));
  await m.waitForTimeout(800);
  await m.click('#bloombtn');
  await m.waitForTimeout(2000);
  await m.screenshot({ path: '/tmp/ftl_m3_bloom.png' });

  console.log(errors.length ? errors.join('\n') : 'NO JS ERRORS');
  await browser.close();
})();
