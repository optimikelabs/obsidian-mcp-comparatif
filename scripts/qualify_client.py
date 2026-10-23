"""Client réel Codex, uniquement serveur factice sur corpus ouvert. Aucun candidat mesuré."""
import shutil
import threading
from campaign_runtime import *
from client_cli import make_config,run_turn
from relay import Stdio,Relay,serve
from test_kit import ADAPTER
from oracles import verify

def main():
    out=RUN/'client-qualification'/str(time.time_ns());gate(out,'before_client_qualification');out.mkdir(parents=True,exist_ok=True)
    vault=out/'vault';shutil.copytree(KIT/'fixtures/synthetique',vault);mon=Monitor(out).start();up=None;server=None
    try:
        up=Stdio([sys.executable,'-X','utf8',str(KIT/'scripts/fake_server.py'),'--vault',str(vault)],str(KIT),out/'upstream.stderr.txt')
        relay=Relay(up,vault,'T2',out/'relay',ADAPTER);server=serve(relay,27348);threading.Thread(target=server.serve_forever,daemon=True).start()
        home,cwd=make_config(out,['read','patch','write','append','create','rank','status'])
        prompt=(KIT/'prompts/T2.txt').read_text(encoding='utf-8')+'\nFiche du serveur factice de qualification : read(path) retourne un objet JSON content/etag. patch(path,old,new) remplace une chaîne unique. write(path,content,etag) remplace conditionnellement. read renvoie le fichier complet. La qualification porte uniquement sur le chemin de ces outils ; aucune autre source.'
        result=run_turn(out,prompt,home,cwd,mon)
        if result['returncode'] or result['stop_reason'] or result['forbidden_tool_events']:
            writej(RUN/'CLIENT-NON-QUALIFIE.json',{'out':str(out),'result':result,'reason':'Client réel non qualifié ; aucune cellule candidate jouée'});print(json.dumps({'qualified':False,'out':str(out),'exit':result},ensure_ascii=False));return
        response=readj(out/'01.final.json');case={'task':'T2','before':relay.before,'after':snapshot(vault),'events':relay.events,'response':response,'expected_before_tree_sha256':manifest(relay.before)['tree_sha256']}
        verdict=verify(case);writej(out/'case.json',case);writej(out/'oracle.json',verdict)
        proof={'qualified':verdict['errors']==[],'model':'gpt-6.1-sol','effort':'high','service_tier':'default','cli_version':'0.160.1','case':'T2 factice uniquement','out':str(out),'result':result,'oracle':verdict}
        writej(RUN/'CLIENT-QUALIFICATION.json',proof);print(json.dumps(proof,ensure_ascii=False))
    finally:
        if server:server.shutdown();server.server_close()
        if up:up.close()
        mon.close()

if __name__=='__main__':
    import sys
    main()
