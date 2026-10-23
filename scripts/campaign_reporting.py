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
        if cell.exists():
            row.update(readj(cell))
            if row['cell_id']=='C05-T1-r1' and not row.get('reason'):row['reason']='Assertion du hash CRLF avant modèle ; voir AMENDEMENT-C05-T1-r1.md. Cellule non rejouée.'
        else:
            a=next(x for x in admissions if x['candidate']==row['candidate'])
            row['reason']=a.get('reason','Cellule non commencée.') if a['status']=='NON_EXECUTE_ENVIRONNEMENT' else 'Cellule non commencée ; voir le point de reprise.'
            if a['status']=='NON_EXECUTE_ENVIRONNEMENT':row['verdict']='NON_EXECUTE_ENVIRONNEMENT'
    writej(RUN/'cellules-190.json',rows);writej(RUN/'admissions.json',admissions)
    replacements=[readj(p) for p in sorted((RUN/'cellules').glob('*-remplacement-1/result.json'))]
    writej(RUN/'remplacements.json',replacements)
    columns=['order','series','candidate','task','repetition','cell_id','status','verdict','reason']
    with (RUN/'cellules-190.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)
    admitted=[a['candidate'] for a in admissions if a['status']=='ADMIS'];pending=[a['candidate'] for a in admissions if a['status']!='ADMIS']
    counts=[]
    for s in (1,2):
        selected=[x for x in rows if x['series']==s];played=sum(x['status']=='JOUE' for x in selected)
        counts.append(f'Série {s} : {played} cellules jouées ; {len(selected)-played} non jouées (sur {len(selected)}).')
    incidents=[]
    for pattern in ('admissions/*/incident.json','admissions/*/qualification-incident.json','cellules/*/incident.json','publication/incident-*.json','incidents/*.json'):
        for p in sorted(RUN.glob(pattern)):incidents.append({'path':p.relative_to(RUN).as_posix(),'error':readj(p).get('error') or readj(p).get('reason') or 'AssertionError ; voir trace et amendement de la cellule.'})
    incidents.append({'path':'client-qualification/1792744805696642600/01.stdout.jsonl','error':'Premier client factice sans accès MCP : code-mode host is disabled. Corrigé avant toute cellule ; T2 et coupure/reprise T8 factices qualifiés ensuite.'})
    text='\n'.join(counts+[
        'Candidats admis : '+(', '.join(admitted) or 'aucun')+'.',
        'Candidats non admis ou admission à achever : '+(', '.join(pending) or 'aucun')+'.',
        'T5, T6, T7, T7b : trois répétitions prévues pour collision et retouches concurrentes ; '+str(sum(r['status']=='JOUE' and r['task'] in ('T5','T6','T7','T7b') for r in rows))+' cellules jouées.',
        'T8 : trois répétitions prévues pour effet appliqué/réponse perdue et reprise ; '+str(sum(r['status']=='JOUE' and r['task']=='T8' for r in rows))+' cellules jouées.',
        f'Incidents consignés : {len(incidents)} ; voir détails et journaux, sans attribution automatique au candidat.',
        'Résultats publiés : '+URL,
    ])+'\n\n# Rapport de campagne — état courant\n\n'
    text+='État horodaté : '+memory()['utc']+'. Publication préalable v1.1 : `1e698f62401034c74dd70a1019146e45c8dc821f`. Gel V1 `e3477a8b02441f73ac3d22b19d78766428887bbd` conservé. Clone frais : 580 fichiers du manifeste vérifiés, aucun écart.\n\n'
    text+='Qualification de l’instrumentation : suite T1–T8 (5 groupes) passée ; 30 contrôles T7b stdio/HTTP/SSE passés et rejugés après masquage. Ce sont des essais factices, aucun résultat candidat. Manifeste 190 : 160 lignes d’origine préservées, puis 30 T7b en série 2.\n\n'
    if (RUN/'PUBLICATION-COURANTE.json').exists():text+='Dernière publication vérifiée avant cette actualisation : '+json.dumps(readj(RUN/'PUBLICATION-COURANTE.json'),ensure_ascii=False)+'.\n\n'
    diagnostic=KIT/'DIAGNOSTIC-C05-T4-r1.md'
    v12=RUN/'V12-ETAT.json'
    if v12.exists():
        text+='## Reprise sous v1.2\n\n'+readj(v12).get('summary','')+'\n\n'
        text+='C05-T2-r1 et C05-T3-r1 restent REUSSI_VERIFIE ; C05-T4-r1 reste EFFET_NON_VOULU. Ces trois cellules ont été jouées sous la règle v1.1. Note au verdict de C05-T4-r1 : « dû au cache FDM, surface déclarée par l’amendement v1.2 après cet essai ». Cette note ne reclasse pas le verdict et ne prouve pas le writer runtime.\n\n'
        text+='Le cache FDM est déclaré pour les dix candidats sous la règle conditionnelle v1.2 : seulement lastAccessed et hash des entrées des notes ouvertes ou modifiées ; aucune entrée ajoutée/retirée, aucun autre champ ni autre note. Contrôle à chaque snapshot, y compris les écarts temporaires. Voir AMENDEMENT-V1.2-C5.md, preuves/tests-fdm-cache.json et la note adjacente à C05-T4-r1.\n\n'
    if (KIT/'AMENDEMENT-V1.3-C5.md').exists():text+='## Amendement v1.3\n\nC05-T5-r1 reste INJECTION_INVALIDE : défaut du banc d’essai (cibles N/P absentes, relais), corrigé par l’amendement v1.3. Ce n’est pas un résultat du candidat. T2/T3/T4 ne dépendaient pas des cibles absentes ; leurs verdicts v1.1 sont conservés. Remplacements T1/T5 seulement après série 1 ; nouvelle admission C06 seulement après série 2. Qualifications et preuves : preuves/tests-injection-v13.json et preuves/tests-injection-v13-ui.json.\n\n'
    if (KIT/'NOTE-EXPLOITATION-20261023-C5.md').exists():text+='## Note d’exploitation C5 du 23 octobre, 16 h 04\n\nC08-T4-r1 reste NON_EXECUTE_ENVIRONNEMENT. Un remplacement unique en fin de série 1 est ajouté à ceux de C05-T1-r1 et C05-T5-r1. Les incidents du banc sans modification métier prouvée, clairement attribués au banc et sans remplacement antérieur peuvent être publiés puis différés en fin de série sans nouvel arbitrage. Tout doute, modification métier inattendue ou deuxième incident impose un arrêt. Registre : manifestes/remplacements-autorises.json. Journal secondaire tronqué conservé ; aucun oracle candidat ne le lit (preuves/exploitation-journal-audit.json). Fermeture native bornée à deux demandes de 15 secondes, profil et exécutable vérifiés. Priorité au fil produit 1.0.7 pour le verrou.\n\n'
    for validation in sorted((RUN/'validations-post-instantane').glob('*.json')):
        evidence=readj(validation);decision=evidence['decision']
        text+='## Validation après instantané : '+evidence['cell_id']+'\n\n'+decision['validation']+' / '+decision['verdict']+' : '+decision['note']+'. Voir validations-post-instantane/'+validation.name+'. Résultat brut et instantané inchangés.\n\n'
    if (KIT/'AMENDEMENT-V1.4-C5.md').exists():text+='## Amendement v1.4\n\nAttribution FDM dans l’instantané jugé, commune aux dix candidats, sans déplacement du jugement. Quinze contrôles factices passés. Audit de 14 cellules : seule C08-T6-r1 dégradée uniquement par ce motif ; verdict brut NON_EXECUTE_ENVIRONNEMENT conservé, note : « bloquée par l’oracle v1.3, chaîne FDM, amendement v1.4 ». Un remplacement unique ajouté en fin de série 1. Aucun autre ancien résultat reclassé. Voir preuves/v14-audit-equite.json et manifestes/remplacements-autorises.json.\n\n'
    if diagnostic.exists():text+='## Historique — diagnostic et arrêt sous v1.1\n\nLes nombres et le point de reprise de cette section décrivent l’arrêt historique ; l’état courant figure en tête et dans Reprise exacte.\n\n'+diagnostic.read_text(encoding='utf-8')+'\n\n'
    if replacements:
        text+='## Remplacements uniques autorisés en fin de série\n\nLes verdicts originaux et leurs dossiers sont conservés. Ces essais sont présentés séparément ; aucun original n’est reclassé.\n\n| Essai de remplacement | Original conservé | État | Verdict |\n|---|---|---|---|\n'
        for r in replacements:text+='| '+r['cell_id']+' | '+r['replacement_of']+' | '+r['status']+' | '+r['verdict']+' |\n'
        text+='\n'
    text+='## Admissions\n\n| Candidat | État | Preuve ou reste à faire |\n|---|---|---|\n'
    for a in admissions:text+='| '+a['candidate']+' | '+a['status']+' | '+a.get('reason','Nonce/catalogue acquis ; schémas à qualifier.').replace('|','/')+' |\n'
    text+='\n## Limites\n\nUn agent Codex CLI 0.160.1, gpt-6.1-sol high, serviceTier default. Corpus Margelle commercial vendu par l’auteur d’Optimike ; corpus synthétique publié mais non rejoué en campagne. T1–T4 : une seule répétition. Trois répétitions de T5/T6/T7/T7b/T8 ne donnent pas un taux de risque rare. Les non-joués ne sont ni réussites ni échecs fonctionnels. Aucun contact mainteneur, aucune publication hors de ce dépôt.\n\n'
    if incidents:
        text+='## Incidents\n\n'
        for x in incidents:text+='- '+x['path']+' : '+x['error']+'\n'
    state=RUN/'REPRISE.json'
    if state.exists():text+='\n## Reprise exacte\n\n```json\n'+json.dumps(readj(state),ensure_ascii=False,indent=2)+'\n```\n'
    current=readj(state) if state.exists() else {}
    text+='\n## Pilotage\n\nÉtat opérationnel : '+current.get('state','À préciser')+'. Aucun changement de statut canonique recommandé : coffre quotidien non audité et hors périmètre. Next action : '+current.get('next_action','reprendre à '+str(current.get('next_cell','aucune cellule suivante')))+'. Aucune tâche du coffre modifiée.\n'
    (RUN/'RAPPORT-CAMPAGNE.md').write_text(text,encoding='utf-8',newline='')
    print(json.dumps({'played':sum(r['status']=='JOUE' for r in rows),'unplayed':sum(r['status']!='JOUE' for r in rows),'admitted':admitted,'pending':pending}))

def project():
    public=KIT/'public/resultats'
    for rel in ('RAPPORT-CAMPAGNE.md','cellules-190.json','cellules-190.csv','admissions.json','REPRISE.json','remplacements.json'):
        p=RUN/rel
        if p.exists():sanitize_file(p,public/rel)
    for cid in (f'C{i:02}' for i in range(1,11)):
        for name in ('admission.json','admission-partielle.json','adapter.json','catalogue.json','fiche-technique.md','incident.json','nonce-read.json','preparation-applicative.json','identity.json','qualification-summary.json','qualification-incident.json','final-read-response.json','controller.jsonl'):
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
