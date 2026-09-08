import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const url = 'file:///home/robertsong/workspace/claude/daizhige-daodu/gujin-fengyao.html';
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });

async function snap(w, h, out) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  await page.goto(url, { waitUntil: 'load' });
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await page.evaluate(async () => {
    const step = Math.round(innerHeight * 0.8);
    for (let y = 0; y <= document.body.scrollHeight; y += step) {
      scrollTo({ top: y, behavior: 'instant' });
      await new Promise(r => setTimeout(r, 60));
    }
    scrollTo({ top: 0, behavior: 'instant' });
  });
  await page.waitForTimeout(400);
  await page.screenshot({ path: out, fullPage: true });
  console.log(out, 'ok', await page.title(), errs.length ? 'JS-ERRORS: ' + errs.join('; ') : '(no js errors)');
  await page.close();
}

await snap(1200, 900, '/tmp/gujin_desktop.png');
await snap(390, 844, '/tmp/gujin_mobile.png');
await browser.close();
console.log('done');
