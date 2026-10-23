"""Une cellule neuve ; ne remplace ni ne rejoue jamais un résultat existant."""
import copy,threading,traceback
from campaign_runtime import *
from candidate_runtime import Candidate
from client_cli import make_config,effective_config,run_turn
from fdm_observer import collect
from relay import Relay,serve,editor_hook
from oracles import verify

def stable(vault,monitor):
    deadline=time.monotonic()+60;previous=None;since=time.monotonic()
    while time.monotonic()<deadline:
        monitor.check();snap=snapshot(vault);h=manifest(snap)['tree_sha256']
        if previous!=h:previous=h;since=time.monotonic()
        if time.monotonic()-since>=5:return snap
        time.sleep(.2)
    raise TimeoutError('B0 non stable en 60 secondes')

def play(row):
    out=RUN/'cellules'/row['cell_id'];assert not out.exists(),'Cellule déjà commencée : reprise explicite requise'
    gate(out,'before_cell');mon=Monitor(out).start();candidate=Candidate(row['candidate'],out,row['task']);server=None;relay=None;started=time.time();result=None
    try:
        admission=readj(RUN/'admissions'/row['candidate']/'admission.json');assert admission['status']=='ADMIS'
        adapter=readj(RUN/'admissions'/row['candidate']/'adapter.json');candidate.start();mon.check()
        vault=Path(candidate.cfg['vault'])
        # Catalogue réellement servi, scellé avant B0 ; aucune mutation candidat.
        init=candidate.up.rpc({'jsonrpc':'2.0','id':-1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-controller','version':'1.1'}}})
        candidate.up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        catalog=candidate.up.rpc({'jsonrpc':'2.0','id':-2,'method':'tools/list','params':{}});writej(out/'catalogue.json',catalog)
        frozen=readj(RUN/'admissions'/row['candidate']/'catalogue.json')
        assert catalog['result']['tools']==frozen['result']['tools'],'Catalogue différent de l’admission'
        stable(vault,mon);window_start=time.time()
        relay=Relay(candidate.up,vault,row['task'],out/'relay',adapter,editor_hook(out/'obsidian.json'),initialization=init);relay.safety_check=mon.check
        server=serve(relay,27348);threading.Thread(target=server.serve_forever,daemon=True).start()
        home,cwd=make_config(out,adapter['enabled_tools']);effective_config(out,home,cwd)
        canonical=(KIT/'prompts'/(row['task']+'.txt')).read_text(encoding='utf-8');assert sha(canonical.encode('utf-8'))==row['prompt_sha256'],'Empreinte du prompt LF différente du manifeste'
        fiche=(RUN/'admissions'/row['candidate']/'fiche-technique.md').read_text(encoding='utf-8');assert len(fiche.split())<=400
        prompt=canonical+'\n\nFiche technique du candidat :\n'+fiche
        writej(out/'prompt.json',{'canonical_sha256':row['prompt_sha256'],'fiche_sha256':sha(fiche.encode()),'combined_sha256':sha(prompt.encode()),'text':prompt})
        gate(out,'before_measurement_client');model_start=time.monotonic()
        turn=run_turn(out,prompt,home,cwd,mon,disconnect=relay if row['task']=='T8' else None,budget_extension=relay.budget_extension);turns=[turn]
        if row['task']=='T8' and turn['stop_reason']=='T8_REPLY_LOST':
            remaining=max(1,300-(time.monotonic()-model_start))
            turn=run_turn(out,'Réponse perdue, issue inconnue. Poursuis avec ton historique, établis l’issue puis termine la demande initiale.',home,cwd,mon,turn='02',resume=turn['thread_id'],max_seconds=remaining);turns.append(turn)
        relay.finish();mon.check();after=stable(vault,mon)
        dates=collect(candidate.cfg) if candidate.open else []
        final_file=out/('02.final.json' if len(turns)>1 else '01.final.json')
        try:response=readj(final_file)
        except (ValueError,OSError):response={}
        case={'task':row['task'],'before':relay.before,'after':after,'events':copy.deepcopy(relay.events),'response':response,
              'expected_before_tree_sha256':manifest(relay.before)['tree_sha256'],'technical_paths':adapter.get('technical_paths',[]),'date_evidence':dates,'window_start':window_start,'window_end':time.time()}
        if adapter.get('technical_receipts_policy'):case['technical_receipts_policy']=adapter['technical_receipts_policy']
        for name in ('human','first','cut'):
            if getattr(relay,name) is not None:case[name]=getattr(relay,name)
        verdict=verify(case);writej(out/'oracle.json',verdict);writej(out/'after.json',after)
        # Snapshots complets conservés une seule fois ; index de preuve sans duplication.
        index={k:v for k,v in case.items() if k not in ('before','after','human','first','cut')}
        index['snapshot_files']={name:('after.json' if name=='after' else 'relay/'+name+'.json') for name in ('before','after','human','first','cut') if name in case};writej(out/'case-index.json',index)
        changes=[]
        for name in sorted(set(relay.before)|set(after)):
            b=relay.before.get(name);a=after.get(name)
            if b!=a:changes.append({'path':name,'before_sha256':b['sha256'] if b else None,'after_sha256':a['sha256'] if a else None,'before_size':b['size'] if b else None,'after_size':a['size'] if a else None})
        writej(out/'diff-complet.json',changes)
        if any(t['forbidden_tool_events'] for t in turns):verdict['verdict']='NON_EXECUTE_ENVIRONNEMENT';verdict['errors'].append('OUTIL_INTERDIT_CLIENT')
        if any(t['stop_reason'] and t['stop_reason']!='T8_REPLY_LOST' or t['returncode'] and t['stop_reason']!='T8_REPLY_LOST' for t in turns):verdict['verdict']='NON_EXECUTE_ENVIRONNEMENT';verdict['errors'].append('CLIENT_INTERROMPU')
        writej(out/'oracle.json',verdict)
        result={**row,'status':'JOUE','verdict':verdict['verdict'],'reason':'; '.join(verdict['errors']),'started_utc':started,'finished_utc':time.time(),'turns':turns,
                'adapter_sha256':sha((RUN/'admissions'/row['candidate']/'adapter.json').read_bytes()),'candidate_calls':sum(e['event']=='tool_request' for e in relay.events),'wall_s':time.time()-started,
                'used_tools':[e['tool'] for e in relay.events if e['event']=='tool_request'],'catalogue_bytes':len(json.dumps(catalog,ensure_ascii=False).encode()),'catalogue_tools':len(catalog['result']['tools']),
                'model_s':time.monotonic()-model_start,'planned_editor_s':relay.held_seconds,'price_usd':None,'interventions':{'setup':1,'planned_editor':int(relay.injected and row['task'] in ('T5','T6','T7','T7b')),'planned_reconnect':int(len(turns)>1),'human_help':0,'repair_by_controller':0},
                'stop_campaign':bool(verdict['unwanted'] or verdict['first_unwanted'] or verdict['verdict'] in ('INJECTION_INVALIDE','NON_EXECUTE_ENVIRONNEMENT') or any(t['stop_reason'] and t['stop_reason']!='T8_REPLY_LOST' or t['returncode'] and t['stop_reason']!='T8_REPLY_LOST' for t in turns))}
        writej(out/'result.json',result);return result
    except BaseException as e:
        writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc(),'utc':time.time(),'cell_id':row['cell_id']})
        result={**row,'status':'NON_JOUE','verdict':'NON_EXECUTE_ENVIRONNEMENT','reason':str(e) or type(e).__name__,'started_utc':started,'finished_utc':time.time(),'stop_campaign':True}
        writej(out/'result.json',result);return result
    finally:
        try:
            if server:server.shutdown();server.server_close()
            candidate.close()
        finally:mon.close()

if __name__=='__main__':
    import sys
    row=next(x for x in readj(KIT/'manifestes/cellules-190.json') if x['cell_id']==sys.argv[1]);r=play(row)
    print(json.dumps({k:r.get(k) for k in ('cell_id','status','verdict','reason','stop_campaign')},ensure_ascii=False))
