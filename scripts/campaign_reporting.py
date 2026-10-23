"""Tableau intégral de campagne et projection publique en liste blanche."""
import csv
from campaign_runtime import *
from redact import sanitize_file,redact

URL='https://github.com/optimikelabs/obsidian-mcp-comparatif/tree/main/resultats'

def build():
    RUN.mkdir(parents=True,exist_ok=True);rows=readj(KIT/'manifestes/cellules-190.json');admissions=[]
    for cid in (f'C{i:02}' for i in range(1,11)):
        base=RUN/'admissions'/cid
        if (base/'admission.json').exists():entry=readj(base/'admission.json')
        elif (base/'admission-partielle.json').exists():entry=readj(base/'admission-partielle.json')
        else:entry={'candidate':cid,'status':'A_INSTRUIRE','reason':'Admission non achevée ; aucun résultat de cellule.'}
        admissions.append(entry)
    for row in rows:
        cell=RUN/'cellules'/row['cell_id']/'result.json'
        if cell.exists():row.update(readj(cell))
        else:row['reason']='Campagne en admission / attente ; cellule non commencée.'
    writej(RUN/'cellules-190.json',rows);writej(RUN/'admissions.json',admissions)
    columns=['order','series','candidate','task','repetition','cell_id','status','verdict','reason']
    with (RUN/'cellules-190.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)
    admitted=[a['candidate'] for a in admissions if a['status']=='ADMIS'];pending=[a['candidate'] for a in admissions if a['status']!='ADMIS']
    counts=[]
    for s in (1,2):
        selected=[x for x in rows if x['series']==s];played=sum(x['status']=='JOUE' for x in selected)
        counts.append(f'Série {s} : {played} cellules jouées ; {len(selected)-played} non jouées (sur {len(selected)}).')
    incidents=[]
    for p in sorted((RUN/'admissions').glob('*/incident.json')):incidents.append({'path':str(p.relative_to(RUN)),'error':readj(p)['error']})
    text='\n'.join(counts+[
        'Candidats admis : '+(', '.join(admitted) or 'aucun')+'.',
        'Candidats non admis ou admission à achever : '+(', '.join(pending) or 'aucun')+'.',
        'T5, T6, T7, T7b : trois répétitions prévues pour collision et retouches concurrentes ; aucune conclusion sans les cellules.',
        'T8 : trois répétitions prévues pour effet appliqué/réponse perdue et reprise ; seules les cellules jouées sont mesurées.',
        f'Incidents consignés : {len(incidents)} ; voir détails et journaux, sans attribution automatique au candidat.',
        'Résultats publiés : '+URL,
    ])+'\n\n# Rapport de campagne — état courant\n\n'
    text+='État horodaté : '+memory()['utc']+'. Publication préalable v1.1 : `1e698f62401034c74dd70a1019146e45c8dc821f`. Gel V1 `e3477a8b02441f73ac3d22b19d78766428887bbd` conservé. Clone frais : 580 fichiers du manifeste vérifiés, aucun écart.\n\n'
    text+='Qualification de l’instrumentation : suite T1–T8 (5 groupes) passée ; 30 contrôles T7b stdio/HTTP/SSE passés et rejugés après masquage. Ce sont des essais factices, aucun résultat candidat. Manifeste 190 : 160 lignes d’origine préservées, puis 30 T7b en série 2.\n\n'
    text+='## Admissions\n\n| Candidat | État | Preuve ou reste à faire |\n|---|---|---|\n'
    for a in admissions:text+='| '+a['candidate']+' | '+a['status']+' | '+a.get('reason','Nonce/catalogue acquis ; schémas à qualifier.').replace('|','/')+' |\n'
    text+='\n## Limites\n\nUn agent Codex CLI 0.160.1, gpt-6.1-sol high, serviceTier default. Corpus Margelle commercial vendu par l’auteur d’Optimike ; corpus synthétique publié mais non rejoué en campagne. T1–T4 : une seule répétition. Trois répétitions de T5/T6/T7/T7b/T8 ne donnent pas un taux de risque rare. Les non-joués ne sont ni réussites ni échecs fonctionnels. Aucun contact mainteneur, aucune publication hors de ce dépôt.\n\n'
    if incidents:
        text+='## Incidents\n\n'
        for x in incidents:text+='- '+x['path']+' : '+x['error']+'\n'
    state=RUN/'REPRISE.json'
    if state.exists():text+='\n## Reprise exacte\n\n```json\n'+json.dumps(readj(state),ensure_ascii=False,indent=2)+'\n```\n'
    text+='\n## Pilotage\n\nAucun changement de statut recommandé à ce stade ; statut canonique non audité (coffre quotidien hors périmètre). Prochaine action : achever les admissions, puis première cellule selon le manifeste, sous les seuils mémoire et verrou. Aucune tâche du coffre modifiée.\n'
    (RUN/'RAPPORT-CAMPAGNE.md').write_text(text,encoding='utf-8',newline='')
    print(json.dumps({'played':sum(r['status']=='JOUE' for r in rows),'unplayed':sum(r['status']!='JOUE' for r in rows),'admitted':admitted,'pending':pending}))

def project():
    public=KIT/'public/resultats'
    for rel in ('RAPPORT-CAMPAGNE.md','cellules-190.json','cellules-190.csv','admissions.json','REPRISE.json'):
        p=RUN/rel
        if p.exists():sanitize_file(p,public/rel)
    for cid in (f'C{i:02}' for i in range(1,11)):
        for name in ('admission.json','admission-partielle.json','adapter.json','catalogue.json','fiche-technique.md','incident.json','nonce-read.json','preparation-applicative.json','identity.json','qualification-summary.json','qualification-incident.json','controller.jsonl'):
            p=RUN/'admissions'/cid/name
            if p.exists():sanitize_file(p,public/'admissions'/cid/name)
        for pattern in ('rpc-*.json','qualification-rpc-*.json'):
            for p in (RUN/'admissions'/cid).glob(pattern):sanitize_file(p,public/'admissions'/cid/p.name)
    for cid,attempt in (('C01','revalidation-sans-hub'),('C02','attempt-02')):
        for name in ('identity.json','nonce-read.json','preparation-applicative.json','controller.jsonl'):
            p=RUN/'admissions'/cid/attempt/name
            if p.exists():sanitize_file(p,public/'admissions'/cid/attempt/name)
    # Aucun profil, coffre commercial, config privée, auth ou artefact candidat dans cette projection.

if __name__=='__main__':build();project()
