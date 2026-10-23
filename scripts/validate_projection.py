"""Valide et empreinte la projection publique courante, jamais les originaux privés."""
import ast
from common import *
from redact import find_leaks

def main():
    public=KIT/'public';entries={}
    for p in sorted(public.rglob('*')):
        rel=p.relative_to(public)
        if not p.is_file() or '.git' in rel.parts or '__pycache__' in rel.parts or p.suffix=='.pyc' or rel.as_posix()=='MANIFEST-PUBLIC.json':continue
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
        elif p.suffix=='.json':assert not find_leaks(readj(p)),str(rel)
        elif p.suffix=='.jsonl':
            for line in p.read_text(encoding='utf-8-sig').splitlines():
                if line.strip():assert not find_leaks(json.loads(line)),str(rel)
        elif p.suffix not in ('.mjs','.bin'):
            text=p.read_text(encoding='utf-8-sig')
            for marker in ('C:\\Users\\','E:\\Mes Vibes Programmes','F:\\OBSIDIAN','C:/Users/'):
                assert marker.lower() not in text.lower(),str(rel)
        entries[rel.as_posix()]={'size':p.stat().st_size,'sha256':sha(p.read_bytes())}
    digest=sha(json.dumps(entries,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
    writej(public/'MANIFEST-PUBLIC.json',{'files':entries,'tree_sha256':digest})
    print(json.dumps({'files':len(entries)+1,'tree_sha256':digest,'private_paths_detected':False}))

if __name__=='__main__':main()
