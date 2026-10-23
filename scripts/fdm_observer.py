"""Observation transparente des appels natifs processFrontMatter, dans le bac isolé uniquement.
Aucune valeur de date n'est assignée par cet observateur.
"""
from campaign_runtime import *

INSTALL=r'''(()=>{
 if(globalThis.__comparatifFdm)throw Error('Observateur déjà installé');
 const plugin=app.plugins.plugins['frontmatter-date-manager'];
 if(plugin?.manifest.version!=='1.6.0')throw Error('FDM non qualifié');
 const log=[];const original=app.fileManager.processFrontMatter;
 app.fileManager.processFrontMatter=function(file,callback,...rest){
   const stack=new Error().stack;const fromFdm=stack.includes('plugin:frontmatter-date-manager');
   let before,after;
   const wrapped=function(fm){before=JSON.parse(JSON.stringify(fm));const value=callback(fm);after=JSON.parse(JSON.stringify(fm));return value;};
   const result=original.call(this,file,wrapped,...rest);
   return Promise.resolve(result).then(async value=>{
     if(fromFdm){const text=await app.vault.read(file);log.push({path:file.path,plugin:'frontmatter-date-manager',version:plugin.manifest.version,before,after,text,observed_utc:Date.now()/1000,stack});}
     return value;
   });
 };
 globalThis.__comparatifFdm={log,original};return {installed:true,version:plugin.manifest.version};
})()'''

def install(cfg):return cdp(cfg,INSTALL,'fdm-observer-install')

def collect(cfg,prefix='fdm-observer'):
    records=cdp(cfg,'(()=>{if(!globalThis.__comparatifFdm)throw Error("Observateur absent");return globalThis.__comparatifFdm.log;})()',prefix+'-collect')
    evidence=[]
    for r in records:
        digest=sha(r['text'].encode('utf-8'))
        for key in ('création','modification'):
            if r['before'].get(key)!=r['after'].get(key):
                evidence.append({'path':r['path'],'key':key,'value':str(r['after'].get(key)),'previous_value':str(r['before'].get(key)),
                    'plugin':r['plugin'],'version':r['version'],'after_sha256':digest,'observed_utc':r['observed_utc'],
                    'stack_sha256':sha(r['stack'].encode('utf-8'))})
    writej(Path(cfg['out'])/(prefix+'-raw.json'),records);writej(Path(cfg['out'])/(prefix+'-evidence.json'),evidence)
    return evidence

def qualify():
    from relay import editor_hook
    out=RUN/'qualification-fdm'/str(time.time_ns());gate(out,'before_fdm_observer');mon=Monitor(out).start();cfg=None
    try:
        cfg=prepare(out);launch(cfg);install(cfg);prepare_application(cfg)
        before=snapshot(Path(cfg['vault']));time.sleep(31);mon.check()
        editor_hook(out/'obsidian.json')('T6')
        deadline=time.monotonic()+35;records=[]
        while time.monotonic()<deadline:
            records=collect(cfg)
            if any(x['path']==P and x['key']=='modification' and x['after_sha256']==sha((Path(cfg['vault'])/P).read_bytes()) for x in records):break
            time.sleep(2);mon.check()
        after=snapshot(Path(cfg['vault']));matches=[e for e in records if e['path']==P and e['after_sha256']==after[P]['sha256']]
        qualified=bool(matches)
        proof={'qualified':qualified,'path':str(out),'fdm_version':'1.6.0','plugin_sha256':sha((Path(cfg['vault'])/'.obsidian/plugins/frontmatter-date-manager/main.js').read_bytes()),
               'before_sha256':before[P]['sha256'],'after_sha256':after[P]['sha256'],'evidence':matches,'method':'Observation du callback natif processFrontMatter ; pas de date assignée par le contrôleur.'}
        writej(out/'qualification.json',proof);writej(RUN/'FDM-QUALIFICATION.json',proof);print(json.dumps(proof,ensure_ascii=False))
    finally:
        if cfg:stop(cfg)
        mon.close()

if __name__=='__main__':qualify()
