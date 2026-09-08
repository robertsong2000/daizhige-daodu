import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/tongpu.html');
await p.waitForTimeout(700);
await p.screenshot({ path: '/tmp/tp_0_cover.png' });

await p.evaluate(() => document.getElementById('s-ji').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(400);
await p.screenshot({ path: '/tmp/tp_1_plan.png' });

await p.evaluate(() => document.getElementById('s-qin').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(400);
const hui = await p.$$('.hui');
await hui[6].click();
await p.waitForTimeout(300);
await p.screenshot({ path: '/tmp/tp_2_qin.png' });

await p.evaluate(() => document.getElementById('s-zashuo').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(400);
await p.screenshot({ path: '/tmp/tp_3_ghost.png' });

const h = await p.evaluate(() => document.body.scrollHeight);
console.log('pageHeight', h, 'errors', JSON.stringify(errors));
await b.close();
