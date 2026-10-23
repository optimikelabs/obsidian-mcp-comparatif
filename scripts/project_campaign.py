"""Projection publique en liste blanche. Aucun coffre, profil, code candidat ou authentifiant."""
from campaign_reporting import build,project
from campaign_runtime import *
from redact import sanitize_file,redact
from oracles import verify

def witness_scope(value):
    if isinstance(value,str):return value in (P,N,Q)
    if isinstance(value,dict):return any(witness_scope(v) for v in value.values())
    if isinstance(value,list):return any(witness_scope(v) for v in value)
    return False

def omitted(value):
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True).encode()
    return {'projection':'octets_hors_temoin_omis','sha256':sha(raw),'bytes':len(raw)}

def project_cells(public):
    for p in sorted((RUN/'cellules').glob('*')):
        if not p.is_dir():continue
        dest=public/'resultats/cellules'/p.name
        for name in ('result.json','oracle.json','incident.json','diff-complet.json','case-index.json','prompt.json','catalogue.json','client-config-proof.json','effective-config.json','controller.jsonl','preparation-applicative.json','identity.json','fdm-observer-evidence.json','01.exit.json','02.exit.json','01.final.json','02.final.json','NOTE-V1.2.md','NOTE-V1.3.md'):
            if (p/name).exists():sanitize_file(p/name,dest/name)
        index=readj(p/'case-index.json') if (p/'case-index.json').exists() else {}
        witnesses={};inventories={}
        for stage,rel in index.get('snapshot_files',{}).items():
            snap=readj(p/rel);witnesses[stage]={k:v for k,v in snap.items() if k in (P,N,Q)};inventories[stage]=manifest(snap)
        if witnesses:writej(dest/'temoins-snapshots.json',redact(witnesses));writej(dest/'inventaires-complets.json',redact(inventories))
        for q in (p/'relay').glob('rpc-*.json'):
            obj=readj(q);req=obj['request']
            if req.get('method')=='tools/call' and not witness_scope(req.get('params',{}).get('arguments',{})):
                obj['response']=omitted(obj.get('response'))
            writej(dest/'relay'/q.name,redact(obj))
        if (p/'relay/events.jsonl').exists():sanitize_file(p/'relay/events.jsonl',dest/'relay/events.jsonl')
        for name in ('01.stdout.jsonl','02.stdout.jsonl'):
            if not (p/name).exists():continue
            lines=[]
            for line in (p/name).read_text(encoding='utf-8').splitlines():
                obj=json.loads(line);item=obj.get('item',{})
                if item.get('type')=='mcp_tool_call' and not witness_scope(item.get('arguments',{})) and item.get('result'):
                    item['result']=omitted(item['result'])
                if item.get('type')=='agent_message':item['text']=omitted(item.get('text'))
                lines.append(redact(obj))
            (dest/name).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in lines),encoding='utf-8')

