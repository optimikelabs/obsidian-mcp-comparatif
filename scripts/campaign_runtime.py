"""Contrôle local de campagne. Aucun accès au coffre quotidien ni à sa configuration."""
import ctypes
from ctypes import wintypes
import datetime
import os
import secrets
import shutil
import socket
import subprocess
import threading
from common import *

RUN=KIT.parent/'resultats'
LOCK=KIT.parents[1]/'VERROU-OBSIDIAN-TEST.txt'
EXE=Path('C:/Program Files/Obsidian/Obsidian.exe')
PORTS={'cdp':27346,'rest':27341,'secure':27342,'native':27344,'relay':27348}

class Perf(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ('CommitTotal','CommitLimit','CommitPeak','PhysicalTotal','PhysicalAvailable','SystemCache','KernelTotal','KernelPaged','KernelNonpaged','PageSize')]+[(n,wintypes.DWORD) for n in ('HandleCount','ProcessCount','ThreadCount')]

def memory():
    p=Perf();p.cb=ctypes.sizeof(p)
    if not ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(p),p.cb):raise ctypes.WinError()
    margin=(p.CommitLimit-p.CommitTotal)*p.PageSize;ram=p.PhysicalAvailable*p.PageSize
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commitFreeBytes':margin,'availableBytes':ram,
            'admitted':min(margin,ram)>=4*2**30,'stop':min(margin,ram)<2*2**30}

