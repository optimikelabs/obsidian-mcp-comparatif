"""Témoins synthétiques de la collecte, sans oracle ni instance Obsidian."""
import base64
from observe_post_snapshot import compare, sha, Path

def entry(text):
    raw=text.encode('utf-8')
    return {'size':len(raw),'sha256':sha(raw),'base64':base64.b64encode(raw).decode()}

def main():
    path='test.md'; judged={path:entry('Témoin\n')}
    stamped='---\ncréation: 2026-10-23T16:29\nmodification: 2026-10-23T16:29\n---\nTémoin\n'
    def run(text,before=None):return compare(before or {},judged,{path:entry(text)},Path('__absent_fake__'))[0]
    ok=run(stamped);assert ok['only_dates'] and ok['date_format'] and ok['touched_in_cell']
    assert not run(stamped.replace('Témoin','Altéré'))['only_dates']
    assert not run(stamped.replace('création:', 'statut:'))['only_dates']
    assert not run(stamped.replace('2026-10-23T16:29','23/10/2026'))['date_format']
    assert not run(stamped,judged)['touched_in_cell']
    assert compare({},judged,judged,Path('__absent_fake__'))==[]
    assert not run(stamped.replace('modification:', 'création:'))['only_dates']
    print('7 contrôles passés ; aucun verdict automatiquement attribué.')

if __name__=='__main__':main()
