import { chromium } from '/home/robertsong/workspace/claude/daizhige-daodu/node_modules/playwright-core/index.mjs';

const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const url = 'file:///home/robertsong/workspace/claude/daizhige-daodu/meiqin-shilun.html';
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });

async function snap(w, h, out, interact) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(url, { waitUntil: 'load' });
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important} .rise{transition:none!important} .zhpath,.zhb,.bigarrow{transition:none!important}' });
  if (interact) await interact(page);
  await page.evaluate(async () => {
    const step = Math.round(innerHeight * 0.8);
    for (let y = 0; y <= document.body.scrollHeight; y += step) {
      scrollTo({ top: y, behavior: 'instant' });
      await new Promise(r => setTimeout(r, 40));
    }
    scrollTo({ top: 0, behavior: 'instant' });
  });
  await page.waitForTimeout(500);
  await page.screenshot({ path: out, fullPage: true });
  console.log(out, 'ok', errs.length ? 'ERRORS: ' + errs.join(' | ') : 'no-js-errors');
  await page.close();
}

await snap(1200, 900, '/tmp/mq_hero_pre.png', async (p) => {
  await p.evaluate(() => scrollTo(0, 0));
});
await snap(1200, 900, '/tmp/mq_desktop_full.png', async (p) => {
  await p.click('#drawBtn');
  await p.evaluate(() => { document.querySelectorAll('.lun').forEach(l => l.classList.add('open')); });
  await p.click('[data-stk="sy2"]');
  await p.click('#yzBtn');
  await p.click('#sdBtn');
  await p.click('#zhBtn');
  await p.click('#fieldBtn');
});
await snap(390, 844, '/tmp/mq_mobile_full.png', async (p) => {
  await p.click('#drawBtn');
  await p.evaluate(() => { document.querySelectorAll('.lun').forEach(l => l.classList.add('open')); });
});
await browser.close();
console.log('done');
