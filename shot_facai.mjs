import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
p.on('pageerror', e => errors.push('pageerror: ' + e.message));
p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/facai-mijue.html');
await p.waitForTimeout(500);

// 1 hero: hold bubble then release
const bub = await p.$('#bubble');
const bb = await bub.boundingBox();
await p.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2);
await p.mouse.down();
await p.waitForTimeout(500);
await p.screenshot({ path: 'shot_facai_hero_blow.png' });
await p.mouse.up();
await p.waitForTimeout(900);
const cnt = await p.textContent('#cnt');
console.log('counter after pop:', cnt);

// 2 door ring + scroll
await p.click('.door[data-go="hui3"]');
await p.waitForTimeout(900);

// 3 scale switch
await p.click('.sbtn[data-lb="24"]');
await p.waitForTimeout(600);
const rdv = await p.textContent('#rdv');
console.log('scale 24liang reading:', rdv);
await p.screenshot({ path: 'shot_facai_scale.png' });

// 4 planchette
await p.click('#jisand');
await p.waitForTimeout(300);
await p.screenshot({ path: 'shot_facai_ji.png' });

// 5 heart flip
await p.evaluate(() => document.getElementById('hui10').scrollIntoView({ behavior: 'instant' }));
await p.waitForTimeout(300);
await p.click('#heartbtn');
await p.waitForTimeout(700);
await p.evaluate(() => document.querySelector('.heartstage').scrollIntoView({ behavior: 'instant', block: 'center' }));
await p.waitForTimeout(200);
await p.screenshot({ path: 'shot_facai_heart.png' });

// 6 full page segments
const h = await p.evaluate(() => document.body.scrollHeight);
console.log('page height', h);
let y = 0, i = 0;
while (y < h) {
  await p.evaluate(v => window.scrollTo(0, v), y);
  await p.waitForTimeout(160);
  await p.screenshot({ path: `shot_facai_p${String(i).padStart(2, '0')}.png` });
  y += 860; i++;
  if (i > 14) break;
}
console.log('errors:', errors.length ? errors : 'none');
await b.close();
