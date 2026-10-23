"""Publication finale du stockage, seulement après qualification factice réussie."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import campaign_run as run
from campaign_runtime import *
assert readj(RUN/'migration-stockage/qualification-finale-etat.json')['state']=='QUALIFICATION_REUSSIE'
proof=readj(RUN/'migration-stockage/bilan.json');assert proof['success'] and proof['directories']==47
assert readj(RUN/'PAUSE-C5.json')['active']
meta=readj(KIT/'preuves/tests-stockage-lourd.json');assert meta['success'] and not meta['real_obsidian_launched'] and not meta['tested_client_launched']
meta['after_complete_transfer']=True
meta['files']={str(p.relative_to(KIT)).replace('\\','/'):sha(p.read_bytes()) for p in [KIT/'scripts'/n for n in ('common.py','heavy_storage.py','campaign_runtime.py','candidate_runtime.py','campaign_run.py','test_heavy_storage.py')]}
meta['pause_guards_verified']=['campaign_runner','obsidian_launcher'];writej(KIT/'preuves/tests-stockage-lourd.json',meta)
for name,digest in readj(KIT/'preuves/v14-code-qualifie.json')['files'].items():assert sha((KIT/name).read_bytes())==digest
for row in proof['items']:
 number=proof['items'].index(row)+1;p=RUN/'migration-stockage/manifestes'/f'{number:03}.json'
 assert sha(p.read_bytes())==row['manifest_sha256']
 assert sha((Path(proof['manifest_backup'])/('manifeste-'+p.name)).read_bytes())==row['manifest_sha256']
for cell in proof['oracle_replays']:
 for kind in ('oracle','result'):assert sha((RUN/'cellules'/cell['cell_id']/(kind+'.json')).read_bytes())==cell[kind+'_sha256']
q=readj(RUN/'migration-stockage/qualification-finale-etat.json')
for p in (KIT.parent/'REPRISE-APRES-QUOTA.md',KIT/'REPRISE-APRES-QUOTA.md'):
 s=p.read_text(encoding='utf-8');s=s.split('\n## Étape encore requise : rejeu factice final')[0];s+='\nQualification finale après transfert : réussie à '+q['utc']+' ; 57 contrôles factices et cinq scénarios FDM v1.4, sans Obsidian ni client testé. Voir kit/preuves/tests-stockage-lourd.json et les journaux resultats/migration-stockage/qualification-finale.*.\n';p.write_text(s,encoding='utf-8')
run.checkpoint('PAUSE_C5_QUOTA_ET_RECETTE_1_0_7',{'cell_id':'C01-T8-r1'},last_cell='C01-T7-r1',last_result='PROTEGE_NON_ACCOMPLI',resume_requires='Quota suffisant et nouveau message explicite de C5 ; verrou libre et seuils mémoire respectés',resume_note='REPRISE-APRES-QUOTA.md',storage_transferred_bytes=proof['bytes'],storage_directories=47,qualification_finale='REUSSIE',resume_command='python -X utf8 scripts/campaign_run.py --after-incident C08-T8-r1 --series 1 --max-cells 1')
# Gardes avant commit : les verdicts publics et les gels déjà publiés restent identiques.
public=KIT/'public';preserved={p:sha(p.read_bytes()) for p in (public/'resultats/cellules').glob('*/*.json') if p.name in ('oracle.json','result.json')}
for name in ('PROTOCOLE-V1.1-GELE.md','PROTOCOLE-V1.2-GELE.md','PROTOCOLE-V1.3-GELE.md'):preserved[public/name]=sha((public/name).read_bytes())
original=run.project
def checked_project():
 original()
 for p,digest in preserved.items():assert sha(p.read_bytes())==digest,'Gel ou résultat modifié : '+str(p)
run.project=checked_project
print(run.publish('Stockage lourd sur B vérifié ; qualification factice et pause quota C5'),flush=True)
