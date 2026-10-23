from campaign_runtime import *
from relay import Stdio
import traceback

def main():
    out=RUN/'admissions/C03';gate(out,'before_admission');mon=Monitor(out).start();cfg=None;up=None
    try:
        cfg=prepare(out,[KIT.parent/'installations/C01']);vault=Path(cfg['vault']);key=secrets.token_hex(32)
        writej(vault/'.obsidian/plugins/obsidian-local-rest-api/data.json',{'port':PORTS['secure'],'insecurePort':PORTS['rest'],'enableInsecureServer':True,'enableSecureServer':False,'apiKey':key,'bindingHost':'127.0.0.1'})
        nonce='ADMISSION-C03-'+secrets.token_hex(20);note='Admission — nonce C03.md';(vault/note).write_text(nonce,encoding='utf-8',newline='')
        launch(cfg);prepare_application(cfg);gate(out,'before_candidate_stdio')
        py=KIT.parent/'installations/C03/venv/Scripts/python.exe';cmd=[str(py),'-X','utf8','-c','import mcp_obsidian;mcp_obsidian.main()']
        env=dict(os.environ,OBSIDIAN_API_KEY=key,OBSIDIAN_HOST='127.0.0.1',OBSIDIAN_PORT=str(PORTS['rest']),OBSIDIAN_PROTOCOL='http',PYTHONUTF8='1')
        up=Stdio(cmd,str(out),out/'stderr.txt',env=env);ident=0
        def rpc(method,params=None):
            nonlocal ident
            ident+=1;req={'jsonrpc':'2.0','id':ident,'method':method,'params':params or {}};resp=up.rpc(req)
            writej(out/f'rpc-{ident:02}.json',{'request':req,'response':resp});return resp
        rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}})
        up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        cat=rpc('tools/list');writej(out/'catalogue.json',cat)
        result=rpc('tools/call',{'name':'obsidian_get_file_contents','arguments':{'filepath':note}});assert nonce in json.dumps(result,ensure_ascii=False)
        writej(out/'nonce-read.json',result)
        writej(out/'admission-partielle.json',{'candidate':'C03','status':'SCHEMAS_A_QUALIFIER','nonceVerified':True,'command':cmd,'mode':'stdio Python vers REST HTTP 5.5.2 ; Obsidian ouvert'})
        print(json.dumps({'candidate':'C03','nonceVerified':True,'read':result,'tools':[x['name'] for x in cat['result']['tools']]},ensure_ascii=False))
    except BaseException as e:writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc()});raise
    finally:
        if up:up.close()
        if cfg:stop(cfg)
        mon.close()

if __name__=='__main__':main()
