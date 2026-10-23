"""Relecture contrefactuelle, sans modification ni reclassement des cellules originales."""
from campaign_runtime import *
from fdm_dates_v14 import context,POLICY
from oracles import verify
from oracles_v13 import verify as frozen


def main():
    rows=[];eligible=[]
    for p in sorted((RUN/'cellules').iterdir()):
        if not (p/'result.json').exists():continue
        result=readj(p/'result.json')
        entry={'cell':p.name,'original_verdict':result['verdict'],'original_status':result['status'],
               'result_sha256':sha((p/'result.json').read_bytes()),'reclassified':False}
        if (p/'case-index.json').exists():
            case=readj(p/'case-index.json')
            for key,rel in case['snapshot_files'].items():case[key]=readj(p/rel)
            previous=frozen(case)
            # L'activation v1.4 est explicite : les preuves anciennes gardent leur oracle.
            assert verify(case)==previous
            case.update(fdm_dates_policy=POLICY,fdm_dates_context=context(p,case['before'],case['window_start']))
            current=verify(case)
            attributable=any(d['attribution']=='indéterminée' for d in previous['dates'])
            only_reason=attributable and not current['errors'] and not current['unwanted'] and not current['first_unwanted']
            entry.update(old_replay=previous,v14_counterfactual=current,only_degraded_by_fdm_chain=only_reason,
                         case_index_sha256=sha((p/'case-index.json').read_bytes()),oracle_sha256=sha((p/'oracle.json').read_bytes()))
            if only_reason:eligible.append(p.name)
        else:
            entry.update(only_degraded_by_fdm_chain=False,reason='Arrêt avant instantané jugé ; motif conservé : '+result.get('reason',''))
        rows.append(entry)
    proof={'success':True,'cells_reviewed':len(rows),'eligible_for_one_replacement':eligible,'rows':rows,
           'original_results_unchanged':True,'counterfactual_is_not_a_new_score':True}
    writej(KIT/'preuves/v14-audit-equite.json',proof)
    print(json.dumps({'reviewed':len(rows),'eligible':eligible},ensure_ascii=False))


if __name__=='__main__':main()
