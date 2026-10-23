"""Achève uniquement installations, sans recopier les dossiers déjà transférés."""
import os,sys,shutil,hashlib,datetime,subprocess,ctypes
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from ctypes import wintypes
sys.path.insert(0,str(Path(__file__).resolve().parent))
from campaign_runtime import KIT,RUN,readj,writej

def inventory(root):
    paths=[];dirs=[]
    for folder,children,files in os.walk(root):
        for name in children+files:
            p=Path(folder)/name
            assert not p.is_symlink() and not p.is_junction(),p
        dirs.extend((Path(folder)/n).relative_to(root).as_posix() for n in children)
        paths.extend(Path(folder)/n for n in files)
    def entry(p):
        stat=p.stat();h=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        return {'path':p.relative_to(root).as_posix(),'bytes':stat.st_size,'sha256':h.hexdigest(),
                'creation_epoch':stat.st_birthtime,'modified_epoch':stat.st_mtime}
    with ThreadPoolExecutor(max_workers=4) as pool:entries=list(pool.map(entry,paths))
    return sorted(entries,key=lambda r:r['path']),dirs

def signature(rows):return {r['path']:(r['bytes'],r['sha256']) for r in rows}

def created_time(path,epoch):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.restype=wintypes.HANDLE
    kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    kernel.SetFileTime.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.FILETIME),ctypes.c_void_p,ctypes.c_void_p]
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.CreateFileW(str(path),0x100,7,None,3,0,None)
    if handle==wintypes.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    try:
        ticks=int((epoch+11644473600)*10000000);ft=wintypes.FILETIME(ticks&0xffffffff,ticks>>32)
        if not kernel.SetFileTime(handle,ctypes.byref(ft),None,None):raise ctypes.WinError(ctypes.get_last_error())
    finally:kernel.CloseHandle(handle)

def main():
    plan=readj(RUN/'migration-stockage/plan.json');item=plan['items'][-1]
    src=Path(item['source']);dst=Path(item['destination']);receipt_path=RUN/'migration-stockage/manifestes/047.json'
    assert src==KIT.parent/'installations' and src.resolve()==src and not src.is_junction()
    archive=Path(plan['destination_root']).resolve();assert archive.drive.upper()=='B:' and dst==archive/'installations'
    assert not receipt_path.exists()
    assert len(list((RUN/'migration-stockage/manifestes').glob('*.json')))==46
    ps="@(Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('node.exe','python.exe','Obsidian.exe') } | Select-Object ProcessId,CommandLine) | ConvertTo-Json -Compress"
    raw=subprocess.check_output(['powershell','-NoProfile','-Command',ps],text=True,encoding='utf-8').strip();processes=__import__('json').loads(raw) if raw else []
    if isinstance(processes,dict):processes=[processes]
    assert not [p for p in processes if str(src) in (p.get('CommandLine') or '')], 'Installation utilisée'
    print('Inventaire SHA-256 installations, quatre lecteurs bornés',flush=True)
    before,dirs=inventory(src);assert sum(r['bytes'] for r in before)==item['bytes']
    dst.mkdir(parents=True,exist_ok=True)
    existing,_=inventory(dst);expected=signature(before)
    assert all(r['path'] in expected and expected[r['path']]==(r['bytes'],r['sha256']) for r in existing),'Copie partielle divergente'
    done={r['path'] for r in existing};print(f'{len(before)} fichiers ; {len(done)} copies déjà exactes conservées',flush=True)
    for name in dirs:(dst/name).mkdir(parents=True,exist_ok=True)
    for r in before:
        target=dst/r['path']
        if r['path'] not in done:shutil.copy2(src/r['path'],target)
        created_time(target,r['creation_epoch'])
    print('Copie terminée ; vérification source et destination',flush=True)
    after,_=inventory(dst);assert signature(after)==expected
    source_again,_=inventory(src);assert signature(source_again)==expected
    proof={'source':str(src),'destination':str(dst),'relative_path':'installations','copied_verified_sha256':True,'source_removed':False,'junction_verified':False,
           'files':before,'bytes':sum(r['bytes'] for r in before),'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'partial_files_reused':len(done),'previous_transfer_stopped_before_source_removal':True}
    writej(receipt_path,proof)
    # Cible absolue exacte contrôlée de nouveau avant retrait récursif natif.
    assert src.resolve()==KIT.parent.resolve()/'installations' and not src.is_junction() and not src.is_symlink()
    shutil.rmtree(src)
    proof['source_removed']=True;writej(receipt_path,proof)
    def quote(p):return "'"+str(p).replace("'","''")+"'"
    subprocess.run(['powershell','-NoProfile','-Command',"$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path "+quote(src)+" -Target "+quote(dst)+" | Out-Null"],check=True)
    assert src.is_junction() and src.resolve()==dst.resolve()
    linked,_=inventory(src);assert signature(linked)==expected
    proof['junction_verified']=True;writej(receipt_path,proof)
    print(f'Installations transférées et vérifiées : {proof["bytes"]} octets',flush=True)

if __name__=='__main__':main()
