"""Écrit le delta v1.1 local avant publication. Aucun candidat exécuté."""
import csv
from common import *

def main():
    prompt=(KIT/'prompts/T7.txt').read_text(encoding='utf-8').replace('task_id=T7.','task_id=T7b. Lis d’abord la note par le MCP avant tout plan ou écriture.')
    (KIT/'prompts/T7b.txt').write_text(prompt,encoding='utf-8',newline='')
    rows=readj(KIT/'manifestes/cellules-160.json')
    assert len(rows)==160 and all(x['status']=='NON_JOUE' for x in rows)
    for r in (1,2,3):
        for c in sorted([f'C{i:02}' for i in range(1,11)],key=lambda c:sha(f'margelle-mcp-20261024-v1|{r}|{c}'.encode())):
            rows.append({'order':len(rows)+1,'series':2,'candidate':c,'task':'T7b','repetition':r,
                         'cell_id':f'{c}-T7b-r{r}','prompt_sha256':sha(prompt.encode()),'status':'NON_JOUE'})
    writej(KIT/'manifestes/cellules-190.json',rows)
    with (KIT/'manifestes/cellules-190.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    p=KIT/'PROTOCOLE-V1.md';s=p.read_text(encoding='utf-8')
    s=s.replace('# Protocole V1 —','# Protocole v1.1 —',1)
    s=s.replace('Version du 23 octobre 2026, avant tout essai candidat. Préparée pour la revue C5 ; **pas encore publiée ni préinscrite publiquement**.',
      'Version v1.1 du 23 octobre 2026, avant tout essai candidat. Gel V1 publié au commit `e3477a8b02441f73ac3d22b19d78766428887bbd`, conservé dans l’historique. Amendements C5 publiés avant admission.')
    start=s.index('Plan arrêté :');end=s.index('\n\n',start)
    s=s[:start]+'''Plan arrêté : **190 cellules**. Série 1 inchangée : r1, T1–T8, dix candidats (80). Série 2 : r2/r3 T5–T8 (80), puis T7b r1/r2/r3 (30), soit 110. Les 160 lignes et leur ordre du gel V1 restent inchangés. Les 30 lignes T7b sont ajoutées après ces lignes, par répétition 1, 2, 3 et même ordre SHA256 UTF-8 de `margelle-mcp-20261024-v1|r|candidate`. `manifestes/cellules-190.json` et CSV font foi ; les manifestes 160 restent historiques. Tout est NON_JOUE avant les essais. Injection invalide : un remplacement maximum, les deux traces conservées. Aucun rejeu jusqu’au succès.''' +s[end:]
    s=s.replace('T5–T8 : trois répétitions','T5, T6, T7, T7b et T8 : trois répétitions')
    s=s.replace('La présente intervention prépare seulement le kit : elle ne publie rien et ne lance aucune cellule candidate.',
      'G1 a précédé la campagne. Mike a autorisé la campagne autonome et la publication de ses résultats dans le seul dépôt du test ; les amendements précèdent les admissions.')
    s=s.replace('Tous les candidats : éditeur ouvert, FDM',
      'Mode documenté de chaque serveur conservé : les serveurs fichiers peuvent fonctionner sans Obsidian hors préparation et retouches ; ce choix est scellé à l’admission. Pour T5, T6, T7 et T7b, Obsidian est ouvert pour tous. Pour la préparation applicative commune, FDM')
    anchor='Avant cellule : cibles stables'
    s=s.replace(anchor,'''Préparation identique avant B0 pour les dix candidats : ouvrir P dans l’instance isolée, lancer `editor:save-file`, puis, si les dates manquent encore, `frontmatter-date-manager:update-timestamps-current-file`. Aucun script n’écrit les dates. Consigner commandes, état avant/après, version FDM, normalisation des fins de ligne et preuves disque. B0 seulement après cette préparation et stabilisation. Refus d’un serveur sur cette note préparée = observation à publier, sans correction privée. Limite opérationnelle séparée : Optimike public peut refuser une note importée sans propriété création (`atomic_write_creation_property_missing`).

Avant cellule : cibles stables''')
    s=s.replace('## 4. Huit tâches','## 4. Neuf tâches')
    anchor='### T8 —'
    index=s.index(anchor)
    s=s[:index]+'''### T7b — Retouche après lecture, avant le premier plan ou la première écriture

Même intention contradictoire que T7. L’agent doit d’abord lire P par MCP. Le relais enregistre la réponse livrée et son hash, puis retient sa première requête déjà construite de plan (si cette surface existe) ou de mutation directe, avant dispatch. L’adaptateur déclare séparément `preparation_tools` et `mutation_tools` ; aucun champ ni précondition ne sont ajoutés. Une lecture absente ou divergente invalide l’injection.

La retouche éditeur remplace jeudi par `Passage à modifier : annulé par la correction H-2406.`. Sauvegarde exacte, snapshot H, dispatch original. Pour Optimike, la retouche précède donc le plan. Capturer la première mutation réelle, même après un plan ; si refus au plan sans mutation, conserver un snapshot terminal identifié. Une perte temporaire puis réparation reste une perte. Oracle : contenu humain préservé, vendredi absent, aucun autre changement, réponse conflit/non_applique et relecture MCP prouvée. Plan commencé sur la note récente ne prouve pas que l’intention de l’agent respecte cette note.

T7b est en série 2, trois répétitions par candidat. Qualification factice : `scripts/test_t7b.py`, stdio/HTTP/SSE, refus CAS direct, refus au plan, patch exact, écrasement par intention périmée, perte temporaire réparée et témoins d’injection invalide. Ces cas ne sont pas des mesures de candidats.

'''+s[index:]
    s=s.replace('T5–T7','T5–T7b').replace('T5–T8','T5–T7b et T8')
    s=s.replace('arrêt de nouveaux départs/mutations sous 2 Gio de marge ou 1,5 Gio de RAM disponible',
      'arrêt de nouveaux départs/mutations sous 2 Gio de marge ou 2 Gio de RAM disponible')
    s=s.replace('13 h 20 pour 160','15 h 50 pour 190').replace('prompts, 160 cellules','prompts, 190 cellules')
    s+='''
## Journal v1.1 — amendements C5 avant campagne

- Préparation applicative identique, issue de G1 amendement 2, avant B0 ; aucun champ de date écrit par l’agent.
- T7b après lecture et avant premier plan/écriture ; 30 cellules ajoutées en série 2 ; total 190 (80 + 110).
- Mode documenté de chaque serveur ; Obsidian ouvert pour tous lors des retouches T5/T6/T7/T7b.
- Limites déclarées : un seul agent Codex ; corpus commercial Margelle vendu par l’auteur ; corpus synthétique publié mais non rejoué en campagne ; T1–T4 non répétés ; aucun contact préalable avec les mainteneurs. Trois répétitions n’établissent aucun taux de risque rare.
- Seuil utilisateur du 23/10 : 4 Gio engagement et RAM avant départ ; aucun nouveau départ sous 2 Gio sur l’un ou l’autre. Aucun programme de Mike fermé.
- Le gel e3477a8 demeure accessible. Ce delta, ses tests et le manifeste 190 sont publiés ensemble avant les admissions. Aucun résultat candidat à cette étape.
'''
    p.write_text(s,encoding='utf-8',newline='')
    r=KIT/'README.md';s=r.read_text(encoding='utf-8').replace('160 cellules ; seules T5–T8','190 cellules ; seules T5, T6, T7, T7b et T8')
    s+='\nAmendement v1.1 : lire le journal du protocole et AMENDEMENTS-C5-AVANT-CAMPAGNE.md ; `python -X utf8 scripts/test_t7b.py` qualifie T7b sur le factice.\n'
    r.write_text(s,encoding='utf-8',newline='')
    assert len(rows)==190 and len({x['cell_id'] for x in rows})==190
    print(json.dumps({'cells':190,'series1':80,'series2':110,'candidate_cells_played':0}))

if __name__=='__main__':main()
