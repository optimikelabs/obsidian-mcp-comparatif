import argparse
import csv
import shutil
import stat
import zipfile
from common import *

EXPECTED='b69c70dcefe3908e14b1489d90bc748e45d7bb51caeb414c1b7a4e181d44e8ce'

def fixture(root, template):
    root=scoped(root)
    props,_=split(template.replace(b'\r\r\n',b'\n').replace(b'\r\n',b'\n'))
    if any(k in props for k in ('création','modification')):
        raise ValueError('Template avec dates : ne pas les réécrire')
    props.update({'statut':'actif','rang':1,'next_action':'Trier trois captures.', 'parent':None,
                  'échéance':None,'temoin_bool':True,'temoin_liste':['café','œuvre'],
                  'temoin_entier':7,'clé_inconnue':'Été — 東京'})
    files={P:render(props,BODY),Q:render({'type':'note','parent':'[[Projet témoin — Test MCP]]'},'Q GELÉE\n'),
           'Leurres/Projet témoin — Test MCP.md':render({'statut':'sommeil'},'Leurre sans code.\n'),
           'Archives/Historique.md':render({'statut':'clos'},'> MARGELLE-TEST-2406 — citation historique.\n'),
           'Pièces/Été d’aujourd’hui — témoin.bin':bytes(range(256))}
    for rel,value in files.items():
        p=target(root,rel);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
    return manifest(snapshot(root))

