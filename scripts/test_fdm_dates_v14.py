"""Serveur factice HTTP et FDM simulé : aucune instance Obsidian ni candidat réel."""
import copy
import datetime
import shutil
import threading
from common import *
from fake_server import Fake,http_server
from relay import HTTP,Relay,serve
from test_kit import ADAPTER,Client
from fdm_dates_v14 import POLICY,content_hash
from oracles import verify
from oracles_v13 import verify as old_verify


def blob(raw):
    return {'base64':base64.b64encode(raw).decode(),'size':len(raw),'sha256':sha(raw)}


def rendered(props,body):
    # Le simulateur FDM ne travaille que sur une fixture synthétique neuve.
    return ('---\n'+yaml.safe_dump(props,allow_unicode=True,sort_keys=False)+'---\n'+body).encode('utf-8')


def scenario(root,mode):
    out=root/mode;assert not out.exists();out.mkdir(parents=True)
    vault=out/'vault';shutil.copytree(KIT/'fixtures/synthetique',vault)
    note=target(vault,P);props,body=split(note.read_bytes())
    props.update(création='2026-10-23T00:00',modification='2026-10-23T00:00');note.write_bytes(rendered(props,body))
    upstream=http_server(Fake(vault));threading.Thread(target=upstream.serve_forever,daemon=True).start()
    up=HTTP(f'http://127.0.0.1:{upstream.server_port}/mcp')
    def human(task):note.write_bytes(note.read_bytes().replace(HOLD.encode(),HNEW.encode()))
    relay=Relay(up,vault,'T6',out/'relay',ADAPTER,human)
    server=serve(relay,0);threading.Thread(target=server.serve_forever,daemon=True).start();client=Client(server)
    start=time.time()
    try:
        client.rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'v14-factice','version':'1'}})
        initial=note.read_bytes();client.read(P)
        response=client.call('write',path=P,etag=sha(initial),content=initial.decode().replace(OLD,NEW))
        assert response['result']['isError']
        bp,bb=split(note.read_bytes());ap=copy.deepcopy(bp)
        value=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
        ap['modification']='23/10/2026' if mode=='bad-format' else value
        if mode=='other-key':ap['rang']=99
        intermediate=rendered(ap,bb);note.write_bytes(intermediate);at=time.time()
        record={'path':P,'plugin':'frontmatter-date-manager','version':'1.6.0','from_fdm_stack':True,
                'before':bp,'after':ap,'note':blob(intermediate),'observed_utc':at,'stack_sha256':sha(b'FAKE_FDM_STACK')}
        client.read(P);client.call('patch',path=P,old=OLD,new=NEW)
        if mode=='human-loss':client.call('patch',path=P,old=HNEW,new=HOLD)
        if mode=='other-note':
            other=target(vault,Q);other.parent.mkdir(parents=True,exist_ok=True)
            other.write_bytes(rendered({'modification':value},'Autre note\n'))
        client.read(P)
        case={'task':'T6','before':relay.before,'human':relay.human,'first':relay.first,'after':snapshot(vault),
              'events':copy.deepcopy(relay.events),'expected_before_tree_sha256':manifest(relay.before)['tree_sha256'],
              'window_start':start,'window_end':time.time(),'protocol_version':'1.4','fdm_dates_policy':POLICY,
              'date_evidence':[{'path':P,'key':'modification','value':ap['modification'],'plugin':'frontmatter-date-manager','version':'1.6.0','after_sha256':sha(intermediate),'observed_utc':at}],
              'fdm_dates_context':{'version':'1.6.0','settings':{'dateFormat':"yyyy-MM-dd'T'HH:mm",'timezone':'','headerCreated':'création','headerUpdated':'modification','enableCreateTime':True,'enableModifiedTime':True,'minSecondsBetweenSaves':30,'delayForNewFiles':20000},'utc_offset_seconds':datetime.datetime.now().astimezone().utcoffset().total_seconds(),'records':[record],'birthtimes':{}},
              'response':{'task_id':'T6','path':P,'etat':'applique','extrait':NEW,'proprietes':{},'message':'Témoin factice v1.4'}}
        verdict=verify(case);writej(out/'case.json',case);writej(out/'oracle.json',verdict)
        assert (verdict['verdict']=='REUSSI_VERIFIE')==(mode=='positive'),(mode,verdict)
        old=copy.deepcopy(case);old.pop('fdm_dates_policy');old.pop('fdm_dates_context')
        if mode=='positive':assert old_verify(old)['verdict']=='NON_EXECUTE_ENVIRONNEMENT'
        writej(out/'oracle-v13.json',old_verify(old))
        return case
    finally:
        server.shutdown();server.server_close();up.close();upstream.shutdown();upstream.server_close()


