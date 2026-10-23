"""Outillage indépendant du candidat. Python 3.12 + PyYAML, UTF-8 explicite."""
import base64
import hashlib
import json
import time
from pathlib import Path
import yaml

KIT = Path(__file__).resolve().parents[1]
P = 'Efforts/Projets/Projet témoin — Test MCP.md'
N = 'Efforts/Projets/Compte rendu — Essai MCP.md'
Q = 'Efforts/Projets/Note Q.md'
OLD = 'Passage à modifier : essai prévu jeudi.'
NEW = 'Passage à modifier : essai prévu vendredi.'
HOLD = 'Témoin humain : version initiale.'
HNEW = 'Témoin humain : correction H-2406.'
CONFLICT = 'Passage à modifier : annulé par la correction H-2406.'
EVENT = 'Trace de suivi : EVENEMENT-2406.'
HUMAN = 'NOTE HUMAINE À CONSERVER\n'
BODY = ('## Fiche du projet\n- Objectif : trier trois captures.\n'
        '- Référence de recherche : MARGELLE-TEST-2406.\n'
        f'- {OLD}\n- {HOLD}\n'
        '- Témoin intact : café, œuvre, [[Projet témoin — Test MCP]].\n')
NBODY = '# Compte rendu — Essai MCP\n\nTrois captures triées.\n'
NPROPS = {'type': 'note', 'parent': '[[Projet témoin — Test MCP]]'}

class StrictLoader(yaml.SafeLoader):
    pass

def mapping(loader, node, deep=False):
    result = {}
    for keynode, valnode in node.value:
        key = loader.construct_object(keynode, deep=deep)
        if key in result:
            raise ValueError(f'Clé YAML dupliquée : {key}')
        result[key] = loader.construct_object(valnode, deep=deep)
    return result

StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def readj(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def writej(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str)+'\n', encoding='utf-8')

def guard():
    if (KIT/'ARRET-MEMOIRE.json').exists():
        raise RuntimeError('Arrêt propre : marge engagement < 1,5 Gio ; état conservé.')

def scoped(path):
    p = Path(path).resolve()
    if not p.is_relative_to(KIT.parent) or p == KIT.parent:
        raise ValueError('Écriture hors test-comparatif interdite')
    return p

def target(vault, rel):
    root = Path(vault).resolve()
    p = (root/rel).resolve()
    if p == root or not p.is_relative_to(root):
        raise ValueError('Chemin hors coffre')
    return p

def split(data):
    text = data.decode('utf-8').replace('\r\n','\n')
    if not text.startswith('---\n'):
        raise ValueError('Frontmatter absent ou fins de ligne non LF')
    header, body = text[4:].split('\n---\n', 1)
    props = yaml.load(header, Loader=StrictLoader)
    if not isinstance(props, dict):
        raise ValueError('Frontmatter non objet')
    return props, body

def render(props, body):
    if 'création' in props or 'modification' in props:
        raise ValueError('Dates réservées à FDM')
    text = '---\n'+yaml.safe_dump(props, allow_unicode=True, sort_keys=False)+'---\n'+body
    split(text.encode('utf-8'))
    return text.encode('utf-8')

def snapshot(root):
    guard()
    result = {}
    for p in sorted(Path(root).rglob('*')):
        if p.is_symlink():
            raise ValueError('Lien symbolique refusé')
        if p.is_file():
            data = p.read_bytes()
            result[p.relative_to(root).as_posix()] = {'size':len(data),'sha256':sha(data),
                                                     'base64':base64.b64encode(data).decode('ascii')}
    return result

def data(snap, rel):
    return base64.b64decode(snap[rel]['base64'])

def manifest(snap):
    entries = {k:{'size':v['size'],'sha256':v['sha256']} for k,v in sorted(snap.items())}
    return {'files':entries, 'tree_sha256':sha(json.dumps(entries,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8'))}

def wait_bytes(path, expected, timeout=60):
    end = time.monotonic()+timeout
    while time.monotonic()<end:
        guard()
        p = Path(path)
        if p.exists() and p.read_bytes()==expected:
            return sha(expected)
        time.sleep(.05)  # sondage d'une condition, jamais preuve par délai
    raise TimeoutError('Sauvegarde disque non observée')
