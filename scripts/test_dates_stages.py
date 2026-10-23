"""Snapshots JSON hypothétiques, pas de création/modification de dates dans une note."""
import copy
from common import *
from oracles import verify

def main():
    source=Path(readj(KIT/'preuves/tests-factice.json')['root']);base=readj(source/'http-T5-good/case.json');checks=[]
    def item(raw):return {'base64':base64.b64encode(raw).decode(),'size':len(raw),'sha256':sha(raw)}
    for stage in ('human','first','after'):
        c=copy.deepcopy(base);c.update(window_start=1,window_end=3,date_evidence=[])
        # Hypothèse : FDM ajoute un frontmatter daté, corps humain strictement intact.
        raw='---\ncréation: 2026-10-23T10:00\nmodification: 2026-10-23T10:00\n---\n'.encode()+HUMAN.encode()
        # Un ajout à human implique que first et after le contiennent également.
        for s in ('human','first','after')[('human','first','after').index(stage):]:
            c[s][N]=item(raw)
        for e in c['events']:
            if e['event']=='ui_disk_verified':e['snapshot_sha256']=manifest(c['human'])['tree_sha256']
            if e['event']=='first_snapshot':e['snapshot_sha256']=manifest(c['first'])['tree_sha256']
            if e['event']=='mcp_read_response' and e.get('path')==N:e['content_sha256']=sha(raw)
        for key in ('création','modification'):c['date_evidence'].append({'path':N,'key':key,'value':'2026-10-23T10:00','plugin':'frontmatter-date-manager','version':'1.6.0','after_sha256':sha(raw),'observed_utc':2})
        v=verify(c);assert v['errors']==[],(stage,v);checks.append({'stage':stage,'case':c,'oracle':v})
        for bad in ('missing','hash','version','window'):
            b=copy.deepcopy(c)
            if bad=='missing':b['date_evidence']=[]
            else:
                for e in b['date_evidence']:e[{'hash':'after_sha256','version':'version','window':'observed_utc'}[bad]]={'hash':'0'*64,'version':'0','window':4}[bad]
            v=verify(b);assert v['verdict']=='NON_EXECUTE_ENVIRONNEMENT' and v['errors'],(stage,bad,v)
            checks.append({'stage':stage,'negative':bad,'case':b,'oracle':v})
    out=KIT/'preuves/date-stages'/str(time.time_ns());out.mkdir(parents=True)
    for i,c in enumerate(checks):writej(out/f'{i:02}.json',c)
    writej(KIT/'preuves/tests-date-stages.json',{'success':True,'checks':len(checks),'root':str(out)})
    print(json.dumps({'success':True,'checks':len(checks)}))
if __name__=='__main__':main()
