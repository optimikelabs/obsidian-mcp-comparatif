"""Artefacts techniques C08 liés à une réponse observée, jamais une exemption de dossier."""
import re
from common import *

def transaction_paths(case):
    if case.get('technical_receipts_policy')!='c08-transactions-v1':return [],[]
    after=case['after'];before=case['before'];paths=[];errors=[]
    allowed={N if case['task'] in ('T4','T5') else P}
    pattern=re.compile(r'^\.obsidian-mcp/transactions/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/manifest\.json$')
    for rel in after:
        match=pattern.fullmatch(rel)
        if not match or rel in before:continue
        try:
            ident=match[1];root=rel.rsplit('/',1)[0];m=json.loads(data(after,rel).decode('utf-8'))
            assert set(m)<= {'id','state','createdAt','snapshots','completedAt'}
            assert m['id']==ident and m['state']=='committed' and isinstance(m['snapshots'],list) and len(m['snapshots'])==1
            snap=m['snapshots'][0]
            assert set(snap)<= {'path','operation','entryType','phase','plannedEtag','recoverable','existed','mode','etag','snapshot','committedEtag'}
            assert snap['path'] in allowed and snap['operation']=='write' and snap['entryType']=='file' and snap['phase']=='applied'
            assert any(e.get('event')=='technical_transaction_receipt' and e.get('transaction_id_sha256')==sha(ident.encode())
                       and e.get('path')==snap['path'] for e in case.get('events',[]))
            assert re.fullmatch('[0-9a-f]{64}',snap['plannedEtag']) and snap['committedEtag']==snap['plannedEtag']
            exact=[rel]
            if snap['existed']:
                assert snap['snapshot']=='0.bin' and re.fullmatch('[0-9a-f]{64}',snap['etag'])
                backup=root+'/0.bin';assert backup in after and sha(data(after,backup))==snap['etag'];exact.append(backup)
            else:assert 'snapshot' not in snap
            assert all(not p.endswith(('.md','main.js')) for p in exact)
            paths.extend(exact)
        except (AssertionError,KeyError,ValueError,TypeError,UnicodeError):errors.append('ARTEFACT_TRANSACTION_NON_QUALIFIE:'+rel)
    return sorted(set(paths)),errors
