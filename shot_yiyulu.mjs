import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const URL = 'file:///home/robertsong/workspace/claude/daizhige-daodu/yiyu-lu.html';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const errors = [];

async function noOverflow(p, tag) {
  const sw = await p.evaluate(() => document.scrollingElement.scrollWidth);
  const iw = await p.evaluate(() => window.innerWidth);
  console.log(tag, 'scrollWidth', sw, 'innerWidth', iw, sw <= iw ? 'OK' : 'OVERFLOW!');
  if (sw > iw) errors.push('overflow ' + tag);
}

async function juanAt(p, frac, path) {
  await p.evaluate((f) => {
    const juan = document.getElementById('juan');
    const top = juan.getBoundingClientRect().top + window.scrollY;
    const total = juan.offsetHeight - window.innerHeight;
    window.scrollTo(0, top + total * f);
  }, frac);
  await p.waitForTimeout(350);
  await p.screenshot({ path });
}

// desktop
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await p.goto(URL);
await p.waitForTimeout(500);
await p.screenshot({ path: '/tmp/yy_0_hero.png' });

await juanAt(p, 0.08, '/tmp/yy_1_juan_start.png');
await juanAt(p, 0.45, '/tmp/yy_2_juan_mid.png');
await juanAt(p, 0.85, '/tmp/yy_3_juan_ice.png');
await juanAt(p, 0.99, '/tmp/yy_4_juan_end.png');

await p.evaluate(() => document.getElementById('chi').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(250);
await p.screenshot({ path: '/tmp/yy_5_chi.png' });

await p.evaluate(() => document.getElementById('qa').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(200);
const d1 = await p.$('#qa details');
await d1.click();
await p.waitForTimeout(250);
await p.screenshot({ path: '/tmp/yy_6_qa.png' });

await p.evaluate(() => document.getElementById('duiyin').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(200);
const cards = await p.$$('#wall .card');
await cards[1].click();
await cards[4].click();
await p.waitForTimeout(700);
await p.screenshot({ path: '/tmp/yy_7_duiyin.png' });

await p.evaluate(() => document.getElementById('fasu').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(250);
await p.screenshot({ path: '/tmp/yy_8_fasu.png' });

await p.evaluate(() => document.getElementById('epi').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(250);
await p.screenshot({ path: '/tmp/yy_9_epi.png' });
await noOverflow(p, 'desktop');
await p.close();

// mobile
const m = await b.newPage({ viewport: { width: 390, height: 844 } });
m.on('pageerror', e => errors.push('m pageerror: ' + e.message));
m.on('console', c => { if (c.type() === 'error') errors.push('m console: ' + c.text()); });
await m.goto(URL);
await m.waitForTimeout(500);
await m.screenshot({ path: '/tmp/yy_m0_hero.png' });
await juanAt(m, 0.5, '/tmp/yy_m1_juan.png');
await m.evaluate(() => document.getElementById('duiyin').scrollIntoView({ behavior: 'instant' }));
await m.waitForTimeout(300);
await m.screenshot({ path: '/tmp/yy_m2_duiyin.png' });
await noOverflow(m, 'mobile');
await m.close();

await b.close();
console.log(errors.length ? 'ERRORS:\n' + errors.join('\n') : 'NO JS ERRORS');
