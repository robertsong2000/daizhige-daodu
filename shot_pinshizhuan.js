const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve(__dirname, 'pinshizhuan.html'));
  await page.waitForTimeout(400);
  await page.evaluate(() => document.querySelectorAll('.fp').forEach(e => e.classList.add('on')));
  await page.waitForTimeout(300);
  const shots = [
    ['1_hero', null],
    ['2_yuan', '#yuan'],
    ['3_bian', '#bian'],
    ['4_mu', '#mu'],
    ['5_pu', '#pu'],
    ['6_hou', '#hou'],
    ['7_coda', '#coda'],
  ];
  for (const [name, sel] of shots) {
    if (sel) await page.evaluate(s => document.querySelector(s).scrollIntoView({ block: 'start', behavior: 'instant' }), sel);
    await page.waitForTimeout(500);
    await page.screenshot({ path: '.psz_' + name + '.png' });
  }
  // interactions
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(200);
  await page.click('.door:nth-child(1)');
  await page.click('.door:nth-child(4)');
  await page.waitForTimeout(900);
  await page.screenshot({ path: '.psz_8_doors.png' });
  await page.click('.qa:nth-of-type(2)');
  await page.evaluate(() => document.querySelector('#yuan').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await page.waitForTimeout(700);
  await page.screenshot({ path: '.psz_9_qa.png' });
  await page.evaluate(() => document.querySelector('#bian').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await page.click('#zgo'); await page.click('#zgo'); await page.click('#zgo');
  await page.waitForTimeout(1100);
  await page.screenshot({ path: '.psz_10_bian.png' });
  await page.evaluate(() => document.querySelector('#mu').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await page.click('.ms:nth-child(5)');
  await page.click('.ms:nth-child(5)');
  await page.click('.ms:nth-child(5)');
  await page.waitForTimeout(800);
  await page.screenshot({ path: '.psz_11_mu.png' });
  await page.evaluate(() => document.querySelector('#pu').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await page.click('.chip[data-i="3"]');
  await page.click('.chip[data-i="68"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '.psz_12_pu.png' });
  // mobile
  const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
  m.on('pageerror', e => errors.push('m: ' + e.message));
  await m.goto('file://' + path.resolve(__dirname, 'pinshizhuan.html'));
  await m.waitForTimeout(400);
  await m.evaluate(() => document.querySelectorAll('.fp').forEach(e => e.classList.add('on')));
  await m.waitForTimeout(300);
  await m.screenshot({ path: '.psz_m1_hero.png' });
  await m.evaluate(() => document.querySelector('#bian').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await m.waitForTimeout(500);
  await m.screenshot({ path: '.psz_m2_bian.png' });
  await m.evaluate(() => document.querySelector('#coda').scrollIntoView({ block: 'start', behavior: 'instant' }));
  await m.waitForTimeout(500);
  await m.screenshot({ path: '.psz_m3_coda.png' });
  const h = await page.evaluate(() => document.body.scrollHeight);
  const hm = await m.evaluate(() => document.body.scrollHeight);
  console.log('pageheight', h, 'mobile', hm, 'errors', JSON.stringify(errors));
  await browser.close();
})();
