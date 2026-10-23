"""Contrôle final et résumé privé/public après transfert intégral."""
import json,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from campaign_runtime import *
from campaign_runtime import _owns_process

def main():
    plan=readj(RUN/'migration-stockage/plan.json')
    receipts=sorted((RUN/'migration-stockage/manifestes').glob('*.json'))
    assert len(receipts)==len(plan['items'])
    rows=[]
    for expected,p in zip(plan['items'],receipts):
        r=readj(p);assert r['copied_verified_sha256'] and r['source_removed'] and r['junction_verified']
        src=Path(r['source']);dest=Path(r['destination'])
        assert str(src)==expected['source'] and str(dest)==expected['destination']
        assert src.is_junction() and src.resolve()==dest.resolve()
        assert int(r['bytes'])==expected['bytes']
        rows.append({'path':r['relative_path'],'bytes':int(r['bytes']),'files':len(r['files']),'manifest_sha256':sha(p.read_bytes()),'copy_verified':True,'source_replaced_by_junction':True})
    # Une seule observation de processus ; aucun arrêt ou retrait de verrou ici.
    ps="@(Get-CimInstance Win32_Process -Filter \"Name='Obsidian.exe'\" | Select-Object ProcessId,ExecutablePath,CommandLine) | ConvertTo-Json -Compress"
    raw=subprocess.check_output(['powershell','-NoProfile','-Command',ps],text=True,encoding='utf-8').strip();processes=json.loads(raw) if raw else []
    if isinstance(processes,dict):processes=[processes]
    owned=[]
    for p in (RUN/'cellules').glob('*/obsidian.json'):
        cfg=readj(p);owned.extend(r['ProcessId'] for r in processes if _owns_process(r,cfg))
    assert not owned
    assert readj(RUN/'PAUSE-C5.json')['active']
    proof={'success':True,'directories':len(rows),'bytes':sum(r['bytes'] for r in rows),'files':sum(r['files'] for r in rows),'items':rows,
           'oracle_replays':readj(RUN/'migration-stockage/oracles-preserves.json'),'owned_obsidian_processes':owned,'lock_present_at_check':LOCK.exists(),
           'campaign_lock_released':True,'foreign_lock_not_modified':True,'pause_active':True,'next_cell':'C01-T8-r1','resume_requires':'nouveau message explicite de C5',
           'utc':memory()['utc'],'free_bytes_E':shutil.disk_usage(KIT).free,'free_bytes_B':shutil.disk_usage(Path(plan['destination_root'])).free}
    assert proof['bytes']==plan['bytes']
    archive=Path(plan['destination_root'])/'_manifestes'/('migration-'+str(time.time_ns()))
    archive.mkdir(parents=True)
    for p in [RUN/'migration-stockage/plan.json',RUN/'migration-stockage/oracles-preserves.json',*receipts]:
        dest=archive/(p.name if p.parent.name!='manifestes' else 'manifeste-'+p.name)
        shutil.copy2(p,dest);assert sha(p.read_bytes())==sha(dest.read_bytes())
    proof['manifest_backup']=str(archive)
    writej(RUN/'migration-stockage/bilan.json',proof)
    writej(KIT/'preuves/stockage-migration-resume.json',proof)
    rows=readj(KIT/'manifestes/cellules-190.json')
    table=[]
    for row in rows:
        p=RUN/'cellules'/row['cell_id']/'result.json'
        if p.exists():table.append('| '+row['cell_id']+' | '+readj(p)['verdict']+' |')
    note="""# Reprise après quota — campagne MCP Obsidian

Pause décidée par C5 le 23 octobre 2026 : recette de la 1.0.7 prioritaire et quota hebdomadaire Codex signalé à 2 %, remise à zéro estimée dans environ six jours. Aucune cellule ni instance Obsidian ne doit être lancée pendant cette pause. Aucun horaire estimé ne vaut autorisation de reprise.

## Point exact

Dernière cellule : C01-T7-r1, PROTEGE_NON_ACCOMPLI, publiée et validée sans différence après fermeture.
**Prochaine cellule : C01-T8-r1.** C05-T6-r1 est déjà jouée et publiée REUSSI_VERIFIE ; ne pas la rejouer.
23 cellules traitées : 18 jouées et 5 non exécutées ou invalidées. Tous les dossiers et verdicts bruts sont conservés.

| Cellule | Verdict brut conservé |
|---|---|
"""+'\n'.join(table)+r"""

Un seul remplacement autorisé en fin de série 1 pour C05-T1-r1, C05-T5-r1, C08-T4-r1, C08-T6-r1 et C08-T8-r1. Aucun de ces remplacements n'a été exécuté. Le motif v1.4 concerne uniquement C08-T6-r1 dans l'audit des cellules antérieures ; aucun reclassement. La nouvelle tentative C06 reste en fin de série 2.

## Verrou et processus

Le verrou de campagne a été supprimé après fermeture et vérification de l'absence de ses processus. Aucun processus Obsidian de campagne ne reste au contrôle final. Le contrôleur et le lanceur sont bloqués par resultats/PAUSE-C5.json. Tout verrou pris ensuite par le fil produit doit rester intact.

## Stockage

Archives lourdes : B:\margelle-campagne\resultats-lourds\, avec la même arborescence. Coffres et profils : resultats/cellules/<cellule>/{vault,profile} ; installations : installations/. Les anciens chemins sur E restent des jonctions. Les prochains coffres, profils et caches serveur sont créés directement sur B. Aucun repli sur E si le volume manque.

Le bilan détaillé est dans resultats/migration-stockage/bilan.json ; les manifestes SHA-256 complets dans resultats/migration-stockage/manifestes/ et leur copie sur B sous _manifestes/. Les instantanés, oracles et journaux nécessaires à la publication restent sur E. Tous les fichiers transférés ont été vérifiés avant retrait de la source puis via leur jonction. Aucun dossier n'est laissé partiellement transféré.

## Conditions et procédure de relance

1. Attendre un nouveau message explicite de C5 autorisant la reprise, la fin de la recette produit et un quota Codex suffisant. La remise à zéro seule ne suffit pas.
2. Lire ce point, kit/public/resultats/REPRISE.json, les décisions C5 et les amendements. Vérifier le commit distant, le volume B, les jonctions, les manifestes et la qualification finale publiée. Ne rejouer ni effacer aucun dossier existant.
3. Contrôler le verrou partagé : ne jamais le forcer. Attendre sa libération. Il faut simultanément 4 Gio de RAM disponible et 4 Gio de marge d'engagement ; arrêt sous 2 Gio sur l'une des deux mesures. Entre cellules, attente mémoire toutes les 10 minutes, 2 heures au maximum.
4. L'orchestrateur reste Astra. Le client testé reste Codex CLI gpt-6.1-sol, effort high, serviceTier default ; s'il est indisponible, arrêt propre sans substitution. Instances isolées seulement, aucun profil quotidien, ni ports 27123/27124, ni écriture dans le coffre quotidien, ni arrêt de programme de Mike ou relance bitnet.
5. Seulement après ces contrôles et le message de C5, lever explicitement active dans resultats/PAUSE-C5.json en conservant la décision de reprise. Depuis kit, exécuter une cellule :

```powershell
python -X utf8 scripts/campaign_run.py --after-incident C08-T8-r1 --series 1 --max-cells 1
```

Le contrôleur saute les résultats conservés et doit commencer C01-T8-r1. Après la cellule : fermeture contrôlée, observation après instantané, attribution éventuelle FDM selon les critères publiés, validation et publication avant la suivante. Les gels précédents restent conservés. Aucun score ou délai de jugement n'est modifié par le déplacement de stockage.
"""
    note+='\nTransfert final : '+str(proof['directories'])+' dossiers, '+str(proof['bytes'])+' octets, '+str(proof['files'])+' fichiers. Contrôle du verrou à '+proof['utc']+' : '+('présent, laissé intact' if proof['lock_present_at_check'] else 'absent')+'.\n'
    (KIT.parent/'REPRISE-APRES-QUOTA.md').write_text(note,encoding='utf-8')
    (KIT/'REPRISE-APRES-QUOTA.md').write_text(note,encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('items','oracle_replays')},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
