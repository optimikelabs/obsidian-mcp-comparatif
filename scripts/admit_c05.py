from campaign_runtime import *
from relay import HTTP
import traceback

def main():
    out=RUN/'admissions/C05';gate(out,'before_admission');mon=Monitor(out).start();cfg=None
    try:
        source=KIT.parent/'installations/C05';cfg=prepare(out,[source]);vault=Path(cfg['vault']);key=secrets.token_hex(32);pid=readj(source/'manifest.json')['id']
        writej(vault/'.obsidian/plugins'/pid/'data.json',{'httpEnabled':True,'httpPort':PORTS['native'],'httpsEnabled':False,'httpsPort':27345,'apiKey':key,'bindMode':'loopback','hasShownBindMigrationNotice':True,'readOnlyMode':False,'enableWebFetch':False,'dangerouslyDisableAuth':False,'autoDetectPortConflicts':False})
        nonce='ADMISSION-C05-'+secrets.token_hex(20);note='Admission — nonce C05.md';(vault/note).write_text(nonce,encoding='utf-8',newline='')
        launch(cfg);prepare_application(cfg)
        up=HTTP(f'http://127.0.0.1:{PORTS["native"]}/mcp',{'Authorization':'Bearer '+key});ident=0
        def rpc(method,params=None):
            nonlocal ident
            ident+=1;req={'jsonrpc':'2.0','id':ident,'method':method,'params':params or {}};resp=up.rpc(req)
            writej(out/f'rpc-{ident:02}.json',{'request':req,'response':resp});return resp
        rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}});up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        cat=rpc('tools/list');writej(out/'catalogue.json',cat)
        tool=next(x for x in cat['result']['tools'] if x['name']=='vault');props=tool['inputSchema']['properties']
        op=next(x for x in ('operation','action') if x in props);args={op:'read','path':note}
        r=rpc('tools/call',{'name':'vault','arguments':args});writej(out/'nonce-read.json',r)
        writej(out/'admission-partielle.json',{'candidate':'C05','status':'SCHEMAS_A_QUALIFIER','nonceVerified':nonce in json.dumps(r,ensure_ascii=False),'operation_key':op,'mode':'Plugin Obsidian HTTP natif /mcp'})
        print(json.dumps({'candidate':'C05','nonceVerified':nonce in json.dumps(r,ensure_ascii=False),'read':r,'vaultSchema':tool['inputSchema'],'tools':[t['name'] for t in cat['result']['tools']]},ensure_ascii=False))
    except BaseException as e:writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc()});raise
    finally:
        if cfg:stop(cfg)
        mon.close()

if __name__=='__main__':main()
