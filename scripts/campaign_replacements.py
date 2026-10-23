"""Les remplacements uniques autorisés par C5, une fois chacun après leur série."""
import argparse
from campaign_run import *

def authorizations():return readj(KIT/'manifestes/remplacements-autorises.json')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dry-run',action='store_true');parser.add_argument('--series',type=int,choices=(1,2),default=1);args=parser.parse_args()
    rows=readj(KIT/'manifestes/cellules-190.json')
    missing=[r['cell_id'] for r in rows if r['series']==args.series and readj(RUN/'admissions'/r['candidate']/'admission.json')['status']=='ADMIS' and not (RUN/'cellules'/r['cell_id']/'result.json').exists()]
    planned=[]
    for authorization in authorizations():
        if authorization['series']!=args.series:continue
        original=authorization['original']
        assert authorization['replacement_limit']==1
        assert sha((RUN/'cellules'/original/'result.json').read_bytes())==authorization['original_result_sha256']
        row=dict(next(r for r in rows if r['cell_id']==original))
        row.update(cell_id=original+'-remplacement-1',replacement_of=original,replacement_index=1)
        planned.append(row)
    if args.dry_run:
        print(json.dumps({'ready':not missing,'series':args.series,'missing_series':missing,'planned':[r['cell_id'] for r in planned],'originals_preserved':True}));return
    assert not missing,'Série incomplète : remplacement interdit'
    assert git('show','HEAD:NOTE-EXPLOITATION-20261023-C5.md')
    assert json.loads(git('show','HEAD:manifestes/remplacements-autorises.json'))==authorizations()
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
        following=planned[i+1] if i+1<len(planned) else next((r for r in rows if r['series']>args.series),None)
        checkpoint('ARRET_INCIDENT_REMPLACEMENT' if result['stop_campaign'] else 'PRET_CELLULE_SUIVANTE',following,last_cell=row['cell_id'],last_result=result['verdict'],last_reason=result['reason'])
        head=publish('Remplacement unique: '+row['cell_id']+' / '+result['verdict'])
        print(json.dumps({'cell_id':row['cell_id'],'verdict':result['verdict'],'published':head,'stop_campaign':result['stop_campaign']}),flush=True)
        if result['stop_campaign']:return

if __name__=='__main__':main()
