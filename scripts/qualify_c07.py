from campaign_runtime import *
from relay import Stdio
import traceback

def main():
    out=RUN/'admissions/C07';cfg=readj(out/'obsidian.json');gate(out,'before_schema_qualification');mon=Monitor(out).start();up=None
    source=KIT.parent/'installations/C07/source'
    try:
        note='Admission — schémas C07.md';p=Path(cfg['vault'])/note
        if p.exists():raise RuntimeError('Note de qualification déjà présente : conserver son état et reprendre depuis les reçus, sans réinitialiser ses dates')
        p.write_text('---\nrang: 1\ninconnu: café\n---\nEssai A.\n',encoding='utf-8',newline='')
        launch(cfg);prepare_application(cfg,note,'preparation-admission');gate(out,'before_candidate_stdio')
        private=readj(out/'server-private.json');up=Stdio(private['command'],str(source),out/'qualification.stderr.txt',env=dict(os.environ,**private['env']));i=0
        def rpc(method,params=None):
            nonlocal i
            i+=1;req={'jsonrpc':'2.0','id':i,'method':method,'params':params or {}};r=up.rpc(req);writej(out/f'qualification-rpc-{i:02}.json',{'request':req,'response':r});return r
        rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}});up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        def call(n,**a):
            r=rpc('tools/call',{'name':n,'arguments':a});assert not r.get('error') and not r['result'].get('isError'),r
            return json.loads(r['result']['content'][0]['text'])
        call('obsidian_read_note',filePath=note)
        key='qualification-admission-c07';plan=call('obsidian_text_patch_plan',path=note,operations=[{'op':'replace_literal','search':'Essai A.','replacement':'Essai B.','occurrence':'unique'}],idempotencyKey=key)
        writej(out/'plan-response.json',plan)
        ref=plan['planRef'];applied=call('obsidian_text_patch_apply',planRef=ref,idempotencyKey=key);writej(out/'apply-response.json',applied)
        print(json.dumps({'apply_keys':list(applied),'state':applied.get('state'),'postflight':applied.get('postflight')}),flush=True)
        deadline=time.monotonic()+120;status=applied
        while status.get('state') not in ('committed','verified') and time.monotonic()<deadline:
            mon.check();time.sleep(1);status=call('obsidian_text_patch_status',planRef=ref)
        writej(out/'status-response.json',status);assert status.get('state') in ('committed','verified'),status
        text=call('obsidian_read_note',filePath=note)['content'];assert text==p.read_text(encoding='utf-8') and 'Essai B.' in text and 'Essai A.' not in text
        writej(out/'qualification-summary.json',{'success':True,'planKeys':list(plan),'applyState':applied.get('state'),'finalState':status.get('state'),'statusKeys':list(status),'read_content_key':'content'})
        print(json.dumps({'candidate':'C07','qualification':True,'finalState':status['state']}))
    except BaseException as e:writej(out/'qualification-incident.json',{'error':str(e),'traceback':traceback.format_exc()});raise
    finally:
        if up:up.close()
        text=str(source).replace("'","''")
        ps=f"$conn=Get-NetTCPConnection -LocalPort 27349 -State Listen -ErrorAction SilentlyContinue;foreach($pidOwned in @($conn.OwningProcess | Select-Object -Unique)){{if($pidOwned){{$p=Get-CimInstance Win32_Process -Filter \"ProcessId=$pidOwned\";if($p.CommandLine -and $p.CommandLine.Contains('{text}')){{Stop-Process -Id $pidOwned -Force}}else{{throw 'Unexpected backend owner'}}}}}}"
        try:command(['powershell','-NoProfile','-Command',ps],out,'qualification-backend-stop',timeout=25)
        finally:stop(cfg);mon.close()

if __name__=='__main__':main()
