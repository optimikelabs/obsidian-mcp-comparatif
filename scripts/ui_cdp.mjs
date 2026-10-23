// Contrôle réservé au profil isolé créé par ui_qualification.py. Aucun MCP.
import fs from 'node:fs';
const [configPath, action, task] = process.argv.slice(2);
const cfg=JSON.parse(fs.readFileSync(configPath,'utf8'));
if (![27346].includes(cfg.port)) throw Error('Port non autorisé');
const pages=(await(await fetch(`http://127.0.0.1:${cfg.port}/json/list`)).json()).filter(p=>p.type==='page');
if(pages.length!==1) throw Error(`Cible ambiguë : ${pages.length} pages`);
const page=pages[0];
function evaluate(expression){return new Promise((resolve,reject)=>{
 const ws=new WebSocket(page.webSocketDebuggerUrl);
 const timer=setTimeout(()=>{ws.close();reject(Error('CDP délai dépassé'));},20000);
 ws.addEventListener('error',()=>{clearTimeout(timer);reject(Error('CDP websocket'));});
 ws.addEventListener('open',()=>ws.send(JSON.stringify({id:1,method:'Runtime.evaluate',params:{expression,returnByValue:true,awaitPromise:true}})));
 ws.addEventListener('message',e=>{const r=JSON.parse(e.data);if(r.id!==1)return;
  clearTimeout(timer);ws.close();if(r.result?.exceptionDetails)reject(Error(JSON.stringify(r.result.exceptionDetails)));else resolve(r.result?.result?.value);});
});}
const identity=`if(app.vault.adapter.basePath.replaceAll('\\\\','/').toLowerCase()!==${JSON.stringify(cfg.vault.replaceAll('\\','/').toLowerCase())}) throw Error('Mauvais coffre');`;
let expression;
if(action==='identity') expression=`(async()=>{${identity}return {base:app.vault.adapter.basePath,name:app.vault.getName(),electron:process.versions.electron,plugins:[...app.plugins.enabledPlugins]};})()`;
if(action==='activate') expression=`(async()=>{${identity}if(!app.plugins.isEnabled())await app.plugins.setEnable(true);await app.plugins.loadManifests();for(const id of ${JSON.stringify(cfg.plugins)})if(!app.plugins.enabledPlugins.has(id))await app.plugins.enablePluginAndSave(id);document.querySelectorAll('.modal-close-button').forEach(b=>b.click());return {plugins:[...app.plugins.enabledPlugins],fdm:app.plugins.plugins['frontmatter-date-manager']?.manifest.version};})()`;
if(action==='inject') {
 const path=task==='T5'?cfg.N:cfg.P;
 expression=`(async()=>{${identity}
 const path=${JSON.stringify(path)};let file=app.vault.getAbstractFileByPath(path);
 if(${JSON.stringify(task)}==='T5'){if(file)throw Error('N existe avant barrière');file=await app.vault.create(path,'');}
 if(!file)throw Error('Fichier cible absent');const leaf=app.workspace.getLeaf(false);await leaf.openFile(file,{state:{mode:'source'}});
 const editor=leaf.view.editor;if(!editor)throw Error('Éditeur absent');const before=editor.getValue();
 let after;
 if(${JSON.stringify(task)}==='T5')after='NOTE HUMAINE À CONSERVER\\n';
 else {const old=${JSON.stringify(task==='T6'?'Témoin humain : version initiale.':'Passage à modifier : essai prévu jeudi.')};
 const replacement=${JSON.stringify(task==='T6'?'Témoin humain : correction H-2406.':'Passage à modifier : annulé par la correction H-2406.')};
 if(before.split(old).length!==2)throw Error('Passage non unique');after=before.replace(old,replacement);}
 editor.setValue(after);return {path,method:'MarkdownView.editor.setValue',expected:after,vault:app.vault.adapter.basePath};})()`;
}
if(!expression)throw Error('Action inconnue');
console.log(JSON.stringify(await evaluate(expression)));
