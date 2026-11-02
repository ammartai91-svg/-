const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
const SP='/tmp/claude-0/-home-user--/44f0374b-d1ad-5875-83a0-57a308b6ed03/scratchpad';
const jobs=JSON.parse(process.argv[2]);
(async()=>{
  const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
  await pg.goto('file://'+SP+'/render/scene.html');
  const d=f=>'data:image/png;base64,'+fs.readFileSync(f).toString('base64');
  await pg.evaluate(async([l,e])=>{await loadImg('logo',l);await loadImg('embryo',e);
    await document.fonts.load('800 80px "Alexandria"','حلم');await document.fonts.load('500 80px "Alexandria"','حلم');
    await document.fonts.load('700 80px "IBM Plex Sans Arabic"','حلم');await document.fonts.load('500 80px "IBM Plex Sans Arabic"','حلم');},
    [d('/home/user/-/clinic-logo/logo-white-outline.png'),d(SP+'/embryo.png')]);
  for(const j of jobs){
    if(j.title)await pg.evaluate(([s,c])=>setTitle(s,c),[j.title,j.check]);
    if(j.stills){for(const t of j.stills){await pg.evaluate(([s,t])=>frame(s,t),[j.scene,t]);
      const u=await pg.evaluate(()=>grab('image/png'));fs.writeFileSync(`${j.out}_${t}.png`,Buffer.from(u.split(',')[1],'base64'));}continue;}
    const alpha=j.scene==='title';
    const args=['-y','-v','error','-f','image2pipe','-framerate','30','-i','-'];
    if(alpha)args.push('-c:v','prores_ks','-profile:v','4444','-pix_fmt','yuva444p10le',j.out);
    else args.push('-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',j.out);
    const ff=spawn('ffmpeg',args,{stdio:['pipe','inherit','inherit']});
    const N=Math.round(j.dur*30);
    for(let i=0;i<N;i++){await pg.evaluate(([s,t])=>frame(s,t),[j.scene,i/30]);
      const u=await pg.evaluate(a=>grab(a?'image/png':'image/jpeg'),alpha);
      const buf=Buffer.from(u.split(',')[1],'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
    ff.stdin.end();await new Promise(r=>ff.on('close',r));console.log('done',j.out);
  }
  await b.close();
})();
