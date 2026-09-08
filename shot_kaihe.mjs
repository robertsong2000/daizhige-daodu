import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const errors = [];

async function shoot(width, height, tag, withRun) {
  const p = await b.newPage({ viewport: { width, height } });
  p.on('pageerror', e => errors.push(tag + ' pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errors.push(tag + ' console: ' + m.text()); });
  await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/kaihe-ji.html');
  await p.waitForTimeout(400);

  const stns = await p.evaluate(() => document.querySelectorAll('.stn').length);
  const qn = await p.evaluate(() => document.querySelectorAll('q').length);
  console.log(tag, 'stns', stns, 'quotes', qn);

  if (withRun) {
    // 桩号点击跳转
    await p.click('.stn[data-t="st6"]');
    await p.waitForTimeout(1600);
    const y6 = await p.evaluate(() => Math.abs(document.getElementById('st6').getBoundingClientRect().top));
    console.log(tag, 'nav st6 offset', y6.toFixed(0));

    // 放鹅验水
    await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
    await p.click('#run');
    await p.waitForTimeout(4300);
    const st = await p.evaluate(() => ({
      on: document.querySelectorAll('.sh.on').length,
      bur: document.querySelectorAll('.sh.bur').length,
      cnt: document.getElementById('gcount').textContent,
      resHidden: document.getElementById('gres').hidden,
    }));
    console.log(tag, 'goose run', JSON.stringify(st));
    if (st.bur !== 129 || st.resHidden) errors.push(tag + ' goose run incomplete: ' + JSON.stringify(st));
    await p.waitForTimeout(200);
    await p.screenshot({ path: `/tmp/kh_${tag}_canal.png` });
  }

  const h = await p.evaluate(() => document.body.scrollHeight);
  console.log(tag, 'page height', h);
  let n = 0;
  for (let y = 0; y < h; y += height) {
    await p.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
    await p.waitForTimeout(150);
    await p.screenshot({ path: `/tmp/kh_${tag}_${String(n).padStart(2, '0')}.png` });
    n++;
  }
  const ov = await p.evaluate(() => {
    let bad = [];
    document.querySelectorAll('*').forEach(el => {
      if (el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0 && !/HTML|BODY/.test(el.tagName))
        bad.push(el.tagName + '.' + String(el.className).slice(0, 24) + ' sw=' + el.scrollWidth + ' cw=' + el.clientWidth);
    });
    return { docW: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, bad: bad.slice(0, 6) };
  });
  console.log(tag, 'overflow', JSON.stringify(ov));
  console.log(tag, 'shots', n);
  await p.close();
}

await shoot(1280, 900, 'd', true);
await shoot(390, 844, 'm', false);
console.log('js errors:', errors.length ? errors.join(' | ') : 'none');
await b.close();
