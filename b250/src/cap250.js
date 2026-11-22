const fs=require('fs');const B250=eval(fs.readFileSync(__dirname+'/b250.js','utf8').replace('const B250=','(').replace(/\];\s*$/,']')+')');
const strip=s=>s.replace(/<[^>]+>/g,'');const em=['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣'];
const tags=['#تداول #فوركس #متداول #أكاديمية_الأمين','#تداول #فوركس #علم_نفس_التداول #أكاديمية_الأمين','#تداول #فوركس #إدارة_المخاطر #أكاديمية_الأمين','#تداول #فوركس #تحليل_فني #أكاديمية_الأمين'];
for(const p of B250){const d=`/home/user/amin-media/b250/${String(p.n).padStart(3,'0')}`;if(!fs.existsSync(d))continue;
 const title=strip([...p.t,p.hl,p.t2].filter(Boolean).join(' ')).replace(/\s+/g,' ').trim();
 const c=`${title} 👇\n${p.sub}\n\n${p.items.map((it,i)=>`${em[i]} ${strip(it[1])}`).join('\n')}\n\n💡 ${strip(p.tip)}\n\n${strip(p.q)} اكتب جوابك بالتعليقات 👇\nاحفظ البوست 🔖 وشاركه ويّا صاحبك\n\n${p.tags||tags[p.n%4]}`;
 fs.writeFileSync(d+'/caption.txt',c);}