def main():
    build();project();public=KIT/'public';project_cells(public)
    names=['common.py','relay.py','oracles.py','technical_receipts.py','client_cli.py','campaign_runtime.py','candidate_runtime.py','campaign_cell.py','campaign_reporting.py','project_campaign.py','validate_projection.py',
           'fdm_observer.py','fdm_cache.py','test_fdm_cache.py','qualify_client.py','qualify_client_t8.py','test_kit.py','test_t7b.py','test_read_mappings.py','test_native_mappings.py','test_technical_receipts.py','test_dates_stages.py','campaign_cdp.mjs','campaign_run.py','ui_cdp.mjs','test_injection_v13.py','campaign_replacements.py','test_closure_operation.py','close_owned_cdp.mjs']
    for name in names:sanitize_file(KIT/'scripts'/name,public/'scripts'/name)
    for name in ('PROTOCOLE-V1.md','PROTOCOLE-V1.1-GELE.md','README.md','AMENDEMENT-ADMISSIONS-ET-CLIENT.md','AMENDEMENT-C05-T1-r1.md','AMENDEMENT-C05-T4-r1.md','AMENDEMENT-V1.2-C5.md','DIAGNOSTIC-C05-T4-r1.md','AMENDEMENT-V1.3-C5.md','AMENDEMENT-C05-T5-r1.md','PROTOCOLE-V1.2-GELE.md','QUALIFICATION-V1.3.md','NOTE-EXPLOITATION-20261023-C5.md','DECISIONS-C5-20261023.md','AMENDEMENT-C08-T4-r1.md'):
        if (KIT/name).exists():sanitize_file(KIT/name,public/name)
    for name in ('v13-audit-cellules.json','v13-resultats-preserves.json','v13-code-qualifie.json','v13-client-preserve.json','v13-ui-sortie.json','tests-injection-v13.json','tests-injection-v13-ui.json','tests-fermeture.json','tests-fermeture-ui.json','exploitation-journal-audit.json','exploitation-resultats-preserves.json','fermeture-native-incident.json'):
        p=KIT/'preuves'/name
        if p.exists():sanitize_file(p,public/'preuves'/name)
    sanitize_file(KIT/'manifestes/remplacements-autorises.json',public/'manifestes/remplacements-autorises.json')
    for p in (RUN/'cellules').glob('*/closure-*.json'):
        sanitize_file(p,public/'resultats/cellules'/p.parent.name/p.name)
    closure_meta=KIT/'preuves/tests-fermeture-ui.json'
    if closure_meta.exists():
        source=Path(readj(closure_meta)['root'])/'ui';dest=public/'preuves/fermeture-ui'
        for q in source.glob('closure-*.json'):sanitize_file(q,dest/q.name)
        if (source.parent/'wrong-vault-negative.json').exists():sanitize_file(source.parent/'wrong-vault-negative.json',dest/'wrong-vault-negative.json')
        for name in ('controller.jsonl','preparation-applicative.json','identity.json'):
            if (source/name).exists():sanitize_file(source/name,dest/name)
    # UI runs can contain the commercial fixture: publish witness bytes only.
    for name in ('tests-injection-v13.json','tests-injection-v13-ui.json'):
        p=KIT/'preuves'/name
        if not p.exists():continue
        root=Path(readj(p)['root']);dest=public/'preuves'/name.removesuffix('.json')
        for scenario in root.iterdir():
            if not scenario.is_dir():continue
            original=scenario/'controller.jsonl'
            if original.exists():
                from redact import find_leaks
                assert not find_leaks(original.read_text(encoding='utf-8'))
                rawdest=dest/scenario.name/'controller-original.jsonl.txt';rawdest.parent.mkdir(parents=True,exist_ok=True);rawdest.write_bytes(original.read_bytes())
            for rel in ('qualification.json','relay/events.jsonl','relay/injection-invalid.json'):
                if (scenario/rel).exists():sanitize_file(scenario/rel,dest/scenario.name/rel)
            for q in (scenario/'relay').glob('rpc-*.json'):sanitize_file(q,dest/scenario.name/'relay'/q.name)
            for stage in ('before','human','first'):
                source=scenario/'relay'/(stage+'.json')
                if source.exists():
                    snap=readj(source)
                    writej(dest/scenario.name/(stage+'-temoins.json'),redact({k:v for k,v in snap.items() if k in (P,N,Q)}))
                    writej(dest/scenario.name/(stage+'-inventaire.json'),redact(manifest(snap)))
    count=0
    for stem in ('factice','t7b','read-mappings','native-mappings','technical-receipts','date-stages','fdm-cache'):
        meta=KIT/'preuves'/('tests-'+stem+'.json')
        if not meta.exists():continue
        sanitize_file(meta,public/'preuves'/meta.name);root=Path(readj(meta)['root']);dest=public/'preuves'/(stem+'-qualification-campagne')
        for p in root.rglob('*'):
            if p.is_file() and p.suffix in ('.json','.jsonl') and 'vault' not in p.relative_to(root).parts:
                sanitize_file(p,dest/p.relative_to(root))
        for p in root.rglob('case.json'):
            c=readj(p);v=readj(p.with_name('oracle.json'));assert verify(c)==v
            assert redact(verify(redact(c)))==redact(v);count+=1
        for p in root.rglob('*.json'):
            obj=readj(p)
            if isinstance(obj,dict) and 'case' in obj and 'oracle' in obj:
                assert redact(verify(redact(obj['case'])))==redact(obj['oracle']);count+=1
    for name in ('CLIENT-QUALIFICATION.json','CLIENT-T8-QUALIFICATION.json','FDM-QUALIFICATION.json'):
        if (RUN/name).exists():sanitize_file(RUN/name,public/'resultats'/name)
    if (RUN/'V12-ETAT.json').exists():sanitize_file(RUN/'V12-ETAT.json',public/'resultats/V12-ETAT.json')
    if (KIT/'preuves/v12-preservation-v11.json').exists():sanitize_file(KIT/'preuves/v12-preservation-v11.json',public/'preuves/v12-preservation-v11.json')
    for p in (RUN/'publication').glob('incident-*.json'):sanitize_file(p,public/'resultats/publication'/p.name)
    for p in (RUN/'incidents').glob('*.json'):sanitize_file(p,public/'resultats/incidents'/p.name)
    for cid in (f'C{i:02}' for i in range(1,11)):
        base=RUN/'admissions'/cid
        for name in ('configuration-parametres.json','configuration-plugins.json'):
            if (base/name).exists():sanitize_file(base/name,public/'resultats/admissions'/cid/name)
        for p in (base/'installation-metadata').glob('*'):
            if p.is_file() and p.suffix in ('.json','.txt'):sanitize_file(p,public/'resultats/admissions'/cid/'installation-metadata'/p.name)
    for p in (RUN/'client-qualification').iterdir():
        if not p.is_dir():continue
        for name in ('01.stdout.jsonl','01.stderr.txt','01.final.json','01.exit.json','oracle.json','case.json','effective-config.json','client-config-proof.json','controller.jsonl'):
            if (p/name).exists():sanitize_file(p/name,public/'resultats/client-qualification'/p.name/name)
        for q in (p/'relay').glob('*.json*'):sanitize_file(q,public/'resultats/client-qualification'/p.name/'relay'/q.name)
    for meta in ('CLIENT-T8-QUALIFICATION.json','FDM-QUALIFICATION.json'):
        if not (RUN/meta).exists():continue
        m=readj(RUN/meta);p=Path(m.get('out',m.get('path')));dest=public/'resultats'/('client-t8' if 'T8' in meta else 'fdm-observer')
        names=('01.stdout.jsonl','01.stderr.txt','01.exit.json','02.stdout.jsonl','02.exit.json','02.final.json','case.json','oracle.json','effective-config.json','qualification.json','fdm-observer-evidence.json','controller.jsonl','identity.json')
        for name in names:
            if (p/name).exists():sanitize_file(p/name,dest/name)
        if meta=='FDM-QUALIFICATION.json' and (p/'fdm-observer-raw.json').exists():
            writej(dest/'fdm-observer-raw.json',redact([r for r in readj(p/'fdm-observer-raw.json') if r['path']==P]))
        if 'T8' in meta:
            for q in (p/'relay').glob('*.json*'):sanitize_file(q,dest/'relay'/q.name)
    writej(public/'preuves/validation-projection-campagne.json',{'success':True,'fake_cases_replayed_after_redaction':count,'candidate_scores_rewritten':False,'utc':time.time()})
    print(json.dumps({'projected':True,'fake_cases_replayed':count}))

if __name__=='__main__':main()
