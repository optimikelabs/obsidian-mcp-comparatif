"""Admission C01 sur un bac distinct ; nonce, catalogue et schémas, aucun score."""
import traceback
from campaign_runtime import *
from relay import HTTP

def main():
    out=RUN/'admissions/C01';out.mkdir(parents=True,exist_ok=True)
    gate(out,'before_admission');monitor=Monitor(out).start();cfg=None
    try:
        source=KIT.parent/'installations/C01'
        artifacts=download_release('coddingtonbear/obsidian-local-rest-api','5.5.2',source)
        cfg=prepare(out,[source]);vault=Path(cfg['vault']);key=secrets.token_hex(32)
        writej(vault/'.obsidian/plugins/obsidian-local-rest-api/data.json',{'port':PORTS['secure'],'insecurePort':PORTS['rest'],'enableInsecureServer':True,'enableSecureServer':False,'apiKey':key,'bindingHost':'127.0.0.1'})
        nonce='ADMISSION-C01-'+secrets.token_hex(20);note='Admission — nonce C01.md';(vault/note).write_text(nonce,encoding='utf-8',newline='')
        launch(cfg);monitor.check();prepare_application(cfg)
        up=HTTP(f'http://127.0.0.1:{PORTS["rest"]}/mcp/',{'Authorization':'Bearer '+key})
        req={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}}}
        init=up.rpc(req);writej(out/'initialize.json',init)
        up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        catalog=up.rpc({'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}});writej(out/'catalogue.json',catalog)
        tools=catalog['result']['tools'];read=next(x for x in tools if x['name']=='vault_read')
        writej(out/'read-schema.json',read)
        result=up.rpc({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'vault_read','arguments':{'path':note}}})
        writej(out/'nonce-read.json',result)
        assert nonce in json.dumps(result,ensure_ascii=False),'Nonce non lu par candidat'
        writej(out/'admission-partielle.json',{'candidate':'C01','nonceVerified':True,'catalogueTools':len(tools),'artifacts':artifacts,
              'isolation':{'vault':cfg['vault'],'profile':cfg['profile'],'pid':cfg['pid'],'port':PORTS['rest']},'status':'SCHEMAS_A_QUALIFIER'})
        print(json.dumps({'candidate':'C01','nonceVerified':True,'tools':len(tools),'names':[x['name'] for x in tools]},ensure_ascii=False))
    except BaseException as e:
        writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc(),'memory':memory()});raise
    finally:
        if cfg:stop(cfg)
        monitor.close()

if __name__=='__main__':main()
