import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const url = 'file:///home/robertsong/workspace/claude/daizhige-daodu/bencao-shiyi.html';
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
const errs = [];

async function snap(w, h, out, fullPage = true) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.on('pageerror', e => errs.push('pageerror: ' + String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await page.goto(url, { waitUntil: 'load' });
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await page.evaluate(async () => {
    const step = Math.round(innerHeight * 0.8);
    for (let y = 0; y <= document.body.scrollHeight; y += step) {
      scrollTo({ top: y, behavior: 'instant' });
      await new Promise(r => setTimeout(r, 50));
    }
    scrollTo({ top: 0, behavior: 'instant' });
  });
  await page.addStyleTag({ content: '.rv{opacity:1!important;transform:none!important}' });
  await page.waitForTimeout(500);
  await page.screenshot({ path: out, fullPage });
  return page;
}

let p = await snap(1200, 900, '/tmp/bsy_desktop.png');
const overflow = await p.evaluate(() => {
  const bad = [];
  const dw = document.documentElement.clientWidth;
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right > dw + 8 || r.left < -8) && getComputedStyle(el).position !== 'fixed') {
      if (el.tagName !== 'HTML' && el.tagName !== 'BODY')
        bad.push(el.tagName + '.' + (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className) + ' right=' + Math.round(r.right));
    }
  });
  return bad.slice(0, 12);
});
console.log('overflow-x 可疑元素:', overflow.length ? overflow : '无');

// interactions
await p.click('.slip');
await p.waitForTimeout(400);
console.log('粘条落下 =', await p.evaluate(() => document.querySelectorAll('.slip.down').length));
await p.evaluate(() => document.querySelector('.slip.down')?.classList.remove('down'));
await p.click('#sealbtn');
console.log('钤印 =', await p.evaluate(() => document.getElementById('xuseal').classList.contains('on')));
await p.click('#etchbtn');
await p.waitForTimeout(2600);
console.log('强水蚀铜 =', await p.evaluate(() => document.getElementById('etchcard').classList.contains('live')));
await p.click('#stillbtn');
await p.waitForTimeout(400);
console.log('药露蒸取 =', await p.evaluate(() => document.getElementById('stillcard').classList.contains('live')));
await p.click('.gtab[data-tab="b"]');
console.log('东洋参tab =', await p.evaluate(() => document.getElementById('gpane').dataset.tab));
await p.click('.lstep[data-s="4"]');
console.log('烟灯step4 =', await p.evaluate(() => document.getElementById('lampbox').className));
await p.click('.lstep[data-s="5"]');
console.log('烟灯step5(end) =', await p.evaluate(() => document.getElementById('lampbox').className));
await p.click('.spine.live[data-panel="p-sy"]');
console.log('串雅panel =', await p.evaluate(() => document.getElementById('p-sy').classList.contains('on')));
await p.click('.spine.live[data-panel="p-sy2"]');
console.log('拾遗panel =', await p.evaluate(() => document.getElementById('p-sy2').classList.contains('on')));
for (let i = 0; i < 4; i++) await p.click('#drawbtn');
await p.waitForTimeout(200);
console.log('抽检产出 =', await p.evaluate(() => document.querySelectorAll('#drawbox .dname').length));
// hero screenshot
await p.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
await p.waitForTimeout(600);
await p.screenshot({ path: '/tmp/bsy_hero.png', clip: { x: 0, y: 0, width: 1200, height: 900 } });
await p.close();

await snap(390, 844, '/tmp/bsy_mobile.png');
await browser.close();
console.log('JS errors:', errs.length ? errs : '无');
console.log('done');
