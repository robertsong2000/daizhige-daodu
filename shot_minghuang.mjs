import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const CHROME = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const URL = 'file:///home/robertsong/workspace/claude/daizhige-daodu/minghuang-zalu.html';
const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });

async function snap(width, height, out, fullPage) {
  const p = await b.newPage({ viewport: { width, height } });
  const errors = [];
  p.on('pageerror', e => errors.push('pageerror: ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  await p.goto(URL);
  await p.waitForTimeout(600);
  // 逐段滚动触发入场与更漏填充
  const H = await p.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < H; y += 600) { await p.evaluate(v => window.scrollTo(0, v), y); await p.waitForTimeout(60); }
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.waitForTimeout(700);
  // 交互：舞马切换 + 雨铃（静音环境不会真出声，只验证不抛错）
  await p.click('.wm .bar button[data-p="p2"]');
  await p.waitForTimeout(200);
  const paneOn = await p.evaluate(() => document.querySelector('.pane.p2').classList.contains('on') && !document.querySelector('.pane.p1').classList.contains('on'));
  await p.click('.wm .bar button[data-p="p1"]');
  await p.click('#bellBtn');
  await p.waitForTimeout(300);
  const ringing = await p.evaluate(() => document.getElementById('bellBtn').classList.contains('ring'));
  const spineH = await p.evaluate(() => {
    document.querySelectorAll('.act').forEach(a => window.scrollTo(0, a.offsetTop + a.offsetHeight / 3));
    window.scrollTo(0, document.querySelector('.act').offsetTop + 200);
    return Array.from(document.querySelectorAll('.act .fill')).map(f => f.style.height);
  });
  if (fullPage) {
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.waitForTimeout(400);
    await p.screenshot({ path: out, fullPage: true });
  } else {
    await p.screenshot({ path: out });
  }
  console.log(out, 'paneOn=' + paneOn, 'ringing=' + ringing, 'spine=' + JSON.stringify(spineH), 'errors=' + errors.length);
  if (errors.length) console.log(errors.join('\n'));
  await p.close();
}

await snap(1280, 900, 'shot_minghuang_hero.png', false);
await snap(390, 844, 'shot_minghuang_mob.png', false);
await snap(1280, 900, 'shot_minghuang_full.png', true);
await b.close();
