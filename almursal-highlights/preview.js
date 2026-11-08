const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:520}});
const f=['01-dr-ibtisam-sahib','02-dr-shahad-hamid','03-almursal-lab'];const l=['د. ابتسام صاحب','د. شهد حامد','المختبر'];
await p.setContent(`<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@500&display=swap" rel="stylesheet"><body dir=rtl style="margin:0;background:#0a0d33;display:flex;gap:70px;justify-content:center;align-items:center;height:520px;font-family:Tajawal">`+
f.map((x,i)=>`<div style="text-align:center;color:#fff;font-size:26px"><div style="width:300px;height:300px;border-radius:50%;padding:8px;border:3px solid #ffffff55"><div style="width:100%;height:100%;border-radius:50%;background:url(data:image/png;base64,${require('fs').readFileSync(__dirname+'/'+x+'.png').toString('base64')}) center/cover"></div></div><div style="margin-top:18px">${l[i]}</div></div>`).join('')+`</body>`);
await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(500);
await p.screenshot({path:__dirname+'/preview-profile.png'});await b.close();})();
