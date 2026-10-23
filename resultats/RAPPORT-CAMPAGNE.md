Série 1 : 0 cellules jouées ; 80 non jouées (sur 80).
Série 2 : 0 cellules jouées ; 110 non jouées (sur 110).
Candidats admis : C01, C02, C03, C04, C05.
Candidats non admis ou admission à achever : C06, C07, C08, C09, C10.
T5, T6, T7, T7b : trois répétitions prévues pour collision et retouches concurrentes ; aucune conclusion sans les cellules.
T8 : trois répétitions prévues pour effet appliqué/réponse perdue et reprise ; seules les cellules jouées sont mesurées.
Incidents consignés : 1 ; voir détails et journaux, sans attribution automatique au candidat.
Résultats publiés : https://github.com/optimikelabs/obsidian-mcp-comparatif/tree/main/resultats

# Rapport de campagne — état courant

État horodaté : 2026-10-23T08:05:55.955736+00:00. Publication préalable v1.1 : `1e698f62401034c74dd70a1019146e45c8dc821f`. Gel V1 `e3477a8b02441f73ac3d22b19d78766428887bbd` conservé. Clone frais : 580 fichiers du manifeste vérifiés, aucun écart.

Qualification de l’instrumentation : suite T1–T8 (5 groupes) passée ; 30 contrôles T7b stdio/HTTP/SSE passés et rejugés après masquage. Ce sont des essais factices, aucun résultat candidat. Manifeste 190 : 160 lignes d’origine préservées, puis 30 T7b en série 2.

## Admissions

| Candidat | État | Preuve ou reste à faire |
|---|---|---|
| C01 | ADMIS | Nonce et schémas acquis ; revalidation en configuration commune sans Hub réussie avant mesure. |
| C02 | ADMIS | Nonce et schémas lecture brute/structurée, patch et frontmatter qualifiés sur notes distinctes. |
| C03 | ADMIS | Nonce et mapping JSON-string vérifiés ; création et append sur note d’admission distincte. |
| C04 | ADMIS | Nonce, création et lecture entière via structuredContent qualifiés sur note d’admission. |
| C05 | ADMIS | Nonce, création, remplacement et relecture intégrale raw:true qualifiés sur note d’admission. |
| C06 | NON_EXECUTE_ENVIRONNEMENT | Isolation CLI non démontrée : runner.py transmet un exécutable OBSIDIAN_PATH et vault=nom, sans identité PID/profil. Aucun nonce lu par le chemin CLI ; appel non lancé pour préserver l’instance quotidienne. Aucun échec de concurrence déduit. |
| C07 | SCHEMAS_A_QUALIFIER | Nonce/catalogue acquis ; schémas à qualifier. |
| C08 | A_INSTRUIRE | Admission non achevée ; aucun résultat de cellule. |
| C09 | A_INSTRUIRE | Admission non achevée ; aucun résultat de cellule. |
| C10 | A_INSTRUIRE | Admission non achevée ; aucun résultat de cellule. |

## Limites

Un agent Codex CLI 0.160.1, gpt-6.1-sol high, serviceTier default. Corpus Margelle commercial vendu par l’auteur d’Optimike ; corpus synthétique publié mais non rejoué en campagne. T1–T4 : une seule répétition. Trois répétitions de T5/T6/T7/T7b/T8 ne donnent pas un taux de risque rare. Les non-joués ne sont ni réussites ni échecs fonctionnels. Aucun contact mainteneur, aucune publication hors de ce dépôt.

## Incidents

- admissions\C02\incident.json : Préparation applicative non stable/LF/datée en 60 s

## Reprise exacte

```json
{
  "phase": "ADMISSIONS_ATTENTE_MEMOIRE",
  "next_admission": "C07",
  "next_cell": "C05-T1-r1",
  "cells_played": 0,
  "candidate_active": null,
  "lock_taken_by_campaign": false,
  "admissions": {
    "C01": "ADMIS",
    "C02": "ADMIS",
    "C03": "ADMIS",
    "C04": "ADMIS",
    "C05": "ADMIS",
    "C06": "NON_EXECUTE_ENVIRONNEMENT",
    "C07": "SCHEMAS_A_QUALIFIER",
    "C08": "A_INSTRUIRE",
    "C09": "A_INSTRUIRE",
    "C10": "A_INSTRUIRE"
  },
  "memory": {
    "utc": "2026-10-23T07:56:56.092177+00:00",
    "commitFreeBytes": 5131620352,
    "availableBytes": 4061315072,
    "admitted": false,
    "stop": false
  },
  "next_check_utc": "2026-10-23T08:06:56.137794+00:00",
  "resume_command": "python -X utf8 scripts/qualify_c07.py",
  "resume_cwd": "test-comparatif/kit",
  "no_daily_application_closed": true,
  "do_not_rerun": [
    "amend_v11.py",
    "publish_v11.py (gel déjà publié)"
  ],
  "remaining_gates_before_cells": [
    "Admissions C07-C10",
    "Parsers natifs et actions multiplexées qualifiés sur factice",
    "Client commun Codex isolé/fournisseur/options scellés",
    "Publication des adaptateurs et du delta avant toute cellule"
  ]
}
```

## Pilotage

Aucun changement de statut recommandé à ce stade ; statut canonique non audité (coffre quotidien hors périmètre). Prochaine action : achever les admissions, puis première cellule selon le manifeste, sous les seuils mémoire et verrou. Aucune tâche du coffre modifiée.
