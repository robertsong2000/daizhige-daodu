import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/guiqian-zhi.html');
await p.waitForTimeout(400);
await p.screenshot({ path: '/tmp/gq_0_hero.png' });

// grind the stele
await p.click('#grindbtn');
await p.waitForTimeout(6000);
await p.screenshot({ path: '/tmp/gq_1_ground.png' });

// mill slab
await p.evaluate(() => document.getElementById('slab').scrollIntoView({ behavior: 'instant', block: 'center' }));
await p.click('#millbtn');
await p.waitForTimeout(1700);
await p.click('#fallbtn');
await p.waitForTimeout(1500);
await p.screenshot({ path: '/tmp/gq_2_mill.png' });

// flip a tablet
await p.evaluate(() => document.getElementById('tab2').scrollIntoView({ behavior: 'instant', block: 'center' }));
await p.click('#tab2');
await p.waitForTimeout(1000);
await p.screenshot({ path: '/tmp/gq_3_tab.png' });

// shifeng toggle + lamps
await p.evaluate(() => document.getElementById('sfZhi').scrollIntoView({ behavior: 'instant', block: 'center' }));
await p.click('#sfZhi');
await p.click('#lamps .lamp:nth-child(2)');
await p.waitForTimeout(700);
await p.screenshot({ path: '/tmp/gq_4_sf.png' });

// full page height + bottom
const h = await p.evaluate(() => document.body.scrollHeight);
console.log('body scrollHeight:', h);
await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await p.waitForTimeout(400);
await p.screenshot({ path: '/tmp/gq_5_end.png' });

console.log('errors:', errors.length ? errors : 'none');
await b.close();
