const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  await page.goto('file://' + path.resolve(__dirname, 'shiyou-tanji.html'));
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot_sy_1_hero.png' });

  // wear the hat
  await page.click('#stage');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'shot_sy_2_hero_on.png' });

  // zhan: four cups in order
  await page.evaluate(() => document.getElementById('zhan').scrollIntoView());
  await page.waitForTimeout(300);
  for (let i = 0; i < 4; i++) {
    await page.evaluate(i => {
      document.querySelectorAll('.cup')[i].dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }, i);
    await page.waitForTimeout(350);
  }
  await page.waitForTimeout(1100);
  await page.screenshot({ path: 'shot_sy_3_cups.png', fullPage: false });
  await page.evaluate(() => document.getElementById('fushou').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_sy_4_fushou.png' });

  // poems open
  await page.evaluate(() => document.querySelectorAll('.jian')[0].scrollIntoView({ block: 'center' }));
  await page.evaluate(() => document.querySelectorAll('.jian').forEach(j => j.click()));
  await page.waitForTimeout(900);
  await page.screenshot({ path: 'shot_sy_5_jian.png' });

  // steps
  await page.evaluate(() => document.querySelector('.steps').scrollIntoView({ block: 'center' }));
  await page.evaluate(() => document.querySelectorAll('.steps button')[2].click());
  await page.waitForTimeout(250);
  await page.screenshot({ path: 'shot_sy_6_steps.png' });

  // coda
  await page.evaluate(() => document.querySelector('.coda').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_sy_7_coda.png' });

  // mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(400);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_sy_8_mobile_hero.png' });
  await page.evaluate(() => document.querySelector('.cards').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_sy_9_mobile_card.png' });

  console.log('errors:', errors.length ? errors : 'none');
  await browser.close();
})();
