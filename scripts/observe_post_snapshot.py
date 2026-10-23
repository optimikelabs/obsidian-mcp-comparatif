"""Observation après fermeture, séparée de l'oracle gelé. Aucune mutation du coffre."""
import base64
import re
from campaign_runtime import *


def fields(entry):
    raw = base64.b64decode(entry['base64'])
    if raw.startswith(b'---\n'):
        props, body = split(raw)
        return props, body.encode('utf-8')
    return {}, raw


def compare(before, judged, closed, vault):
    differences = []
    touched = {p for p in set(before) | set(judged) if before.get(p) != judged.get(p)}
    for path in sorted(set(judged) | set(closed)):
        a, b = judged.get(path), closed.get(path)
        if a == b:
            continue
        item = {'path': path, 'judged': a, 'closed': b, 'touched_in_cell': path in touched}
        if path.endswith('.md') and a and b:
            try:
                ap, ab = fields(a); bp, bb = fields(b)
                keys = sorted(k for k in set(ap) | set(bp) if ap.get(k) != bp.get(k))
                item.update(changed_keys=keys, body_unchanged=ab == bb,
                            only_dates=bool(keys) and set(keys) <= {'création', 'modification'} and ab == bb,
                            date_format=all(isinstance(bp.get(k), str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', bp[k]) is not None for k in keys),
                            values={k: bp.get(k) for k in keys})
            except (ValueError, UnicodeError):
                item['only_dates'] = False
        disk = vault/path
        if disk.exists():
            st = disk.stat()
            item['disk_stat'] = {'birthtime': st.st_birthtime, 'mtime': st.st_mtime,
                                 'seconds_from_creation': st.st_mtime-st.st_birthtime}
        differences.append(item)
    return differences


def observe(cell):
    out = RUN/'cellules'/cell
    dest = RUN/'observations-post-instantane'/cell
    assert not dest.exists(), 'Observation déjà conservée : ne pas remplacer'
    cfg = readj(out/'obsidian.json')
    from campaign_runtime import _owned_processes
    assert not _owned_processes(cfg), 'Instance encore ouverte'
    judged = readj(out/'after.json'); before = readj(out/'relay/before.json')
    old = out/'after-close-observation.json'
    closed = readj(old) if old.exists() else snapshot(Path(cfg['vault']))
    writej(dest/'snapshot-prive.json', closed)
    plugin = Path(cfg['vault'])/'.obsidian/plugins/frontmatter-date-manager'
    differences = compare(before, judged, closed, Path(cfg['vault']))
    public_differences = []
    for d in differences:
        if d['path'] not in (P, N, Q):
            d = {**d, **{stage: {'sha256': d[stage]['sha256'], 'size': d[stage]['size']} if d[stage] else None for stage in ('judged', 'closed')}}
        public_differences.append(d)
    evidence = {'cell_id': cell, 'observed_utc': memory()['utc'], 'judged_snapshot_sha256': sha((out/'after.json').read_bytes()),
                'result_sha256': sha((out/'result.json').read_bytes()), 'judged_inventory': manifest(judged),
                'closed_inventory': manifest(closed), 'differences': public_differences,
                'fdm_manifest': readj(plugin/'manifest.json'), 'fdm_settings': readj(plugin/'data.json'),
                'fdm_main_sha256': sha((plugin/'main.js').read_bytes()),
                'judgment_window_unchanged': True, 'verdict_automatically_changed': False}
    writej(dest/'observation.json', evidence)
    print(json.dumps({'cell': cell, 'differences': [{k:v for k,v in d.items() if k not in ('judged','closed')} for d in differences]}, ensure_ascii=False))
    return evidence


if __name__ == '__main__':
    import sys
    observe(sys.argv[1])
