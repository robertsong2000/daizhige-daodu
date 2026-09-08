import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const errors = [];

async function shoot(width, height, tag, clickSlip) {
  const p = await b.newPage({ viewport: { width, height } });
  p.on('pageerror', e => errors.push(tag + ' pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errors.push(tag + ' console: ' + m.text()); });
  await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/yushaobao.html');
  await p.waitForTimeout(400);

  // 断言：回目格 40、月令格无、五签兑现文可开
  const rows = await p.evaluate(() => document.querySelectorAll('#ml .mu').length);
  const slips = await p.evaluate(() => document.querySelectorAll('.slot').length);
  console.log(tag, 'mulu rows', rows, 'slots', slips);
  if (clickSlip) {
    await p.click('.slot[data-k="a"] .slip');
    await p.waitForTimeout(500);
    const pay = await p.evaluate(() => document.getElementById('payoff').textContent.length);
    console.log(tag, 'payoff len after click', pay);
    await p.evaluate(() => document.getElementById('board').scrollIntoView());
    await p.waitForTimeout(200);
    await p.screenshot({ path: `/tmp/ysb_${tag}_board.png` });
  }

  const h = await p.evaluate(() => document.body.scrollHeight);
  console.log(tag, 'page height', h);
  let n = 0;
  for (let y = 0; y < h; y += height) {
    await p.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
    await p.waitForTimeout(160);
    await p.screenshot({ path: `/tmp/ysb_${tag}_${String(n).padStart(2, '0')}.png` });
    n++;
  }
  // 横向溢出检查
  const ov = await p.evaluate(() => {
    let bad = [];
    document.querySelectorAll('*').forEach(el => {
      if (el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0 && !/HTML|BODY/.test(el.tagName))
        bad.push(el.tagName + '.' + (el.className && el.className.baseVal !== undefined ? '' : String(el.className).slice(0, 24)) + ' sw=' + el.scrollWidth + ' cw=' + el.clientWidth);
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
