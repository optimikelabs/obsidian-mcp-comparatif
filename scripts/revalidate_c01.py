"""Revalidation C01 sans Hub, avant toute mesure ; conserve les essais initiaux."""
from campaign_runtime import *
from relay import HTTP

def main():
    root=RUN/'admissions/C01';out=root/'revalidation-sans-hub';gate(out,'before_revalidation')
    cfg=prepare(out,[KIT.parent/'installations/C01']);mon=Monitor(out).start()
    try:
        vault=Path(cfg['vault']);key=secrets.token_hex(32)
        writej(vault/'.obsidian/plugins/obsidian-local-rest-api/data.json',{'port':PORTS['secure'],'insecurePort':PORTS['rest'],'enableInsecureServer':True,'enableSecureServer':False,'apiKey':key,'bindingHost':'127.0.0.1'})
        nonce='ADMISSION-C01-REVALIDATION-'+secrets.token_hex(20);note='Admission — nonce C01.md';(vault/note).write_text(nonce,encoding='utf-8',newline='')
        launch(cfg);prepare_application(cfg)
        up=HTTP(f'http://127.0.0.1:{PORTS["rest"]}/mcp/',{'Authorization':'Bearer '+key})
        up.rpc({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}}});up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        r=up.rpc({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'vault_read','arguments':{'path':note}}});assert nonce in json.dumps(r,ensure_ascii=False)
        writej(out/'nonce-read.json',r);assert 'elysia-os' not in readj(out/'identity.json')['plugins']
        a=readj(root/'admission.json');a.update(status='ADMIS',reason='Nonce et schémas acquis ; revalidation en configuration commune sans Hub réussie avant mesure.',
            configuration=cfg['plugins'],runtime_admission=str(out),utc=memory()['utc'])
        writej(root/'admission.json',a)
        shutil.copyfile(out/'preparation-applicative.json',root/'preparation-applicative.json')
        print(json.dumps({'candidate':'C01','status':'ADMIS','hub_disabled':True}))
    finally:stop(cfg);mon.close()

if __name__=='__main__':main()
