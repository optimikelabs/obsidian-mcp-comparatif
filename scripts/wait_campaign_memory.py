"""Attente bornée ; contrôle toutes les 10 min, sans fermer de programme."""
from campaign_runtime import *

def main():
    out=RUN/'attente-memoire';out.mkdir(parents=True,exist_ok=True)
    for turn in range(4):
        m=memory();record(out,'memory_10min',check=turn,**m)
        writej(RUN/'REPRISE.json',{'phase':'ADMISSIONS_ATTENTE_MEMOIRE','next_admission':'C03','next_cell':'C05-T1-r1',
            'cells_played':0,'candidate_active':None,'lock_taken_by_campaign':False,
            'C01':'Nonce/schémas vérifiés ; revalidation sans Hub requise avant mesure',
            'C02':'Admis, bac attempt-02 arrêté ; schéma lecture structurée à qualifier dans le relais',
            'C03':'Wheel et dépendances installés ; aucun bac ni serveur démarré (gate 4 Gio refusé)',
            'C04_C10':'Admissions non commencées','memory':m,'next_check_utc':datetime.datetime.fromtimestamp(time.time()+600,datetime.timezone.utc).isoformat(),
            'resume_command':'python -X utf8 scripts/admit_c03.py','resume_cwd':'test-comparatif/kit','no_daily_application_closed':True})
        print(json.dumps({'check':turn,**m}),flush=True)
        if m['admitted']:return
        if turn<3:time.sleep(600)
    print('ATTENTE_30_MIN_SANS_ADMISSION_4GIO : état conservé, aucun candidat lancé',flush=True)

if __name__=='__main__':main()
