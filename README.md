# Kit ouvert du comparatif MCP Obsidian

Préparation avant essais, pour revue C5. Aucun résultat candidat. Lire `PROTOCOLE-V1.md` puis les manifestes. Le plan contient 160 cellules ; seules T5–T8 sont prévues en trois répétitions.

## Vérifier l’outillage sans installer de candidat

Prérequis déjà utilisés pour qualifier ce kit : Python 3.12.10, PyYAML 6.0.3, Node 24.17.0. La dépendance Python est figée dans requirements.txt ; aucune installation n’est exécutée par ces scripts. Les tests n’utilisent que le serveur factice écrit dans scripts/fake_server.py, lancé localement et arrêté à la fin de chaque scénario.

```powershell
python -X utf8 scripts/test_kit.py
python -X utf8 scripts/redact.py
```

Traces conservées dans preuves/factice/<horodatage>. Les scénarios couvrent stdio, Streamable HTTP, SSE legacy, écritures différées, refus différés, effet puis réponse perdue, et témoins négatifs. Une trace factice n’est pas une preuve runtime d’un candidat réel.

Le corpus `fixtures/synthetique` et son manifeste suffisent à ces tests. Ils ne reproduisent pas les règles/plugins du coffre commercial. Pour préparer la voie Margelle sous licence, sans modifier de coffre existant :

```powershell
python -X utf8 scripts/prepare.py --archive "<archive autorisée ELYSIA-OS-V1-1.0.6.zip>"
```

SHA256 attendu : b69c70dcefe3908e14b1489d90bc748e45d7bb51caeb414c1b7a4e181d44e8ce, 4 385 139 octets. Ne jamais ajouter reference/, fixtures/Margelle-*/ ou runtime/ à un dépôt public. Leur contenu commercial est exclu de ce paquet.

## Retoucher dans l’éditeur isolé

`scripts/retouche-editeur.mjs` est autonome, paramétrable et **qualifié**. Voir `scripts/RETOUCHE-EDITEUR.md` et `preuves/qualification-editeur.json`. Il lit les fichiers ; seul l’éditeur Obsidian les enregistre. Son retour exige la sauvegarde disque exacte. Il ne prend pas le verrou : le contrôleur doit déjà le détenir et vérifier l’instance. Le lanceur ui_qualification.py le fait pour sa propre qualification.

La commande d’insertion accepte le port CDP de G1, son coffre, sa note, son texte et la position. Aucun recours au profil quotidien ni aux ports 27123/27124. Le verrou partagé doit être libéré dès la fin de l’instance. Une saisie CDP est simulée, pas réalisée par une personne.

## Relais et oracles

`relay.py --config <json>` expose <CHEMIN_PRIVE>`adaptateurs/factice.example.json` est un exemple **factice**, pas un adaptateur de candidat. Les dix admissions sont explicitement non effectuées dans manifestes/admissions.json. Les catalogues/artefacts/configs réels sont à figer avant mesure ; une forme inconnue bloque l’injection.

Le relais retient une requête T5–T7, confirme la retouche via l’éditeur et le disque, transmet les arguments intacts et capture la première mutation. Pour une opération pending, le premier effet est observé au disque ou clos par un statut terminal relu par l’agent ; une réparation ne passe pas avant le snapshot. Pour T8, la connexion client est coupée au constat d’effet complet ; le backend demeure vivant. Le client de mesure doit conserver son historique et reprendre par lecture/statut.

`oracles.py <case.json> --out <verdict.json>` juge les snapshots et les traces indépendantes du relais, jamais le seul état annoncé par l’agent. Schéma de case : task, expected_before_tree_sha256, before, after, events, response ; human/first pour T5–T7 et cut pour T8. Les snapshots incluent les bytes en base64, taille et SHA256. Les cas factices publiés fournissent des exemples complets. Les changements de dates non attribués restent indéterminés ; aucune exemption YAML globale. Le dossier de cellule doit figer les chemins techniques exacts et son empreinte d’avant après stabilisation FDM.

## Avant de mesurer ou de publier

Revue C5 du kit, publication du gel horodatée, admission/empreintes des candidats, fournisseur/options identiques, G1 puis les deux séries. Aucun script de ce paquet ne lance la campagne ni n’installe un candidat. Le client Codex doit exposer seulement le relais, avec shell/navigateur/eval/autres MCP interdits et un contexte neuf par cellule. serviceTier default et effort high sont communs.

Le masquage est testé, les originaux privés restent séparés. Les mécanismes des candidats peuvent rester reconnaissables ; masquage de secrets ≠ juge parfaitement aveugle. Les sources et versions des candidats sont documentaires, pas des installations validées.
