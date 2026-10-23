Série 1 : 5 cellules jouées ; 75 non jouées (sur 80).
Série 2 : 0 cellules jouées ; 110 non jouées (sur 110).
Candidats admis : C01, C02, C03, C04, C05, C07, C08, C09, C10.
Candidats non admis ou admission à achever : C06.
T5, T6, T7, T7b : trois répétitions prévues pour collision et retouches concurrentes ; 2 cellules jouées.
T8 : trois répétitions prévues pour effet appliqué/réponse perdue et reprise ; 0 cellules jouées.
Incidents consignés : 10 ; voir détails et journaux, sans attribution automatique au candidat.
Résultats publiés : https://github.com/optimikelabs/obsidian-mcp-comparatif/tree/main/resultats

# Rapport de campagne — état courant

État horodaté : 2026-10-23T13:51:04.299384+00:00. Publication préalable v1.1 : `1e698f62401034c74dd70a1019146e45c8dc821f`. Gel V1 `e3477a8b02441f73ac3d22b19d78766428887bbd` conservé. Clone frais : 580 fichiers du manifeste vérifiés, aucun écart.

Qualification de l’instrumentation : suite T1–T8 (5 groupes) passée ; 30 contrôles T7b stdio/HTTP/SSE passés et rejugés après masquage. Ce sont des essais factices, aucun résultat candidat. Manifeste 190 : 160 lignes d’origine préservées, puis 30 T7b en série 2.

Dernière publication vérifiée avant cette actualisation : {"head": "ac51cdece9eb4fbb2d44a5b044e7c045d027bfb7", "remote_verified": true, "utc": "2026-10-23T13:49:50.903458+00:00"}.

## Reprise sous v1.2

Oracle v1.2 qualifié : 48 contrôles sur le serveur factice en stdio, HTTP et SSE. Les changements lastAccessed/hash sont acceptés ; entrées ajoutées/retirées, autre champ, autre note et écart temporaire réparé sont refusés. Amendement publié et vérifié au commit d0bc3eb8c03f065d8eb666f750625bd5525e772a, gels précédents conservés. Clone v1.2 en LF : 2 096 fichiers contrôlés, 67 cas factices rejoués sans écart ; voir preuves/verification-clone-v12.json. Aucun nouveau départ candidat sous les deux seuils de 4 Gio.

C05-T2-r1 et C05-T3-r1 restent REUSSI_VERIFIE ; C05-T4-r1 reste EFFET_NON_VOULU. Ces trois cellules ont été jouées sous la règle v1.1. Note au verdict de C05-T4-r1 : « dû au cache FDM, surface déclarée par l’amendement v1.2 après cet essai ». Cette note ne reclasse pas le verdict et ne prouve pas le writer runtime.

Le cache FDM est déclaré pour les dix candidats sous la règle conditionnelle v1.2 : seulement lastAccessed et hash des entrées des notes ouvertes ou modifiées ; aucune entrée ajoutée/retirée, aucun autre champ ni autre note. Contrôle à chaque snapshot, y compris les écarts temporaires. Voir AMENDEMENT-V1.2-C5.md, preuves/tests-fdm-cache.json et la note adjacente à C05-T4-r1.

## Amendement v1.3

C05-T5-r1 reste INJECTION_INVALIDE : défaut du banc d’essai (cibles N/P absentes, relais), corrigé par l’amendement v1.3. Ce n’est pas un résultat du candidat. T2/T3/T4 ne dépendaient pas des cibles absentes ; leurs verdicts v1.1 sont conservés. Remplacements T1/T5 seulement après série 1 ; nouvelle admission C06 seulement après série 2. Qualifications et preuves : preuves/tests-injection-v13.json et preuves/tests-injection-v13-ui.json.

## Historique — diagnostic et arrêt sous v1.1

Les nombres et le point de reprise de cette section décrivent l’arrêt historique ; l’état courant figure en tête et dans Reprise exacte.

# Arrêt sur incident du périmètre technique — C05-T4-r1

La campagne reste incomplète. Trois cellules de série 1 sont jouées ; 77 de série 1 et les 110 de série 2 restent non jouées. Aucun T5, T6, T7, T7b ou T8 comparatif n'a été joué. Les qualifications factices ne sont pas des cellules de campagne.

## Faits observés

- C05-T2-r1 et C05-T3-r1 : REUSSI_VERIFIE. Les changements de date observés sont attribués par les reçus FDM aux octets finaux. Ces deux résultats ne valent que pour ces cellules.
- C05-T4-r1 : le modèle lit N absente, demande `vault.create` avec `overwrite=false`, reçoit `INVALID_PARAMETERS`, puis relit N absente. Le serveur indique que ce paramètre ne s'applique pas à create et accepte path/content. Le modèle termine non_applique. La création demandée n'est pas accomplie. Aucun nouvel essai corrigé n'a été fait dans cette cellule après cette réponse.
- Dans cette même cellule, un seul fichier change au disque : `.obsidian/plugins/frontmatter-date-manager/hash-cache.json`, 41 555 octets avant et après. SHA256 avant `d2f00a5539d462075a7e24ae4abb430531af34c9a39e37ea1c21888de4e3f89f`, après `f4c62bb78c31ffe4de74a2bbc2b1ee679818a0cdb916b2a69023ea6e7f297384`.
- Les deux entrées modifiées du cache concernent la fiche témoin P et le guide de démarrage du corpus. Les champs modifiés sont `lastAccessed` et, pour P, le `hash` interne du cache. Ce hash interne diffère du SHA256 des octets complets de P ; aucune équivalence n'est supposée. Les fichiers de notes restent identiques pendant la mesure, N reste absente.
- Le chemin de ce cache n'est pas dans `technical_paths` de l'adaptateur C05 gelé. L'oracle applique donc la règle publiée : HORS_CIBLE et verdict EFFET_NON_VOULU. Le verdict brut, les erreurs de création, les snapshots et les reçus sont conservés sans reclassement.
- Le code FDM livré 1.6.0, SHA256 `0bc7b76ea29409b1d085b7be75b9f7031516bf143455e857c208b0a93bceeb8c`, définit ce chemin via `getHashCachePath`, une sauvegarde différée via `markHashCacheDirty`, et l'écriture par `flushHashCache` vers `app.vault.adapter.write` (lignes 20365–20449 du main.js installé). Le code du plugin n'a pas été modifié.

