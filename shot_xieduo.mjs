import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/xie-duo.html');
await p.waitForTimeout(600);
await p.screenshot({ path: '/tmp/xd_0_hero.png' });

await p.click('#bell');
await p.waitForTimeout(500);
await p.screenshot({ path: '/tmp/xd_1_ring.png' });

for (const [sel, name] of [['#origin', 'origin'], ['#wall', 'wall'], ['#ring', 'ring'], ['#author', 'author'], ['#colla', 'colla'], ['footer', 'footer']]) {
  await p.evaluate(s => document.querySelector(s).scrollIntoView({ behavior: 'instant', block: 'start' }), sel);
  await p.waitForTimeout(250);
  await p.screenshot({ path: `/tmp/xd_2_${name}.png` });
}
console.log(JSON.stringify({ errors }));
await b.close();
