import subprocess
from ui_qualification import CONFIG, cdp, inject, stop, RUNTIME
from common import *

def run():
    cfg=readj(CONFIG);vault=Path(cfg['vault']);results=[]
    try:
        # La création de N ouvre une note vide dans Obsidian ; son texte passe par l'éditeur.
        _,_,proof=inject('T5');results.append({'task':'T5','proof':proof})
        for task,old,new in [('T6',HOLD,HNEW),('T7',OLD,CONFLICT)]:
            guard();source=(vault/P).read_text(encoding='utf-8');assert source.count(old)==1
            # Les offsets JS sont en unités UTF-16, même avec des emojis avant le passage.
            offset=len(source[:source.index(old)].encode('utf-16-le'))//2
            cmd=['node',str(KIT/'scripts'/'retouche-editeur.mjs'),'--port',str(cfg['port']),
                 '--vault',str(vault),'--note',P,'--position',str(offset),'--delete-length',str(len(old)),
                 '--text',new,'--expected-before-sha256',sha(source.encode('utf-8'))]
            r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=65)
            if r.returncode:raise RuntimeError(r.stderr)
            results.append({'task':task,'proof':json.loads(r.stdout)})
        # Insertion pure à la fin puis au début, avec accents/emoji et confirmation disque.
        for position,text in [('end','\nÉpreuve de saisie : café, œuvre, 東京 🧪.\n'),('start','<!-- témoin insertion -->\n')]:
            r=subprocess.run(['node',str(KIT/'scripts'/'retouche-editeur.mjs'),'--port',str(cfg['port']),
                '--vault',str(vault),'--note',N,'--position',position,'--text',text],capture_output=True,text=True,encoding='utf-8',timeout=65)
            if r.returncode:raise RuntimeError(r.stderr)
            results.append({'position':position,'proof':json.loads(r.stdout)})
        before=snapshot(vault)
        bad=subprocess.run(['node',str(KIT/'scripts'/'retouche-editeur.mjs'),'--port',str(cfg['port']),
            '--vault',str(vault),'--note',P,'--position','0','--text','INTERDIT',
            '--expected-before-sha256','0'*64],capture_output=True,text=True,encoding='utf-8')
        assert bad.returncode and snapshot(vault)==before
        results.append({'negative':'stale_before_hash','rejected':True,'no_write':True})
        writej(KIT/'preuves'/'qualification-editeur.json',{'qualified':True,'method':'CDP MarkdownView.editor',
             'results':results,'plugins':readj(RUNTIME/'plugins.json'),'identity':readj(RUNTIME/'identity.json'),
             'limits':'Une instance Windows isolée ; retouche simulée. Chaque injection de campagne doit confirmer sa sauvegarde disque.'})
        print('QUALIFIE : T5, T6, T7 et script autonome ; sauvegardes disque confirmées.')
    except BaseException as e:
        writej(KIT/'preuves'/'qualification-editeur.json',{'qualified':False,'results':results,'error':str(e)});raise
    finally:stop()

if __name__=='__main__':run()
