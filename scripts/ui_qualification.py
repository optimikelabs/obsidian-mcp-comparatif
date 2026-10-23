"""Démarre UN Obsidian sans serveur MCP, sous verrou exclusif, puis retouches éditeur."""
import argparse
import os
import shutil
import socket
import subprocess
import uuid
from common import *

RUNTIME=KIT/'runtime'/'ui'
CONFIG=RUNTIME/'config.json'
LOCK=KIT.parents[1]/'VERROU-OBSIDIAN-TEST.txt'
PORT=27346

def cdp(action,task=''):
    guard()
    r=subprocess.run(['node',str(KIT/'scripts'/'ui_cdp.mjs'),str(CONFIG),action,task],capture_output=True,text=True,encoding='utf-8',timeout=25)
    if r.returncode: raise RuntimeError(r.stderr)
    return json.loads(r.stdout)

def launch():
    guard();RUNTIME.mkdir(parents=True,exist_ok=True)
    token=f'Codex implementation-kit | {time.strftime("%Y-%m-%dT%H:%M:%S%z")} | CDP {PORT} | aucun REST/MCP | {uuid.uuid4()}'
    try:
        with LOCK.open('x',encoding='utf-8') as f:f.write(token+'\n')
    except FileExistsError:
        print('VERROU_OCCUPE : aucune instance lancée');return False
    try:
        with socket.socket() as s:s.bind(('127.0.0.1',PORT))
        profile=RUNTIME/'profile';profile.mkdir(exist_ok=True)
        vault=RUNTIME/f'Margelle-qualification-{time.time_ns()}'
        if vault.exists(): raise RuntimeError('Sortie UI existante : ne pas écraser')
        shutil.copytree(KIT/'fixtures'/'Margelle-1.0.6',vault)
        plugins=['quickadd','templater-obsidian','journals','notebook-navigator','frontmatter-date-manager']
        writej(vault/'.obsidian'/'community-plugins.json',plugins)
        writej(profile/'obsidian.json',{'vaults':{'be24060000000001':{'path':str(vault),'ts':int(time.time()*1000),'open':True}},'updateDisabled':True})
        # Ressource distribuée avec l'exécutable ; aucun accès au profil quotidien.
        asar=Path(r'C:\Program Files\Obsidian\resources\obsidian.asar')
        shutil.copyfile(asar,profile/'obsidian-1.13.7.asar')
        cfg={'vault':str(vault),'profile':str(profile),'port':PORT,'P':P,'N':N,'plugins':plugins,'lock_token':token,'asar_sha256':sha(asar.read_bytes())}
        writej(CONFIG,cfg)
        ps="$p=Start-Process -FilePath 'C:/Program Files/Obsidian/Obsidian.exe' -ArgumentList @('--user-data-dir=\""+str(profile)+"\"','--remote-debugging-port="+str(PORT)+"','--remote-debugging-address=127.0.0.1') -WindowStyle Hidden -PassThru; $p.Id"
        r=subprocess.run(['powershell','-NoProfile','-Command',ps],capture_output=True,text=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stderr)
        cfg['pid']=int(r.stdout.strip());writej(CONFIG,cfg)
        end=time.monotonic()+45
        while time.monotonic()<end:
            guard()
            try:
                identity=cdp('identity');writej(RUNTIME/'identity.json',identity)
                active=cdp('activate');writej(RUNTIME/'plugins.json',active)
                assert active['fdm']=='1.6.0';print(json.dumps(identity,ensure_ascii=False));return True
            except (RuntimeError,subprocess.TimeoutExpired,AssertionError) as e:
                (RUNTIME/'last-error.txt').write_text(str(e),encoding='utf-8');time.sleep(.25)
        raise TimeoutError('Instance isolée non prête')
    except BaseException:
        stop();raise

def stop():
    if CONFIG.exists():
        cfg=readj(CONFIG)
        if cfg.get('pid'):
            # PID et ligne de commande doivent correspondre tous deux au profil appartenant au kit.
            profile=cfg['profile'].replace("'","''")
            ps=f"$p=Get-CimInstance Win32_Process -Filter 'ProcessId={cfg['pid']}'; if($p -and $p.CommandLine.Contains('{profile}')){{ Stop-Process -Id {cfg['pid']} -Force }}"
            subprocess.run(['powershell','-NoProfile','-Command',ps],capture_output=True,timeout=20)
        if LOCK.exists() and LOCK.read_text(encoding='utf-8').strip()==cfg['lock_token']:
            LOCK.unlink()

def inject(task):
    cfg=readj(CONFIG);vault=Path(cfg['vault']);b=snapshot(vault)
    result=cdp('inject',task);expected=result.pop('expected').encode('utf-8')
    wait_bytes(vault/result['path'],expected)
    h=snapshot(vault)
    result.update({'before_tree':manifest(b)['tree_sha256'],'after_tree':manifest(h)['tree_sha256'],
                   'expected_sha256':sha(expected),'disk_save_observed':True,'utc':time.time()})
    writej(RUNTIME/f'{task}-injection.json',result)
    return b,h,result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','inject','stop']);p.add_argument('--task',choices=['T5','T6','T7']);a=p.parse_args()
    if a.action=='launch':launch()
    elif a.action=='inject':inject(a.task)
    else:stop()
