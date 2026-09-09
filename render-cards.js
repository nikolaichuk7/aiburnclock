// Render share images (1200x630 PNG) for the national release and every state, from site/data.json.
// Usage: node render-cards.js  (needs playwright; uses the GlossPlate node_modules if run from there via NODE_PATH)
const fs = require('fs'); const path = require('path');
const { chromium } = require('playwright');
const SITE = path.join(__dirname, 'site'); const OUT = path.join(SITE, 'og'); fs.mkdirSync(OUT, { recursive: true });
const D = JSON.parse(fs.readFileSync(path.join(SITE, 'data.json'), 'utf8'));
const full = n => '$' + Math.round(n).toLocaleString('en-US');
const money = n => { for (const [v, s] of [[1e12,'T'],[1e9,'B'],[1e6,'M'],[1e3,'K']]) if (Math.abs(n) >= v) return '$' + (n / v).toFixed(n / v >= 100 ? 0 : 1) + s; return '$' + Math.round(n); };
const P = {}; for (const k in D.params) P[k] = D.params[k].default;
const emblem = fs.readFileSync(path.join(__dirname, 'templates', 'emblem.svg'), 'utf8').replace(/width="200" height="200"/, 'width="150" height="150"');
function card({ kicker, line1, line2, figure, sub, foot }) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
  body{margin:0;width:1200px;height:630px;background:#fcfcfb;font-family:"Public Sans","Helvetica Neue",Helvetica,Arial,sans-serif;color:#1b1b1b;position:relative;overflow:hidden}
  .band{position:absolute;left:0;top:0;width:1200px;height:118px;background:#1a4480;color:#fff}
  .band .n{position:absolute;left:60px;top:26px;font-family:Georgia,"Times New Roman",serif;font-weight:900;font-size:40px}
  .band .s{position:absolute;left:60px;top:78px;font-size:15px;letter-spacing:4px;opacity:.85}
  .emb{position:absolute;right:44px;top:136px}
  .k{position:absolute;left:60px;top:160px;font-family:Menlo,monospace;font-size:18px;letter-spacing:3px;color:#565c65}
  .l{position:absolute;left:60px;top:196px;width:860px;font-family:Georgia,serif;font-weight:700;font-size:32px;line-height:1.22}
  .f{position:absolute;left:60px;top:338px;font-family:Menlo,monospace;font-weight:700;font-size:92px;color:#b50909;letter-spacing:-2px;white-space:nowrap}
  .sub{position:absolute;left:60px;top:462px;width:1080px;font-size:24px;color:#565c65}
  .rule{position:absolute;left:60px;top:520px;width:1080px;height:3px;background:#1b1b1b}
  .foot{position:absolute;left:60px;top:545px;font-family:Menlo,monospace;font-size:18px;color:#565c65}
  </style></head><body>
  <div class="band"><div class="n">AI Burn Clock</div><div class="s">INDEX OF THE COST OF RETRIEVAL BY READING IN AI SYSTEMS</div></div>
  <div class="emb">${emblem}</div>
  <div class="k">${kicker}</div><div class="l">${line1}${line2 ? '<br>' + line2 : ''}</div>
  <div class="f">${figure}</div><div class="sub">${sub}</div><div class="rule"></div><div class="foot">${foot}</div>
  </body></html>`;
}
(async () => {
  const browser = await chromium.launch(); const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  const date = D.fetched_utc.slice(0, 10);
  const jobs = [];
  // national: agency of 2,000 at reference parameters
  const T = { req: 40, bytes: 150, price: 3, days: 250 }; const devs = 2000;
  const read = devs * T.req * T.days * (T.bytes * 1024 / 4) / 1e6 * T.price; const burn = read * P.overhead;
  jobs.push(['national.png', card({ kicker: `RELEASE ${date} · SERIES AIB-1`, line1: 'AI agents read up to 47 times more than they use.', line2: 'Avoidable reading, agency of 2,000 developers:', figure: full(burn) + ' a year', sub: `${full(burn / 12)} a month · the fully loaded cost of ${(burn / 185000).toFixed(1)} senior engineers · reference parameters, every one a control on the page`, foot: 'aiburnclock.org · Treasury · USAspending · Census · Gartner · open method' })]);
  for (const s of D.states) {
    const yr = s.ai_fy2026 * P.inference_share * P.agent_share * P.overhead;
    jobs.push([`state-${s.code.toLowerCase()}.png`, card({ kicker: `STATE RELEASE ${date} · ${s.name.toUpperCase()}`, line1: `Federal contracts naming AI performed in ${s.name},`, line2: 'fiscal year 2026 to date:', figure: money(s.ai_fy2026), sub: `${s.pop ? '$' + (s.ai_fy2026 / s.pop).toFixed(2) + ' per resident · ' : ''}avoidable reading on that figure at the reference factors: ${full(yr)} a year, a scenario computed from a published floor`, foot: `aiburnclock.org/state/${s.code.toLowerCase()}/ · USAspending.gov · Census Bureau` })]);
  }
  { const e = fs.readFileSync(path.join(__dirname,'templates','emblem.svg'),'utf8'); await page.setViewportSize({width:512,height:512}); await page.setContent(`<body style="margin:0;background:#fff">${e.replace(/width="200" height="200"/,'width="512" height="512"')}</body>`); await page.screenshot({path: path.join(SITE,'emblem.png'), type:'png'}); await page.setViewportSize({width:1200,height:630}); }
  for (const [name, html] of jobs) { await page.setContent(html, { waitUntil: 'load' }); await page.screenshot({ path: path.join(OUT, name), type: 'png' }); }
  await browser.close(); console.log(`rendered ${jobs.length} cards to site/og/`);
})();
