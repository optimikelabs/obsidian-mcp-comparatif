"""Reçus techniques : aucune note, aucun code et aucun dossier entier n'est masqué."""
import copy
from common import *
from oracles import verify

def main():
    root=KIT/'preuves/technical-receipts'/str(time.time_ns());root.mkdir(parents=True);checks=[]
    original=Path(readj(KIT/'preuves/tests-factice.json')['root'])
    ident='11111111-2222-4333-8444-555555555555';base='.obsidian-mcp/transactions/'+ident
    def item(blob):return {'size':len(blob),'sha256':sha(blob),'base64':base64.b64encode(blob).decode()}
    for task in ('T2','T6','T8'):
        c=readj(original/f'http-{task}-good/case.json');origin=c.get('human',c['before']);backup=data(origin,P)
        entry={'path':P,'operation':'write','entryType':'file','phase':'applied','plannedEtag':sha(data(c['after'],P)),
               'recoverable':True,'existed':True,'mode':33206,'etag':sha(backup),'snapshot':'0.bin','committedEtag':sha(data(c['after'],P))}
        m={'id':ident,'state':'committed','createdAt':'2026-10-23T00:00:00.000Z','completedAt':'2026-10-23T00:00:01.000Z','snapshots':[entry]}
        c['after'][base+'/manifest.json']=item(json.dumps(m,ensure_ascii=False).encode());c['after'][base+'/0.bin']=item(backup)
        c['technical_receipts_policy']='c08-transactions-v1';c['events'].append({'event':'technical_transaction_receipt','transaction_id_sha256':sha(ident.encode()),'path':P})
        v=verify(c);assert v['errors']==[],v;assert len(v['technical_receipt_paths'])==2
        writej(root/f'{task}-positive.json',{'case':c,'oracle':v});checks.append({'case':task,'verdict':v['verdict']})
        for kind in ('no_receipt','other_note','corrupt_backup','hidden_note'):
            bad=copy.deepcopy(c)
            if kind=='no_receipt':bad['events']=[e for e in bad['events'] if e['event']!='technical_transaction_receipt']
            if kind=='other_note':
                altered=copy.deepcopy(m);altered['snapshots'][0]['path']=Q;bad['after'][base+'/manifest.json']=item(json.dumps(altered,ensure_ascii=False).encode())
            if kind=='corrupt_backup':bad['after'][base+'/0.bin']=item(b'Bytes non conformes')
            if kind=='hidden_note':bad['after'][base+'/cache.md']=item(b'Une autre note ne devient jamais technique')
            result=verify(bad)
            assert result['verdict']==('EFFET_NON_VOULU' if kind=='hidden_note' else 'NON_EXECUTE_ENVIRONNEMENT'),result
            writej(root/f'{task}-negative-{kind}.json',{'case':bad,'oracle':result});checks.append({'case':task+'-'+kind,'verdict':result['verdict']})
    writej(KIT/'preuves/tests-technical-receipts.json',{'success':True,'root':str(root),'checks':checks})
    print(json.dumps({'success':True,'checks':len(checks)}))

if __name__=='__main__':main()
