import { chromium } from 'playwright-core';
const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe });
const errors = [];
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/huayang-taoyinjuji.html');
await page.waitForTimeout(600);

const report1 = await page.evaluate(() => ({
  title: document.title,
  overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth,
  qCount: document.querySelectorAll('q').length,
  bodyLen: document.body.innerText.length,
  dashFound: /[—–]/.test(document.body.innerText),
}));
console.log(JSON.stringify(report1));

// hero interaction
await page.click('#zhaoBtn');
await page.waitForTimeout(3000);
await page.screenshot({ path: 'shot_tyj_hero.png' });

// sec1 ledger
await page.locator('#yi').scrollIntoViewIfNeeded();
await page.waitForTimeout(800);
await page.click('.zrow[data-f="f3"]');
await page.waitForTimeout(400);
await page.screenshot({ path: 'shot_tyj_yi.png' });

// sec2 slips
await page.locator('#er').scrollIntoViewIfNeeded();
await page.waitForTimeout(800);
await page.click('.slip:nth-child(1)');
await page.click('.slip:nth-child(5)');
await page.waitForTimeout(400);
await page.screenshot({ path: 'shot_tyj_er.png' });

// sec3 fire
await page.locator('#san').scrollIntoViewIfNeeded();
await page.waitForTimeout(800);
await page.click('#fireBtn');
await page.waitForTimeout(1500);
await page.screenshot({ path: 'shot_tyj_san.png' });

// sec4 palace
await page.locator('#si').scrollIntoViewIfNeeded();
await page.waitForTimeout(800);
await page.click('#gongBtn');
await page.waitForTimeout(900);
await page.screenshot({ path: 'shot_tyj_si.png' });

// sec5 lai
await page.locator('#wu').scrollIntoViewIfNeeded();
await page.waitForTimeout(800);
await page.click('.lai[data-b="b3"] .lh');
await page.waitForTimeout(400);
await page.screenshot({ path: 'shot_tyj_wu.png' });

// coda
await page.locator('.sealbig').scrollIntoViewIfNeeded();
await page.waitForTimeout(900);
await page.screenshot({ path: 'shot_tyj_coda.png' });

const report2 = await page.evaluate(() => {
  let maxDots = 0, badLine = '';
  document.querySelectorAll('p,div,span,small,h2,h3,button,q,.who,.lab,.js,.gd').forEach(el => {
    if (el.children.length === 0) {
      const n = (el.innerText.match(/·/g) || []).length;
      if (n > maxDots) { maxDots = n; badLine = el.innerText.slice(0, 40); }
    }
  });
  return { maxDots, badLine };
});
console.log(JSON.stringify(report2));
console.log('errors:', JSON.stringify(errors));
await browser.close();
