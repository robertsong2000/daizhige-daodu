import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';
const exe = process.env.HOME + '/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: {width:1280,height:900} });
page.on('pageerror', e => console.log('PAGEERROR:', e.message));
page.on('console', m => { if (m.type() === 'error') console.log('CONSOLE:', m.text()); });
await page.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/huiwen-leiju.html');
await page.waitForTimeout(500);
const w = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
console.log('scrollWidth', w.sw, w.sw > w.cw ? 'OVERFLOW!' : 'ok');
// 1 hero: tile 数
console.log('hero tiles:', await page.locator('#strip i.tl').count());
// 2 flip
await page.click('#flipbtn');
await page.waitForTimeout(600);
console.log('flip state:', await page.textContent('#stripstate'), '| njrv visible:', await page.locator('#njrv').isVisible(), '| first tile:', await page.textContent('#strip i.tl >> nth=0'));
await page.screenshot({ path: '/tmp/hui_hero_flip.png' });
await page.click('#flipbtn');
// 3 knot
await page.click('.knot[data-k="3"]');
await page.waitForTimeout(200);
console.log('knot3:', (await page.textContent('#kpanel .ktit')).trim());
// 4 rvbtn
await page.click('.rvbtn[data-t="fw1"]');
await page.waitForTimeout(200);
console.log('rv1 on:', await page.locator('#rv1').getAttribute('class'), 'tiles:', await page.locator('#rv1 .rvt i').count(), 'first:', await page.textContent('#rv1 .rvt i >> nth=0'));
// 5 五色 tiles
console.log('weave rows tiles:', await page.locator('#weave .wrow i').count());
// 6 tag
await page.click('.tag[data-t="5"]');
await page.waitForTimeout(200);
console.log('tag5:', (await page.textContent('#tagpanel .tg')).trim());
// 7 jline
await page.click('.jcard:has-text("次圭甫韵") .jline >> nth=0');
console.log('jline rev class:', await page.locator('.jcard:has-text("次圭甫韵") .jline >> nth=0').getAttribute('class'));
// 8 chip
await page.click('.chip[data-c="3"]');
await page.waitForTimeout(200);
console.log('chip3:', (await page.textContent('#chippanel .ktit')).trim());
await page.screenshot({ path: '/tmp/hui_full.png', fullPage: true });
const mob = await browser.newPage({ viewport: {width:390,height:844} });
await mob.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/huiwen-leiju.html');
await mob.waitForTimeout(400);
const mw = await mob.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
console.log('mobile scrollWidth', mw.sw, mw.sw > mw.cw ? 'OVERFLOW!' : 'ok');
await mob.screenshot({ path: '/tmp/hui_mobile.png', fullPage: true });
await browser.close();
console.log('done');