def main():
    root=KIT/'preuves/fdm-dates-v14'/str(time.time_ns());root.mkdir(parents=True)
    cases={mode:scenario(root,mode) for mode in ('positive','other-key','other-note','bad-format','human-loss')}
    base=cases['positive'];checks=[]
    for mode in ('missing-trace','wrong-writer','wrong-version','wrong-note','corrupt-hash','outside-window','incompatible-time','future-value'):
        case=copy.deepcopy(base);record=case['fdm_dates_context']['records'][0]
        if mode=='missing-trace':case['fdm_dates_context']['records']=[]
        elif mode=='wrong-writer':record['from_fdm_stack']=False
        elif mode=='wrong-version':record['version']='0'
        elif mode=='wrong-note':record['path']=Q
        elif mode=='corrupt-hash':record['note']['sha256']='0'*64
        elif mode=='outside-window':record['observed_utc']=case['window_end']+100
        elif mode=='incompatible-time':case['fdm_dates_context']['settings']['minSecondsBetweenSaves']=1e12
        else:
            record['after']['modification']='2099-01-01T00:00'
            p,b=split(data(case['after'],P));p['modification']='2099-01-01T00:00';case['after'][P]=blob(rendered(p,b))
            p,b=split(base64.b64decode(record['note']['base64']));p['modification']='2099-01-01T00:00';record['note']=blob(rendered(p,b))
        verdict=verify(case);assert verdict['verdict']!='REUSSI_VERIFIE',(mode,verdict)
        writej(root/(mode+'.json'),{'case':case,'oracle':verdict});checks.append(mode)
    # La branche cache reste permise quand le délai seul n'est pas établi.
    case=copy.deepcopy(base);case['fdm_dates_context']['settings']['minSecondsBetweenSaves']=1e12
    from fdm_cache import CACHE
    at=case['fdm_dates_context']['records'][0]['observed_utc']
    case['before'][CACHE]=blob(json.dumps({P:{'hash':'0'*64,'lastAccessed':0}}).encode())
    for name in ('human','first'):case[name][CACHE]=copy.deepcopy(case['before'][CACHE])
    case['after'][CACHE]=blob(json.dumps({P:{'hash':content_hash(base64.b64decode(case['fdm_dates_context']['records'][0]['note']['base64']),case['fdm_dates_context']['settings']),'lastAccessed':at*1000}}).encode())
    case['technical_paths']=[CACHE];case['fdm_cache_policy']='fdm-cache-v1.2'
    case['expected_before_tree_sha256']=manifest(case['before'])['tree_sha256']
    for e in case['events']:
        if e['event']=='ui_disk_verified':e['snapshot_sha256']=manifest(case['human'])['tree_sha256']
        if e['event']=='first_snapshot':e['snapshot_sha256']=manifest(case['first'])['tree_sha256']
    verdict=verify(case);assert verdict['verdict']=='REUSSI_VERIFIE',verdict
    writej(root/'cache-positive.json',{'case':case,'oracle':verdict})
    bad=copy.deepcopy(case);bad['after'][CACHE]=blob(json.dumps({P:{'hash':'a'*64,'lastAccessed':at*1000}}).encode())
    v=verify(bad);assert v['verdict']!='REUSSI_VERIFIE'
    writej(root/'cache-wrong-hash.json',{'case':bad,'oracle':v})
    writej(KIT/'preuves/tests-fdm-dates-v14.json',{'success':True,'root':str(root),'checks':15,'http_scenarios':5,'additional_negatives':checks,'simulated_fdm':True,'real_candidate':False})
    print(json.dumps({'success':True,'checks':15,'root':str(root)}))

if __name__=='__main__':main()
