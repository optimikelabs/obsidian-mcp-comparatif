"""Qualification de la fermeture : simulation du temps et option UI isolée."""
import argparse,copy
from unittest.mock import patch
from campaign_runtime import *
from campaign_runtime import _close_sequence,_owns_process,_request_owned_close

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ui',action='store_true');parser.add_argument('--label',default='fermeture',choices=['fermeture','fermeture-timeout']);args=parser.parse_args()
    root=RUN/'qualification-fermeture'/str(time.time_ns());root.mkdir(parents=True)
    checks=[]
    for name,ends_at,expected_attempts,remaining in [('already_closed',0,0,False),('slow_8s',8,1,False),('retry_22s',22,2,False),('still_active',100,2,True)]:
        now=[0];requests=[]
        def observe():return [{'ProcessId':101}] if now[0]<ends_at else []
        def request(n):requests.append(n);return {'attempt':n,'requested':True}
        def sleep(n):now[0]+=n
        proof=_close_sequence(observe,request,clock=lambda:now[0],sleep=sleep)
        assert len(requests)==expected_attempts and bool(proof['remaining'])==remaining
        writej(root/(name+'.json'),proof);checks.append({'case':name,'passed':True,'requests':len(requests),'elapsed_simulated_s':now[0]})
    for name,ends_at,expected_attempts,remaining in [('timeout_then_closed',8,1,False),('timeout_then_retry_closed',22,2,False),('timeout_still_active',100,2,True)]:
        now=[0];requests=[]
        def observe():return [{'ProcessId':101}] if now[0]<ends_at else []
        def request(n):
            requests.append(n)
            raise TimeoutError('Commande expirée après envoi possible')
        def sleep(n):now[0]+=n
        proof=_close_sequence(observe,request,clock=lambda:now[0],sleep=sleep)
        assert len(requests)==expected_attempts and bool(proof['remaining'])==remaining
        assert len(proof['attempts'])==expected_attempts and all(a['request_outcome']=='unknown' for a in proof['attempts'])
        writej(root/(name+'.json'),proof);checks.append({'case':name,'passed':True,'requests':len(requests),'elapsed_simulated_s':now[0]})
    cfg={'profile':str(root/'profile')}
    row={'ProcessId':101,'ExecutablePath':str(EXE),'CommandLine':'Obsidian.exe --user-data-dir="'+cfg['profile']+'" --remote-debugging-port=27346'}
    for name,item,expected in [('own_exact',row,True),('foreign_profile',{**row,'CommandLine':'Obsidian.exe --user-data-dir="C:\\foreign-profile"'},False),('prefix_collision',{**row,'CommandLine':row['CommandLine'].replace('profile"','profile-other"')},False),('foreign_executable',{**row,'ExecutablePath':'C:/Windows/notepad.exe'},False),('missing_command',{**row,'CommandLine':None},False)]:
        assert _owns_process(item,cfg)==expected;checks.append({'case':name,'passed':True})
    with patch('campaign_runtime._owned_processes',return_value=[row]),patch('campaign_runtime.command',return_value='{\"attempt\":1,\"requested\":true}') as command_mock:
        request_result=_request_owned_close({**cfg,'out':str(root),'pid':999},1)
        assert request_result['observed_main_pid']==101
        assert command_mock.call_args.args[0][1].endswith('close_owned_cdp.mjs')
        checks.append({'case':'reexecuted_main_pid','passed':True})
    guard=root/'guard';guard.mkdir();test_cfg={'out':str(guard),'profile':str(guard/'profile'),'pid':999,'lock_token':'owned','_close_requests_used':2}
    fake_lock=root/'lock.txt';fake_lock.write_text('owned',encoding='utf-8')
    with patch('campaign_runtime.LOCK',fake_lock),patch('campaign_runtime._owned_processes',return_value=[row]),patch('campaign_runtime._request_owned_close') as request_mock:
        try:stop(test_cfg);raise AssertionError('Persistance ignoree')
        except RuntimeError:pass
        assert request_mock.call_count==0 and fake_lock.exists()
        checks.append({'case':'no_third_request_lock_retained','passed':True})
    with patch('campaign_runtime.LOCK',fake_lock),patch('campaign_runtime._owned_processes',return_value=[]):stop(test_cfg)
    assert not fake_lock.exists();checks.append({'case':'owned_lock_released_after_empty','passed':True})
    fake_lock.write_text('foreign',encoding='utf-8')
    with patch('campaign_runtime.LOCK',fake_lock),patch('campaign_runtime._owned_processes',return_value=[]):stop(test_cfg)
    assert fake_lock.read_text(encoding='utf-8')=='foreign';checks.append({'case':'foreign_lock_preserved','passed':True})
    meta={'success':True,'checks':checks,'root':str(root),'real_ui':False}
    if args.ui:
        gate(root,'qualification_fermeture_ui');assert not LOCK.exists(),'Priorite au detenteur du verrou'
        cfg=prepare(root/'ui');mon=Monitor(root/'ui').start();closed_ok=False
        try:
            launch(cfg);prepare_application(cfg);mon.check()
            wrong=root/'wrong-cfg';wrong.mkdir();wrong_cfg={**cfg,'out':str(wrong),'vault':str(wrong/'vault'),'profile':str(wrong/'profile')};writej(wrong/'obsidian.json',wrong_cfg)
            negative=subprocess.run(['node',str(KIT/'scripts/close_owned_cdp.mjs'),str(wrong/'obsidian.json')],capture_output=True,text=True,encoding='utf-8',timeout=15)
            assert negative.returncode and 'Wrong vault; no close' in negative.stderr
            from campaign_runtime import _owned_processes
            assert _owned_processes(cfg),'Le temoin negatif a ferme une instance'
            writej(root/'wrong-vault-negative.json',{'passed':True,'returncode':negative.returncode,'reason':'Wrong vault; no close','instance_still_present':True})
            before=snapshot(Path(cfg['vault']));writej(root/'before-close.json',before);stop(cfg);closed_ok=True
            after=snapshot(Path(cfg['vault']));business_changes=[name for name in set(before)|set(after) if not name.startswith('.') and before.get(name)!=after.get(name)]
            assert not business_changes,'La fermeture a modifie une note metier'
            records=[json.loads(line) for line in (root/'ui/controller.jsonl').read_text(encoding='utf-8').splitlines()]
            closed=[r for r in records if r['event']=='owned_instance_stopped'];assert closed and not closed[-1]['lock_present']
            proofs=[readj(p) for p in (root/'ui').glob('closure-*.json')];assert proofs and not proofs[-1]['remaining']
            meta.update(real_ui=True,ui_closed=True,wrong_vault_negative=True,closure=proofs[-1],root_pid=cfg['pid'],business_changes=business_changes,before_inventory=manifest(before),after_inventory=manifest(after))
        finally:
            try:
                if not closed_ok and cfg.get('pid'):stop(cfg)
            finally:mon.close()
    writej(root/'qualification.json',meta);writej(KIT/'preuves'/('tests-'+args.label+('-ui' if args.ui else '')+'.json'),meta)
    print(json.dumps({k:v for k,v in meta.items() if k not in ('before_inventory','after_inventory')},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
