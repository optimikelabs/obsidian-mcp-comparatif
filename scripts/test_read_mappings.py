"""Lectures structurées : preuve issue du MCP, aucun texte reconstitué depuis le disque."""
import copy
import shutil
import sys
import threading
from common import *
from fake_server import Fake,http_server
from relay import Relay,HTTP,Stdio,LegacySSE,serve
from test_kit import Client,ADAPTER
from oracles import verify

def main():
    root=KIT/'preuves/read-mappings'/str(time.time_ns());root.mkdir(parents=True);checks=[]
    for transport in ('stdio','http','sse'):
        out=root/transport;out.mkdir();vault=out/'vault';shutil.copytree(KIT/'fixtures/synthetique',vault);backend=None
        if transport=='stdio':up=Stdio([sys.executable,'-X','utf8',str(KIT/'scripts/fake_server.py'),'--vault',str(vault)],str(KIT),out/'stderr.txt')
        else:
            backend=http_server(Fake(vault),sse=transport=='sse');threading.Thread(target=backend.serve_forever,daemon=True).start()
            up=LegacySSE(f'http://127.0.0.1:{backend.server_port}/sse') if transport=='sse' else HTTP(f'http://127.0.0.1:{backend.server_port}/mcp')
        def ui(task):
            p=vault/P;p.write_text(p.read_text(encoding='utf-8').replace(OLD,CONFLICT),encoding='utf-8',newline='')
        adapter={**ADAPTER,'read_tools':['read_structured'],'read_mappings':{'read_structured':{'format':'body_frontmatter','content_key':'content','frontmatter_key':'fm'}}}
        relay=Relay(up,vault,'T7b',out/'relay',adapter,ui);server=serve(relay,0);threading.Thread(target=server.serve_forever,daemon=True).start();client=Client(server)
        try:
            client.call('read_structured',path=P);client.call('patch',path=P,old=OLD,new=NEW);client.call('read_structured',path=P);relay.finish()
            case={'task':'T7b','before':relay.before,'human':relay.human,'first':relay.first,'after':snapshot(vault),'events':copy.deepcopy(relay.events),
                  'expected_before_tree_sha256':manifest(relay.before)['tree_sha256'],
                  'response':{'task_id':'T7b','path':P,'etat':'conflit','extrait':CONFLICT,'proprietes':{},'message':'Factice lecture structurée.'}}
            result=verify(case);assert result['errors']==[],result
            writej(out/'case.json',case);writej(out/'oracle.json',result);checks.append({'transport':transport,'case':'structured_positive','result':result})
            for label,field,value in [('wrong_type','properties',{'rang':'1'}),('wrong_body','body_sha256','0'*64),('missing_response','response_received',False)]:
                c=copy.deepcopy(case);next(e for e in reversed(c['events']) if e['event']=='mcp_read_response')[field]=value
                v=verify(c);assert 'RELECTURE_MCP_ABSENTE' in v['errors'];writej(out/f'negative-{label}.json',{'case':c,'oracle':v});checks.append({'transport':transport,'case':label,'result':v})
            c=copy.deepcopy(case);next(e for e in c['events'] if e['event']=='mcp_read_response')['body_sha256']='0'*64
            v=verify(c);assert 'INJECTION_INVALIDE' in v['errors'];writej(out/'negative-initial-proof.json',{'case':c,'oracle':v});checks.append({'transport':transport,'case':'initial_proof_mismatch','result':v})
        finally:
            server.shutdown();server.server_close()
            if backend:backend.messages.put(None)
            up.close()
            if backend:backend.shutdown();backend.server_close()
    writej(KIT/'preuves/tests-read-mappings.json',{'success':True,'root':str(root),'checks':checks})
    print(json.dumps({'success':True,'checks':len(checks)}))

if __name__=='__main__':main()
