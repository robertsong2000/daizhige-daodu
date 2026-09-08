import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 860 } });
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/quxue-pian.html');
await page.waitForTimeout(500);

let n = 0;
await page.screenshot({ path: `/tmp/qx_${String(++n).padStart(2, '0')}_fold.png` });

const H = await page.evaluate(() => document.body.scrollHeight);
for (let y = 820; y < H; y += 800) {
  await page.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(120);
  await page.screenshot({ path: `/tmp/qx_${String(++n).padStart(2, '0')}.png` });
}

// 五知交互:点知惧
await page.click('.seal[data-k="1"]');
await page.waitForTimeout(200);
await page.evaluate(() => document.querySelector('.seals').scrollIntoView({ block: 'center', behavior: 'instant' }));
await page.waitForTimeout(150);
await page.screenshot({ path: `/tmp/qx_${String(++n).padStart(2, '0')}_seal2.png` });

// 检查 JS 错误与面板渲染
const panelHTML = await page.evaluate(() => document.getElementById('fpanel').innerHTML.length);
console.log('panel html len:', panelHTML, 'screens:', n);
await browser.close();
