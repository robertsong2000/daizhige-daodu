const { chromium } = require('playwright');
(async () => {
  const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
  const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.addStyleTag; // noop
  await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/zuozhi-yaoyan.html');
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important} .rv{opacity:1!important;transform:none!important}' });
  await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/zz_hero_dark.png' });

  await page.click('#ignite');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: '/tmp/zz_hero_lit.png' });

  await page.evaluate(() => document.getElementById('yaogui').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: '/tmp/zz_wall.png' });

  await page.click('#wall .dk:nth-child(17) .face');
  await page.waitForTimeout(500);
  await page.click('#wall .dk:nth-child(24) .face');
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/zz_drawers_open.png' });

  await page.evaluate(() => document.getElementById('sanan').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: '/tmp/zz_case1.png', fullPage: false });

  await page.evaluate(() => document.getElementById('ghost').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(300);
  await page.click('#gnext'); await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/zz_ghost2.png' });
  await page.click('#gnext'); await page.waitForTimeout(400);
  await page.screenshot({ path: '/tmp/zz_ghost3.png' });

  await page.evaluate(() => document.getElementById('ledger').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(300);
  for (let i = 0; i < 5; i++) { await page.click('#ledgo'); await page.waitForTimeout(350); }
  await page.screenshot({ path: '/tmp/zz_ledger.png' });

  await page.evaluate(() => document.getElementById('hangdang').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: '/tmp/zz_hangdang.png' });

  await page.evaluate(() => document.getElementById('coda').scrollIntoView());
  await page.waitForTimeout(300);
  await page.screenshot({ path: '/tmp/zz_coda.png' });

  await page.screenshot({ path: '/tmp/zz_full.png', fullPage: true });

  const mob = await browser.newPage({ viewport: { width: 400, height: 860 } });
  await mob.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/zuozhi-yaoyan.html');
  await mob.addStyleTag({ content: 'html{scroll-behavior:auto!important} .rv{opacity:1!important;transform:none!important}' });
  await mob.waitForTimeout(400);
  await mob.click('#ignite');
  await mob.waitForTimeout(2400);
  await mob.screenshot({ path: '/tmp/zz_mob_hero.png' });
  await mob.evaluate(() => document.getElementById('yaogui').scrollIntoView());
  await mob.waitForTimeout(300);
  await mob.screenshot({ path: '/tmp/zz_mob_wall.png' });
  await mob.evaluate(() => document.getElementById('coda').scrollIntoView());
  await mob.waitForTimeout(300);
  await mob.screenshot({ path: '/tmp/zz_mob_coda.png' });

  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await browser.close();
  console.log('done', errors);
})();
