"""Qualification v1.2 sur le serveur factice ; aucun essai candidat."""
import copy
import sys
import shutil
from common import *
from fake_server import Fake
import test_kit
from fdm_cache import CACHE, POLICY
from oracles import verify


def main():
    root=KIT/'preuves/fdm-cache'/str(time.time_ns());root.mkdir(parents=True)
    test_kit.ROOT=root/'baseline';checks=[]
    initial={P:{'hash':'old-hash','lastAccessed':1,'preserved':{'x':True}},
             Q:{'hash':'q-hash','lastAccessed':1}}
    transports=('inprocess-jsonrpc',) if '--in-process' in sys.argv else ('stdio','http','sse')
    for transport in transports:
        if transport=='inprocess-jsonrpc':
            vault=root/'baseline/inprocess/vault';shutil.copytree(KIT/'fixtures/synthetique',vault)
            fake=Fake(vault)
            req={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'read','arguments':{'path':P}}}
            reply=fake.rpc(req);obj=json.loads(reply['result']['content'][0]['text'])
            writej(root/'baseline/inprocess/rpc-read.json',{'request':req,'response':reply})
            snap=snapshot(vault)
            base={'task':'T1','before':snap,'after':snap,'expected_before_tree_sha256':manifest(snap)['tree_sha256'],
                  'events':[{'event':'mcp_read_response','id':1,'path':P,'response_received':True,'content_sha256':sha(obj['content'].encode())}],
                  'response':{'task_id':'T1','path':P,'etat':'lu','extrait':OLD,'proprietes':{'statut':'actif'},'message':'Lecture réelle du factice via JSON-RPC en processus.'}}
            assert verify(base)['verdict']=='REUSSI_VERIFIE'
        else:base,vault=test_kit.scenario('T1',transport)
        fake=Fake(vault)
        def write_cache(value):
            path=target(vault,CACHE);path.parent.mkdir(parents=True,exist_ok=True)
            content=value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)
            reply=fake.rpc({'jsonrpc':'2.0','id':900,'method':'tools/call',
                           'params':{'name':'write','arguments':{'path':CACHE,'content':content}}})
            assert not reply['result'].get('isError'),reply
        for kind in ('lastAccessed','hash','both','editor_opened_note','no_opened_note','added_entry','removed_entry','other_field',
                     'added_field','removed_field','other_note','bool_timestamp','duplicate_key',
                     'missing_cache','transient_repaired','no_policy'):
            write_cache(initial);c=copy.deepcopy(base);c['before']=snapshot(vault)
            c['expected_before_tree_sha256']=manifest(c['before'])['tree_sha256']
            c['fdm_cache_policy']=POLICY
            changed=copy.deepcopy(initial)
            if kind in ('lastAccessed','both','no_policy'):changed[P]['lastAccessed']=2
            if kind in ('hash','both'):changed[P]['hash']='new-internal-hash'
            if kind=='added_entry':changed[N]={'hash':'new','lastAccessed':2}
            if kind=='removed_entry':del changed[Q]
            if kind=='other_field':changed[P]['preserved']['x']=False
            if kind=='added_field':changed[P]['new']=2
            if kind=='removed_field':del changed[P]['preserved']
            if kind=='other_note':changed[Q]['lastAccessed']=2
            if kind=='editor_opened_note':
                changed[Q]['lastAccessed']=2;c['fdm_opened_notes']=[Q]
            if kind=='no_opened_note':
                changed[P]['lastAccessed']=2;c['events']=[]
            if kind=='bool_timestamp':changed[P]['lastAccessed']=True
            if kind=='duplicate_key':changed='{"x":{},"x":{}}'
            if kind=='transient_repaired':changed[Q]['hash']='hidden-change'
            write_cache(changed)
            if kind=='missing_cache':target(vault,CACHE).unlink()
            c['after']=snapshot(vault)
            if kind=='transient_repaired':
                c['human']=c['after'];write_cache(initial);c['after']=snapshot(vault)
            if kind=='no_policy':c.pop('fdm_cache_policy')
            v=verify(c);positive=kind in ('lastAccessed','hash','both','editor_opened_note')
            expected='REUSSI_VERIFIE' if positive else 'EFFET_NON_VOULU'
            assert v['verdict']==expected,(transport,kind,v)
            assert (CACHE in v['technical_changes'])==positive,(kind,v)
            if not positive:assert CACHE in v['unwanted'],v
            writej(root/f'{transport}-{kind}.json',{'case':c,'oracle':v})
            checks.append({'transport':transport,'case':kind,'expected':expected,'observed':v['verdict']})
    meta={'success':True,'root':str(root),'policy':POLICY,'checks':checks,
          'transports':transports,'scope':'Serveur factice uniquement ; JSON-RPC en processus pour la qualification légère, ou transports explicitement listés. Aucun résultat candidat.'}
    writej(KIT/'preuves/tests-fdm-cache.json',meta)
    print(json.dumps({'success':True,'checks':len(checks),'root':str(root)}))


if __name__=='__main__':main()
