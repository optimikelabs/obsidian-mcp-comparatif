// Node 24, aucune dépendance. Lecture disque uniquement ; saisie via l'éditeur Obsidian.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const opts={};
for(let i=2;i<process.argv.length;i+=2){if(!process.argv[i]?.startsWith('--')||process.argv[i+1]===undefined)throw Error('Arguments --nom valeur');opts[process.argv[i].slice(2)]=process.argv[i+1];}
const port=Number(opts.port), vault=path.resolve(opts.vault||''), note=opts.note;
if(!Number.isInteger(port)||port<1024||port>65535||[27123,27124].includes(port))throw Error('Port CDP invalide ou quotidien');
if(!opts.vault||!note||path.isAbsolute(note)||note.split(/[\\/]/).includes('..'))throw Error('--vault absolu et --note relatif requis');
const file=path.resolve(vault,note);
if(!file.startsWith(vault+path.sep))throw Error('Note hors coffre');
const text=opts['text-file']?fs.readFileSync(opts['text-file'],'utf8'):opts.text;
if(typeof text!=='string')throw Error('--text ou --text-file requis');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const before=fs.readFileSync(file,'utf8');
if(opts['expected-before-sha256']&&hash(Buffer.from(before))!==opts['expected-before-sha256'])throw Error('Précondition disque périmée');
const offset=opts.position==='end'?before.length:opts.position==='start'?0:Number(opts.position);
const remove=Number(opts['delete-length']||0);
if(!Number.isInteger(offset)||offset<0||offset>before.length||!Number.isInteger(remove)||remove<0||offset+remove>before.length)throw Error('Position UTF-16 ou delete-length invalide');
const expected=before.slice(0,offset)+text+before.slice(offset+remove);
const targets=(await(await fetch(`http://127.0.0.1:${port}/json/list`)).json()).filter(p=>p.type==='page');
if(targets.length!==1)throw Error(`Cible ambiguë (${targets.length} pages), aucune retouche`);
async function evaluate(expression){return await new Promise((resolve,reject)=>{
 const ws=new WebSocket(targets[0].webSocketDebuggerUrl);const timer=setTimeout(()=>{ws.close();reject(Error('CDP timeout'));},20000);
 ws.addEventListener('error',()=>{clearTimeout(timer);reject(Error('CDP websocket'));});
 ws.addEventListener('open',()=>ws.send(JSON.stringify({id:1,method:'Runtime.evaluate',params:{expression,awaitPromise:true,returnByValue:true}})));
 ws.addEventListener('message',e=>{const r=JSON.parse(e.data);if(r.id!==1)return;clearTimeout(timer);ws.close();if(r.result?.exceptionDetails)reject(Error(JSON.stringify(r.result.exceptionDetails)));else resolve(r.result.result.value);});
});}
const result=await evaluate(`(async()=>{
 if(app.vault.adapter.basePath.replaceAll('\\\\','/').toLowerCase()!==${JSON.stringify(vault.replaceAll('\\','/').toLowerCase())})throw Error('Mauvaise instance');
 const file=app.vault.getAbstractFileByPath(${JSON.stringify(note.replaceAll('\\','/'))});if(!file)throw Error('Note absente');
 const leaf=app.workspace.getLeaf(false);await leaf.openFile(file,{state:{mode:'source'}});const editor=leaf.view.editor;
 if(!editor||editor.getValue()!==${JSON.stringify(before)})throw Error('Éditeur divergent, aucune saisie');
 editor.replaceRange(${JSON.stringify(text)},editor.offsetToPos(${offset}),editor.offsetToPos(${offset+remove}),'margelle-cdp-insertion');
 if(editor.getValue()!==${JSON.stringify(expected)})throw Error('Texte éditeur inattendu');
 return {vault:app.vault.adapter.basePath,note:file.path,method:'MarkdownView.editor.replaceRange',editorConfirmed:true};})()`);
const deadline=Date.now()+Number(opts['timeout-ms']||60000);let confirmed=false;
while(Date.now()<deadline){
 if(fs.existsSync(new URL('../ARRET-MEMOIRE.json',import.meta.url)))throw Error('Arrêt mémoire demandé');
 if(fs.readFileSync(file,'utf8')===expected){confirmed=true;break;}
 await new Promise(resolve=>setTimeout(resolve,50)); // condition disque, pas attente arbitraire de course
}
if(!confirmed)throw Error('Sauvegarde disque exacte non observée, ne pas transmettre la mutation');
console.log(JSON.stringify({...result,positionUTF16:offset,deletedUTF16:remove,beforeSha256:hash(Buffer.from(before)),afterSha256:hash(Buffer.from(expected)),diskConfirmed:true,utc:new Date().toISOString(),label:'retouche saisie dans l’éditeur d’Obsidian (saisie simulée par un script, pas par une personne)'}));
