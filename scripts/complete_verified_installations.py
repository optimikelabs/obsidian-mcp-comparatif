"""Achève le retrait d'une source déjà entièrement copiée et vérifiée."""
import sys,os,stat,shutil,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from campaign_runtime import KIT,RUN,readj,writej
from finish_installations_migration import inventory,signature
p=RUN/'migration-stockage/manifestes/047.json';proof=readj(p)
assert proof['copied_verified_sha256'] and not proof['source_removed'] and not proof['junction_verified']
src=Path(proof['source']);dst=Path(proof['destination'])
assert src.resolve()==KIT.parent.resolve()/'installations' and not src.is_junction()
plan=readj(RUN/'migration-stockage/plan.json');assert dst.resolve()==Path(plan['destination_root']).resolve()/'installations'
assert dst.exists() and sum(r['bytes'] for r in proof['files'])==plan['items'][-1]['bytes']
# Le reçu a été écrit après comparaison intégrale des SHA-256 source/destination.
# L'échec ne concernait que le retrait local d'un pack Git en lecture seule.
proof['source_removal_incident']='WinError 5 sur pack Git en lecture seule ; copie complète déjà vérifiée, aucune recopie'
writej(p,proof)
def writable_retry(fn,path,exc):
    target=Path(path)
    if not isinstance(exc,PermissionError) or not target.resolve().is_relative_to(src) or target.is_symlink() or target.is_junction():raise exc
    os.chmod(path,stat.S_IWRITE);fn(path)
shutil.rmtree(src,onexc=writable_retry)
proof['source_removed']=True;writej(p,proof)
def quote(v):return "'"+str(v).replace("'","''")+"'"
subprocess.run(['powershell','-NoProfile','-Command',"$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path "+quote(src)+" -Target "+quote(dst)+" | Out-Null"],check=True)
assert src.is_junction() and src.resolve()==dst.resolve()
print('Jonction installations créée ; dernière vérification SHA-256',flush=True)
after,_=inventory(src);assert signature(after)==signature(proof['files'])
proof['junction_verified']=True;writej(p,proof)
print('Installations intégralement transférées et vérifiées',flush=True)
