import { chromium } from 'playwright-core';
const browser = await chromium.launch({ executablePath: process.env.CHROME_EXE, args: ['--no-sandbox','--font-render-hinting=none'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/baoyou-dengkelu.html');
await page.waitForTimeout(500);
await page.screenshot({ path: '/tmp/dk/01_hero_closed.png' });
await page.click('#btnUnroll');
await page.waitForTimeout(2300);
await page.screenshot({ path: '/tmp/dk/02_hero_open.png' });
await page.evaluate(async () => {
  document.documentElement.style.scrollBehavior = 'auto';
  for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); }
  window.scrollTo(0, 0);
  document.querySelectorAll('.rv').forEach(el => el.classList.add('on'));
});
await page.waitForTimeout(1000);
await page.screenshot({ path: '/tmp/dk/03_full.png', fullPage: true });
const cards = page.locator('[data-flip]');
await cards.first().scrollIntoViewIfNeeded(); await page.waitForTimeout(400);
for (let i = 0; i < 3; i++) await cards.nth(i).click();
await page.waitForTimeout(1000);
await cards.first().screenshot({ path: '/tmp/dk/04_flip.png' });
const wall = page.locator('#wall');
await wall.scrollIntoViewIfNeeded(); await page.waitForTimeout(6500);
await wall.screenshot({ path: '/tmp/dk/07_wall.png' });
const m = await browser.newPage({ viewport: { width: 390, height: 844 } });
await m.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/baoyou-dengkelu.html');
await m.waitForTimeout(400);
await m.click('#btnUnroll');
await m.waitForTimeout(2300);
await m.screenshot({ path: '/tmp/dk/05_mob_hero.png' });
await m.evaluate(async () => {
  document.documentElement.style.scrollBehavior = 'auto';
  for (let y = 0; y < document.body.scrollHeight; y += 350) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 70)); }
  document.querySelectorAll('.rv').forEach(el => el.classList.add('on'));
  window.scrollTo(0, 0);
});
await m.waitForTimeout(800);
await m.screenshot({ path: '/tmp/dk/06_mob_full.png', fullPage: true });
await browser.close();
console.log('done');
