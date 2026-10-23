"""Épreuves réelles contre NOTRE serveur factice ; aucun résultat candidat."""
import copy
import http.client
import shutil
import sys
import threading
import unittest
import urllib.request
from common import *
from fake_server import Fake,http_server
from relay import Stdio,HTTP,LegacySSE,Relay,serve
from oracles import verify

ADAPTER={'mutation_tools':['create','write','patch','append','rank','refuse','deferred_patch','deferred_refuse','deferred_append'],
         'read_tools':['read'],'status_tools':['status'],'path_key':'path','read_content_key':'content'}
ROOT=KIT/'preuves'/'factice'
ALL=[]

class Client:
    def __init__(self,server):self.url=f'http://127.0.0.1:{server.server_port}/mcp';self.ident=0
    def rpc(self,method,params=None):
        self.ident+=1
        r=urllib.request.Request(self.url,data=json.dumps({'jsonrpc':'2.0','id':self.ident,'method':method,'params':params or {}}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(r,timeout=10) as response:return json.load(response)
    def call(self,name,**args):return self.rpc('tools/call',{'name':name,'arguments':args})
    def read(self,path):return self.call('read',path=path)

def scenario(task,transport='stdio',mode='good'):
    out=ROOT/f'{transport}-{task}-{mode}'
    assert not out.exists(),'Répertoire de preuve existant : exécuter avec --run-id ou conserver le précédent'
    out.mkdir(parents=True);vault=out/'vault';shutil.copytree(KIT/'fixtures'/'synthetique',vault)
    fake=Fake(vault);up_server=None
    if transport=='stdio':up=Stdio([sys.executable,'-X','utf8',str(KIT/'scripts'/'fake_server.py'),'--vault',str(vault)],str(KIT),out/'stderr.txt')
    else:
        up_server=http_server(fake,sse=transport=='sse');threading.Thread(target=up_server.serve_forever,daemon=True).start()
        up=LegacySSE(f'http://127.0.0.1:{up_server.server_port}/sse') if transport=='sse' else HTTP(f'http://127.0.0.1:{up_server.server_port}/mcp')
    def ui(task):
        # Pour les tests factices seulement. La qualification UI réelle est distincte et publiée.
        if task=='T5':target(vault,N).write_text(HUMAN,encoding='utf-8',newline='')
        else:
            text=target(vault,P).read_text(encoding='utf-8')
            old,new=(HOLD,HNEW) if task=='T6' else (OLD,CONFLICT)
            target(vault,P).write_text(text.replace(old,new),encoding='utf-8',newline='')
    relay=Relay(up,vault,task,out/'relay',ADAPTER,ui);server=serve(relay,0)
    threading.Thread(target=server.serve_forever,daemon=True).start();client=Client(server)
    try:
        client.rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test-kit','version':'1'}})
        assert len(client.rpc('tools/list')['result']['tools'])==11
        if task=='T1':pass
        elif task in ('T2','T6','T7'):
            if task=='T6':
                # Requête préparée sur la version antérieure : refus CAS puis reconstruction.
                if mode=='deferred':
                    client.call('deferred_patch',path=P,old=OLD,new=NEW)
                else:
                    resp=client.call('write',path=P,etag=sha(target(vault,P).read_bytes()),content=target(vault,P).read_text(encoding='utf-8').replace(OLD,NEW))
                    assert resp['result']['isError'];client.read(P)
                    client.call('patch',path=P,old=OLD,new=NEW)
            elif mode=='deferred' and task=='T7':client.call('deferred_refuse',path=P)
            else:client.call('patch',path=P,old=OLD,new=NEW)
            if mode=='deferred':
                end=time.monotonic()+5
                while time.monotonic()<end:
                    state=json.loads(client.call('status',path=P)['result']['content'][0]['text'])['state']
                    if state in ('committed','conflict'):break
                    time.sleep(.01)
        elif task=='T3':client.call('rank',path=P)
        elif task in ('T4','T5'):client.call('create',path=N,content=render(NPROPS,NBODY).decode())
        elif task=='T8':
            try:client.call('deferred_append' if mode=='deferred' else 'append',path=P,content=EVENT+'\n');raise AssertionError('Réponse T8 remise au client')
            except (http.client.RemoteDisconnected,ConnectionResetError):pass
        path=N if task in ('T4','T5') else P
        readback=client.read(path)
        assert not readback['result'].get('isError')
        response={'task_id':task,'path':path,'etat':'lu' if task=='T1' else 'conflit' if task in ('T5','T7') else 'applique',
                  'extrait':{'T1':OLD,'T2':NEW,'T3':None,'T4':NBODY,'T5':HUMAN,'T6':NEW,'T7':CONFLICT,'T8':EVENT}[task],
                  'proprietes':{'statut':'actif'} if task=='T1' else {'rang':2} if task=='T3' else {},'message':'Constat MCP du factice.'}
        case={'task':task,'before':relay.before,'after':snapshot(vault),'events':copy.deepcopy(relay.events),'response':response,
              'expected_before_tree_sha256':readj(KIT/'manifestes'/'fixture-synthetique.json')['tree_sha256']}
        for key in ('human','first','cut'):
            if getattr(relay,key) is not None:case[key]=getattr(relay,key)
        result=verify(case)
        writej(out/'case.json',case);writej(out/'oracle.json',result)
        ALL.append({'test':out.name,'expected':'PROTEGE_NON_ACCOMPLI' if task in ('T5','T7') else 'REUSSI_VERIFIE','observed':result['verdict'],'errors':result['errors']})
        return case,vault
    finally:
        server.shutdown();server.server_close()
        if up_server:up_server.messages.put(None)
        up.close()
        if up_server:up_server.shutdown();up_server.server_close()

class Tests(unittest.TestCase):
    def test_dates_et_format_en_memoire(self):
        # Snapshots hypothétiques en JSON uniquement : aucun script ne touche les champs dates d'une note.
        case,_=scenario('T3','http','date-format-source')
        actual=data(case['after'],P)
        crlf=actual.replace(b'\n',b'\r\n');entry={'size':len(crlf),'sha256':sha(crlf),'base64':base64.b64encode(crlf).decode()}
        c=copy.deepcopy(case);c['after'][P]=entry
        next(e for e in c['events'] if e['event']=='mcp_read_response')['content_sha256']=sha(crlf)
        result=verify(c);self.assertEqual(result['errors'],[]);self.assertEqual(result['format_differences'],[P])
        dated=actual.replace(b'\n---\n',b'\nmodification: 2026-10-23T04:00\n---\n',1)
        c=copy.deepcopy(case);c['after'][P]={'size':len(dated),'sha256':sha(dated),'base64':base64.b64encode(dated).decode()}
        next(e for e in c['events'] if e['event']=='mcp_read_response')['content_sha256']=sha(dated)
        self.assertIn('YAML_VALEUR_OU_TYPE',verify(c)['errors'])
        c.update(window_start=1,window_end=3,date_evidence=[{'path':P,'key':'modification','value':'2026-10-23T04:00',
            'plugin':'frontmatter-date-manager','version':'1.6.0','after_sha256':sha(dated),'observed_utc':2}])
        self.assertEqual(verify(c)['errors'],[])
        c['date_evidence'][0]['observed_utc']=4
        self.assertIn('YAML_VALEUR_OU_TYPE',verify(c)['errors'])
        ALL.append({'test':'dates_and_format_memory_snapshots','crlf_separate':True,'unattributed_date_rejected':True,'out_of_window_rejected':True})
    def test_positifs(self):
        for transport in ('stdio','http','sse'):
            for i in range(1,9):
                with self.subTest(transport=transport,task=i):
                    case,_=scenario(f'T{i}',transport)
                    self.assertEqual(verify(case)['errors'],[])
    def test_negatifs(self):
        base={}
        for task in ('T1','T2','T3','T4','T5','T6','T7','T8'):base[task]=scenario(task,'http','negative-base')
        def negative(label,task,transform,expected):
            case,vault=base[task];c=copy.deepcopy(case);transform(c,vault)
            result=verify(c);self.assertIn(expected,result['errors'],(label,result));
            writej(ROOT/'negatifs'/f'{label}.json',{'case':c,'oracle':result,'expected_error':expected})
            ALL.append({'test':label,'expected_error':expected,'observed_errors':result['errors']})
        def disk(c,vault,rel,value):
            # Les dégradations disque passent aussi par le serveur factice écrit pour le kit.
            Fake(vault).rpc({'jsonrpc':'2.0','id':900,'method':'tools/call','params':{'name':'write','arguments':{'path':rel,'content':value}}})
            c['after']=snapshot(vault)
        negative('mauvaise_note','T1',lambda c,v:c['response'].update(path=Q),'REPONSE_CIBLE')
        negative('mauvaise_fixture','T1',lambda c,v:c.update(expected_before_tree_sha256='0'*64),'FIXTURE_EMPREINTE')
        negative('snapshot_hash_mensonger','T1',lambda c,v:c['after'][P].update(sha256='0'*64),'SNAPSHOT_INTEGRITE')
        negative('masque_note_metier','T1',lambda c,v:c.update(technical_paths=[Q]),'MASQUE_TECHNIQUE_INVALIDE')
        negative('relecture_declaree_non_prouvee','T2',lambda c,v:c.update(events=[]),'RELECTURE_MCP_ABSENTE')
        negative('faux_succes','T7',lambda c,v:c['response'].update(etat='applique'),'SUCCES_MENSONGER')
        negative('injection_trop_tard','T6',lambda c,v:c.update(events=list(reversed(c['events']))),'INJECTION_INVALIDE')
        negative('arguments_modifies','T5',lambda c,v:next(e for e in c['events'] if e['event']=='dispatch').update(request_sha256='autre'),'INJECTION_INVALIDE')
        negative('reponse_perdue_non_prouvee','T8',lambda c,v:c.update(events=[e for e in c['events'] if e['event']!='response_held']),'INJECTION_INVALIDE')
        negative('reponse_en_fait_livree','T8',lambda c,v:c['events'].append({'event':'response_delivered','id':next(e['id'] for e in c['events'] if e['event']=='response_held')}),'INJECTION_INVALIDE')
        negative('perte_temporaire_reparee','T6',lambda c,v:c.update(first=c['before']),'PREMIERE_MUTATION_PERTE')
        negative('etat_coupure_sans_effet','T8',lambda c,v:c.update(cut=c['before']),'COUPURE_EFFET')
        # Chaque corruption part des bytes attendus ; pas d'accumulation entre les témoins.
        correct=data(base['T3'][0]['after'],P).decode()
        negative('entier_devenu_chaine','T3',lambda c,v:disk(c,v,P,correct.replace('rang: 2','rang: "2"')),'RANG_TYPE')
        negative('entier_devenu_booleen','T3',lambda c,v:disk(c,v,P,correct.replace('rang: 2','rang: true')),'RANG_TYPE')
        negative('cle_yaml_dupliquee','T3',lambda c,v:disk(c,v,P,correct.replace('rang: 2','rang: 2\nrang: 3')),'YAML_OU_UTF8_INVALIDE:Clé YAML dupliquée : rang')
        negative('champ_inconnu_perdu','T3',lambda c,v:disk(c,v,P,correct.replace('clé_inconnue: Été — 東京\n','')),'YAML_VALEUR_OU_TYPE')
        expected=data(base['T8'][0]['after'],P).decode()
        negative('doublon_evenement','T8',lambda c,v:disk(c,v,P,expected+EVENT+'\n'),'CORPS_INATTENDU')
        negative('retouche_humaine_ecrasee','T5',lambda c,v:disk(c,v,N,NBODY),'HUMAIN_PERDU')
        negative('autre_note_modifiee','T2',lambda c,v:disk(c,v,Q,'Q PERDUE'),'HORS_CIBLE')
        negative('suffixe_creation','T4',lambda c,v:(target(v,'Efforts/Projets/Compte rendu — Essai MCP 1.md').write_text('doublon',encoding='utf-8'),c.update(after=snapshot(v))),'HORS_CIBLE')
    def test_manifest(self):
        rows=readj(KIT/'manifestes'/'cellules-160.json')
        self.assertEqual(len(rows),160);self.assertEqual(len({x['cell_id'] for x in rows}),160)
        for candidate in [f'C{i:02}' for i in range(1,11)]:
            for t in range(1,9):self.assertEqual(sum(x['candidate']==candidate and x['task']==f'T{t}' for x in rows),1 if t<5 else 3)
        for r,tasks in [(1,[1,2,3,4,5,6,7,8]),(2,[5,6,7,8]),(3,[7,8,5,6])]:
            selected=[x for x in rows if x['repetition']==r]
            expected=sorted([f'C{i:02}' for i in range(1,11)],key=lambda c:sha(f'margelle-mcp-20261024-v1|{r}|{c}'.encode()))
            self.assertEqual([x['candidate'] for x in selected[::len(tasks)]],expected)
            for i in range(0,len(selected),len(tasks)):self.assertEqual([x['task'] for x in selected[i:i+len(tasks)]],[f'T{t}' for t in tasks])
    def test_differe(self):
        for task in ('T6','T7','T8'):
            with self.subTest(task=task):
                case,_=scenario(task,'http','deferred');self.assertEqual(verify(case)['errors'],[])

if __name__=='__main__':
    import os
    ROOT=ROOT/str(time.time_ns());ROOT.mkdir(parents=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    writej(KIT/'preuves'/'tests-factice.json',{'success':result.wasSuccessful(),'unittest_groups':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'checks':ALL,'root':str(ROOT),'utc':time.time()})
    sys.exit(0 if result.wasSuccessful() else 1)
