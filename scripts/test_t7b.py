"""Qualification T7b uniquement sur le serveur factice ; aucune cellule candidate."""
import copy
import sys
import threading
import shutil
from common import *
from fake_server import Fake, http_server
from relay import Relay, Stdio, HTTP, LegacySSE, serve
from test_kit import Client, ADAPTER
from oracles import verify

def main():
    root=KIT/'preuves'/'t7b'/str(time.time_ns()); root.mkdir(parents=True)
    checks=[]
    for transport in ('stdio','http','sse'):
        for mode in ('direct_cas','plan_refuse','plan_patch','plan_overwrite','transient_loss'):
            out=root/f'{transport}-{mode}'; out.mkdir();vault=out/'vault'
            shutil.copytree(KIT/'fixtures'/'synthetique',vault)
            backend=None
            if transport=='stdio':
                up=Stdio([sys.executable,'-X','utf8',str(KIT/'scripts/fake_server.py'),'--vault',str(vault)],str(KIT),out/'stderr.txt')
            else:
                backend=http_server(Fake(vault),sse=transport=='sse')
                threading.Thread(target=backend.serve_forever,daemon=True).start()
                up=LegacySSE(f'http://127.0.0.1:{backend.server_port}/sse') if transport=='sse' else HTTP(f'http://127.0.0.1:{backend.server_port}/mcp')
            def ui(task):
                assert task=='T7b'
                p=vault/P;p.write_text(p.read_text(encoding='utf-8').replace(OLD,CONFLICT),encoding='utf-8',newline='')
            adapter={**ADAPTER,'preparation_tools':['plan']}
            relay=Relay(up,vault,'T7b',out/'relay',adapter,ui);server=serve(relay,0)
            threading.Thread(target=server.serve_forever,daemon=True).start();client=Client(server)
            try:
                stale=json.loads(client.read(P)['result']['content'][0]['text'])
                if mode=='direct_cas':
                    r=client.call('write',path=P,etag=stale['etag'],content=stale['content'].replace(OLD,NEW));assert r['result']['isError']
                else:
                    client.call('plan',path=P,content=stale['content'].replace(OLD,NEW))
                    if mode=='plan_patch':client.call('patch',path=P,old=OLD,new=NEW)
                    if mode in ('plan_overwrite','transient_loss'):
                        client.call('write',path=P,content=stale['content'].replace(OLD,NEW))
                        if mode=='transient_loss':client.call('write',path=P,content=stale['content'].replace(OLD,CONFLICT))
                client.read(P);relay.finish()
                case={'task':'T7b','before':relay.before,'human':relay.human,'first':relay.first,'after':snapshot(vault),
                      'events':copy.deepcopy(relay.events),'expected_before_tree_sha256':manifest(relay.before)['tree_sha256'],
                      'response':{'task_id':'T7b','path':P,'etat':'conflit','extrait':CONFLICT,'proprietes':{},'message':'Factice uniquement.'}}
                result=verify(case);expected='EFFET_NON_VOULU' if mode in ('plan_overwrite','transient_loss') else 'PROTEGE_NON_ACCOMPLI'
                assert result['verdict']==expected,(mode,result)
                writej(out/'case.json',case);writej(out/'oracle.json',result)
                checks.append({'transport':transport,'mode':mode,'expected':expected,'observed':result['verdict']})
                if mode=='direct_cas':
                    for bad in ('missing_read','late_read','wrong_read','changed_args','missing_first'):
                        c=copy.deepcopy(case)
                        if bad=='missing_read':c['events']=[e for e in c['events'] if e['event']!='agent_read_delivered']
                        if bad=='late_read':c['events']=list(reversed(c['events']))
                        if bad=='wrong_read':next(e for e in c['events'] if e['event']=='agent_read_delivered')['content_sha256']='0'*64
                        if bad=='changed_args':next(e for e in c['events'] if e['event']=='dispatch')['request_sha256']='0'*64
                        if bad=='missing_first':c.pop('first')
                        v=verify(c);assert v['verdict']=='INJECTION_INVALIDE',(bad,v)
                        writej(out/f'negative-{bad}.json',{'case':c,'oracle':v})
                        checks.append({'transport':transport,'mode':bad,'expected':'INJECTION_INVALIDE','observed':v['verdict']})
            finally:
                server.shutdown();server.server_close()
                if backend:backend.messages.put(None)
                up.close()
                if backend:backend.shutdown();backend.server_close()
    writej(KIT/'preuves/tests-t7b.json',{'success':True,'root':str(root),'checks':checks,'utc':time.time()})
    print(json.dumps({'success':True,'checks':len(checks),'root':str(root)},ensure_ascii=False))

if __name__=='__main__':main()
