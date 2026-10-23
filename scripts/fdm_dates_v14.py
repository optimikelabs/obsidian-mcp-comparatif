"""Attribution FDM dans les instantanés v1.4. Aucune exemption du corps ou d'une autre clé."""
import datetime
import math
import re
from common import *
from fdm_cache import CACHE, strict_json, typed

POLICY = 'fdm-dates-v1.4'
PLUGIN = '.obsidian/plugins/frontmatter-date-manager/'
KEYS = {'création', 'modification'}


def stamp(value, offset):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', value):
        raise ValueError('Format non FDM')
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M').replace(
        tzinfo=datetime.timezone(datetime.timedelta(seconds=offset))).timestamp()


def context(out, before, window_start):
    """Contexte du contrôleur, jamais fourni par le candidat ; aucune écriture dans le coffre."""
    out=Path(out)
    settings=strict_json(data(before, PLUGIN+'data.json'))
    version=strict_json(data(before, PLUGIN+'manifest.json'))['version']
    cfg=readj(out/'obsidian.json')
    records=[]
    source=out/'fdm-observer-raw.json'
    for r in readj(source) if source.exists() else []:
        if r['path'] not in (P,N,Q):continue
        raw=r['text'].encode('utf-8')
        records.append({k:r[k] for k in ('path','plugin','version','before','after','observed_utc')} | {
            'from_fdm_stack':'plugin:frontmatter-date-manager' in r['stack'],
            'stack_sha256':sha(r['stack'].encode('utf-8')),
            'note':{'base64':base64.b64encode(raw).decode(),'size':len(raw),'sha256':sha(raw)},
            'stat_before':r.get('stat_before')})
    births={rel:(Path(cfg['vault'])/rel).stat().st_birthtime for rel in (P,N,Q) if (Path(cfg['vault'])/rel).exists()}
    return {'version':version,'settings':settings,'records':records,'birthtimes':births,
            'utc_offset_seconds':datetime.datetime.fromtimestamp(window_start).astimezone().utcoffset().total_seconds()}


def stage_time(case, stage):
    for name,event in (('human','ui_disk_verified'),('first','first_snapshot'),('cut','effect_disk_verified')):
        if stage is case.get(name):
            return next((e.get('utc',case['window_end']) for e in case['events'] if e.get('event')==event),case['window_end'])
    return case['window_end']


def content_hash(raw, settings):
    """Même projection textuelle que getContentForHashing de FDM 1.6.0 livré."""
    text=raw.decode('utf-8').strip();mode=settings.get('hashTrackingMode','body')
    if mode not in ('body','frontmatter','both'):raise ValueError('Mode de hash FDM inconnu')
    match=re.match(r'^---\r?\n([\s\S]*?\r?\n)?---\r?\n?',text)
    if not match:return sha(('' if mode=='frontmatter' else text).encode('utf-8'))
    header=match.group(1) or '';body=text[match.end():]
    if mode=='body':return sha(body.encode('utf-8'))
    excluded={settings.get('headerCreated','').strip(),settings.get('headerUpdated','').strip(),
              settings.get('headerLastViewed','viewed').strip(),settings.get('headerUpdateCount','').strip()}
    excluded.update(k.strip() for k in settings.get('frontmatterHashExcludeKeys',[]));excluded.discard('')
    result=[];skip=False
    for line in re.split(r'\r?\n',header):
        key=re.match(r'^([^\s:][^:]*?)\s*:',line)
        if key:skip=key.group(1) in excluded
        elif re.match(r'^\S',line) and line.strip():skip=False
        if not skip:result.append(line)
    filtered='\n'.join(result)
    return sha((filtered+(body if mode=='both' else '')).encode('utf-8'))


def cache_passage(case, rel, at, until, expected_hash):
    previous=None
    for name in ('before','human','first','cut','after'):
        stage=case.get(name)
        if stage is None or CACHE not in stage:continue
        current=strict_json(data(stage,CACHE)).get(rel)
        if name!='before' and current and current!=previous and current.get('hash')==expected_hash:
            accessed=current.get('lastAccessed')
            if type(accessed) in (int,float) and math.isfinite(accessed) and at<=accessed/1000<=until:
                return {'stage':name,'entry':current}
        previous=current
    return None


def evidence(case, rel, key, actual, expected, stage):
    if case.get('fdm_dates_policy')!=POLICY:return None
    try:
        ctx=case['fdm_dates_context'];settings=ctx['settings'];offset=ctx['utc_offset_seconds']
        if ctx['version']!='1.6.0' or settings['dateFormat']!="yyyy-MM-dd'T'HH:mm" or settings.get('timezone','')!='':return None
        if settings.get('headerCreated')!='création' or settings.get('headerUpdated')!='modification':return None
        target_note=N if case['task'] in ('T4','T5') else P
        if case['task']=='T1' or rel!=target_note or key not in KEYS:return None
        stamp(actual,offset)
        if key=='création' and not settings.get('enableCreateTime'):return None
        if key=='modification' and not settings.get('enableModifiedTime'):return None
        until=stage_time(case,stage);chain=[];current=expected
        records=sorted(ctx['records'],key=lambda r:r['observed_utc'])
        for r in records:
            at=r['observed_utc']
            if r['path']!=rel or not case['window_start']<=at<=until:continue
            if not r.get('from_fdm_stack') or r['plugin']!='frontmatter-date-manager' or r['version']!='1.6.0':continue
            before,after=r['before'],r['after']
            changed={k for k in set(before)|set(after) if not typed(before.get(k),after.get(k)) or (k in before)!=(k in after)}
            if not changed or not changed<=KEYS or key not in changed or not typed(before.get(key),current):continue
            raw=base64.b64decode(r['note']['base64'],validate=True)
            if sha(raw)!=r['note']['sha256'] or len(raw)!=r['note']['size']:continue
            props,_=split(raw)
            if not typed(props,after):continue
            for k in changed:stamp(after.get(k),offset)
            value_time=stamp(after[key],offset)
            if value_time>at:continue
            # Valeur existante : FDM attend minSecondsBetweenSaves avant son prochain traitement.
            timing=False
            if before.get(key) is not None:
                timing=at>=stamp(before[key],offset)+settings['minSecondsBetweenSaves']
            # Nouvelle note : fenêtre armée à sa création, jamais à la fin du jugement.
            elif rel not in case['before'] and rel in ctx.get('birthtimes',{}):
                birth=ctx['birthtimes'][rel]
                timing=case['window_start']<=birth<=at and at>=birth+settings['delayForNewFiles']/1000
            passage=cache_passage(case,rel,at,until,content_hash(raw,settings))
            if not timing and not passage:continue
            chain.append({'observed_utc':at,'after_sha256':r['note']['sha256'],'changed_keys':sorted(changed),
                          'basis':'delai_FDM' if timing else 'hash-cache.json','cache_passage':passage})
            current=after[key]
            if typed(current,actual):return {'policy':POLICY,'chain':chain}
    except (ValueError,KeyError,TypeError,UnicodeError,yaml.YAMLError,OverflowError):
        return None
    return None
