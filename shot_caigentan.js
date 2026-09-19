const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  await page.goto('file://' + path.resolve(__dirname, 'caigentan.html'));
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_cg_1_hero_dark.png' });

  await page.click('#ignite');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: 'shot_cg_2_hero_lit.png' });

  // chew: hold pointer down for full duration
  await page.evaluate(() => document.getElementById('sec-chew').scrollIntoView());
  await page.waitForTimeout(300);
  const cb = await page.locator('#chewbtn').boundingBox();
  await page.mouse.move(cb.x + cb.width / 2, cb.y + cb.height / 2);
  await page.mouse.down();
  await page.waitForTimeout(2900);
  await page.mouse.up();
  await page.screenshot({ path: 'shot_cg_3_chew.png' });

  // plates: open first
  await page.evaluate(() => document.getElementById('sec-plates').scrollIntoView());
  await page.click('#p1 .dish');
  await page.waitForTimeout(900);
  await page.screenshot({ path: 'shot_cg_4_plate.png' });

  // pick all 8
  await page.evaluate(() => document.getElementById('sec-pick').scrollIntoView());
  for (let i = 0; i < 8; i++) { await page.click('#pickbtn'); await page.waitForTimeout(120); }
  await page.waitForTimeout(700);
  await page.screenshot({ path: 'shot_cg_5_sticks.png' });

  // coda seal
  await page.evaluate(() => document.getElementById('codabox').scrollIntoView({ block: 'center' }));
  await page.click('#codabox');
  await page.waitForTimeout(1200);
  await page.screenshot({ path: 'shot_cg_6_coda.png' });

  await page.screenshot({ path: 'shot_cg_7_full.png', fullPage: true });

  // mobile
  const mp = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mp.goto('file://' + path.resolve(__dirname, 'caigentan.html'));
  await mp.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await mp.waitForTimeout(300);
  await mp.click('#ignite');
  await mp.waitForTimeout(2400);
  await mp.evaluate(() => document.getElementById('codabox').scrollIntoView({ block: 'center' }));
  await mp.waitForTimeout(400);
  await mp.screenshot({ path: 'shot_cg_8_mobile_coda.png' });
  await mp.evaluate(() => document.getElementById('sec-plates').scrollIntoView());
  await mp.waitForTimeout(400);
  await mp.screenshot({ path: 'shot_cg_9_mobile_plates.png' });

  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no page errors');
  await browser.close();
})();
