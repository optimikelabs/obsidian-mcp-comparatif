from campaign_runtime import *
from relay import Stdio
import traceback

def main():
    out=RUN/'admissions/C04';gate(out,'before_admission');mon=Monitor(out).start();cfg=None;up=None
    try:
        cfg=prepare(out,[KIT.parent/'installations/C01']);vault=Path(cfg['vault']);key=secrets.token_hex(32)
        writej(vault/'.obsidian/plugins/obsidian-local-rest-api/data.json',{'port':PORTS['secure'],'insecurePort':PORTS['rest'],'enableInsecureServer':True,'enableSecureServer':False,'apiKey':key,'bindingHost':'127.0.0.1'})
        nonce='ADMISSION-C04-'+secrets.token_hex(20);note='Admission — nonce C04.md';(vault/note).write_text(nonce,encoding='utf-8',newline='')
        launch(cfg);prepare_application(cfg);gate(out,'before_candidate_stdio')
        cmd=['node',str(KIT.parent/'installations/C04/node_modules/obsidian-mcp-server/dist/index.js')]
        state=out/'server-state';state.mkdir()
        env=dict(os.environ,OBSIDIAN_API_KEY=key,OBSIDIAN_BASE_URL=f'http://127.0.0.1:{PORTS["rest"]}',MCP_TRANSPORT_TYPE='stdio',MCP_LOG_LEVEL='warning',OBSIDIAN_ENABLE_COMMANDS='false',MCP_LOGS_DIR=str(state/'logs'),MCP_STORAGE_PATH=str(state/'storage'))
        up=Stdio(cmd,str(out),out/'stderr.txt',env=env);ident=0
        def rpc(method,params=None):
            nonlocal ident
            ident+=1;req={'jsonrpc':'2.0','id':ident,'method':method,'params':params or {}};resp=up.rpc(req)
            writej(out/f'rpc-{ident:02}.json',{'request':req,'response':resp});return resp
        rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}});up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        cat=rpc('tools/list');writej(out/'catalogue.json',cat)
        def call(n,**a):return rpc('tools/call',{'name':n,'arguments':a})
        result=call('obsidian_get_note',format='content',target={'type':'path','path':note});writej(out/'nonce-read.json',result);assert nonce in json.dumps(result,ensure_ascii=False)
        path='Admission — schémas C04.md';body='---\nrang: 1\ninconnu: café\n---\nEssai A.\n'
        r=call('obsidian_write_note',target={'type':'path','path':path},content=body,overwrite=False);assert not r.get('error') and not r['result'].get('isError'),r
        result=call('obsidian_get_note',format='content',target={'type':'path','path':path});writej(out/'raw-read.json',result)
        writej(out/'admission-partielle.json',{'candidate':'C04','status':'SCHEMAS_A_QUALIFIER','nonceVerified':True,'command':cmd,'mode':'stdio Node 24 vers REST HTTP 5.5.2 ; Obsidian ouvert'})
        print(json.dumps({'candidate':'C04','nonceVerified':True,'rawRead':result,'tools':[x['name'] for x in cat['result']['tools']]},ensure_ascii=False))
    except BaseException as e:writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc()});raise
    finally:
        if up:up.close()
        if cfg:stop(cfg)
        mon.close()

if __name__=='__main__':main()
