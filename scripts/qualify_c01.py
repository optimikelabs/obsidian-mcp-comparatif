"""Qualifie le mapping C01 sur notes d'admission distinctes de P/N."""
from campaign_runtime import *
from relay import HTTP

def main():
    out=RUN/'admissions/C01';cfg=readj(out/'obsidian.json');mon=Monitor(out).start()
    gate(out,'before_schema_qualification')
    try:
        launch(cfg);prepare_application(cfg)
        key=readj(Path(cfg['vault'])/'.obsidian/plugins/obsidian-local-rest-api/data.json')['apiKey']
        up=HTTP(f'http://127.0.0.1:{PORTS["rest"]}/mcp/',{'Authorization':'Bearer '+key});ident=0
        def rpc(method,params=None):
            nonlocal ident
            ident+=1;req={'jsonrpc':'2.0','id':ident,'method':method,'params':params or {}};resp=up.rpc(req)
            writej(out/f'qualification-rpc-{ident:02}.json',{'request':req,'response':resp});return resp
        rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-admission','version':'1.1'}})
        up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        def call(name,**args):return rpc('tools/call',{'name':name,'arguments':args})
        path='Admission — schémas C01.md'
        first=call('vault_write',path=path,content='Témoin admission A.\n',ifNoneMatch='*');assert not first['result'].get('isError')
        r=call('vault_read',path=path);obj=json.loads(r['result']['content'][0]['text']);assert obj['content']=='Témoin admission A.\n'
        collision=call('vault_write',path=path,content='NE DOIT PAS PASSER',ifNoneMatch='*');assert collision['result'].get('isError')
        changed=call('vault_append',path=path,content='B.\n',ifMatch=obj['version']);assert not changed['result'].get('isError')
        stale=call('vault_write',path=path,content='NE DOIT PAS PASSER',ifMatch=obj['version']);assert stale['result'].get('isError')
        r=call('vault_read',path=path);assert json.loads(r['result']['content'][0]['text'])['content']=='Témoin admission A.\nB.\n'
        adapter={'candidate':'C01','transport':'http','mutation_tools':['vault_write','vault_append','vault_patch','vault_delete','vault_move','vault_copy'],
                 'preparation_tools':[],'read_tools':['vault_read'],'read_format':'json','read_content_key':'content','path_key':'path','status_tools':[],
                 'enabled_tools':['vault_read','vault_list','search_simple','search_query','tag_list','vault_get_document_map','vault_write','vault_append','vault_patch'],
                 'technical_paths':['.obsidian/workspace.json','.obsidian/plugins/frontmatter-date-manager/data.json']}
        writej(out/'adapter.json',adapter)
        summary=readj(out/'admission-partielle.json');summary.update(status='ADMIS',reason='Nonce et schémas lecture/écriture qualifiés dans le bac ; CAS et création conditionnelle vérifiés sur notes d’admission.',
                   catalog_sha256=sha((out/'catalogue.json').read_bytes()),adapter_sha256=sha((out/'adapter.json').read_bytes()),mode='Plugin Obsidian ouvert, MCP HTTP natif',utc=memory()['utc'])
        writej(out/'admission.json',summary)
        (out/'fiche-technique.md').write_text('C01 — Local REST API with MCP 5.5.2\n\nPlugin Obsidian, MCP HTTP natif. Lire avec vault_read (content/version). vault_write crée ou remplace ; ifNoneMatch="*" permet une création conditionnelle. ifMatch reprend la version lue pour write/append/patch. vault_patch cible heading/block/frontmatter. Relecture complète par vault_read pour vérifier les octets. Pas de statut durable ni de reprise présumée sur une réponse perdue. Utiliser les outils de notes/recherche autorisés ; aucune commande arbitraire.\n',encoding='utf-8')
        print(json.dumps({'candidate':'C01','status':'ADMIS','nonceVerified':True,'schemaMappingVerified':True}))
    finally:stop(cfg);mon.close()

if __name__=='__main__':main()
