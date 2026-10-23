"""Qualification v1.3 : serveur factice, bacs neufs, aucune cellule candidate."""
import argparse,copy,shutil,threading,urllib.error
from unittest.mock import patch
from types import SimpleNamespace
from common import *
from relay import Relay,HTTP,serve,editor_hook
from fake_server import Fake,http_server
from test_kit import ADAPTER,Client
from campaign_runtime import prepare,launch,stop,prepare_application,Monitor,gate,memory

TASKS=('T5','T6','T7','T7b')

def scenario(root,task,mode,real_ui=False):
    out=root/(task+'-'+mode);out.mkdir()
    monitor=Monitor(out).start();cfg=None;backend=server=None
    try:
        if real_ui:
            gate(out,'qualification_ui_v13')
            cfg=prepare(out);assert cfg['N']==N and cfg['P']==P
            launch(cfg);prepare_application(cfg);vault=Path(cfg['vault'])
        else:
            vault=out/'vault';shutil.copytree(KIT/'fixtures/synthetique',vault)
            cfg={'vault':str(vault),'N':N,'P':P,'port':27346}
            writej(out/'obsidian.json',cfg)
        before=snapshot(vault)
        if mode.startswith('missing_'):
            cfg.pop(mode.removeprefix('missing_'));writej(out/'obsidian.json',cfg)
        def simulated_ui(t):
            assert t==task
            if t=='T5':(vault/N).write_text(HUMAN,encoding='utf-8',newline='')
            else:
                p=vault/P;old,new=(HOLD,HNEW) if t=='T6' else (OLD,CONFLICT)
                p.write_text(p.read_text(encoding='utf-8').replace(old,new),encoding='utf-8',newline='')
        hook=editor_hook(out/'obsidian.json') if real_ui or mode!='positive' else simulated_ui
        backend=http_server(Fake(vault));threading.Thread(target=backend.serve_forever,daemon=True).start()
        relay=Relay(HTTP(f'http://127.0.0.1:{backend.server_port}/mcp'),vault,task,out/'relay',{**ADAPTER,'preparation_tools':['plan']},hook)
        relay.safety_check=monitor.check
        server=serve(relay,0);threading.Thread(target=server.serve_forever,daemon=True).start();client=Client(server)
        client.read(P)
        path=N if task=='T5' else P
        name='create' if task=='T5' else 'plan' if task=='T7b' else 'patch'
        args={'path':path,'content':render(NPROPS,NBODY).decode()} if task=='T5' else {'path':P,'content':data(before,P).decode().replace(OLD,NEW)} if task=='T7b' else {'path':P,'old':OLD,'new':NEW}
        if mode=='positive':
            client.call(name,**args)
            if task=='T7b':client.call('patch',path=P,old=OLD,new=NEW)
            relay.finish()
            assert relay.injected and not relay.injection_failed.is_set()
            assert relay.human is not None and (out/'relay/human.json').exists()
            h=data(relay.human,path).decode()
            assert (h==HUMAN if task=='T5' else HNEW in h if task=='T6' else CONFLICT in h)
            events=[e['event'] for e in relay.events]
            assert events.index('request_held')<events.index('ui_disk_verified')<events.index('dispatch')
            result={'success':True,'task':task,'mode':mode,'real_ui':real_ui,'human_snapshot':True,'ui_disk_verified':True,'dispatch_after_save':True}
        else:
            # Failing subprocess models the real editor hook error before saving.
            with patch('relay.subprocess.run',return_value=SimpleNamespace(returncode=1,stderr='CROCHET_ECHEC_TEMOIN',stdout='')) as subprocess_mock:
                for attempt in (1,2):
                    try:client.call(name,**args);raise AssertionError('Mutation non bloquée')
                    except urllib.error.HTTPError as error:assert error.code==503
                if mode=='hook_failure':assert subprocess_mock.call_count==1
                else:assert subprocess_mock.call_count==0
            # Even another tool/action and a preparation remain barred.
            for other in ('write','plan'):
                try:client.call(other,path=P,content='INTERDIT');raise AssertionError('Barrière contournée')
                except urllib.error.HTTPError as error:assert error.code==503
            assert relay.injection_failed.is_set() and not relay.injected
            assert not any(e['event'] in ('dispatch','mutation_dispatch') for e in relay.events)
            assert snapshot(vault)==before
            result={'success':True,'task':task,'mode':mode,'verdict':'INJECTION_INVALIDE','candidate_mutations':0,'second_mutation_blocked':True,'preparation_blocked':True,'disk_unchanged':True}
        writej(out/'qualification.json',result)
        return result
    finally:
        if server:server.shutdown();server.server_close()
        if backend:backend.shutdown();backend.server_close()
        if real_ui and cfg:stop(cfg)
        monitor.close()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ui',action='store_true');a=parser.parse_args()
    root=KIT.parent/'resultats/qualification-v13'/str(time.time_ns());root.mkdir(parents=True)
    gate(root,'before_qualification_v13')
    checks=[]
    try:
        for task in TASKS:
            for mode in (('positive',) if a.ui else ('positive','missing_N','missing_P','hook_failure')):
                checks.append(scenario(root,task,mode,a.ui))
        if not a.ui:
            from client_cli import run_turn
            c=root/'client-stop';c.mkdir();binary=c/'fake-binary';binary.write_bytes(b'qualification-only')
            failure=threading.Event();failure.set()
            class Process:
                pid=0;returncode=None;terminated=False
                def poll(self):return self.returncode
                def terminate(self):self.terminated=True;self.returncode=1
                def wait(self,timeout=None):return self.returncode
            proc=Process()
            with patch('client_cli.executable',return_value=binary),patch('subprocess.Popen',return_value=proc):
                r=run_turn(c,'instrumentation factice',c,c,SimpleNamespace(stopped=threading.Event()),injection_failed=failure)
            assert proc.terminated and r['stop_reason']=='INJECTION_INVALIDE' and r['duration_s']<1
            checks.append({'success':True,'mode':'client_stop','stop_reason':r['stop_reason'],'no_model_started':True})
        meta={'success':True,'root':str(root),'checks':checks,'utc':time.time(),'real_ui':a.ui,'scope':'Serveur factice uniquement, aucun score candidat.'}
        writej(KIT/'preuves'/('tests-injection-v13-ui.json' if a.ui else 'tests-injection-v13.json'),meta)
        print(json.dumps(meta,ensure_ascii=False),flush=True)
    except BaseException as error:
        writej(root/'qualification-error.json',{'error':str(error),'checks_completed':checks,'utc':time.time()});raise

if __name__=='__main__':main()
