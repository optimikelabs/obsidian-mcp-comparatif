"""Installation locale d'une version npm figée, sans script lifecycle ni global."""
import urllib.request
import urllib.parse
from campaign_runtime import *

def main():
    import sys
    candidate,name,version=sys.argv[1:]
    out=KIT.parent/'installations'/candidate;gate(RUN/'admissions'/candidate,'before_install_npm')
    out.mkdir(parents=True,exist_ok=True)
    info=json.load(urllib.request.urlopen('https://registry.npmjs.org/'+urllib.parse.quote(name,safe='')+'/'+version,timeout=60))
    writej(out/'registry.json',info)
    raw=urllib.request.urlopen(info['dist']['tarball'],timeout=60).read();(out/'package.tgz').write_bytes(raw)
    import hashlib
    assert hashlib.sha1(raw).hexdigest()==info['dist']['shasum']
    writej(out/'artifact.json',{'name':name,'version':version,'sha256':sha(raw),'sha1':info['dist']['shasum'],'integrity':info['dist'].get('integrity'),'url':info['dist']['tarball'],'lifecycle_scripts':info.get('scripts',{}),'scripts_executed':False})
    npm=Path('C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js')
    command(['node',str(npm),'install','--prefix',str(out),'--cache',str(KIT.parent/'installations/npm-cache'),'--ignore-scripts','--no-audit','--no-fund',f'{name}@{version}'],out,'npm-install',timeout=900)
    writej(out/'installed-tree.json',manifest(snapshot(out/'node_modules')))
    print(json.dumps({'candidate':candidate,'installed':name,'version':version,'artifact_sha256':sha(raw),'scripts_executed':False}))

if __name__=='__main__':main()
