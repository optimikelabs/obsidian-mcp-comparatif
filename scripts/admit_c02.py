from campaign_runtime import *
from relay import Stdio
import traceback

def main():
    out=RUN/'admissions/C02/attempt-02';gate(out,'before_admission');mon=Monitor(out).start();cfg=None;up=None
    try:
        cfg=prepare(out);vault=Path(cfg['vault']);nonce='ADMISSION-C02-'+secrets.token_hex(20);note='Admission — nonce C02.md'
        (vault/note).write_text(nonce,encoding='utf-8',newline='')
        launch(cfg);prepare_application(cfg);stop(cfg)
        gate(out,'before_candidate_stdio')
        cmd=['node',str(KIT.parent/'installations/C02/node_modules/@bitbonsai/mcpvault/dist/server.js'),str(vault)]
        up=Stdio(cmd,str(out),out/'stderr.txt');ident=0
        def rpc(method,params=None):
            nonlocal ident
            ident+=1;req={'jsonrpc':'2.0','id':ident,'method':method,'params':params or {}};resp=up.rpc(req)
            writej(out/f'rpc-{ident:02}.json',{'request':req,'response':resp});return resp
        rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}})
        up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        catalog=rpc('tools/list');writej(out/'catalogue.json',catalog)
        result=rpc('tools/call',{'name':'read_note','arguments':{'path':note}});assert nonce in json.dumps(result,ensure_ascii=False)
        writej(out/'nonce-read.json',result)
        writej(out/'admission-partielle.json',{'candidate':'C02','nonceVerified':True,'status':'SCHEMAS_A_QUALIFIER','command':cmd,'mode':'fichiers sans Obsidian hors préparation/retouches'})
        print(json.dumps({'candidate':'C02','nonceVerified':True,'tools':[x['name'] for x in catalog['result']['tools']],'readResponse':result},ensure_ascii=False))
    except BaseException as e:writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc()});raise
    finally:
        if up:up.close()
        if cfg:stop(cfg)
        mon.close()

if __name__=='__main__':main()
