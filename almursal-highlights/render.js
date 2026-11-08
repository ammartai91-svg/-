const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+__dirname+'/covers.html');await p.waitForLoadState('networkidle');await p.evaluate(()=>document.fonts.ready);
const names={c1:'01-dr-ibtisam-sahib',c2:'02-dr-shahad-hamid',c3:'03-almursal-lab'};
for(const id in names){await (await p.$('#'+id)).screenshot({path:__dirname+'/'+names[id]+'.png'});}
await b.close();})();