def record(out,event,**kw):
    out.mkdir(parents=True,exist_ok=True)
    with (out/'controller.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'utc':time.time(),'event':event,**kw},ensure_ascii=False)+'\n')

def gate(out,reason):
    m=memory();record(out,'memory_gate',reason=reason,**m)
    if not m['admitted']:raise RuntimeError('ATTENTE_MEMOIRE_4GIO '+json.dumps(m))
    return m

class Monitor:
    def __init__(self,out):self.out=out;self.end=threading.Event();self.stopped=threading.Event();self.thread=None
    def start(self):
        def work():
            while not self.end.is_set():
                m=memory();record(self.out,'memory_1s',**m)
                if m['stop']:
                    self.stopped.set();writej(self.out/'ARRET-MEMOIRE.json',m);return
                self.end.wait(1)
        self.thread=threading.Thread(target=work,daemon=True);self.thread.start();return self
    def check(self):
        if self.stopped.is_set() or memory()['stop']:raise RuntimeError('ARRET_MEMOIRE_SOUS_2GIO')
    def close(self):
        self.end.set()
        if self.thread:self.thread.join(timeout=3)

def command(args,out,name,timeout=120,env=None,cwd=None):
    out.mkdir(parents=True,exist_ok=True)
    with (out/(name+'.stdout.txt')).open('w',encoding='utf-8') as stdout,(out/(name+'.stderr.txt')).open('w',encoding='utf-8') as stderr:
        p=subprocess.run(args,stdout=stdout,stderr=stderr,timeout=timeout,env=env,cwd=cwd)
    record(out,'command',name=name,returncode=p.returncode)
    if p.returncode:raise RuntimeError(f'{name} exit {p.returncode}; voir journaux locaux')
    return (out/(name+'.stdout.txt')).read_text(encoding='utf-8-sig')

def download_release(repo,tag,out):
    out.mkdir(parents=True,exist_ok=True)
    info=json.loads(command(['gh','api',f'repos/{repo}/releases/tags/{tag}'],out,'release-api'))
    writej(out/'release.json',info)
    import urllib.request
    entries=[]
    for asset in info['assets']:
        if asset['name'] not in ('main.js','manifest.json','styles.css'):continue
        raw=urllib.request.urlopen(asset['browser_download_url'],timeout=60).read();digest=sha(raw)
        if asset.get('digest'):assert asset['digest']=='sha256:'+digest
        (out/asset['name']).write_bytes(raw)
        entries.append({'name':asset['name'],'size':len(raw),'sha256':digest,'url':asset['browser_download_url']})
    assert (out/'main.js').is_file() and (out/'manifest.json').is_file()
    writej(out/'artifacts.json',entries);return entries

def cdp(cfg,expression,name):
    # Reprend la méthode qualifiée du run, en validant l'identité à chaque appel.
    script=KIT/'scripts/campaign_cdp.mjs';expr=Path(cfg['out'])/(name+'.expression.js')
    expr.write_text(expression,encoding='utf-8',newline='')
    raw=command(['node',str(script),str(Path(cfg['out'])/'obsidian.json'),str(expr)],Path(cfg['out']),name,timeout=25)
    return json.loads(raw)['result']

def prepare(out,plugin_sources=()):
    assert out.resolve().is_relative_to(KIT.parent.resolve())
    out.mkdir(parents=True,exist_ok=True);vault=out/'vault';profile=out/'profile'
    if vault.exists():raise RuntimeError('Bac existant : ne pas réutiliser')
    shutil.copytree(KIT/'fixtures/Margelle-1.0.6',vault);profile.mkdir()
    plugins=readj(vault/'.obsidian/community-plugins.json')
    plugins=[p for p in plugins if p!='elysia-hub']
    # Les identifiants exacts livrés sont contrôlés, sans hypothèse sur le nom Hub.
    for p in list(plugins):
        manifest_file=vault/'.obsidian/plugins'/p/'manifest.json'
        if manifest_file.exists():
            pm=readj(manifest_file)
            if 'hub' in (pm.get('id','')+' '+pm.get('name','')).lower():plugins.remove(p)
    for source in plugin_sources:
        ident=readj(source/'manifest.json')['id'];dest=vault/'.obsidian/plugins'/ident
        if dest.exists():raise RuntimeError('Plugin déjà présent, ne pas écraser')
        dest.mkdir(parents=True)
        for name in ('main.js','manifest.json','styles.css'):
            if (source/name).exists():shutil.copyfile(source/name,dest/name)
        plugins.append(ident)
    writej(vault/'.obsidian/community-plugins.json',plugins)
    writej(profile/'obsidian.json',{'vaults':{'be24062300000001':{'path':str(vault),'ts':int(time.time()*1000),'open':True}},'updateDisabled':True})
    asar=EXE.parent/'resources/obsidian.asar';shutil.copyfile(asar,profile/'obsidian-1.13.7.asar')
    cfg={'out':str(out),'vault':str(vault),'profile':str(profile),'port':PORTS['cdp'],'ports':PORTS,'plugins':plugins,'pid':None,
         'asar_sha256':sha(asar.read_bytes())}
    writej(out/'obsidian.json',cfg);return cfg

def launch(cfg):
    out=Path(cfg['out']);gate(out,'before_obsidian')
    token='Campagne comparatif | '+memory()['utc']+' | CDP 27346 REST 27341 natif 27344 | '+secrets.token_hex(12)
    with LOCK.open('x',encoding='utf-8') as f:f.write(token+'\n')
    cfg['lock_token']=token;writej(out/'obsidian.json',cfg)
    try:
        for port in PORTS.values():
            with socket.socket() as s:s.bind(('127.0.0.1',port))
        args=['--user-data-dir="'+cfg['profile']+'"','--remote-debugging-port='+str(PORTS['cdp']),'--remote-debugging-address=127.0.0.1']
        ps="$p=Start-Process -FilePath '"+str(EXE).replace("'","''")+"' -ArgumentList @("+','.join("'"+a.replace("'","''")+"'" for a in args)+") -WindowStyle Hidden -PassThru; $p.Id"
        cfg['pid']=int(command(['powershell','-NoProfile','-Command',ps],out,'launch',timeout=30).strip());writej(out/'obsidian.json',cfg)
        deadline=time.monotonic()+90;last=''
        while time.monotonic()<deadline:
            if memory()['stop']:raise RuntimeError('ARRET_MEMOIRE_SOUS_2GIO')
            try:
                result=cdp(cfg,'(async()=>{await new Promise(r=>app.workspace.onLayoutReady(r));if(!app.plugins.isEnabled())await app.plugins.setEnable(true);await app.plugins.loadManifests();for(const id of '+json.dumps(cfg['plugins'])+'){if(!app.plugins.enabledPlugins.has(id))await app.plugins.enablePluginAndSave(id);if(!app.plugins.plugins[id])await app.plugins.loadPlugin(id);}document.querySelectorAll(".modal-close-button").forEach(b=>b.click());return {vault:app.vault.adapter.basePath,plugins:Object.fromEntries(Object.entries(app.plugins.plugins).map(([id,p])=>[id,p.manifest.version]))};})()','activate')
                assert result['plugins']['frontmatter-date-manager']=='1.6.0'
                assert all(x in result['plugins'] for x in cfg['plugins'])
                writej(out/'identity.json',result);record(out,'obsidian_started',pid=cfg['pid']);return
            except (RuntimeError,AssertionError,ValueError) as e:last=str(e);time.sleep(.5)
        raise TimeoutError('Instance isolée non prête : '+last)
    except BaseException:
        stop(cfg);raise

def stop(cfg):
    out=Path(cfg['out']);pid=cfg.get('pid');profile=cfg['profile'].replace("'","''")
    if pid:
        ps=f"$p=Get-CimInstance Win32_Process -Filter 'ProcessId={pid}'; if($p -and $p.CommandLine.Contains('{profile}')){{Stop-Process -Id {pid} -Force}}; Start-Sleep -Milliseconds 500; @(Get-CimInstance Win32_Process -Filter \"Name='Obsidian.exe'\" | Where-Object {{$_.CommandLine -and $_.CommandLine.Contains('{profile}')}}).Count"
        remaining=int(command(['powershell','-NoProfile','-Command',ps],out,'stop',timeout=25).strip())
        if remaining:raise RuntimeError('Instance de campagne encore active ; verrou conservé')
    if LOCK.exists() and LOCK.read_text(encoding='utf-8').strip()==cfg.get('lock_token'):LOCK.unlink()
    record(out,'owned_instance_stopped',pid=pid,lock_present=LOCK.exists())

def prepare_application(cfg):
    out=Path(cfg['out']);vault=Path(cfg['vault']);p=vault/P;before=p.read_bytes()
    result=cdp(cfg,'(async()=>{const f=app.vault.getAbstractFileByPath('+json.dumps(P)+');const leaf=app.workspace.getLeaf(false);await leaf.openFile(f,{state:{mode:"source"}});app.workspace.setActiveLeaf(leaf,{focus:true});if(app.workspace.getActiveFile()?.path!==f.path)throw Error("Fiche non active");const result=await app.commands.executeCommandById("editor:save-file");return {command:"editor:save-file",result,note:f.path,active:app.workspace.getActiveFile()?.path};})()','native-save')
    deadline=time.monotonic()+60;fallback=False;last=None;since=time.monotonic()
    while time.monotonic()<deadline:
        if memory()['stop']:raise RuntimeError('ARRET_MEMOIRE_SOUS_2GIO')
        raw=p.read_bytes();props,body=split(raw)
        if not all(k in props for k in ('création','modification')) and not fallback and time.monotonic()-since>=5:
            fallback=True
            cdp(cfg,'(async()=>{if(app.workspace.getActiveFile()?.path!=='+json.dumps(P)+')throw Error("Mauvaise fiche active");const id="frontmatter-date-manager:update-timestamps-current-file";return {id,result:await app.commands.executeCommandById(id),active:app.workspace.getActiveFile()?.path};})()','fdm-fallback')
        if raw!=last:last=raw;since=time.monotonic()
        if time.monotonic()-since>=5 and all(k in props for k in ('création','modification')) and b'\r\n' not in raw:
            assert split(before)[1]==body
            proof={'command':result,'fdmFallback':fallback,'datesPresent':True,'beforeSha256':sha(before),'afterSha256':sha(raw),'bodyPreserved':True,'CRLF':0}
            writej(out/'preparation-applicative.json',proof);return proof
        time.sleep(.1)
    raise TimeoutError('Préparation applicative non stable/LF/datée en 60 s')

if __name__=='__main__':print(json.dumps(memory()))
