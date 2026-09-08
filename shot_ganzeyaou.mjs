import { chromium } from '/home/robertsong/workspace/claude/raptor-engine-3d/node_modules/playwright-core/index.mjs';

const exe = '/home/robertsong/.cache/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-linux64/chrome-headless-shell';
const url = 'file:///home/robertsong/workspace/claude/daizhige-daodu/ganzeyaou.html';
const errors = [];
const browser = await chromium.launch({ executablePath: exe });

for (const vp of [{ width: 1280, height: 900, tag: 'desktop' }, { width: 390, height: 844, tag: 'mobile' }]) {
  const page = await browser.newPage({ viewport: vp });
  page.on('pageerror', e => errors.push(vp.tag + ' pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(vp.tag + ' console: ' + m.text()); });
  await page.goto(url, { waitUntil: 'load' });
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important} *{animation:none!important;transition:none!important}' });

  // 溢出检查
  const ov = await page.evaluate(() => {
    const bad = [];
    const dw = document.documentElement.clientWidth;
    document.querySelectorAll('body *').forEach(el => {
      if (el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0) {
        bad.push(el.tagName + '.' + (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className) + ' sw=' + el.scrollWidth + ' cw=' + el.clientWidth);
      }
      const r = el.getBoundingClientRect();
      if (r.right > dw + 2 && r.width > 8) bad.push('RIGHT ' + el.tagName + '.' + el.className + ' right=' + Math.round(r.right));
    });
    return { bad: bad.slice(0, 12), docW: document.documentElement.scrollWidth };
  });
  console.log(vp.tag, 'overflow:', ov.bad.length ? ov.bad : 'none', 'docW=', ov.docW);

  // 分屏截图（long page）
  const H = await page.evaluate(() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));
  console.log(vp.tag, 'pageHeight=', H);
  let n = 0;
  for (let y = 0; y < H && n < 14; y += vp.height) {
    await page.evaluate(sy => window.scrollTo(0, sy), y);
    await page.waitForTimeout(120);
    await page.screenshot({ path: `shot_ganzeyaou_${vp.tag}_${String(n).padStart(2, '0')}.png` });
    n++;
  }

  // 交互断言（desktop 跑一遍）
  if (vp.tag === 'desktop') {
    await page.click('#bagbtn');
    const slipsOpen = await page.evaluate(() => document.getElementById('slips').classList.contains('open'));
    const slipsVisible = await page.evaluate(() => getComputedStyle(document.querySelector('.paper.w')).display !== 'none');
    console.log('interact slips open/visible:', slipsOpen, slipsVisible);
    await page.evaluate(() => document.querySelector('#p9').scrollIntoView());
    await page.waitForTimeout(200);
    await page.click('#blowbtn');
    await page.waitForTimeout(600);
    const cracked = await page.evaluate(() => ({
      cls: document.getElementById('flute').classList.contains('crack'),
      btn: document.getElementById('blowbtn').textContent,
      dis: document.getElementById('blowbtn').disabled
    }));
    console.log('interact flute:', JSON.stringify(cracked));
    // 锚点跳转
    await page.click('.scale a[href="#p7"]');
    await page.waitForTimeout(300);
    const near = await page.evaluate(() => {
      const r = document.getElementById('p7').getBoundingClientRect();
      return Math.abs(r.top) < 120;
    });
    console.log('anchor #p7 near top:', near);
    // 引文块可见性（纸底墨字）
    const qcolor = await page.evaluate(() => {
      const q = document.querySelector('.q p');
      return getComputedStyle(q).color;
    });
    console.log('quote ink color:', qcolor);
    await page.evaluate(() => document.getElementById('bagbtn').scrollIntoView({ block: 'center' }));
    await page.waitForTimeout(150);
    await page.screenshot({ path: 'shot_ganzeyaou_slips.png' });
    await page.evaluate(() => document.getElementById('flute').scrollIntoView({ block: 'center' }));
    await page.waitForTimeout(150);
    await page.screenshot({ path: 'shot_ganzeyaou_flute.png' });
  }
  await page.close();
}
await browser.close();
console.log('ERRORS:', errors.length, errors.slice(0, 6));
process.exit(errors.length ? 1 : 0);
