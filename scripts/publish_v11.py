"""Prépare la projection v1.1 en liste blanche ; git/push restent explicites."""
import ast
from common import *
from redact import sanitize_file, find_leaks, selftest

def main():
    assert readj(KIT/'preuves/tests-factice.json')['success']
    assert readj(KIT/'preuves/tests-t7b.json')['success']
    selftest();public=KIT/'public'
    rows=readj(KIT/'manifestes/cellules-190.json');old=readj(KIT/'manifestes/cellules-160.json')
    assert rows[:160]==old and len(rows)==190
    assert [sum(x['series']==s for x in rows) for s in (1,2)]==[80,110]
    for c in (f'C{i:02}' for i in range(1,11)):
        assert sum(x['candidate']==c and x['task']=='T7b' for x in rows)==3
    files=['PROTOCOLE-V1.md','README.md','prompts/T7b.txt','manifestes/cellules-190.json','manifestes/cellules-190.csv',
           'scripts/relay.py','scripts/oracles.py','scripts/fake_server.py','scripts/test_t7b.py','scripts/amend_v11.py','scripts/publish_v11.py',
           'preuves/tests-t7b.json']
    for rel in files:sanitize_file(KIT/rel,public/rel)
    for name in ('AMENDEMENTS-C5-AVANT-CAMPAGNE.md','DECISIONS-C5.md'):
        sanitize_file(KIT.parent/name,public/name)
    sanitize_file(KIT.parents[1]/'G1/AMENDEMENT-2.md',public/'PREPARATION-G1-AMENDEMENT-2.md')
    root=Path(readj(KIT/'preuves/tests-t7b.json')['root'])
    for p in root.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.jsonl') and 'vault' not in p.relative_to(root).parts:
            sanitize_file(p,public/'preuves/t7b-validation'/p.relative_to(root))
    # Rejuger les traces publiées après masquage, y compris les échecs attendus.
    from oracles import verify
    checks=[]
    for p in sorted((public/'preuves/t7b-validation').rglob('case.json')):
        observed=verify(readj(p));expected=readj(p.with_name('oracle.json'))
        assert observed==expected,(p,observed,expected);checks.append(p.relative_to(public).as_posix())
    for p in sorted((public/'preuves/t7b-validation').rglob('negative-*.json')):
        obj=readj(p);assert verify(obj['case'])==obj['oracle'];checks.append(p.relative_to(public).as_posix())
    writej(public/'preuves/validation-v1.1.json',{'success':True,'masked_cases_replayed':len(checks),
           'series1':80,'series2':110,'original160_preserved':True,'candidate_cells_played':0,
           'original_freeze':'e3477a8b02441f73ac3d22b19d78766428887bbd','utc':time.time()})
    assert len(checks)==30
    paths=[]
    for p in sorted(public.rglob('*')):
        if not p.is_file() or '.git' in p.relative_to(public).parts or '__pycache__' in p.parts:continue
        rel=p.relative_to(public).as_posix()
        if rel=='MANIFEST-PUBLIC.json':continue
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
        elif p.suffix=='.json':assert not find_leaks(readj(p)),rel
        elif p.suffix=='.jsonl':
            for line in p.read_text(encoding='utf-8-sig').splitlines():
                if line.strip():assert not find_leaks(json.loads(line)),rel
        elif p.suffix not in ('.mjs','.bin'):
            raw=p.read_text(encoding='utf-8-sig')
            for marker in ('C:\\Users\\','E:\\Mes Vibes Programmes','F:\\OBSIDIAN'):
                assert marker.lower() not in raw.lower(),rel
        paths.append(p)
    entries={p.relative_to(public).as_posix():{'size':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in paths}
    writej(public/'MANIFEST-PUBLIC.json',{'files':entries,'tree_sha256':sha(json.dumps(entries,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())})
    print(json.dumps({'validated':True,'files':len(entries)+1,'masked_cases_replayed':len(checks)},ensure_ascii=False))

if __name__=='__main__':main()
