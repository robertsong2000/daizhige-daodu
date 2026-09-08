import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const URL = 'file:///home/robertsong/workspace/claude/daizhige-daodu/xuanhe-huapu.html';

async function shoot(mobile) {
  const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const vp = mobile ? { width: 390, height: 844 } : { width: 1280, height: 900 };
  const p = await b.newPage({ viewport: vp });
  const errors = [];
  p.on('pageerror', e => errors.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await p.goto(URL);
  await p.waitForTimeout(400);

  const tag = mobile ? 'm_' : 'd_';

  // hero + ticker countup
  await p.evaluate(() => window.scrollTo(0, 40));
  await p.waitForTimeout(2300);
  const ticker = await p.$eval('#axcount', el => el.textContent);
  console.log(tag + 'ticker:', ticker);
  await p.screenshot({ path: `/tmp/xh_${tag}0_hero.png` });

  // doors: bars grow + open one door
  await p.evaluate(() => document.getElementById('dgrid').scrollIntoView({ behavior: 'instant', block: 'center' }));
  await p.waitForTimeout(1400);
  const doors = await p.$$('.door .drow');
  await doors[5].click();
  await p.waitForTimeout(700);
  await p.screenshot({ path: `/tmp/xh_${tag}1_doors.png` });

  // slips: open one
  await p.evaluate(() => document.querySelector('.slipgrid').scrollIntoView({ behavior: 'instant', block: 'center' }));
  const slips = await p.$$('.slip');
  await slips[8].click();
  await p.waitForTimeout(700);
  await p.screenshot({ path: `/tmp/xh_${tag}2_slips.png` });

  // bars
  await p.evaluate(() => document.getElementById('bars').scrollIntoView({ behavior: 'instant', block: 'center' }));
  await p.waitForTimeout(1500);
  const barsCls = await p.$eval('#bars', el => el.className + ' | ' + getComputedStyle(document.querySelector('.bfill')).width);
  console.log(tag + 'bars state:', barsCls);
  await p.screenshot({ path: `/tmp/xh_${tag}3_bars.png` });

  // oust + collate
  await p.evaluate(() => document.querySelector('.oust .table').scrollIntoView({ behavior: 'instant', block: 'center' }));
  await p.waitForTimeout(300);
  await p.screenshot({ path: `/tmp/xh_${tag}4_oust.png` });
  await p.evaluate(() => document.querySelector('.collate .clist').scrollIntoView({ behavior: 'instant', block: 'center' }));
  await p.waitForTimeout(300);
  await p.screenshot({ path: `/tmp/xh_${tag}5_collate.png` });

  // sealoff + footer
  await p.evaluate(() => document.querySelector('.sealoff .inner').scrollIntoView({ behavior: 'instant', block: 'center' }));
  await p.waitForTimeout(300);
  await p.screenshot({ path: `/tmp/xh_${tag}6_seal.png` });
  await p.evaluate(() => document.querySelector('footer.page').scrollIntoView({ behavior: 'instant', block: 'end' }));
  await p.waitForTimeout(300);
  await p.screenshot({ path: `/tmp/xh_${tag}7_footer.png` });

  // horizontal overflow check
  const over = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log(tag + 'h-overflow px:', over);

  // door open state second door while first open (accordion switch)
  if (!mobile) {
    await p.evaluate(() => document.getElementById('dgrid').scrollIntoView({ behavior: 'instant', block: 'center' }));
    await doors[8].click();
    await p.waitForTimeout(600);
    const openCount = await p.$$eval('.door.open', els => els.length);
    console.log(tag + 'open doors after switching:', openCount);
  }

  console.log(tag + 'errors:', errors.length ? errors : 'none');
  await b.close();
  return errors;
}

const e1 = await shoot(false);
const e2 = await shoot(true);
if (e1.length || e2.length) process.exit(1);
console.log('SHOTS OK');
