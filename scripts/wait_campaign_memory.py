"""Attente bornée ; contrôle toutes les 10 min, sans fermer de programme."""
from campaign_runtime import *

def main():
    import sys
    candidate=sys.argv[1] if len(sys.argv)>1 else 'C03'
    resume=sys.argv[2] if len(sys.argv)>2 else 'python -X utf8 scripts/admit_c03.py'
    out=RUN/'attente-memoire';out.mkdir(parents=True,exist_ok=True)
    for turn in range(4):
        m=memory();record(out,'memory_10min',check=turn,**m)
        states={}
        for cid in (f'C{i:02}' for i in range(1,11)):
            d=RUN/'admissions'/cid
            p=next((d/n for n in ('admission.json','admission-partielle.json') if (d/n).exists()),None)
            states[cid]=readj(p).get('status') if p else 'A_INSTRUIRE'
        writej(RUN/'REPRISE.json',{'phase':'ADMISSIONS_ATTENTE_MEMOIRE','next_admission':candidate,'next_cell':'C05-T1-r1',
            'cells_played':0,'candidate_active':None,'lock_taken_by_campaign':False,
            'admissions':states,'memory':m,'next_check_utc':datetime.datetime.fromtimestamp(time.time()+600,datetime.timezone.utc).isoformat(),
            'resume_command':resume,'resume_cwd':'test-comparatif/kit','no_daily_application_closed':True,
            'do_not_rerun':['amend_v11.py','publish_v11.py (gel déjà publié)'],
            'remaining_gates_before_cells':['Admissions C07-C10','Parsers natifs et actions multiplexées qualifiés sur factice','Client commun Codex isolé/fournisseur/options scellés','Publication des adaptateurs et du delta avant toute cellule']})
        print(json.dumps({'check':turn,**m}),flush=True)
        if m['admitted']:return
        if turn<3:time.sleep(600)
    print('ATTENTE_30_MIN_SANS_ADMISSION_4GIO : état conservé, aucun candidat lancé',flush=True)

if __name__=='__main__':main()