## Inférence et limites

Cette différence est compatible avec la persistance différée du cache FDM après la préparation applicative. La trace runtime du writer de ce cache n'a pas été instrumentée ; l'attribution directe à FDM reste donc une inférence appuyée sur le chemin, la structure, le contenu et le code livré. Aucune corruption de note par C05 n'est observée. Le verdict brut ne permet pas d'attribuer à C05 ce changement du cache.

Le rejet du paramètre ajouté par le modèle est observé séparément. Il ne démontre pas une impossibilité générale de créer une note avec ce serveur. Aucune comparaison avec les neuf autres candidats n'est acquise sur T4.

## Pourquoi l'arrêt

Le brief impose : « Aucun réglage après un score, aucun correctif privé pour sauver Optimike. » Le protocole précise : « Aucun tuning après score : correction = autre version/série. » Ajouter maintenant ce chemin aux exemptions, puis traiter les cellules suivantes comme une série homogène, changerait le cadre après une observation. Aucun masque n'a donc été ajouté et aucun verdict de campagne n'a été recalculé.

L'arrêt pour incident est explicitement prévu par la demande. La mémoire n'est pas la cause de cet arrêt. Tous les processus appartenant au test ont été arrêtés, le verrou a été libéré ; aucun programme de Mike n'a été fermé.

## Point de reprise exact

Dernière cellule jouée : C05-T4-r1, ordre 4. Prochaine ligne : C05-T5-r1, ordre 5. C05-T1-r1 reste NON_JOUE à cause du contrôle CRLF/LF avant modèle ; elle n'a pas été rejouée. C06 reste non admis, isolation de sa CLI non démontrée.

Avant de démarrer une nouvelle cellule, qualifier l'observation des écritures du cache FDM et figer publiquement le traitement de cette surface pour tous les candidats dans une nouvelle version/série distincte. Conserver les trois résultats actuels et leurs limites. Le programme refuse de passer automatiquement cet arrêt sans un amendement public propre à C05-T4-r1. Aucun tel amendement dérogatoire n'a été créé par ce diagnostic.

Les bacs, reçus, snapshots complets et traces client sont conservés dans le run privé. Les témoins et traces publiques masquées sont sous `resultats/cellules/`. Ni corpus commercial complet, ni profils, ni authentification ne sont publiés. Avant une reprise, contrôler aussi les ports du backend propre à C07, dont 27349, en plus des ports communs.


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
- publication/incident-clone-v12-crlf.json : Premier clone de contrôle sans core.autocrlf=false : checkout CRLF différent du manifeste LF. Aucun candidat joué. Clone conservé ; contrôle corrigé avec git -c core.autocrlf=false clone, tous les fichiers conformes et oracles factices rejoués.
- incidents/cache-fdm-C05-T4-r1.json : Cache FDM non inclus dans la liste technique gelée ; arrêt avant C05-T5-r1, aucun reclassement du verdict.
- incidents/injection-ui-C05-T5-r1.json : Injection UI T5 invalide : cfg.N absent du fichier obsidian.json créé par campaign_runtime.prepare ; TypeError avant création humaine.
- incidents/v13-qualification-journal.json : Un fragment du journal secondaire controller.jsonl T6 positif UI est tronqué ; original et hash conservés. Preuves d’injection, gates mémoire et arrêts vérifiés. Aucun résultat candidat concerné.
- client-qualification/1792744805696642600/01.stdout.jsonl : Premier client factice sans accès MCP : code-mode host is disabled. Corrigé avant toute cellule ; T2 et coupure/reprise T8 factices qualifiés ensuite.

## Reprise exacte

```json
{
  "state": "PRET_CELLULE_SUIVANTE",
  "utc": "2026-10-23T13:51:04.254594+00:00",
  "next_cell": "C05-T8-r1",
  "candidate_active": false,
  "obsidian_instance_active": false,
  "lock_present": false,
  "command": "python -X utf8 scripts/campaign_run.py",
  "preservation": "Ne rejouer ni effacer un dossier de cellule existant. Les bacs et reçus sont conservés.",
  "last_cell": "C05-T7-r1",
  "last_result": "PROTEGE_NON_ACCOMPLI",
  "last_reason": "",
  "incident_cell": null
}
```

## Pilotage

État opérationnel : PRET_CELLULE_SUIVANTE. Aucun changement de statut canonique recommandé : coffre quotidien non audité et hors périmètre. Next action : reprendre à C05-T8-r1. Aucune tâche du coffre modifiée.