def prepare(archive):
    guard()
    archive=Path(archive); content=archive.read_bytes()
    assert sha(content)==EXPECTED, 'SHA256 archive inattendu'
    assert len(content)==4385139, 'Taille archive inattendue'
    ref=KIT/'reference'/'Margelle'
    if not ref.exists():
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                assert item.filename.startswith('Margelle/') and not stat.S_ISLNK(item.external_attr>>16)
                dest=target(KIT/'reference',item.filename)
                if not item.is_dir():
                    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(item))
    with zipfile.ZipFile(archive) as z:
        members=[item for item in z.infolist() if not item.is_dir()]
        assert len({item.filename.lower() for item in members})==len(members),'Chemins ZIP ambigus sur Windows'
        for item in members:
            assert target(KIT/'reference',item.filename).read_bytes()==z.read(item),'Référence extraite altérée'
        assert set(snapshot(ref))=={item.filename.removeprefix('Margelle/') for item in members},'Fichier supplémentaire dans référence'
    baseline=manifest(snapshot(ref));writej(KIT/'manifestes'/'reference.json',baseline)
    writej(KIT/'manifestes'/'provenance.json',{'archive_name':archive.name,'archive_sha256':EXPECTED,
        'archive_bytes':len(content),'commit':'8ca5bdb729b5aa2c5b2cd84a8a0e611f7ad2ec72',
        'reference_tree_sha256':baseline['tree_sha256'],'redistribution':'archive commerciale exclue du paquet public'})
    template=(ref/'X/Modèles/Élysia TP/Projets TP.md').read_bytes()
    commercial=KIT/'fixtures'/'Margelle-1.0.6'
    if not commercial.exists(): shutil.copytree(ref,commercial)
    fixture(commercial,template)
    writej(KIT/'manifestes'/'fixture-margelle.json',manifest(snapshot(commercial)))
    # Le corpus ouvert ne recopie ni les règles commerciales ni leur template.
    synthetic=KIT/'fixtures'/'synthetique'
    own=render({'type':'projet','parent':None,'collection':['[[Projets]]'],'entité':None,
                'statut':'actif','notes_liees':None,'rang':1,'client':False,'échéance':None,
                'next_action':None,'budget_h':None,'budget_euros':None,'type_projet':None},'')
    fixture(synthetic,own)
    target(synthetic,'.obsidian').mkdir(exist_ok=True)
    writej(synthetic/'.obsidian/app.json',{'alwaysUpdateLinks':True})
    writej(KIT/'manifestes'/'fixture-synthetique.json',manifest(snapshot(synthetic)))
    assert (commercial/P).read_bytes()==(synthetic/P).read_bytes()
    writej(KIT/'manifestes'/'equivalence.json',{'task_target_bytes_equal':True,
      'equivalence_limit':'P, Q, leurres et binaire identiques ; règles, plugins, FDM et environnement Margelle non équivalents.'})
    prompts=build_prompts(); rows=[]
    for r in (1,2,3):
        candidates=sorted([f'C{i:02}' for i in range(1,11)],key=lambda c:sha(f'margelle-mcp-20261024-v1|{r}|{c}'.encode()))
        tasks={1:list(range(1,9)),2:[5,6,7,8],3:[7,8,5,6]}[r]
        for c in candidates:
            for t in tasks:
                tid=f'T{t}';rows.append({'order':len(rows)+1,'series':1 if r==1 else 2,'candidate':c,
                    'task':tid,'repetition':r,'cell_id':f'{c}-{tid}-r{r}',
                    'prompt_sha256':sha(prompts[tid].encode()),'status':'NON_JOUE'})
    assert len(rows)==160 and len({r['cell_id'] for r in rows})==160
    writej(KIT/'manifestes'/'cellules-160.json',rows)
    with (KIT/'manifestes'/'cellules-160.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({'reference_files':len(baseline['files']),'reference_sha256':baseline['tree_sha256'],'cells':len(rows)}))

def build_prompts():
    common=('Tu utilises uniquement le MCP candidat. Aucun shell, disque direct, navigateur, eval arbitraire, '
        'installation ou autre MCP. Préserve tout hors de la demande. Utilise les protections documentées disponibles. '
        'Relis par MCP avant de conclure ; respecte une retouche contradictoire et ne répète pas aveuglément une écriture incertaine. '
        'Retourne seulement un objet JSON : task_id, path (relatif), etat (lu/applique/conflit/non_applique/inconnu), '
        'extrait (texte exact ou null), proprietes (objet), message (court). ')
    instructions={
      'T1':f'Retrouve le projet actif portant MARGELLE-TEST-2406. Sans écrire, rends son chemin, proprietes.statut et le passage « Passage à modifier ».',
      'T2':f'Dans {P}, remplace seulement « {OLD} » par « {NEW} ». Rends le nouveau passage.',
      'T3':f'Dans {P}, change seulement rang de l’entier 1 à l’entier 2. Rends proprietes.rang ; extrait=null.',
      'T4':f'Crée exactement {N}, sans écrasement ni suffixe. Propriétés : '+json.dumps(NPROPS,ensure_ascii=False)+f'. Corps exact (JSON) : {json.dumps(NBODY,ensure_ascii=False)}. Rends ce corps dans extrait.',
      'T5':f'Crée exactement {N}, sans écraser une note existante ni suffixe. Propriétés : '+json.dumps(NPROPS,ensure_ascii=False)+f'. Corps (JSON) : {json.dumps(NBODY,ensure_ascii=False)}. Si collision, conserve la note et signale le conflit ; rends son contenu dans extrait.',
      'T6':f'Dans {P}, remplace seulement « {OLD} » par « {NEW} ». Préserve toute autre retouche. Après refus, relis et reconstruis si compatible. Rends le nouveau passage.',
      'T7':f'Dans {P}, remplace « {OLD} » par « {NEW} » seulement sans remplacer de retouche contradictoire. Si contradiction, conserve-la et signale le conflit ; rends le passage effectivement conservé.',
      'T8':f'Ajoute une seule fois « {EVENT} » comme ligne finale à {P}. Après perte de réponse, reconnecte avec ton historique, établis l’issue par statut ou lecture puis vérifie sans doublon. Rends cette ligne.'}
    result={k:common+f'task_id={k}. '+v+'\n' for k,v in instructions.items()}
    for k,v in result.items():
        p=KIT/'prompts'/f'{k}.txt';p.parent.mkdir(exist_ok=True);p.write_text(v,encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);prepare(p.parse_args().archive)
