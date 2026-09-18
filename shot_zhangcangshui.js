const { chromium } = require('/home/robertsong/workspace/claude/likec4-demo/node_modules/playwright-core');
(async () => {
  const browser = await chromium.launch({
    executablePath: '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell',
    args: ['--no-sandbox']
  });
  const errors = [];
  const report = {};

  // ---------- desktop ----------
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text()); });
  await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/zhangcangshui-ji.html');
  await page.waitForTimeout(700);
  await page.screenshot({ path: '/tmp/zcs_1_hero.png' });

  // 拾叶：点满7张
  for (let i = 0; i < 7; i++) {
    await page.locator('.torn').nth(i).click({ force: true, position: { x: 31, y: 97 } });
    await page.waitForTimeout(180);
  }
  await page.waitForTimeout(1400);
  report.heroFull = await page.evaluate(() => document.getElementById('hero').classList.contains('full'));
  report.leafCount = await page.evaluate(() => document.getElementById('leafcount').textContent);
  await page.screenshot({ path: '/tmp/zcs_2_assembled.png' });

  // 三发三中
  await page.evaluate(() => document.querySelector('.bows').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(600);
  for (const r of await page.$$('.ring')) { await r.click({ force: true }); await page.waitForTimeout(250); }
  await page.waitForTimeout(500);
  report.bowStamp = await page.evaluate(() => document.getElementById('bowstamp').classList.contains('on'));
  await page.screenshot({ path: '/tmp/zcs_3_bow.png' });

  // 军报：点击一个站点展开 + 顺流
  await page.evaluate(() => document.querySelector('.river').scrollIntoView({ block: 'start' }));
  await page.waitForTimeout(500);
  await page.click('.st[data-i="6"]', { force: true });
  await page.waitForTimeout(700);
  await page.screenshot({ path: '/tmp/zcs_4_station.png' });
  await page.click('#flowbtn');
  await page.waitForTimeout(4800);
  report.flowMid = await page.evaluate(() => document.querySelectorAll('.st.lit').length);
  await page.click('#flowbtn'); // 停
  await page.waitForTimeout(300);
  await page.screenshot({ path: '/tmp/zcs_5_flow.png' });

  // 百日诗程
  await page.evaluate(() => document.querySelectorAll('.day')[2].scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(900);
  await page.screenshot({ path: '/tmp/zcs_6_day.png' });

  // 湖上三席：点南屏
  await page.evaluate(() => document.querySelector('.lake-wrap').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(500);
  await page.click('.tomb[data-t="zhang"]', { force: true });
  await page.waitForTimeout(700);
  report.tkCur = await page.evaluate(() => document.querySelector('.tk.cur').getAttribute('data-tk'));
  await page.screenshot({ path: '/tmp/zcs_7_lake.png' });

  // 集不可泯
  await page.evaluate(() => document.querySelector('.chain').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(500);
  await page.click('.chain-card[data-c="3"]', { force: true });
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/zcs_8_chain.png' });

  // 尾屏
  await page.evaluate(() => document.getElementById('fin').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(1600);
  report.finVis = await page.evaluate(() => document.getElementById('fin').classList.contains('vis'));
  await page.screenshot({ path: '/tmp/zcs_9_fin.png' });

  report.desktopOverflow = await page.evaluate(() => document.body.scrollWidth - window.innerWidth);
  await page.close();

  // ---------- mobile ----------
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  m.on('pageerror', e => errors.push('M-PAGEERROR: ' + e.message));
  m.on('console', x => { if (x.type() === 'error') errors.push('M-CONSOLE: ' + x.text()); });
  await m.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/zhangcangshui-ji.html');
  await m.waitForTimeout(700);
  await m.screenshot({ path: '/tmp/zcs_m1_hero.png' });
  for (let i = 0; i < 7; i++) {
    await m.locator('.torn').nth(i).click({ force: true, position: { x: 25, y: 78 } });
    await m.waitForTimeout(150);
  }
  await m.waitForTimeout(1300);
  await m.screenshot({ path: '/tmp/zcs_m2_assembled.png' });
  await m.evaluate(() => document.querySelector('.river').scrollIntoView({ block: 'start' }));
  await m.waitForTimeout(500);
  await m.screenshot({ path: '/tmp/zcs_m3_river.png' });
  await m.evaluate(() => document.querySelector('.lake-wrap').scrollIntoView({ block: 'center' }));
  await m.waitForTimeout(600);
  await m.click('.tomb[data-t="zhang"]', { force: true });
  await m.waitForTimeout(600);
  await m.screenshot({ path: '/tmp/zcs_m4_lake.png' });
  report.mobileOverflow = await m.evaluate(() => document.body.scrollWidth - window.innerWidth);
  await m.close();

  report.errors = errors;
  console.log(JSON.stringify(report, null, 2));
  await browser.close();
})();
