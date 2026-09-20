const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve(__dirname, 'dandaohui.html'));
  await page.waitForTimeout(400);
  await page.evaluate(() => document.querySelectorAll('.fp').forEach(e => e.classList.add('on')));
  await page.waitForTimeout(300);
  const shots = [
    ['1_hero', null],
    ['2_zheping', '#zheping'],
    ['3_zhe1', '#zhe1'],
    ['4_zhe2', '#zhe2'],
    ['5_zhe3', '#zhe3'],
    ['6_zhongliu', '#zhongliu'],
    ['7_xishang', '#xishang'],
    ['8_coda', '#coda'],
  ];
  for (const [name, sel] of shots) {
    if (sel) await page.evaluate(s => document.querySelector(s).scrollIntoView({ block: 'start', behavior: 'instant' }), sel);
    await page.waitForTimeout(400);
    await page.screenshot({ path: 'shot_dd_' + name + '.png' });
  }
  // karaoke
  await page.evaluate(() => document.querySelector('#zhongliu').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await page.evaluate(() => window.scrollBy(0, 300));
  await page.click('#gest');
  await page.waitForTimeout(3500);
  await page.screenshot({ path: 'shot_dd_9_karaoke.png' });
  await page.waitForTimeout(3500);
  await page.screenshot({ path: 'shot_dd_10_karaoke_full.png' });
  // mirror break
  await page.evaluate(() => document.querySelector('#xishang').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await page.evaluate(() => window.scrollBy(0, 500));
  await page.click('#mstage');
  await page.waitForTimeout(1200);
  await page.screenshot({ path: 'shot_dd_11_mirror.png' });
  // zhe panel toggle
  await page.evaluate(() => document.querySelector('#zheping').scrollIntoView({ block: 'start', behavior: 'instant' }));
  const zs = await page.$$('.zhe');
  await zs[1].click(); await zs[3].click();
  await page.waitForTimeout(700);
  await page.screenshot({ path: 'shot_dd_12_zhe_toggle.png' });
  // river ripple
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(200);
  await page.click('#riverbox', { position: { x: 200, y: 150 } });
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'shot_dd_13_ripple.png' });
  // nav click
  await page.click('.jian a[href="#zhe2"]');
  await page.waitForTimeout(1300);
  await page.screenshot({ path: 'shot_dd_14_nav.png' });
  // mobile
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  m.on('pageerror', e => errors.push('M:' + e.message));
  await m.goto('file://' + path.resolve(__dirname, 'dandaohui.html'));
  await m.waitForTimeout(400);
  await m.evaluate(() => document.querySelectorAll('.fp').forEach(e => e.classList.add('on')));
  await m.waitForTimeout(300);
  await m.screenshot({ path: 'shot_dd_m1_hero.png' });
  for (const [name, sel] of [['m2_zheping','#zheping'],['m3_zhe1','#zhe1'],['m4_zhongliu','#zhongliu'],['m5_xishang','#xishang'],['m6_coda','#coda']]) {
    await m.evaluate(s => document.querySelector(s).scrollIntoView({ block: 'start', behavior: 'instant' }), sel);
    await m.waitForTimeout(400);
    await m.screenshot({ path: 'shot_dd_' + name + '.png' });
  }
  console.log('errors:', errors.length ? errors : 'none');
  await browser.close();
})();
