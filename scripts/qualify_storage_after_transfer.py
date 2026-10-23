"""Attend les seuils puis rejoue uniquement le factice, jamais une cellule."""
import sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from campaign_runtime import *
root=RUN/'migration-stockage';start=time.monotonic();checks=[]
for index in range(13):
    if index:
        print('Attente mémoire : contrôle dans dix minutes',flush=True)
        for _ in range(10):time.sleep(60)
    m=memory();checks.append(m);writej(root/'attente-memoire-qualification.json',{'checks':checks,'elapsed_s':time.monotonic()-start,'max_wait_s':7200})
    print(json.dumps({'memory_check':index,**m}),flush=True)
    if m['stop']:
        writej(root/'qualification-finale-etat.json',{'state':'ARRET_MEMOIRE_SOUS_2GIO','checks':checks,'final_fake_server_replay_executed':False});raise SystemExit(2)
    if m['admitted']:break
else:
    writej(root/'qualification-finale-etat.json',{'state':'ARRET_MEMOIRE_APRES_120_MIN','checks':checks});raise SystemExit(2)
assert readj(RUN/'PAUSE-C5.json')['active']
print('Seuils atteints : rejeu factice seul',flush=True)
with (root/'qualification-finale.stdout.txt').open('w',encoding='utf-8') as out,(root/'qualification-finale.stderr.txt').open('w',encoding='utf-8') as err:
    result=subprocess.run([sys.executable,'-X','utf8',str(KIT/'scripts/test_heavy_storage.py')],cwd=KIT,stdout=out,stderr=err)
writej(root/'qualification-finale-etat.json',{'state':'QUALIFICATION_REUSSIE' if result.returncode==0 else 'QUALIFICATION_ECHOUEE','returncode':result.returncode,'checks':checks,'utc':memory()['utc']})
print('Qualification finale : '+str(result.returncode),flush=True)
raise SystemExit(result.returncode)
