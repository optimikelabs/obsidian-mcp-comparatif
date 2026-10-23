from campaign_runtime import *
from relay import Stdio
import traceback

def main():
    out=RUN/'admissions/C07';gate(out,'before_admission');mon=Monitor(out).start();cfg=None;up=None
    source=KIT.parent/'installations/C07/source';backend_port=27349
    try:
        bundle=KIT.parent/'installations/C07/bridges/optimike-bridge-bundle-v3.13.0'
        bm=readj(KIT.parent/'installations/C07/optimike-bridge-bundle-v3.13.0.manifest.json')
        for bridge in bm['bridges']:
            for f in bridge['files']:assert sha((bundle/f['path']).read_bytes())==f['sha256']
        atomic=bundle/'bridges/obsidian-atomic-write-bridge';assert readj(atomic/'manifest.json')['version']=='0.8.1'
        cfg=prepare(out,[KIT.parent/'installations/C01',atomic]);vault=Path(cfg['vault']);key=secrets.token_hex(32)
        writej(vault/'.obsidian/plugins/obsidian-local-rest-api/data.json',{'port':PORTS['secure'],'insecurePort':PORTS['rest'],'enableInsecureServer':True,'enableSecureServer':False,'apiKey':key,'bindingHost':'127.0.0.1'})
        writej(vault/'.obsidian/plugins/obsidian-atomic-write-bridge/data.json',{'allowWrites':True,'allowCanvasWrites':False,'allowNativeMoves':False,'allowNoteCreates':True})
        nonce='ADMISSION-C07-'+secrets.token_hex(20);note='Admission — nonce C07.md';(vault/note).write_text(nonce,encoding='utf-8',newline='')
        launch(cfg);prepare_application(cfg);gate(out,'before_candidate_stdio')
        with socket.socket() as s:s.bind(('127.0.0.1',backend_port))
        state=out/'server-state';state.mkdir()
        for name in ('tmp','localappdata','home'): (state/name).mkdir()
        env=dict(os.environ,OBSIDIAN_VAULT=str(vault),OBSIDIAN_RUNTIME_MODE='live',OBSIDIAN_BASE_URL=f'http://127.0.0.1:{PORTS["rest"]}',OBSIDIAN_API_KEY=key,
                 MCP_TRANSPORT_TYPE='stdio',MCP_TOOL_PROFILE='operational',MCP_WRITE_MODE='full',MCP_LOG_LEVEL='warning',MCP_HTTP_HOST='127.0.0.1',MCP_HTTP_PORT=str(backend_port),
                 OBSIDIAN_SHARED_CACHE_DB_PATH=str(state/'shared-cache.sqlite'),MCP_OBSIDIAN_NOTE_REPLACE_JOURNAL_PATH=str(state/'note-replace.sqlite'),MCP_OBSIDIAN_BASE_FORMULA_JOURNAL_PATH=str(state/'base-formula.sqlite'),MCP_OBSIDIAN_CANVAS_JOURNAL_PATH=str(state/'canvas.sqlite'),MCP_EXTERNAL_MOVE_JOURNAL_PATH=str(state/'external-moves.sqlite'),
                 LOCALAPPDATA=str(state/'localappdata'),TEMP=str(state/'tmp'),TMP=str(state/'tmp'),HOME=str(state/'home'),USERPROFILE=str(state/'home'),OPERON_MUTATIONS_ENABLED='false',SEMANTIC_SEARCH_PREWARM='false',ENABLE_QUERY_EMBEDDING='false',OBSIDIAN_STARTUP_BLOCKING='true')
        # Config privée locale : clé uniquement dans le bac autorisé, jamais projetée.
        writej(out/'server-private.json',{'env':{k:v for k,v in env.items() if k not in os.environ or os.environ[k]!=v},'command':['node',str(source/'dist/stdio-proxy.js')]})
        up=Stdio(['node',str(source/'dist/stdio-proxy.js')],str(source),out/'stderr.txt',env=env);ident=0
        def rpc(method,params=None):
            nonlocal ident
            ident+=1;req={'jsonrpc':'2.0','id':ident,'method':method,'params':params or {}};resp=up.rpc(req)
            writej(out/f'rpc-{ident:02}.json',{'request':req,'response':resp});return resp
        rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}});up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        cat=rpc('tools/list');writej(out/'catalogue.json',cat)
        r=rpc('tools/call',{'name':'obsidian_read_note','arguments':{'filePath':note}});writej(out/'nonce-read.json',r);assert nonce in json.dumps(r,ensure_ascii=False)
        writej(out/'admission-partielle.json',{'candidate':'C07','status':'SCHEMAS_A_QUALIFIER','nonceVerified':True,'source_commit':'8696687e1a449f5f74550331ac902b0b358b4ccf','mode':'Proxy stdio operational / backend HTTP full propre au run, REST 5.5.2 + Atomic 0.8.1','backend_port':backend_port})
        print(json.dumps({'candidate':'C07','nonceVerified':True,'read':r,'tools':[t['name'] for t in cat['result']['tools']]},ensure_ascii=False))
    except BaseException as e:writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc()});raise
    finally:
        if up:up.close()
        # Le backend détaché du proxy appartient à CETTE source et à CE port.
        text=str(source).replace("'","''")
        ps=f"$conn=Get-NetTCPConnection -LocalPort {backend_port} -State Listen -ErrorAction SilentlyContinue; foreach($pidOwned in @($conn.OwningProcess | Select-Object -Unique)){{if($pidOwned){{$p=Get-CimInstance Win32_Process -Filter \"ProcessId=$pidOwned\";if($p.CommandLine -and $p.CommandLine.Contains('{text}')){{Stop-Process -Id $pidOwned -Force}}else{{throw 'Backend port owner is not campaign source; no process stopped'}}}}}}"
        try:command(['powershell','-NoProfile','-Command',ps],out,'backend-stop',timeout=25)
        finally:
            if cfg:stop(cfg)
            mon.close()

if __name__=='__main__':main()
