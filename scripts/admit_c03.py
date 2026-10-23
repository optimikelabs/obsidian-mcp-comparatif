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
        path='Admission — schémas C03.md';body='---\nrang: 1\ninconnu: café\n---\nEssai A.\n'
        def call(name,**args):return rpc('tools/call',{'name':name,'arguments':args})
        r=call('obsidian_put_content',filepath=path,content=body);assert not r['result'].get('isError')
        r=call('obsidian_append_content',filepath=path,content='Essai B.\n');assert not r['result'].get('isError')
        r=call('obsidian_get_file_contents',filepath=path);text=json.loads(r['result']['content'][0]['text']);assert text==body+'Essai B.\n'
        adapter={'candidate':'C03','transport':'stdio','mutation_tools':['obsidian_put_content','obsidian_append_content','obsidian_patch_content','obsidian_delete_file'],
                 'preparation_tools':[],'read_tools':['obsidian_get_file_contents'],'read_format':'json_string','path_key':'filepath','status_tools':[],
                 'enabled_tools':[t['name'] for t in cat['result']['tools'] if t['name'] not in ('obsidian_delete_file','obsidian_periodic_notes','obsidian_recent_periodic_notes')],
                 'technical_paths':['.obsidian/workspace.json','.obsidian/plugins/frontmatter-date-manager/data.json']}
        writej(out/'adapter.json',adapter)
        summary={'candidate':'C03','status':'ADMIS','reason':'Nonce et mapping JSON-string vérifiés ; création et append sur note d’admission distincte.','nonceVerified':True,'command':cmd,'mode':'stdio Python vers REST HTTP 5.5.2 ; Obsidian ouvert',
                 'artifact_sha256':'573491093065f0af7546c8a26b884974997e8d91f148cb9d8471d4857c1b6286','catalog_sha256':sha((out/'catalogue.json').read_bytes()),'adapter_sha256':sha((out/'adapter.json').read_bytes()),'utc':memory()['utc']}
        writej(out/'admission.json',summary)
        (out/'fiche-technique.md').write_text('C03 — mcp-obsidian 0.2.3 (MarkusPfundstein)\n\nPython stdio vers REST 5.5.2. obsidian_get_file_contents retourne un texte JSON encodant le fichier entier ; chemin filepath. obsidian_put_content crée ou remplace entièrement ; obsidian_append_content ajoute ; obsidian_patch_content cible heading/block/frontmatter (operation/target_type/target/content). Pas de ifMatch dans le schéma observé, ni statut durable exposé. Relecture complète après mutation ou réponse perdue. Les outils de lecture/recherche de notes sont autorisés ; aucun autre serveur de secours.\n',encoding='utf-8')
        print(json.dumps({'candidate':'C03','nonceVerified':True,'status':'ADMIS','tools':[x['name'] for x in cat['result']['tools']]},ensure_ascii=False))
    except BaseException as e:writej(out/'incident.json',{'error':str(e),'traceback':traceback.format_exc()});raise
    finally:
        if up:up.close()
        if cfg:stop(cfg)
        mon.close()

if __name__=='__main__':main()
