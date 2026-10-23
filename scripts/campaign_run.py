"""Suite dans l'ordre publié, avec checkpoint et publication après chaque cellule.
Une erreur de sécurité, d'instrumentation ou de publication arrête la boucle.
"""
import argparse,sys
from campaign_runtime import *
from campaign_cell import play
from project_campaign import main as project

def git(*args):
    return subprocess.check_output(['git','-c','core.autocrlf=false',*args],cwd=KIT/'public',stderr=subprocess.STDOUT,text=True,encoding='utf-8').strip()

def publish(message):
    project()
    command([sys.executable,'-X','utf8',str(KIT/'scripts/validate_projection.py')],RUN/'publication','validate',timeout=120,cwd=KIT)
    git('add','--all');git('-c','core.whitespace=cr-at-eol','diff','--cached','--check')
    git('commit','-m',message);head=git('rev-parse','HEAD');git('push','origin','HEAD:main')
    remote=git('ls-remote','origin','refs/heads/main').split()[0];assert remote==head
    git('merge-base','--is-ancestor','e3477a8b02441f73ac3d22b19d78766428887bbd','HEAD')
    writej(RUN/'PUBLICATION-COURANTE.json',{'head':head,'remote_verified':True,'utc':memory()['utc']});return head

def checkpoint(state,next_row,**kw):
    writej(RUN/'REPRISE.json',{'state':state,'utc':memory()['utc'],'next_cell':next_row['cell_id'] if next_row else None,
          'candidate_active':False,'obsidian_instance_active':False,'lock_present':LOCK.exists(),
          'command':'python -X utf8 scripts/campaign_run.py','preservation':'Ne rejouer ni effacer un dossier de cellule existant. Les bacs et reçus sont conservés.',**kw})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--max-cells',type=int);parser.add_argument('--after-incident');parser.add_argument('--series',type=int,choices=(1,2));a=parser.parse_args()
    rows=readj(KIT/'manifestes/cellules-190.json');done=0
    assert readj(RUN/'CLIENT-QUALIFICATION.json')['qualified'] and readj(RUN/'CLIENT-T8-QUALIFICATION.json')['qualified'] and readj(RUN/'FDM-QUALIFICATION.json')['qualified']
    assert not LOCK.exists(),'Verrou occupé : aucune suppression autorisée'
    assert readj(KIT/'preuves/tests-fdm-cache.json')['success']
    assert git('show','HEAD:AMENDEMENT-V1.2-C5.md')
    assert git('ls-remote','origin','refs/heads/main').split()[0]==git('rev-parse','HEAD')
    boundary=0
    if a.after_incident:
        incident=next(r for r in rows if r['cell_id']==a.after_incident);boundary=incident['order']
        assert readj(RUN/'cellules'/a.after_incident/'result.json')['stop_campaign']
        name='AMENDEMENT-'+a.after_incident+'.md'
        assert git('show','HEAD:'+name),'Amendement absent du commit courant'
        assert git('ls-remote','origin','refs/heads/main').split()[0]==git('rev-parse','HEAD'),'Amendement non publié'
    for i,row in enumerate(rows):
        if row['order']<=boundary:continue
        if a.series and row['series']!=a.series:continue
        p=RUN/'cellules'/row['cell_id']
        admission=readj(RUN/'admissions'/row['candidate']/'admission.json')
        if admission['status']!='ADMIS':continue
        if p.exists():
            if (p/'result.json').exists() and not readj(p/'result.json').get('stop_campaign'):continue
            checkpoint('ARRET_INCIDENT_A_INSTRUIRE',row,reason='Dossier commencé ou arrêt conservé ; aucun rejeu automatique.');return
        if not memory()['admitted']:
            checkpoint('ATTENTE_MEMOIRE',row,memory=memory());publish('Checkpoint: attente mémoire avant '+row['cell_id'])
            for wait in range(3):
                time.sleep(600);m=memory();record(RUN/'attente','memory_10min',**m)
                if m['admitted']:break
            else:
                checkpoint('ARRET_MEMOIRE_APRES_30_MIN',row,memory=memory());publish('Checkpoint: seuil mémoire non atteint');return
        checkpoint('CELLULE_EN_COURS',row);print(json.dumps({'starting':row['cell_id'],'utc':memory()['utc']}),flush=True)
        result=play(row);following=next((r for r in rows[i+1:] if readj(RUN/'admissions'/r['candidate']/'admission.json')['status']=='ADMIS'),None)
        checkpoint('ARRET_INCIDENT' if result['stop_campaign'] else 'PRET_CELLULE_SUIVANTE',following,
                   last_cell=row['cell_id'],last_result=result['verdict'],last_reason=result['reason'],incident_cell=row['cell_id'] if result['stop_campaign'] else None)
        head=publish('Résultat brut: '+row['cell_id']+' / '+result['verdict']);done+=1
        print(json.dumps({'finished':row['cell_id'],'verdict':result['verdict'],'stop_campaign':result['stop_campaign'],'published':head},ensure_ascii=False),flush=True)
        if result['stop_campaign']:return
        if a.max_cells and done>=a.max_cells:return
    checkpoint('SERIE_'+str(a.series)+'_TERMINEE' if a.series else 'SERIES_TERMINEES',None)
    publish('Campagne: cellules admissibles de la sélection traitées')

if __name__=='__main__':
    import sys
    main()
