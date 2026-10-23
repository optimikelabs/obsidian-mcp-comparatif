Série 1 : 3 cellules jouées ; 77 non jouées (sur 80).
Série 2 : 0 cellules jouées ; 110 non jouées (sur 110).
Candidats admis : C01, C02, C03, C04, C05, C07, C08, C09, C10.
Candidats non admis ou admission à achever : C06.
T5, T6, T7, T7b : trois répétitions prévues pour collision et retouches concurrentes ; aucune conclusion sans les cellules.
T8 : trois répétitions prévues pour effet appliqué/réponse perdue et reprise ; seules les cellules jouées sont mesurées.
Incidents consignés : 6 ; voir détails et journaux, sans attribution automatique au candidat.
Résultats publiés : https://github.com/optimikelabs/obsidian-mcp-comparatif/tree/main/resultats

# Rapport de campagne — état courant

État horodaté : 2026-10-23T09:24:30.172324+00:00. Publication préalable v1.1 : `1e698f62401034c74dd70a1019146e45c8dc821f`. Gel V1 `e3477a8b02441f73ac3d22b19d78766428887bbd` conservé. Clone frais : 580 fichiers du manifeste vérifiés, aucun écart.

Qualification de l’instrumentation : suite T1–T8 (5 groupes) passée ; 30 contrôles T7b stdio/HTTP/SSE passés et rejugés après masquage. Ce sont des essais factices, aucun résultat candidat. Manifeste 190 : 160 lignes d’origine préservées, puis 30 T7b en série 2.

Vérification de publication : {"head": "96919dd2fd5eec67d135825b899ae1f9ae2608f0", "remote_verified": true, "utc": "2026-10-23T09:23:33.288464+00:00"}.

## Admissions

| Candidat | État | Preuve ou reste à faire |
|---|---|---|
| C01 | ADMIS | Nonce et schémas acquis ; revalidation en configuration commune sans Hub réussie avant mesure. |
| C02 | ADMIS | Nonce et schémas lecture brute/structurée, patch et frontmatter qualifiés sur notes distinctes. |
| C03 | ADMIS | Nonce et mapping JSON-string vérifiés ; création et append sur note d’admission distincte. |
| C04 | ADMIS | Nonce, création et lecture entière via structuredContent qualifiés sur note d’admission. |
| C05 | ADMIS | Nonce, création, remplacement et relecture intégrale raw:true qualifiés sur note d’admission. |
| C06 | NON_EXECUTE_ENVIRONNEMENT | Isolation CLI non démontrée : runner.py transmet un exécutable OBSIDIAN_PATH et vault=nom, sans identité PID/profil. Aucun nonce lu par le chemin CLI ; appel non lancé pour préserver l’instance quotidienne. Aucun échec de concurrence déduit. |
| C07 | ADMIS | Nonce, plan/apply différé, statut terminal committed/verified et relecture complète acquis. Incident du contrôleur conservé : mauvais champ state, polling excessif puis 429 à la requête 98. |
| C08 | ADMIS | Nonce, création, remplacement conditionnel et refus de révision périmée qualifiés. Règle de reçus techniques liée aux transaction_id testée sur factice (15 contrôles), à publier avant toute cellule. |
| C09 | ADMIS | Nonce via candidat et backend isolé, création, remplacement et lecture complète qualifiés. Package ISC / LICENSE MIT : divergence déclarée, aucun code redistribué. |
| C10 | ADMIS | Nonce, création, remplacement et décodage de vue numérotée vérifiés. HTTP/SSE natif ; WebSocket et terminal désactivés, CLAUDE_CONFIG_DIR borné au run. LICENSE 0BSD / package MIT déclaré, code non redistribué. |

## Limites

Un agent Codex CLI 0.160.1, gpt-6.1-sol high, serviceTier default. Corpus Margelle commercial vendu par l’auteur d’Optimike ; corpus synthétique publié mais non rejoué en campagne. T1–T4 : une seule répétition. Trois répétitions de T5/T6/T7/T7b/T8 ne donnent pas un taux de risque rare. Les non-joués ne sont ni réussites ni échecs fonctionnels. Aucun contact mainteneur, aucune publication hors de ce dépôt.

## Incidents

- admissions/C02/incident.json : Préparation applicative non stable/LF/datée en 60 s
- admissions/C08/incident.json : 'content'
- admissions/C07/qualification-incident.json : {'jsonrpc': '2.0', 'id': 98, 'error': {'code': -32603, 'message': 'MCP backend rejected the request (status=429).'}}
- cellules/C05-T1-r1/incident.json : AssertionError ; voir trace et amendement de la cellule.
- publication/incident-20261023T0915.json : AssertionError pendant le rejeu masqué de T2-negative-hidden_note.json : ordre différent de deux chemins technical_changes, verdict et erreurs identiques. Publication arrêtée avant commit.
- client-qualification/1792744805696642600/01.stdout.jsonl : Premier client factice sans accès MCP : code-mode host is disabled. Corrigé avant toute cellule ; T2 et coupure/reprise T8 factices qualifiés ensuite.

## Reprise exacte

```json
{
  "state": "ARRET_INCIDENT",
  "utc": "2026-10-23T09:24:30.143327+00:00",
  "next_cell": "C05-T5-r1",
  "candidate_active": false,
  "obsidian_instance_active": false,
  "lock_present": false,
  "command": "python -X utf8 scripts/campaign_run.py",
  "preservation": "Ne rejouer ni effacer un dossier de cellule existant. Les bacs et reçus sont conservés.",
  "last_cell": "C05-T4-r1",
  "last_result": "EFFET_NON_VOULU",
  "last_reason": "HORS_CIBLE; CIBLE_ABSENTE; YAML_OU_UTF8_INVALIDE:absente",
  "incident_cell": "C05-T4-r1"
}
```

## Pilotage

Aucun changement de statut recommandé à ce stade ; statut canonique non audité (coffre quotidien hors périmètre). Prochaine action : suivre le point de reprise exact, puis le manifeste sous les seuils mémoire et verrou. Aucune tâche du coffre modifiée.
