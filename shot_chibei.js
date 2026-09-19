const { chromium } = require('/home/robertsong/workspace/claude/likec4-demo/node_modules/playwright-core');
(async () => {
  const browser = await chromium.launch({
    executablePath: '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell',
    args: ['--no-sandbox']
  });
  const page = await browser.newPage({ viewport: { width: 1100, height: 1000 } });
  await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/chibei-outan.html');
  await page.waitForTimeout(600);
  // 首屏未点燃
  await page.screenshot({ path: '/tmp/cb_0_hero_dark.png' });
  // 点池心点燃
  await page.click('#hit');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: '/tmp/cb_1_hero_lit.png' });
  // 谒陵
  await page.click('#lxgo');
  await page.waitForTimeout(2800);
  const gu = await page.$('#gu'); if (gu) await gu.screenshot({ path: '/tmp/cb_2_gu.png' });
  // 倾瓢
  await page.click('#piaobox');
  await page.waitForTimeout(2200);
  const xian = await page.$('#xian'); if (xian) await xian.screenshot({ path: '/tmp/cb_3_xian.png' });
  // 木板
  await page.click('[data-plank="1"]');
  await page.click('[data-plank="2"]');
  await page.waitForTimeout(1800);
  const yi = await page.$('#yi'); if (yi) await yi.screenshot({ path: '/tmp/cb_4_yi.png' });
  // 裤
  await page.click('#kubox');
  await page.waitForTimeout(1500);
  // 林四娘拍2、拍3
  await page.click('[data-b="1"]');
  await page.waitForTimeout(600);
  await page.click('[data-b="2"]');
  await page.waitForTimeout(400);
  // 剑侠走满
  for (let i = 0; i < 4; i++) { await page.click('#xgo'); await page.waitForTimeout(500); }
  const nt = await page.$('#night'); if (nt) await nt.screenshot({ path: '/tmp/cb_5_night.png' });
  // 尾屏
  await page.evaluate(() => document.querySelector('#coda').scrollIntoView());
  await page.waitForTimeout(1200);
  await page.evaluate(() => window.scrollBy(0, 400));
  await page.waitForTimeout(2600);
  await page.screenshot({ path: '/tmp/cb_6_coda.png' });
  // 整页高度/溢出检查
  const m = await page.evaluate(() => {
    const d = document.documentElement;
    return { sw: d.scrollWidth, cw: d.clientWidth, sh: d.scrollHeight };
  });
  console.log(JSON.stringify(m));
  // 移动端
  const mp = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mp.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/chibei-outan.html');
  await mp.waitForTimeout(500);
  await mp.click('#hit');
  await mp.waitForTimeout(2400);
  await mp.screenshot({ path: '/tmp/cb_m_hero.png' });
  const mm = await mp.evaluate(() => {
    const d = document.documentElement;
    return { sw: d.scrollWidth, cw: d.clientWidth };
  });
  console.log('mobile', JSON.stringify(mm));
  await browser.close();
  console.log('done');
})();
