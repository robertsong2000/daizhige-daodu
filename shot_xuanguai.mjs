import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const errors = [];

async function shoot(width, height, tag, withRun) {
  const p = await b.newPage({ viewport: { width, height } });
  p.on('pageerror', e => errors.push(tag + ' pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errors.push(tag + ' console: ' + m.text()); });
  await p.goto('file:///home/robertsong/workspace/claude/daizhige-daodu/xuanguai-lu.html');
  await p.waitForTimeout(400);

  const qn = await p.evaluate(() => document.querySelectorAll('q').length);
  console.log(tag, 'quotes', qn);

  if (withRun) {
    // 四物点灯 → 雨止 + 判词
    for (const t of ['p1','p2','p3','p4']) {
      await p.click(`.obj[data-poem="${t}"]`);
      await p.waitForTimeout(120);
    }
    await p.waitForTimeout(900);
    const st = await p.evaluate(() => ({
      lit: document.querySelectorAll('.obj.lit').length,
      on: document.querySelectorAll('.couplets q.on').length,
      dry: document.getElementById('scene').classList.contains('dry'),
      punch: document.getElementById('punch').classList.contains('on'),
    }));
    console.log(tag, 'objects', JSON.stringify(st));
    if (st.lit !== 4 || st.on !== 4 || !st.dry || !st.punch) errors.push(tag + ' objects incomplete');

    // 六情牌：点爱
    await p.click('#love');
    await p.waitForTimeout(200);
    const yi = await p.evaluate(() => document.getElementById('yi').classList.contains('on'));
    if (!yi) errors.push(tag + ' love chip failed');

    // 剖桔
    await p.click('#cut-bt');
    await p.waitForTimeout(900);
    const ju = await p.evaluate(() => ({
      cut: document.getElementById('ju').classList.contains('cut'),
      q: !document.getElementById('juquote').hidden,
    }));
    console.log(tag, 'orange', JSON.stringify(ju));
    if (!ju.cut || !ju.q) errors.push(tag + ' orange failed');

    // 击鼓两步
    await p.click('#drum-bt'); await p.waitForTimeout(300);
    await p.click('#drum-bt'); await p.waitForTimeout(800);
    const d = await p.evaluate(() => document.querySelectorAll('.drumlines q.on').length);
    if (d !== 2) errors.push(tag + ' drum failed: ' + d);

    await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
    await p.waitForTimeout(300);
    await p.screenshot({ path: '/tmp/xg_d_scene.png' });
  }

  const h = await p.evaluate(() => document.body.scrollHeight);
  console.log(tag, 'page height', h);
  let n = 0;
  for (let y = 0; y < h; y += height) {
    await p.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
    await p.waitForTimeout(150);
    await p.screenshot({ path: `/tmp/xg_${tag}_${String(n).padStart(2, '0')}.png` });
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
