"""Instances éphémères des modes admis ; aucune installation quotidienne."""
from campaign_runtime import *
from relay import Stdio,HTTP,LegacySSE
from fdm_observer import install

class Candidate:
    def __init__(self,cid,out,task):self.cid=cid;self.out=out;self.task=task;self.cfg=None;self.up=None;self.backend=False;self.open=False
    def start(self):
        cid=self.cid;out=self.out;base=KIT.parent/'installations';sources=[]
        if cid in ('C01','C03','C04','C07','C09'):sources.append(base/'C01')
        if cid in ('C05','C10'):sources.append(base/cid)
        if cid=='C07':sources.append(base/'C07/bridges/optimike-bridge-bundle-v3.13.0/bridges/obsidian-atomic-write-bridge')
        cfg=self.cfg=prepare(out,sources);v=Path(cfg['vault']);key=secrets.token_hex(32)
        if cid in ('C01','C03','C04','C07','C09'):
            writej(v/'.obsidian/plugins/obsidian-local-rest-api/data.json',{'port':27342,'insecurePort':27341,'enableInsecureServer':True,'enableSecureServer':False,'apiKey':key,'bindingHost':'127.0.0.1'})
        if cid=='C07':writej(v/'.obsidian/plugins/obsidian-atomic-write-bridge/data.json',{'allowWrites':True,'allowCanvasWrites':False,'allowNativeMoves':False,'allowNoteCreates':True})
        if cid=='C05':writej(v/'.obsidian/plugins/semantic-vault-mcp/data.json',{'httpEnabled':True,'httpPort':27344,'httpsEnabled':False,'httpsPort':27345,'apiKey':key,'bindMode':'loopback','hasShownBindMigrationNotice':True,'readOnlyMode':False,'enableWebFetch':False,'dangerouslyDisableAuth':False,'autoDetectPortConflicts':False})
        if cid=='C10':
            ident=readj(base/cid/'manifest.json')['id'];claude=out/'claude-config';claude.mkdir()
            cfg['process_env']={'CLAUDE_CONFIG_DIR':str(claude)}
            writej(v/'.obsidian/plugins'/ident/'data.json',{'mcpHttpPort':27344,'enableWebSocketServer':False,'enableHttpServer':True,'enableEmbeddedTerminal':False,'autoCloseTerminalOnClaudeExit':True,'startupCommand':'claude'})
        writej(out/'obsidian.json',cfg);launch(cfg);self.open=True;install(cfg);prepare_application(cfg)
        if cid in ('C02','C08') and self.task not in ('T5','T6','T7','T7b'):
            stop(cfg);self.open=False
        gate(out,'before_candidate');env=dict(os.environ);cmd=None;cwd=str(out)
        if cid=='C01':self.up=HTTP('http://127.0.0.1:27341/mcp/',{'Authorization':'Bearer '+key})
        elif cid=='C05':self.up=HTTP('http://127.0.0.1:27344/mcp',{'Authorization':'Bearer '+key})
        elif cid=='C10':self.up=LegacySSE('http://127.0.0.1:27344/sse')
        elif cid=='C02':cmd=['node',str(base/'C02/node_modules/@bitbonsai/mcpvault/dist/server.js'),str(v)]
        elif cid=='C03':
            cmd=[str(base/'C03/venv/Scripts/python.exe'),'-X','utf8','-c','import mcp_obsidian;mcp_obsidian.main()']
            env.update(OBSIDIAN_API_KEY=key,OBSIDIAN_HOST='127.0.0.1',OBSIDIAN_PORT='27341',OBSIDIAN_PROTOCOL='http',PYTHONUTF8='1')
        elif cid=='C04':
            cmd=['node',str(base/'C04/node_modules/obsidian-mcp-server/dist/index.js')]
            state=out/'server-state';state.mkdir()
            env.update(OBSIDIAN_API_KEY=key,OBSIDIAN_BASE_URL='http://127.0.0.1:27341',MCP_TRANSPORT_TYPE='stdio',MCP_LOG_LEVEL='warning',OBSIDIAN_ENABLE_COMMANDS='false',MCP_LOGS_DIR=str(state/'logs'),MCP_STORAGE_PATH=str(state/'storage'))
        elif cid=='C07':
            private=readj(RUN/'admissions/C07/server-private.json');old=str(RUN/'admissions/C07');state=out/'server-state'
            for name in ('tmp','localappdata','home'):(state/name).mkdir(parents=True)
            for k,value in private['env'].items():env[k]=value.replace(old,str(out))
            env['OBSIDIAN_API_KEY']=key;env['OBSIDIAN_VAULT']=str(v)
            cmd=private['command'];cwd=str(base/'C07/source');self.backend=True
        elif cid=='C08':cmd=['node',str(base/'C08/node_modules/obsidian-mcp/dist/main.js'),'serve','--vault','test='+str(v)]
        elif cid=='C09':
            cmd=['node',str(base/'C09/node_modules/@huangyihe/obsidian-mcp/build/index.js')]
            env.update(OBSIDIAN_VAULT_PATH=str(v),OBSIDIAN_API_TOKEN=key,OBSIDIAN_API_PORT='27341',OBSIDIAN_API_HOST='127.0.0.1')
        else:raise ValueError('Candidat non admis')
        if cmd:self.up=Stdio(cmd,cwd,out/'upstream.stderr.txt',env=env)
        return self
    def close(self):
        if self.up:self.up.close()
        if self.backend:
            source=str(KIT.parent/'installations/C07/source').replace("'","''")
            ps=f"$c=Get-NetTCPConnection -LocalPort 27349 -State Listen -ErrorAction SilentlyContinue;foreach($owned in @($c.OwningProcess|Select-Object -Unique)){{if($owned){{$p=Get-CimInstance Win32_Process -Filter \"ProcessId=$owned\";if($p.CommandLine -and $p.CommandLine.Contains('{source}')){{Stop-Process -Id $owned -Force}}else{{throw 'Backend non identifié; aucun arrêt'}}}}}}"
            command(['powershell','-NoProfile','-Command',ps],self.out,'backend-stop',timeout=25)
        if self.cfg and self.open:stop(self.cfg);self.open=False
