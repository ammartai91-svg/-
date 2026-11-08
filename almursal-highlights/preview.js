const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:720,height:300}});
const f=['03-almursal-lab','01-dr-ibtisam-sahib','02-dr-shahad-hamid'];const l=['المختبر','د. ابتسام صاحب','د. شهد حامد'];
await p.setContent(`<body dir=rtl style="margin:0;background:#16181d;display:flex;gap:40px;justify-content:center;align-items:center;height:300px;font-family:sans-serif">`+
f.reverse().map((x,i)=>`<div style="text-align:center;color:#fff;font-size:20px"><div style="width:136px;height:136px;border-radius:50%;padding:5px;border:3px solid #555"><div style="width:100%;height:100%;border-radius:50%;background:url(data:image/png;base64,${fs.readFileSync(__dirname+'/'+x+'.png').toString('base64')}) center/cover"></div></div><div style="margin-top:12px">${l.slice().reverse()[i]}</div></div>`).join('')+`</body>`);
await p.waitForTimeout(300);await p.screenshot({path:__dirname+'/preview-profile.png'});await b.close();})();
