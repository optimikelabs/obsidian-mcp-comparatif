"""Qualification de coupure/reprise du client commun sur factice, aucun candidat."""
import shutil,threading,sys
from campaign_runtime import *
from client_cli import make_config,run_turn,effective_config
from relay import Stdio,Relay,serve
from test_kit import ADAPTER
from oracles import verify

def main():
    out=RUN/'client-qualification-t8'/str(time.time_ns());gate(out,'before_client_t8');out.mkdir(parents=True,exist_ok=True)
    vault=out/'vault';shutil.copytree(KIT/'fixtures/synthetique',vault);mon=Monitor(out).start();up=None;server=None
    try:
        up=Stdio([sys.executable,'-X','utf8',str(KIT/'scripts/fake_server.py'),'--vault',str(vault)],str(KIT),out/'upstream.stderr.txt')
        init=up.rpc({'jsonrpc':'2.0','id':-1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'comparatif-controller','version':'1.1'}}})
        up.rpc({'jsonrpc':'2.0','method':'notifications/initialized'})
        relay=Relay(up,vault,'T8',out/'relay',ADAPTER,initialization=init);server=serve(relay,27348);threading.Thread(target=server.serve_forever,daemon=True).start()
        home,cwd=make_config(out,['read','patch','write','append','create','rank','status']);effective_config(out,home,cwd)
        fiche='\nFiche factice de qualification : read(path) retourne JSON content/etag. append(path,content,etag) ajoute le texte à la fin ; etag est la révision lue. write(path,content,etag) remplace conditionnellement. Aucun statut durable ne prouve l’effet d’une écriture directe ; relire.'
        a=run_turn(out,(KIT/'prompts/T8.txt').read_text(encoding='utf-8')+fiche,home,cwd,mon,disconnect=relay)
        assert a['stop_reason']=='T8_REPLY_LOST',a
        b=run_turn(out,'Réponse perdue, issue inconnue. Poursuis avec ton historique, établis l’issue puis termine la demande initiale.',home,cwd,mon,turn='02',resume=a['thread_id'])
        response=readj(out/'02.final.json');case={'task':'T8','before':relay.before,'cut':relay.cut,'after':snapshot(vault),'events':relay.events,'response':response,'expected_before_tree_sha256':manifest(relay.before)['tree_sha256']}
        verdict=verify(case);writej(out/'case.json',case);writej(out/'oracle.json',verdict)
        proof={'qualified':not verdict['errors'] and not b['forbidden_tool_events'] and b['returncode']==0,'out':str(out),'first':a,'resume':b,'oracle':verdict,'upstream_kept_alive':up.p.poll() is None,'same_thread':a['thread_id']==b['thread_id']}
        writej(RUN/'CLIENT-T8-QUALIFICATION.json',proof);print(json.dumps(proof,ensure_ascii=False))
    finally:
        if server:server.shutdown();server.server_close()
        if up:up.close()
        mon.close()

if __name__=='__main__':main()
