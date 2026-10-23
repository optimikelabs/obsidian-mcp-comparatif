"""Les deux remplacements autorisés par C5, une fois chacun après série 1."""
import argparse
from campaign_run import *

ORIGINALS=('C05-T1-r1','C05-T5-r1')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');args=parser.parse_args()
    rows=readj(KIT/'manifestes/cellules-190.json')
    missing=[r['cell_id'] for r in rows if r['series']==1 and readj(RUN/'admissions'/r['candidate']/'admission.json')['status']=='ADMIS' and not (RUN/'cellules'/r['cell_id']/'result.json').exists()]
    planned=[]
    for original in ORIGINALS:
        row=dict(next(r for r in rows if r['cell_id']==original))
        row.update(cell_id=original+'-remplacement-1',replacement_of=original,replacement_index=1)
        planned.append(row)
    if args.dry_run:
        print(json.dumps({'ready':not missing,'missing_series_1':missing,'planned':[r['cell_id'] for r in planned],'originals_preserved':True}));return
    assert not missing,'Série 1 incomplète : remplacement interdit'
    assert git('show','HEAD:AMENDEMENT-V1.3-C5.md')
    assert git('ls-remote','origin','refs/heads/main').split()[0]==git('rev-parse','HEAD')
    assert readj(KIT/'preuves/tests-injection-v13-ui.json')['success']
    for i,row in enumerate(planned):
        out=RUN/'cellules'/row['cell_id']
        if out.exists():
            if (out/'result.json').exists() and not readj(out/'result.json').get('stop_campaign'):continue
            raise RuntimeError('Remplacement déjà commencé ou arrêté : aucun second essai autorisé')
        old=readj(RUN/'cellules'/row['replacement_of']/'result.json')
        assert old['status']=='NON_JOUE'
        if not wait_resources(row):return
        checkpoint('REMPLACEMENT_EN_COURS',row)
        result=play(row)
        following=planned[i+1] if i+1<len(planned) else next(r for r in rows if r['series']==2)
        checkpoint('ARRET_INCIDENT_REMPLACEMENT' if result['stop_campaign'] else 'PRET_CELLULE_SUIVANTE',following,last_cell=row['cell_id'],last_result=result['verdict'],last_reason=result['reason'])
        head=publish('Remplacement unique: '+row['cell_id']+' / '+result['verdict'])
        print(json.dumps({'cell_id':row['cell_id'],'verdict':result['verdict'],'published':head,'stop_campaign':result['stop_campaign']}),flush=True)
        if result['stop_campaign']:return

if __name__=='__main__':main()
