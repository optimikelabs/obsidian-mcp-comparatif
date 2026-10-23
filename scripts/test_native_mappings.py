"""Serveur factice avec formes natives observées C03/C04/C05 ; aucun score candidat."""
import copy
import shutil
from common import *
from campaign_runtime import RUN
from relay import Relay
from fake_server import Fake
from oracles import verify

class NativeFake(Fake):
    def rpc(self,req):
        if req.get('method')!='tools/call':return super().rpc(req)
        params=req['params'];name=params['name'];a=params.get('arguments',{})
        if name=='obsidian_get_file_contents':
            text=target(self.vault,a['filepath']).read_text(encoding='utf-8')
            return {'id':req['id'],'result':{'content':[{'type':'text','text':json.dumps(text,ensure_ascii=False)}]}}
        if name=='obsidian_get_note':
            text=target(self.vault,a['target']['path']).read_text(encoding='utf-8')
            return {'id':req['id'],'result':{'content':[{'type':'text','text':'Présentation\n'+text}],
                    'structuredContent':{'result':{'format':'content','path':a['target']['path'],'content':text}}}}
        if name=='vault' and a['action']=='read':
            text=target(self.vault,a['path']).read_text(encoding='utf-8')
            return {'id':req['id'],'result':{'content':[{'type':'text','text':json.dumps({'result':{'content':text}},ensure_ascii=False)}]}}
        if name=='vault' and a['action']=='create':tool='create';args={'path':a['path'],'content':a['content']}
        elif name=='edit':tool='patch';args={'path':a['path'],'old':a['oldText'],'new':a['newText']}
        elif name=='obsidian_replace_in_note':tool='patch';args={'path':a['target']['path'],'old':a['old'],'new':a['new']}
        else:return super().rpc(req)
        c=copy.deepcopy(req);c['params']={'name':tool,'arguments':args};return super().rpc(c)

def main():
    root=KIT/'preuves/native-mappings'/str(time.time_ns());root.mkdir(parents=True);checks=[]
    for candidate,task in (('C03','T1'),('C04','T7b'),('C05','T7b'),('C05','T5')):
        out=root/f'{candidate}-{task}';out.mkdir();vault=out/'vault';shutil.copytree(KIT/'fixtures/synthetique',vault)
        adapter=readj(RUN/'admissions'/candidate/'adapter.json')
        def ui(task):
            if task=='T5':target(vault,N).write_text(HUMAN,encoding='utf-8',newline='')
            else:
                p=target(vault,P);p.write_text(p.read_text(encoding='utf-8').replace(OLD,CONFLICT),encoding='utf-8',newline='')
        relay=Relay(NativeFake(vault),vault,task,out/'relay',adapter,ui);ident=0
        def call(name,**args):
            nonlocal ident
            ident+=1;return relay.process({'jsonrpc':'2.0','id':ident,'method':'tools/call','params':{'name':name,'arguments':args}})
        def read(path):
            if candidate=='C03':return call('obsidian_get_file_contents',filepath=path)
            if candidate=='C04':return call('obsidian_get_note',target={'type':'path','path':path},format='content')
            return call('vault',action='read',path=path,raw=True)
        if task!='T5':
            read(P);assert not relay.injected,'Une lecture multiplexée ne doit pas déclencher une mutation'
        if task=='T7b':
            if candidate=='C04':call('obsidian_replace_in_note',target={'type':'path','path':P},old=OLD,new=NEW)
            else:call('edit',action='window',path=P,oldText=OLD,newText=NEW)
        if task=='T5':call('vault',action='create',path=N,content=NBODY)
        path=N if task=='T5' else P;read(path);relay.finish()
        case={'task':task,'before':relay.before,'after':snapshot(vault),'events':copy.deepcopy(relay.events),
              'expected_before_tree_sha256':manifest(relay.before)['tree_sha256'],
              'response':{'task_id':task,'path':path,'etat':'lu' if task=='T1' else 'conflit','extrait':OLD if task=='T1' else HUMAN if task=='T5' else CONFLICT,'proprietes':{'statut':'actif'} if task=='T1' else {},'message':'Factice forme native.'}}
        for key in ('human','first'):
            if getattr(relay,key) is not None:case[key]=getattr(relay,key)
        verdict=verify(case);assert verdict['errors']==[],verdict
        writej(out/'case.json',case);writej(out/'oracle.json',verdict);checks.append({'case':out.name,'verdict':verdict})
        if task=='T7b':
            c=copy.deepcopy(case);tech='.obsidian/workspace.json'
            def item(b):return {'size':len(b),'sha256':sha(b),'base64':base64.b64encode(b).decode()}
            for name in ('before','human'):c[name][tech]=item(b'{"state":1}')
            for name in ('first','after'):c[name][tech]=item(b'{"state":2}')
            c['technical_paths']=[tech];c['expected_before_tree_sha256']=manifest(c['before'])['tree_sha256']
            for e in c['events']:
                if e['event']=='ui_disk_verified':e['snapshot_sha256']=manifest(c['human'])['tree_sha256']
                if e['event']=='first_snapshot':e['snapshot_sha256']=manifest(c['first'])['tree_sha256']
            v=verify(c);assert v['errors']==[],v
            writej(out/'technical-first.json',{'case':c,'oracle':v});checks.append({'case':out.name+'-technical-first','verdict':v})
            c['first'][Q]=item(b'Autre note perdue temporairement')
            next(e for e in c['events'] if e['event']=='first_snapshot')['snapshot_sha256']=manifest(c['first'])['tree_sha256']
            v=verify(c);assert v['verdict']=='EFFET_NON_VOULU' and 'PREMIERE_MUTATION_HORS_CIBLE' in v['errors']
            writej(out/'negative-temporary-other-note.json',{'case':c,'oracle':v});checks.append({'case':out.name+'-temporary-other-note','verdict':v})
    writej(KIT/'preuves/tests-native-mappings.json',{'success':True,'root':str(root),'checks':checks})
    print(json.dumps({'success':True,'checks':len(checks)}))

if __name__=='__main__':main()
