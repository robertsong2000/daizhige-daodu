const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  await page.goto('file://' + path.resolve(__dirname, 'zhuanghuang-zhi.html'));
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_zh_1_hero_dark.png' });

  await page.click('#ignite');
  await page.waitForTimeout(2800);
  await page.screenshot({ path: 'shot_zh_2_hero_lit.png' });

  await page.evaluate(() => document.getElementById('yiyu').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_zh_3_yiyu.png' });

  await page.evaluate(() => document.getElementById('wuzhen').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_zh_4_wuzhen_xi.png' });

  await page.click('#rail button[data-t="p-jie"]');
  await page.waitForTimeout(400);
  await page.click('#stack .layer.l2');
  await page.waitForTimeout(900);
  await page.click('#stack .layer.l1');
  await page.waitForTimeout(900);
  await page.screenshot({ path: 'shot_zh_5_jie_peeled.png' });

  await page.click('#rail button[data-t="p-quan"]');
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot_zh_6_quan.png' });

  await page.evaluate(() => document.getElementById('bingan').scrollIntoView());
  await page.waitForTimeout(300);
  for (const s of ['1', '2', '3', '4']) {
    await page.click(`#stagebar button[data-s="${s}"]`);
    await page.waitForTimeout(350);
  }
  await page.screenshot({ path: 'shot_zh_7_case1_st4.png' });

  await page.click('#seambar button[data-s="good"]');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'shot_zh_8_seam_good.png' });

  await page.evaluate(() => document.getElementById('jianghu').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_zh_9_jianghu.png' });

  await page.evaluate(() => document.getElementById('an-shang').scrollIntoView());
  await page.waitForTimeout(300);
  await page.click('#seasons button[data-v="冬"]');
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_zh_10_bench.png' });

  await page.evaluate(() => document.getElementById('coda').scrollIntoView());
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot_zh_11_coda.png' });

  // mobile pass
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot_zh_12_mobile_hero.png' });
  await page.evaluate(() => document.getElementById('bingan').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_zh_13_mobile_case.png' });

  console.log(errors.length ? 'JS ERRORS:\n' + errors.join('\n') : 'no js errors');
  await browser.close();
})();
