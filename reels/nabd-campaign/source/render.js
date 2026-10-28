const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = process.argv[2], mode = process.argv[3] || 'test';
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const paths = fs.readFileSync(path.join(dir, 'paths.json'), 'utf8');
  await page.addInitScript(`window.__PATHS__ = ${paths};`);
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.goto('file://' + path.join(dir, process.env.PAGE || 'reel.html'));
  await page.evaluate(() => window.__ready);
  const el = await page.$('#stage');
  if (mode === 'test') {
    const ts = process.argv.slice(4).map(Number);
    for (const t of ts) { await page.evaluate(t => render(t), t); await el.screenshot({ path: path.join(dir, `test_${t}.jpg`), type: 'jpeg', quality: 80 }); }
  } else {
    fs.mkdirSync(path.join(dir, 'frames'), { recursive: true });
    const fps = 30, N = 40 * fps;
    for (let i = 0; i < N; i++) {
      await page.evaluate(t => render(t), i / fps);
      await el.screenshot({ path: path.join(dir, 'frames', `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92 });
      if (i % 150 === 0) console.log('frame', i);
    }
  }
  await browser.close();
})();
