const { chromium } = require('playwright-core');
const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';

(async () => {
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = [];
  page.on('pageerror', e => errs.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/yiguan.html');
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important} *{animation-play-state:paused!important;transition:none!important}' });
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot_yg_1_hero_lo.png' });

  await page.click('.dial button[data-k="hi"]');
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_yg_2_hero_hi.png' });
  console.log('hi spin:', await page.evaluate(() => getComputedStyle(document.getElementById('wheel')).animationDuration));

  await page.click('.dial button[data-k="off"]');
  await page.waitForTimeout(300);
  console.log('off paused:', await page.evaluate(() => getComputedStyle(document.getElementById('wheel')).animationPlayState));
  console.log('still-note visible:', await page.evaluate(() => getComputedStyle(document.querySelector('.still-note')).display));
  await page.screenshot({ path: 'shot_yg_3_hero_off.png' });

  // 十二官
  await page.click('.guan.zhu');
  await page.waitForTimeout(200);
  await page.evaluate(() => document.querySelector('.guan-grid').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_yg_4_guan_zhu.png' });
  console.log('zhu panel q:', await page.evaluate(() => document.querySelector('.gd[data-g="11"]').textContent.trim().slice(0, 30)));
  await page.click('.guan[data-i="0"]');
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_yg_5_guan_xin.png' });

  // s5 stage
  await page.evaluate(() => document.querySelector('.stage').scrollIntoView({ block: 'center' }));
  await page.click('#btnRain');
  await page.waitForTimeout(700);
  await page.screenshot({ path: 'shot_yg_6_rain.png' });
  console.log('rain class:', await page.evaluate(() => document.body.className));
  await page.click('#btnGui');
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot_yg_7_gui.png' });

  // footer + overflow checks
  const oflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log('overflow-x @1280:', oflow);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_yg_8_outro.png' });

  // mobile
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/yiguan.html');
  await m.addStyleTag({ content: 'html{scroll-behavior:auto!important} *{animation-play-state:paused!important}' });
  await m.waitForTimeout(300);
  const moflow = await m.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log('overflow-x @390:', moflow);
  await m.screenshot({ path: 'shot_yg_9_mobile_hero.png' });
  await m.evaluate(() => document.querySelector('.guan-grid').scrollIntoView({ block: 'center' }));
  await m.waitForTimeout(200);
  await m.screenshot({ path: 'shot_yg_10_mobile_guan.png' });

  console.log('errors:', errs.length ? errs : 'none');
  await browser.close();
})();
