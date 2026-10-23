"""Masquage public conservateur. Originaux conservés hors paquet, jamais modifiés."""
import re
from common import *

SENSITIVE={'authorization','proxyauthorization','apikey','obsidianapikey','token','accesstoken','refreshtoken',
           'secret','password','cookie','setcookie','sessionid','installationid','accountid','privateid','licencekey','licensekey'}
PATTERNS=[
 (re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/%=-]+'),'Bearer <MASQUE>'),
 (re.compile(r'(?i)\b(?:sk|ghp|github_pat)-?_[A-Za-z0-9_\-]{8,}'),'<JETON_MASQUE>'),
 (re.compile(r'(?i)\b[A-Z]:[\\/]+[^\r\n"<>`]*'),'<CHEMIN_PRIVE>'),
 # Chemins absolus WSL, y compris les volumes montés ; exclure les URL.
 (re.compile(r'(?:^|(?<=[\s`(=\[{]))/(?![/\s])[^/\r\n"<>`]+/[^\r\n"<>`]+'),'<CHEMIN_PRIVE>'),
 (re.compile(r'(?:^|(?<=[\s`(=\[{]))\\{2,}[^\r\n"<>`]+'),'<CHEMIN_PRIVE>'),
 (re.compile(r'(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'),'<IDENTIFIANT_MASQUE>'),
 (re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'),'<EMAIL_MASQUE>'),
 (re.compile(r'(?i)([?&](?:api[_-]?key|token|secret|session[_-]?id)=)[^&\s"<>]+'),r'\1<MASQUE>'),
]

def text_redact(value):
    for pattern,replacement in PATTERNS:value=pattern.sub(replacement,value)
    return value

def redact(value):
    if isinstance(value,dict):
        return {k:('<MASQUE>' if re.sub(r'[^a-z]','',k.lower()) in SENSITIVE else redact(v)) for k,v in value.items()}
    if isinstance(value,list):return [redact(v) for v in value]
    if isinstance(value,str):return text_redact(value)
    return value

def find_leaks(value,canaries=()):
    raw=json.dumps(value,ensure_ascii=False)
    leaks=[f'canary:{i}' for i,s in enumerate(canaries) if s in raw]
    for i,(pattern,_) in enumerate(PATTERNS):
        # Le champ JSON est inspecté récursivement pour éviter les backslashes d'échappement.
        strings=[]
        def walk(obj):
            if isinstance(obj,dict):
                for key,val in obj.items():
                    if re.sub(r'[^a-z]','',key.lower()) in SENSITIVE and val not in ('<MASQUE>',None,''):
                        leaks.append('sensitive-field:'+key)
                    walk(val)
            elif isinstance(obj,list):
                for val in obj:walk(val)
            elif isinstance(obj,str):strings.append(obj)
        walk(value)
        if any(pattern.search(s) for s in strings):leaks.append('pattern:'+str(i))
    return sorted(set(leaks))

def sanitize_file(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    # Code neuf revu, sans secrets réels ; conserver ses tests-canaris et sa syntaxe.
    # Le masquage de données n'est jamais une réécriture lexicale de code source.
    if source.suffix in ('.py','.mjs'):dest.write_bytes(source.read_bytes())
    elif source.suffix=='.json':writej(dest,redact(readj(source)))
    elif source.suffix=='.jsonl':
        lines=[redact(json.loads(line)) for line in source.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
        dest.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in lines),encoding='utf-8')
    else:dest.write_text(text_redact(source.read_text(encoding='utf-8-sig')),encoding='utf-8',newline='')

def selftest():
    # Tous les secrets ci-dessous sont synthétiques, fabriqués pour éprouver le masquage.
    secrets=['CANARY_KEY_2406','CANARY_TOKEN_2406','CANARY_BEARER_2406','CANARY_URL_2406',
             '01234567-89ab-cdef-0123-456789abcdef','private-canary@example.invalid',
             'PATH_CANARY_2406','CANARY_COOKIE_2406']
    sample={'Authorization':'bEaReR '+secrets[2],'OBSIDIAN_API_KEY':secrets[0],
        'nested':[{'apiKey':secrets[0],'access_token':secrets[1],'cookie':secrets[7]}],
        'message':'Bearer '+secrets[2]+' '+secrets[4]+' '+secrets[5],
        'url':'http://127.0.0.1:27346/mcp?token='+secrets[3]+'&x=1',
        'path':r'Z:\PATH_CANARY_2406\notes\été.md',
        'useful':{'cell':'C07-T8-r3','sha256':'a'*64,'count':1,'text':'café, œuvre, 東京'}}
    masked=redact(sample);serialized=json.dumps(masked,ensure_ascii=False)
    assert not any(s in serialized for s in secrets)
    assert masked['useful']==sample['useful']
    assert sample['Authorization'].endswith(secrets[2]),'Original muté'
    roundtrip=redact(json.loads(json.dumps(sample)))
    assert roundtrip==masked
    assert not find_leaks(masked,secrets)
    assert find_leaks({'unexpected':secrets[0]},secrets)==['canary:0']
    assert find_leaks({'deep':[{'access_token':'oubli'}]})
    # Répertoires et identités inventés : aucune dépendance à un poste réel.
    paths=[r'Z:\PATH_CANARY_2406\sous dossier\été.md',
           'Y:/PATH_CANARY_2406/sous dossier/été.md',
           '/mnt/z/PATH_CANARY_2406/sous dossier/été.md',
           '/home/PATH_CANARY_2406/sous dossier/été.md',
           '/opt/PATH_CANARY_2406/sous dossier/été.md',
           r'\\HOST_CANARY_2406\share\sous dossier\été.md']
    for path in paths:
        assert text_redact(path)=='<CHEMIN_PRIVE>',path
        assert redact(json.loads(json.dumps({'nested':[{'path':path}]})))=={'nested':[{'path':'<CHEMIN_PRIVE>'}]}
        assert find_leaks({'nested':[{'path':path}]}),path
    for safe in ('Efforts/Projets/Témoin.md','https://example.invalid/notes/été.md',
                 'http://127.0.0.1:27346/mcp','/mcp','café, œuvre, 東京','a'*64,
                 base64.b64encode(bytes(range(256))).decode('ascii')):
        assert text_redact(safe)==safe,safe
    proof={'success':True,'canaries':len(secrets),'nested_json':True,'json_escaped_paths':True,
           'generic_absolute_paths':True,'absolute_path_cases':len(paths),'relative_paths_and_urls_preserved':True,
           'unicode_and_measurements_preserved':True,'source_unchanged':True,
           'scope':'Secrets nommés, Bearer, IDs UUID, emails et chemins personnels ; liste blanche du paquet. Aucun anonymat parfait des mécanismes.'}
    writej(KIT/'preuves'/'masquage.json',proof);return proof

if __name__=='__main__':print(json.dumps(selftest(),ensure_ascii=False))
