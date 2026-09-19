const { chromium } = require('playwright-core');
const path = require('path');

(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  await page.goto('file://' + path.resolve(__dirname, 'jinzhang-lanpu.html'));
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_jz_1_hero_dark.png' });

  // 点三盆
  await page.click('#pot0');
  await page.waitForTimeout(700);
  await page.click('#pot1');
  await page.waitForTimeout(700);
  await page.click('#pot2');
  await page.waitForTimeout(2400);
  await page.screenshot({ path: 'shot_jz_2_hero_lit.png' });

  // 缘起
  await page.evaluate(() => document.querySelectorAll('section')[0].scrollIntoView());
  await page.waitForTimeout(1100);
  await page.screenshot({ path: 'shot_jz_3_yuanqi.png' });

  // 品第两榜
  await page.evaluate(() => document.querySelectorAll('section')[1].scrollIntoView());
  await page.waitForTimeout(1100);
  await page.screenshot({ path: 'shot_jz_4_pinzhe.png' });

  // 鱼魫沉水
  await page.evaluate(() => document.getElementById('yushen').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(800);
  await page.click('#sinkbtn');
  await page.waitForTimeout(2200);
  await page.screenshot({ path: 'shot_jz_5_sink.png' });

  // 得名考
  await page.evaluate(() => document.querySelectorAll('section')[2].scrollIntoView());
  await page.waitForTimeout(1100);
  await page.screenshot({ path: 'shot_jz_6_deming.png' });

  // 手泽
  await page.evaluate(() => document.querySelectorAll('section')[3].scrollIntoView());
  await page.waitForTimeout(1100);
  await page.screenshot({ path: 'shot_jz_7_shouze.png' });

  // 尾屏
  await page.evaluate(() => document.querySelector('.codabox').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(1400);
  await page.screenshot({ path: 'shot_jz_8_coda.png' });

  await page.screenshot({ path: 'shot_jz_9_full.png', fullPage: true });

  // mobile
  const mp = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mp.goto('file://' + path.resolve(__dirname, 'jinzhang-lanpu.html'));
  await mp.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await mp.waitForTimeout(300);
  await mp.click('#pot0 .hit'); await mp.click('#pot1 .hit'); await mp.click('#pot2 .hit');
  await mp.waitForTimeout(2200);
  await mp.screenshot({ path: 'shot_jz_10_mobile_hero.png' });
  await mp.evaluate(() => document.querySelector('.codabox').scrollIntoView({ block: 'center' }));
  await mp.waitForTimeout(1200);
  await mp.screenshot({ path: 'shot_jz_11_mobile_coda.png' });
  await mp.evaluate(() => document.getElementById('yushen').scrollIntoView({ block: 'center' }));
  await mp.waitForTimeout(800);
  await mp.click('#sinkbtn');
  await mp.waitForTimeout(1800);
  await mp.screenshot({ path: 'shot_jz_12_mobile_sink.png' });

  console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'no page errors');
  await browser.close();
})();
