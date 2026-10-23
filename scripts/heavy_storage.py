"""Répertoires lourds sur volume d'archive ; chemins historiques via jonctions."""
import subprocess
from common import KIT,Path,readj

CONFIG=KIT.parent/'STOCKAGE-LOURD.json'
NAMES={'vault','profile','server-state'}

def storage_root():
    cfg=readj(CONFIG)
    root=Path(cfg['root'])
    if not cfg.get('enabled') or not root.is_absolute() or root.drive.upper()!='B:':
        raise RuntimeError('Stockage lourd sur B requis ; aucun repli silencieux sur E')
    return root.resolve()

def empty_directory(out,name):
    out=Path(out);base=KIT.parent.resolve();run=base/'resultats'
    if name not in NAMES or not out.resolve().is_relative_to(run):
        raise ValueError('Répertoire lourd hors périmètre')
    source=out/name;root=storage_root();dest=root/source.relative_to(base)
    if source.exists() or source.is_junction() or dest.exists():
        raise FileExistsError('Artefact existant : aucun rejeu ni écrasement')
    if not dest.resolve().is_relative_to(root):raise ValueError('Destination hors archive')
    out.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True)
    def quote(p):return "'"+str(p).replace("'","''")+"'"
    subprocess.run(['powershell','-NoProfile','-Command',
        "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path "+quote(source)+" -Target "+quote(dest)+" | Out-Null"],check=True,capture_output=True,text=True)
    if not source.is_junction() or source.resolve()!=dest.resolve():raise RuntimeError('Jonction non vérifiée')
    return source


def is_archive_path(path):
    """N'accepter que les sous-arbres reliés à leur jonction du run."""
    if not CONFIG.exists():return False
    root=storage_root();p=Path(path).resolve()
    if not p.is_relative_to(root/'resultats'):return False
    for candidate in (p,*p.parents):
        if candidate==root:break
        if candidate.name not in NAMES:continue
        source=KIT.parent/candidate.relative_to(root)
        if source.is_junction() and source.resolve()==candidate:
            return True
    return False
