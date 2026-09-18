const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  await page.goto('file://' + path.resolve(__dirname, 'tanglv.html'));
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important} *{transition:none!important;animation-duration:0s!important}' });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_tl_1_hero.png' });

  await page.click('#drumBtn');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: 'shot_tl_2_hero_drummed.png' });

  await page.evaluate(() => document.getElementById('wuxing').scrollIntoView());
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_tl_3_wuxing.png' });
  await page.click('.lad[data-p="p3"]');
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_tl_4_wuxing_liu.png' });

  await page.evaluate(() => document.getElementById('shier').scrollIntoView());
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_tl_5_shier.png' });
  await page.click('.plq:nth-child(1)');
  await page.click('.plq:nth-child(7)');
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_tl_6_shier_open.png' });

  await page.evaluate(() => document.getElementById('bayi').scrollIntoView());
  await page.click('.jd:nth-child(3)');
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_tl_7_bayi.png' });

  await page.evaluate(() => document.getElementById('andu').scrollIntoView());
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_tl_8_case1.png' });
  await page.click('#nextCase'); await page.click('#nextCase'); await page.click('#nextCase');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'shot_tl_9_case4.png' });

  await page.evaluate(() => document.getElementById('pian').scrollIntoView());
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_tl_10_doors.png' });

  await page.evaluate(() => document.querySelector('.coda').scrollIntoView());
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'shot_tl_11_coda.png' });

  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await m.goto('file://' + path.resolve(__dirname, 'tanglv.html'));
  await m.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await m.waitForTimeout(300);
  await m.screenshot({ path: 'shot_tl_m1_hero.png' });
  await m.evaluate(() => document.getElementById('shier').scrollIntoView());
  await m.waitForTimeout(200);
  await m.screenshot({ path: 'shot_tl_m2_shier.png' });
  await m.evaluate(() => document.getElementById('pian').scrollIntoView());
  await m.waitForTimeout(200);
  await m.screenshot({ path: 'shot_tl_m3_doors.png' });

  console.log('errors:', errors.length ? errors : 'none');
  await browser.close();
})();
