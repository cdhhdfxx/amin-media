const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
p.on('pageerror',e=>console.log('ERR',e.message));const fs=require('fs');
const [a,z]=process.argv[2].split('-').map(Number);
for(let n=a;n<=z;n++){await p.goto('file://'+process.cwd()+'/c250.html#'+n);await p.reload();await p.evaluate(()=>document.fonts.ready);await p.waitForFunction(()=>window.done);await p.waitForTimeout(120);
const out=`/home/user/amin-media/b250/${String(n).padStart(3,'0')}`;fs.mkdirSync(out,{recursive:true});
for(let i=1;i<=3;i++){await (await p.$('#s'+i)).screenshot({path:`${out}/0${i}.jpg`,type:'jpeg',quality:90})}}
await b.close()})();
