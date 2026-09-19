const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  await page.goto('file://' + path.resolve(__dirname, 'guitian-shihua.html'));
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'shot_gt_1_hero.png' });

  await page.click('#pull');
  await page.waitForTimeout(1800);
  await page.screenshot({ path: 'shot_gt_2_pulled.png' });

  await page.evaluate(() => document.getElementById('li').scrollIntoView());
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'shot_gt_3_li.png' });

  await page.evaluate(() => document.getElementById('an').scrollIntoView());
  await page.waitForTimeout(1000);
  await page.click('.fan .fcard:nth-child(1)');
  await page.click('.fan .fcard:nth-child(3)');
  await page.waitForTimeout(1200);
  await page.screenshot({ path: 'shot_gt_4_jie.png' });

  await page.evaluate(() => document.getElementById('g_huo') ? document.getElementById('g_huo').scrollIntoView() : document.querySelectorAll('.groupt')[1].scrollIntoView());
  await page.waitForTimeout(900);
  await page.screenshot({ path: 'shot_gt_5_huo.png' });

  await page.evaluate(() => document.getElementById('chen').scrollIntoView());
  await page.waitForTimeout(1000);
  await page.click('#thump');
  await page.waitForTimeout(1600);
  await page.screenshot({ path: 'shot_gt_6_chen.png' });

  await page.evaluate(() => document.getElementById('sai').scrollIntoView());
  await page.waitForTimeout(900);
  await page.screenshot({ path: 'shot_gt_7_sai_top.png' });
  await page.evaluate(() => window.scrollBy(0, 500));
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'shot_gt_8_sai_night.png' });

  await page.evaluate(() => document.getElementById('xu').scrollIntoView());
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'shot_gt_9_xu.png' });

  await page.evaluate(() => document.getElementById('yan').scrollIntoView());
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'shot_gt_10_yan.png' });
  await page.click('#maskbtn');
  await page.waitForTimeout(1600);
  await page.screenshot({ path: 'shot_gt_11_masked.png' });
  await page.click('#mclose');
  await page.waitForTimeout(800);

  // 移动端
  const mp = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mp.goto('file://' + path.resolve(__dirname, 'guitian-shihua.html'));
  await mp.waitForTimeout(500);
  await mp.click('#pull');
  await mp.waitForTimeout(1600);
  await mp.screenshot({ path: 'shot_gt_m1_hero.png' });
  await mp.evaluate(() => document.getElementById('li').scrollIntoView());
  await mp.waitForTimeout(900);
  await mp.screenshot({ path: 'shot_gt_m2_li.png' });
  await mp.evaluate(() => document.getElementById('chen').scrollIntoView());
  await mp.waitForTimeout(900);
  await mp.screenshot({ path: 'shot_gt_m3_chen.png' });
  await mp.evaluate(() => document.getElementById('yan').scrollIntoView());
  await mp.waitForTimeout(900);
  await mp.screenshot({ path: 'shot_gt_m4_yan.png' });

  console.log('errors:', errors.length ? errors : 'none');
  await browser.close();
})();
