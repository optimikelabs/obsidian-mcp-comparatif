"""Qualification du stockage : factice sur jonctions, sans Obsidian ni client testé."""
import copy,json,shutil,sys,time,unittest
from unittest.mock import patch
from common import *
from campaign_runtime import RUN,prepare
from heavy_storage import empty_directory,storage_root
import test_kit
import test_fdm_dates_v14 as v14
from oracles import verify

def main():
    root=RUN/'qualification-stockage'/str(time.time_ns());root.mkdir(parents=True)
    checks=[]
    cfg=prepare(root/'preparation')
    for name in ('vault','profile'):
        source=Path(cfg[name]);assert source.is_junction() and source.resolve().is_relative_to(storage_root())
        checks.append({'case':'prepare_'+name+'_on_B','passed':True})
    assert cfg['N']==N and cfg['P']==P
    assert sha((Path(cfg['profile'])/'obsidian-1.13.7.asar').read_bytes())==cfg['asar_sha256']
    before=manifest(snapshot(Path(cfg['vault'])))
    try:prepare(root/'preparation');raise AssertionError('Rejeu autorisé')
    except RuntimeError:pass
    assert manifest(snapshot(Path(cfg['vault'])))==before
    checks.append({'case':'existing_vault_refused_and_preserved','passed':True})
    for out,name in ((KIT/'public','vault'),(root/'invalid','unknown')):
        try:empty_directory(out,name);raise AssertionError('Hors périmètre autorisé')
        except ValueError:checks.append({'case':'invalid_scope_refused','passed':True})
    state=empty_directory(root/'state','server-state');assert state.resolve().drive.upper()=='B:'
    checks.append({'case':'candidate_cache_on_B','passed':True})
    assert scoped(Path(cfg['vault']))==Path(cfg['vault']).resolve()
    for unsafe in (storage_root(),storage_root()/'resultats/unmapped/vault',KIT.parent):
        try:scoped(unsafe);raise AssertionError('Archive sans jonction autorisée')
        except ValueError:checks.append({'case':'unmapped_archive_refused','passed':True})
    original=shutil.copytree
    def linked_copy(src,dst,*args,**kwargs):
        dst=Path(dst)
        if dst.name=='vault' and dst.is_relative_to(root):
            empty_directory(dst.parent,'vault');kwargs['dirs_exist_ok']=True
        return original(src,dst,*args,**kwargs)
    test_kit.ROOT=root/'factice';test_kit.ALL=[]
    with patch('shutil.copytree',side_effect=linked_copy):
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_kit.Tests)
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            writej(root/'qualification-echec.json',{'success':False,'errors':result.errors,'failures':result.failures})
            raise AssertionError('Qualification factice échouée')
        cases={mode:v14.scenario(root/'v14',mode) for mode in ('positive','other-key','other-note','bad-format','human-loss')}
    for mode,case in cases.items():checks.append({'case':'v14_'+mode,'verdict':verify(case)['verdict'],'passed':True})
    junctions=[p for p in root.rglob('vault') if p.is_junction()]
    assert len(junctions)>=40 and all(p.resolve().drive.upper()=='B:' for p in junctions)
    meta={'success':True,'root':str(root),'checks':checks,'factice_checks':test_kit.ALL,'unittest_groups':result.testsRun,
          'vault_junctions':len(junctions),'real_obsidian_launched':False,'tested_client_launched':False,'new_paths':'B via directory junctions','utc':time.time()}
    writej(root/'qualification.json',meta);writej(KIT/'preuves/tests-stockage-lourd.json',meta)
    print(json.dumps({k:v for k,v in meta.items() if k not in ('checks','factice_checks')},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
