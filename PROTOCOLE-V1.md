# Protocole v1.1 — test comparatif ouvert des serveurs MCP Obsidian

Version v1.1 du 23 octobre 2026, avant tout essai candidat. Gel V1 publié au commit `e3477a8b02441f73ac3d22b19d78766428887bbd`, conservé dans l’historique. Amendements C5 publiés avant admission. La décision C5 prévaut sur le brouillon. Aucun score n’existe dans ce kit. Les traces du serveur factice sont uniquement des tests de l’instrumentation.

## 1. Contrat, responsabilité et ordre des opérations

Question : avec le même agent et le même coffre Margelle, quels gestes chaque serveur permet-il d’achever, vérifier et reprendre, avec quels effets non voulus et coûts ? Mike est l’auteur d’Optimike et du site qui présentera le test. Ce conflit d’intérêt est déclaré. C5 relit le panel, les oracles, l’équité et le masquage ; une revue IA ne vaut pas reproduction indépendante par un tiers.

Panel : C01–C10, sans retrait opportuniste. H01 est exclu selon la règle « dépôt archivé », ratifiée avant observation. Versions documentées le 23/10, pas de latest mobile. Les artefacts installés devront être empreintés à l’admission ; aucune installation de candidat n’est incluse dans la préparation du kit.

Plan arrêté : **190 cellules**. Série 1 inchangée : r1, T1–T8, dix candidats (80). Série 2 : r2/r3 T5, T6, T7 et T8 (80), puis T7b r1/r2/r3 (30), soit 110. Les 160 lignes et leur ordre du gel V1 restent inchangés. Les 30 lignes T7b sont ajoutées après ces lignes, par répétition 1, 2, 3 et même ordre SHA256 UTF-8 de `margelle-mcp-20261024-v1|r|candidate`. `manifestes/cellules-190.json` et CSV font foi ; les manifestes 160 restent historiques. Tout est NON_JOUE avant les essais. Injection invalide : un remplacement maximum, les deux traces conservées. Aucun rejeu jusqu’au succès.

**Seules les tâches effectivement jouées trois fois peuvent fonder une phrase de résultat.** T1–T4 servent à l’admission et à la description de gestes courants ; ne pas extrapoler leurs observations uniques en résultat répété. T5, T6, T7, T7b et T8 : trois répétitions ne permettent ni taux fiable de risque rare ni test de significativité suffisant. Pas de classement global pondéré, pas de superlatif de sécurité, non-joués toujours visibles avec leur raison.

Ordre autorisé par Mike dans DECISIONS-C5 : kit prêt, **revue C5**, publication publique du gel sous optimikelabs, G1, série 1, série 2. G1 a précédé la campagne, selon l’ordre de lancement du 23/10. Mike a autorisé la campagne autonome et la publication de ses résultats dans le seul dépôt du test ; les amendements précèdent les admissions. Toute phrase publique résultante : C5 puis contre-audit nemesis.

Même agent pour tous : **Codex CLI 0.160.1, gpt-6.1-sol, reasoning effort high, serviceTier default, vitesse normale**, endpoint/fournisseur identiques, contexte neuf par cellule ; T8 conserve l’historique lors de la reconnexion. Alias de modèle non immuable : limite déclarée. Les options/fournisseur réellement chargés doivent être exportés et figés à l’admission ; l’agent de préparation n’est pas l’agent de mesure. Démarrage depuis un répertoire client vide, hors du coffre et hors des scripts/oracles ; seul le MCP candidat via le relais est exposé. Aucun MCP de secours. Le client ne reçoit ni le chemin P pour T1, ni les oracles, ni le mapping du juge. Les règles du coffre accessibles au candidat sont les mêmes pour tous.

Le client de mesure interdit shell, accès disque direct, navigateur, eval/commandes arbitraires, installation, outils plugins/workspaces et autres MCP. Fiches techniques de même structure et plafond 400 mots, issues des docs ; protections existantes autorisées, aucune précondition inventée. Capturer catalogue et coût de contexte, outils réellement utilisés, options, hashes de configuration et de prompt. Un contournement reste dans les traces et invalide le chemin concerné.

## 2. Candidats : version, installation réelle et garanties annoncées

Les parcours suivants sont **documentés, à exécuter ultérieurement dans le bac**. Ils ne sont pas déclarés installés ou fonctionnels sur le poste cette nuit. Windows est le système de campagne ; la portabilité documentée n’est pas une validation Mac/Linux. Aucune commande d’installation citée ici n’a été exécutée.

### C01 — Local REST API with MCP 5.5.2

- **Version/licence :** `coddingtonbear/obsidian-local-rest-api`, 5.5.2 publiée le 17/10/2026 à 16:23:52 UTC ; SHA `7c603fbc42918bd9ec6f34ab5b46300bac0d0eaa`. MIT. Manifest : Obsidian ≥ 1.13.1. Le Node ≥ 22 du package concerne le développement, pas un runtime Node séparé requis pour le plugin compilé.
- **Installation :** fichiers de release 5.5.2 dans `.obsidian/plugins/obsidian-local-rest-api` du coffre jetable ; activation, clé propre et ports libres. Client vers `/mcp/` avec Bearer : HTTP de boucle locale activé explicitement ou HTTPS avec certificat dédié. Aucun intermédiaire Python/Node avec un client HTTP compatible ; un éventuel `mcp-remote` doit être versionné. Obsidian ouvert nécessaire.
- **Écriture :** `vault_write`, `vault_append`, `vault_patch`, delete/move/copy ; sections et propriétés via patch. `vault_read` retourne `version`. `ifMatch` sur les écritures, `ifNoneMatch: "*"` sur write/append pour la création conditionnelle ; version périmée : refus 412 et aucune écriture annoncée. File des écritures API par fichier. La précondition reste à utiliser, elle n’est pas implicite dans toute requête.
- **Limites :** la file API ne verrouille pas les acteurs externes/éditeur. Pas de plan durable équivalent établi par cette lecture, ni de preuve runtime de reprise après réponse perdue. Outils texte et REST binaire ont des surfaces différentes. Un wrapper ne reçoit pas automatiquement les paramètres MCP natifs.

Sources : [README 5.5.2](https://github.com/coddingtonbear/obsidian-local-rest-api/blob/5.5.2/README.md), [manifest](https://github.com/coddingtonbear/obsidian-local-rest-api/blob/5.5.2/manifest.json), [implémentation MCP](https://github.com/coddingtonbear/obsidian-local-rest-api/blob/5.5.2/src/mcpHandler.ts), [release](https://github.com/coddingtonbear/obsidian-local-rest-api/releases/tag/5.5.2). Consultation : 23/10/2026. Captures : `source-lra.json`, `evidence-lra-mcp-source.json`.

### C02 — MCPVault 0.17.0

- **Version/licence :** `bitbonsai/mcpvault`, v0.17.0 du 22/10/2026 à 12:59:11 UTC ; npm à 12:53:37 UTC ; SHA `df3b4d14acd4fbb4265fe6ce52784677717e6e01`. MIT ; Node ≥ 20.
- **Installation :** paquet `@bitbonsai/mcpvault@0.17.0`, dépendances/cache npm confinés au run ; lancement stdio avec chemin absolu du coffre. Le parcours `npx` télécharge et exécute : ce n’est pas une absence d’installation. Aucun plugin requis, Obsidian peut être fermé ; il sera ouvert dans notre condition commune pour inclure UI et gestionnaire de dates.
- **Écriture :** `write_note` (overwrite par défaut, append, prepend), patch, frontmatter/tags, déplacements/suppressions. Préservation du format des propriétés non modifiées annoncée ; confinement de chemins ; confirmation par chemin pour certaines destructions. Exclusions 0.17 de recherche/listing : pas une interdiction générale d’accès direct.
- **Limites :** précondition de révision et reçu durable non établis dans le README lu, pas déclarés impossibles. Accès fichier, sans couche des objets des plugins ni verrou automatique de l’éditeur. T5 doit éprouver la collision, sans présumer que `write_note` crée exclusivement.

Sources : [README v0.17.0](https://github.com/bitbonsai/mcpvault/blob/v0.17.0/README.md), [release](https://github.com/bitbonsai/mcpvault/releases/tag/v0.17.0), [npm](https://registry.npmjs.org/@bitbonsai%2fmcpvault). Consultation : 23/10/2026. `source-vault.json`, `evidence-npm-vault.json`.

### C03 — MarkusPfundstein/mcp-obsidian 0.2.3

- **Version/licence :** PyPI confirme **0.2.3**, publiée le 20/08/2026 à 13:00:14 UTC. GitHub au SHA `5ee0b84fa8319fd2fdf0db0ee1febb065e712a15` indique 0.2.2 dans pyproject ; pas de release latest. Ne pas appeler 0.2.2 le paquet PyPI testé. Dépôt sous MIT ; conserver aussi la licence de l’artefact. Python ≥ 3.11 ; PyPI impose `mcp>=1.1.0,<2.0.0`.
- **Installation :** environnement Python jetable dans le run, `mcp-obsidian==0.2.3` et dépendances figées ; lancement stdio `mcp-obsidian`. Variante uvx possible avec version/cache locaux. `OBSIDIAN_API_KEY`, `OBSIDIAN_HOST`, `OBSIDIAN_PORT` vers REST 5.5.2 de l’instance isolée ; Obsidian et plugin REST ouverts. Présence actuelle du paquet non vérifiée.
- **Écriture :** append, patch heading/block/frontmatter, suppression confirmée ; le code amont expose notamment `obsidian_append_content`, `obsidian_patch_content`. Aucun `ifMatch` trouvé dans ce schéma source. L’adaptateur devra être établi sur **l’artefact 0.2.3**, car main n’atteste pas ses octets.
- **Limites :** pas de journal durable/relecture automatique établis ici. Le backend récent ne transmet pas ses préconditions au wrapper. SHA256 du wheel PyPI : `573491093065f0af7546c8a26b884974997e8d91f148cb9d8471d4857c1b6286`.

Sources : [PyPI](https://pypi.org/pypi/mcp-obsidian/json), [pyproject figé](https://github.com/MarkusPfundstein/mcp-obsidian/blob/5ee0b84fa8319fd2fdf0db0ee1febb065e712a15/pyproject.toml), [tools amont](https://github.com/MarkusPfundstein/mcp-obsidian/blob/5ee0b84fa8319fd2fdf0db0ee1febb065e712a15/src/mcp_obsidian/tools.py). Consultation : 23/10/2026. `source-markus.json`, `evidence-pypi-markus.json`, `evidence-markus-tools.json`.

### C04 — cyanheads/obsidian-mcp-server 3.7.0

- **Version/licence :** v3.7.0 du 06/10/2026 à 06:02:24 UTC ; npm 06:00:51 UTC ; SHA `1f0b662214fc34a1db0773f00f02d2c282ade622`. Apache-2.0. Node ≥ 24 ou Bun ≥ 1.4 ; Node installé suffit au parcours npm, sans ajouter Bun.
- **Installation :** paquet local `obsidian-mcp-server@3.7.0`, stdio (`MCP_TRANSPORT_TYPE=stdio`), `OBSIDIAN_API_KEY`/`OBSIDIAN_BASE_URL` vers REST 5.5.2 isolé. Obsidian ouvert. `.mcpb` et Docker existent, non nécessaires au client commun ; aucun Docker supplémentaire.
- **Écriture :** write, append, patch, remplacements ciblés, `obsidian_manage_frontmatter`, tags et suppression. Whole-file write existant refusé sauf `overwrite:true`. Append/patch ciblés refusent le contenu préexistant selon leurs options : pas une preuve d’idempotence durable générale. Édition body-only, validation YAML et permissions par chemins documentées.
- **Limites :** `ifMatch` du wrapper et statut/reprise durables non établis dans ce README. REST récent ne prouve pas leur exposition par le wrapper. Suppression permanente par défaut, confirmation configurable. Aucune protection des écritures par d’autres chemins.

Sources : [README v3.7.0](https://github.com/cyanheads/obsidian-mcp-server/blob/v3.7.0/README.md), [package](https://github.com/cyanheads/obsidian-mcp-server/blob/v3.7.0/package.json), [npm](https://registry.npmjs.org/obsidian-mcp-server), [release](https://github.com/cyanheads/obsidian-mcp-server/releases/tag/v3.7.0). Consultation : 23/10/2026. `source-cyan.json`, `evidence-npm-cyan.json`.

### C05 — Semantic Notes Vault MCP 0.12.9

- **Version/licence :** `aaronsb/obsidian-mcp-plugin`, 0.12.9 du 16/09/2026 à 01:09:16 UTC ; SHA `945996ab98aae729156d6919456df2b2d78c2dbd`. MIT ; Obsidian ≥ 1.13.0 dans le manifest.
- **Installation :** plugin `semantic-vault-mcp` de la release exacte dans le bac ; activation, clé et ports propres ; HTTP natif `/mcp` (documenté 3001, HTTPS 3443), ports adaptés à l’instance. `.mcpb` est un parcours Claude Desktop, pas une nécessité ; son update est distinct du plugin. Dataview requis seulement pour ses requêtes, hors périmètre commun. Obsidian ouvert.
- **Écriture :** familles `vault` create/update/delete/move/split/combine et `edit` (passage/append/section). Droits par opérations/chemins, `.mcpignore`, readonly. Des versions récentes refusent les paramètres inapplicables aux actions destructives ; ne pas convertir ce refus en garantie universelle de CAS.
- **Limites :** token de révision et reçu durable non établis par les docs lues. Le lien annoncé `docs/tools/edit.md` retourne 404 ; catalogue réel/sources à compléter avant admission. Relecture possible par vault.read, garantie de relecture automatique non établie.

Sources : [README 0.12.9](https://github.com/aaronsb/obsidian-mcp-plugin/blob/0.12.9/README.md), [manifest](https://github.com/aaronsb/obsidian-mcp-plugin/blob/0.12.9/manifest.json), [vault](https://github.com/aaronsb/obsidian-mcp-plugin/blob/0.12.9/docs/tools/vault.md), [releases](https://github.com/aaronsb/obsidian-mcp-plugin/releases). Consultation : 23/10/2026. `source-semantic.json`, `evidence-semantic-vault.json`, `evidence-semantic-release.json`.

### C06 — Storks/obsidian-mcp 0.1.0, sans release

- **Version/licence :** pyproject 0.1.0 ; SHA `a932c9e0e690e88063f23a2dd93814afc921947d`, dernier commit 28/02/2026 à 06:31:13 UTC. Pas de release latest. README : MIT ; fichier LICENSE absent au chemin consulté, licence seulement déclarée.
- **Installation :** source de ce SHA dans le run, Python ≥ 3.11, `uv sync` avec environnement/cache locaux, stdio `uv run --directory <source> obsidian-mcp`. Obsidian ≥ 1.12 et CLI activée. README Windows demande encore `Obsidian.com` et mentionne Catalyst : texte ancien, pas pris pour une règle commerciale actuelle. Le redirecteur existe sur le poste ; aucune activation de CLI cette nuit.
- **Écriture :** wrappers CLI create/overwrite, append/prepend, propriétés, move/delete et tâches. Cible `vault` ou `OBSIDIAN_VAULT`, binaire `OBSIDIAN_PATH`. CAS/journal/statut durable non établis dans le README.
- **Limite poste :** la CLI peut parler à l’instance quotidienne plutôt qu’à l’instance isolée. Le nom du coffre ne prouve pas le bon processus. Admission : témoin lu par **ce chemin CLI** dans l’instance d’essai, sans ouvrir le bac dans le profil quotidien. Si impossible sans toucher Mike : `NON_EXECUTE_ENVIRONNEMENT — isolation CLI non démontrée`, pas échec de concurrence. Commandes plugin/workspace interdites aux tâches.

Sources : [README figé](https://github.com/Storks/obsidian-mcp/blob/a932c9e0e690e88063f23a2dd93814afc921947d/README.md), [pyproject](https://github.com/Storks/obsidian-mcp/blob/a932c9e0e690e88063f23a2dd93814afc921947d/pyproject.toml), [commits](https://github.com/Storks/obsidian-mcp/commits/master/). Consultation : 23/10/2026. `source-storks.json`. Compatibilité CLI non essayée ici.

### C07 — Optimike Obsidian MCP 3.13.0

- **Version/licence :** v3.13.0 du 18/10/2026 à 00:08:11 UTC ; SHA public `8696687e1a449f5f74550331ac902b0b358b4ccf`. Apache-2.0, filiation cyanheads déclarée. Mike en est l’auteur. Version privée modifiée et lanceur/backend quotidien exclus de la condition mesurée.
- **Installation :** archive publique figée, Node ≥ 22.12, dépendances locales et build ; stdio `dist/stdio-proxy.js`, profil `operational` à vérifier par tools/list. `OBSIDIAN_VAULT`, `OBSIDIAN_RUNTIME_MODE=live`, `OBSIDIAN_BASE_URL`, clé et journaux vers le bac. REST 5.5.2 + Atomic Write Bridge **0.8.1** pour notes/propriétés protégées. Bases Bridge **1.2.2** seulement si une famille choisie l’exige ; Bases/Canvas/Operon/sémantique hors des huit tâches, sans installation de leurs dépendances par principe. Le guide bundle demande de fermer Obsidian : seulement l’instance de test, jamais celle de Mike ; sinon préparation manuelle des fichiers du bac et écart déclaré.
- **Écriture :** text patch, remplacement, frontmatter en plan/apply/status/recover ; préconditions scellées, refus de révision périmée, postflight annoncés. Interrupteurs de mutations opt-in et permissions indépendants du profil : exporter les valeurs exactes avant gel, pas les deviner. Consigner aussi les outils directs du catalogue et leur usage par l’agent.
- **Limites :** seulement les gestes couverts et chemins empruntés, pas un verrou de toutes les écritures ni une garantie d’accord humain. Aucune création exclusive présumée pour T4/T5 : vérifier la surface **publique 3.13.0**. `pending` n’est pas committed/verified ; attendre status dans le budget commun.
- **Historique distinct :** A rapporte npm 58 s puis build 14 s, premier incident, copie de plugins et réglages. Ce n’est pas le temps complet d’installation ni un novice chronométré. Ses 34/48 essais MCP portaient sur 1.0.5, pas sur la 1.0.6 de cette campagne.

Sources : [README 3.13.0](https://github.com/optimikelabs/optimike-obsidian-mcp/blob/v3.13.0/README.md), [installation](https://github.com/optimikelabs/optimike-obsidian-mcp/blob/v3.13.0/docs/installation-options.md), [bundle](https://github.com/optimikelabs/optimike-obsidian-mcp/blob/v3.13.0/docs/bridge-packaging.md), [release](https://github.com/optimikelabs/optimike-obsidian-mcp/releases/tag/v3.13.0), `A-mise-en-route/RAPPORT.md`. Consultation : 23/10/2026. `source-optimike.json`, `evidence-optimike-install.json`, `evidence-optimike-bundle.json`.

### C08 — StevenStavrakis/obsidian-mcp 2.0.1 — ajout nécessaire

- **Version/licence :** npm `obsidian-mcp` **2.0.1**, 14/08/2026 à 01:25:53 UTC. GitHub latest reste v2.0.0 (00:02:32 UTC) : tester le paquet 2.0.1. MIT ; Node ≥ 22 ; 742 étoiles au relevé.
- **Installation :** paquet local `obsidian-mcp@2.0.1` ; stdio `serve --vault test=<chemin absolu>`. `.obsidian` doit exister. Aucun plugin, Obsidian peut être fermé mais reste ouvert dans la série commune. Le README distribué 2.0.1 donne npx ; celui du tag 2.0.0 proposait d’abord le global, non retenu.
- **Écriture :** create atomique sans écrasement, edit append/prepend/remplacement exact, tags et move/delete. Read retourne etag SHA256 ; `if_match` pour edit/move/delete, `expected_etags` pour tags ; `REVISION_CONFLICT` annoncé. Mutations journalisées, remplacement atomique, transactions, snapshots/récupération CLI serveur arrêté : alternative explicite aux garanties d’Optimike.
- **Limites :** pas d’outil dédié de propriété quelconque identifié, mais édition exacte du YAML autorisée pour T3 ; pas d’objets des plugins. Restauration refuse un contenu changé depuis la transaction ; pas automatiquement un statut MCP de réponse perdue. Idempotence après reconnexion non présumée.

Sources : [registre npm](https://registry.npmjs.org/obsidian-mcp), [paquet 2.0.1](https://registry.npmjs.org/obsidian-mcp/-/obsidian-mcp-2.0.1.tgz), [README 2.0.0](https://github.com/StevenStavrakis/obsidian-mcp/blob/v2.0.0/README.md). Consultation : 23/10/2026. `evidence-steven-published.json` contient le README réellement distribué ; `evidence-npm-steven.json`, `source-steven.json`.

### C09 — newtype-01 / @huangyihe/obsidian-mcp 1.6.0 — ajout

- **Version/licence :** npm stable **1.6.0**, 08/07/2025 à 08:01:48 UTC ; gitHead npm `8d3388eaea55dd8ce9961424ed704c22e5d07a5a`. Main GitHub annonce 1.7.1-beta, manifest DXT 1.6.0 ; pas de release latest. **Package ISC, LICENSE distribué MIT** : incohérence à signaler, clarification avant redistribution. 310 étoiles.
- **Installation :** Node ≥ 16, paquet local `@huangyihe/obsidian-mcp@1.6.0`, stdio ; `OBSIDIAN_VAULT_PATH`, `OBSIDIAN_API_TOKEN`, `OBSIDIAN_API_PORT` vers le bac/REST. README distribué demande Obsidian et REST. DXT et source possibles ; pas de compilation de main bêta en lieu de stable.
- **Écriture :** create/update par remplacements, delete/move/folders. Main promet des insertions PATCH plus riches et un fallback filesystem ; le README **publié 1.6.0** est antérieur : ne pas lui attribuer ces ajouts sans inspection de l’artefact/catalogue. Précondition de version, journal durable, relecture automatique non établis dans la doc publiée lue.
- **Limites :** propriété via texte faute d’outil dédié établi ; contrôler la cible de tout fallback éventuel. Un fallback ne doit pas masquer une mauvaise cible REST. Les écarts licence/version sont des points d’admission documentaire, pas des défauts runtime déjà observés.

Sources : [npm](https://registry.npmjs.org/@huangyihe%2fobsidian-mcp), [dépôt](https://github.com/newtype-01/obsidian-mcp), artefact stable capturé dans `evidence-newtype-published.json`. Consultation : 23/10/2026. `evidence-newtype-registry.json`, `detail-newtype-01.json`, `screen-newtype-01.json`.

### C10 — iansinnott/obsidian-claude-code-mcp 1.1.8 — ajout

- **Version/licence :** release 1.1.8 du 23/06/2025 à 06:07:06 UTC ; 355 étoiles. Manifest desktop-only, Obsidian ≥ 1.0.0. **LICENSE 0BSD mais package MIT** : conserver les deux déclarations, clarification pour redistribution.
- **Installation :** plugin `claude-code-mcp` de cette release dans l’instance isolée, activation et port propre. MCP HTTP/SSE legacy `/sse`, port documenté 22360 ; ne pas confondre avec l’intégration IDE WebSocket de Claude Code. Même client que les autres via HTTP, ou pont versionné dont le coût est enregistré. `CLAUDE_CONFIG_DIR`<CHEMIN_PRIVE>
- **Écriture :** outils partagés `view`, `str_replace`, `create`, `insert`. Au tag, str_replace relit et cherche une occurrence unique ; create vérifie l’existence. Cela peut préserver une retouche distincte, sans preuve de CAS atomique lecture/écriture. `obsidian_api`, exécution plus large, interdit comme contournement de la tâche.
- **Limites :** pas de recherche dédiée établie dans les outils partagés, mais liste + lecture autorisées pour T1, appels comptés. Token de révision/reçu durable non établis. Le texte de compatibilité du README date de 2025 : admission à vérifier sur le client figé, sans en faire une vérité actuelle des clients.

Sources : [README](https://github.com/iansinnott/obsidian-claude-code-mcp/blob/1.1.8/README.md), [outils partagés](https://github.com/iansinnott/obsidian-claude-code-mcp/blob/1.1.8/src/tools/general-tools.ts), [release](https://github.com/iansinnott/obsidian-claude-code-mcp/releases/tag/1.1.8), [LICENSE](https://github.com/iansinnott/obsidian-claude-code-mcp/blob/1.1.8/LICENSE). Consultation : 23/10/2026. `detail-iansinnott.json`, `screen-iansinnott.json`, `evidence-ians-tools.json`.

### H01 — MCP Tools for Obsidian 0.2.33 — EXCLU (dépôt archivé, C5)

`jacksteamdev/obsidian-mcp-tools`, 0.2.33 du 13/05/2026 à 16:13:42 UTC, SHA `44f08c00d91a01558aa95ad2ec398d4b5d0aecd4`, MIT selon GitHub, archivé (API et README). Manifest minAppVersion 0.15.0, README demande 1.7.7 : divergence conservée. 827 étoiles ; l’auteur rapporte 87 000 téléchargements, déclaration non mesurée ici.

Parcours : plugin + REST + bouton Install Server ; binaire par plateforme dans le coffre, mais configuration Claude Desktop et logs sous AppData. Templater/Smart Connections servent les fonctions correspondantes, pas nécessaires par principe au test commun. Lecture/recherche/exécution de templates annoncées ; surface d’écriture effective à inventorier, pas de CAS/reçu durable établi par ce README. Il faudrait isoler installateur/config/logs ; jamais son bouton sur le coffre quotidien. Exclusion primaire proposée sur l’archivage, à ratifier avant gel ; aucun résultat inventé à son sujet.

Sources : [README 0.2.33](https://github.com/jacksteamdev/obsidian-mcp-tools/blob/0.2.33/README.md), [release](https://github.com/jacksteamdev/obsidian-mcp-tools/releases/tag/0.2.33). Consultation : 23/10/2026. `source-tools.json`.


## 3. Référence et corpus ouverts

Référence commerciale : archive `ELYSIA-OS-V1-1.0.6.zip`, 4 385 139 octets, racine Margelle/, SHA256 **b69c70dcefe3908e14b1489d90bc748e45d7bb51caeb414c1b7a4e181d44e8ce**. Provenance : build-1.0.6-gel, commit `8ca5bdb729b5aa2c5b2cd84a8a0e611f7ad2ec72`. Le build homonyme revue-aveugle est exclu. Extraction contrôlée :

```powershell
python -X utf8 scripts/prepare.py --archive "<archive Margelle 1.0.6 obtenue sous licence>"
```

La commande contrôle hash et taille **avant** extraction, confine les chemins et refuse les liens. `manifestes/reference.json` contient les tailles, SHA256 individuels et empreinte d’arbre des 749 fichiers, cachés compris. La référence extraite n’est jamais ouverte ; le runtime reçoit une copie. Aucune identité ZIP inventée par reconstruction d’un autre commit. Core 1.0.6, Sources & Clipping 1.0.1, Builder 1.0.1, Hub 0.4.0 : provenance documentaire et fichiers du gel, sans activation de licence.

Fixture P : `Efforts/Projets/Projet témoin — Test MCP.md`, construite depuis le template livré `X/Modèles/Élysia TP/Projets TP.md` avec parser YAML ; inconnu et ordre utile conservés ; statut actif, rang entier 1, parent/échéance vides, next_action « Trier trois captures. ». Témoins booléen, liste, entier, Unicode, clé inconnue ; corps canonique en LF des prompts. N est absent ; Q gelée ; deux leurres et une pièce binaire de 256 octets sont ajoutés. Manifestes distincts référence / fixture commerciale / synthétique ; copier la fixture neuve à chaque cellule.

`fixtures/synthetique` est redistribuable, écrit pour ce kit. P, Q, leurres et binaire sont identiques à l’octet aux cibles commerciales (preuve `manifestes/equivalence.json`). **Les règles, skills, plugins et automatismes du coffre commercial ne sont pas équivalents au corpus synthétique.** Les tests factices sont joués sur ce corpus ouvert. La campagne Margelle se joue avec l’archive sous licence ; une reproduction synthétique devra être rapportée comme un autre environnement. Le paquet public ne contient ni archive commerciale, ni copie de ses règles, skills, template ou plugins. Il contient ses empreintes et la voie d’extraction.

Mode documenté de chaque serveur conservé : les serveurs fichiers peuvent fonctionner sans Obsidian hors préparation et retouches ; ce choix est scellé à l’admission. Pour T5, T6, T7 et T7b, Obsidian est ouvert pour tous. Pour la préparation applicative commune, FDM **1.6.0**, réglages livrés conservés (création/modification, 20 s nouvelles notes, intervalle minimal 30 s, aucune post-update command). Aucun script/agent ne crée ou ne corrige ces champs. Hub sans licence ni mise à jour ; la qualification de l’éditeur a désactivé seulement le Hub dans sa copie, delta publié. À l’admission, désactiver le Hub dans toutes les copies de campagne de la même façon avant le gel final des configurations. Pas de téléchargement réseau nécessaire au Hub.

Préparation identique avant B0 pour les dix candidats : ouvrir P dans l’instance isolée, lancer `editor:save-file`, puis, si les dates manquent encore, `frontmatter-date-manager:update-timestamps-current-file`. Aucun script n’écrit les dates. Consigner commandes, état avant/après, version FDM, normalisation des fins de ligne et preuves disque. B0 seulement après cette préparation et stabilisation. Refus d’un serveur sur cette note préparée = observation à publier, sans correction privée. Limite opérationnelle séparée : Optimike public peut refuser une note importée sans propriété création (`atomic_write_creation_property_missing`).

Avant cellule : cibles stables au moins 5 s dans une fenêtre d’au plus 60 s couvrant FDM ; inventorier ensuite tous les fichiers et sceller l’empreinte d’avant dans le dossier de cellule. Pas de glob .obsidian/**, .elysia/** ou YAML. Liste exacte des chemins techniques attendus à déclarer par configuration avant lancement, avec croissance et deltas visibles. Toute modification de règles, code, plugin ou note hors cible reste un incident.

## 4. Neuf tâches vérifiables par script

Même intention en français et même autorisation explicite d’écrire les cibles. Noms d’outils naturellement différents ; pas de conseil favorisant Optimike. Relire et utiliser la meilleure opération documentée autorisés. Pas de shell, accès disque direct, navigateur, commande Obsidian arbitraire ou autre MCP de secours pour l’agent. L’oracle lit le disque séparément sans donner sa lecture au modèle.

Sortie finale commune à imposer dans chaque prompt : un seul objet JSON UTF-8, champs `task_id`, `path` (relatif au coffre), `etat` (`lu`, `applique`, `conflit`, `non_applique`, `inconnu`), `extrait` (texte exact ou null), `proprietes` (objet JSON, vide si sans objet), `message` (explication courte). T1 exige aussi `proprietes.statut`, T3 `proprietes.rang`. La relecture se prouve par les appels MCP enregistrés, jamais par une simple déclaration du modèle dans cet objet. Le verdict du script demeure indépendant de `etat`.

### T1 — Retrouver et lire le projet actif

Consigne : retrouver le projet actif portant MARGELLE-TEST-2406 ; rendre chemin, statut et passage « Passage à modifier », sans écrire. Recherche native ou liste + lecture autorisées.

Oracle : réponse JSON commune, `path == P`, statut actif et passage exact, comparés au disque caché. Aucun fichier métier modifié/créé/supprimé. Trace d’une vraie lecture par le candidat, pas réponse devinée depuis le prompt. Leurres intacts. Temps/appels mesurés, aucun jugement rédactionnel.

### T2 — Modifier un passage unique

Consigne : dans P, remplacer seulement `Passage à modifier : essai prévu jeudi.` par `Passage à modifier : essai prévu vendredi.`, relire par MCP et rendre l’extrait.

Oracle : une occurrence nouvelle, zéro ancienne ; reste du corps exact, propriétés égales hors dates automatiques bornées, témoins intacts, autre note intacte. Extrait de relecture conforme au disque. Réussite logique, relecture et écarts de format sont des colonnes distinctes.

### T3 — Modifier une propriété structurée

Consigne : changer seulement rang de l’entier 1 à l’entier 2, relire.

Oracle : YAML parseable sans clés dupliquées ; `type(rang) == int`, valeur 2, pas chaîne/booléen. Autres clés/types conservés, corps exact, témoins inconnus/listes/Unicode intacts. Champs perdus = échec. Outil spécialisé facultatif : édition exacte du YAML réussit aussi. Formatage du frontmatter mesuré séparément du sens ; dates automatiques rapportées à part.

### T4 — Créer une note rattachée

Consigne : créer N `Efforts/Projets/Compte rendu — Essai MCP.md`, titre/contenu exacts fournis, `parent: "[[Projet témoin — Test MCP]]"`, sans écrasement ni suffixe ; relire.

Oracle : N au chemin exact, contenu/parent attendus, YAML valide, Q et autres notes intactes. Aucun doublon `… 1.md`, renommage ou création ailleurs. Dates éventuelles seulement observées. Ne prouve pas l’exclusivité de création : T5 teste la collision.

### T5 — Refuser une création en collision

Préparation : N absent. Relais intercepte la requête de création **déjà construite** avant transmission ; l’opérateur crée N par l’éditeur Obsidian de test avec `NOTE HUMAINE À CONSERVER`. Sauvegarde et contrôle disque, puis transmission des arguments originaux, sans ajout d’une précondition absente.

Oracle : note humaine intacte hors dates attribuées à l’automatisation ; aucun doublon/suffixe, aucune réparation ultérieure, pas d’annonce de création agent réussie. Refus sûr = succès de protection, création demandée non accomplie. Distinguer refus serveur et prudence du modèle. Si sauvegarde humaine non observée avant dispatch : injection invalide.

### T6 — Deux écritures distinctes dans la même fiche

Agent prépare T2. Relais retient sa première mutation sur P avant dispatch (apply ou écriture directe). Retouche par l’éditeur : `Témoin humain : correction H-2406.` remplace la version initiale. Sauvegarde observée, snapshot H, puis mutation originale transmise. Après refus/relecture, l’agent peut reconstruire pour atteindre la demande.

Oracle final : correction humaine ET vendredi une fois, reste préservé. Capturer aussi l’état immédiatement après la **première mutation**, avant réparation : perte temporaire puis restitution reste un incident. Patch ciblé sans refus et CAS refusé puis reconstruit peuvent tous deux être sûrs ; publier leurs coûts/refus séparément. Comparaison de la première mutation contre H, pas contre l’état antérieur à l’humain.

### T7 — Deux intentions incompatibles sur un passage

Même barrière, mais la retouche UI remplace jeudi par `Passage à modifier : annulé par la correction H-2406.` ; la requête préparée demande vendredi. Prompt commun : ne pas remplacer une retouche humaine contradictoire, signaler le conflit. Le modèle ne tranche pas à la place de l’humain.

Oracle : version humaine conservée, vendredi absent, aucun autre contenu touché ; statut final conflit/non appliqué. Distinguer refus mécanique et détection par relecture. Vendredi silencieusement appliqué = mise à jour perdue, même avec retour success et relecture. Refus sûr : protection réussie, écriture non accomplie. Sauvegarde humaine non prouvée avant dispatch : injection invalide.

### T7b — Retouche après lecture, avant le premier plan ou la première écriture

Même intention contradictoire que T7. L’agent doit d’abord lire P par MCP. Le relais enregistre la réponse livrée et son hash, puis retient sa première requête déjà construite de plan (si cette surface existe) ou de mutation directe, avant dispatch. L’adaptateur déclare séparément `preparation_tools` et `mutation_tools` ; aucun champ ni précondition ne sont ajoutés. Une lecture absente ou divergente invalide l’injection.

La retouche éditeur remplace jeudi par `Passage à modifier : annulé par la correction H-2406.`. Sauvegarde exacte, snapshot H, dispatch original. Pour Optimike, la retouche précède donc le plan. Capturer la première mutation réelle, même après un plan ; si refus au plan sans mutation, conserver un snapshot terminal identifié. Une perte temporaire puis réparation reste une perte. Oracle : contenu humain préservé, vendredi absent, aucun autre changement, réponse conflit/non_applique et relecture MCP prouvée. Plan commencé sur la note récente ne prouve pas que l’intention de l’agent respecte cette note.

T7b est en série 2, trois répétitions par candidat. Qualification factice : `scripts/test_t7b.py`, stdio/HTTP/SSE, refus CAS direct, refus au plan, patch exact, écrasement par intention périmée, perte temporaire réparée et témoins d’injection invalide. Ces cas ne sont pas des mesures de candidats.

### T8 — Effet appliqué, réponse perdue

Consigne : ajouter une fois `Trace de suivi : EVENEMENT-2406.` à P et vérifier après reconnexion ; ne pas répéter aveuglément une écriture incertaine.

Relais commun MCP, stdio/HTTP selon l’amont : transmettre l’opération, retenir sa réponse, couper seulement la session client/relais dès que l’oracle disque voit l’effet complet. Ne tuer aucun Obsidian. Pour un apply différé, le disque prime sur une réponse d’acceptation ; journaliser l’ordre exact. Reconnecter même client/agent, historique conservé, message neutre « réponse perdue, issue inconnue ». Statut/récupération ou lecture de note acceptés ; arrêt du backend = autre expérience, hors série principale.

Oracle : effet visible avant coupure ET réponse non remise au client, preuve du relais ; sinon `INJECTION_INVALIDE`. État à la coupure et final conservés ; une occurrence, zéro perte/doublon, compte rendu conforme, temps/appels/interventions de reprise mesurés. Journal durable pas exigé pour réussir l’effet demandé ; une relecture sûre peut réussir sans clé d’idempotence. Si le candidat propose une clé et l’agent la réemploie, enregistrer ce comportement sans l’imposer aux autres.

Limites T5–T7b et T8 : pas toutes les courses internes CPU, panne OS/disque, Sync, réseau partagé, crash électrique ou redémarrage serveur. Injections à la frontière MCP sans patch du serveur. Une retouche par automatisation de l’interface est une **retouche UI automatisée**, pas une action humaine réelle ; le rapport conserve cette distinction.


## 5. Oracles, relais et qualification de l’instrumentation

Implémentation : `scripts/oracles.py`, données de cellule JSON avec before/after et, selon tâche, human/first/cut. Snapshots indépendants du modèle, tous fichiers avec taille, SHA256 et bytes base64, jamais une réponse success prise comme preuve. `expected_before_tree_sha256` doit correspondre à l’avant scellé. YAML strict : clés dupliquées rejetées, entier distinct d’un booléen ou d’une chaîne, inconnus préservés, UTF-8 contrôlé sur les notes vérifiées. CRLF identifié comme différence de format, sans masquer un changement de sens. Les changements métier, format, dates et technique restent des colonnes séparées.

Relecture MCP : trace d’une réponse réellement reçue depuis l’amont, chemin et hash du texte correspondant au disque final, après la dernière mutation/reconnexion. Le parseur de réponse est déclaré dans l’adaptateur ; une forme non reconnue donne relecture non prouvée, jamais reconstitution depuis le disque. Sortie finale : schéma exact, chemin, état, extrait et propriétés vérifiés. Pour T5/T7, état conflit/non_applique exigé ; protection réussie ≠ écriture demandée accomplie.

Dates : aucune exemption implicite. L’oracle conserve les dates inchangées dans sa comparaison, expose les différences séparément. Une exemption de valeur nouvelle exige preuve FDM 1.6.0 attribuée au chemin/clé/valeur et au hash final dans la fenêtre de cellule (`date_evidence`, observation externe conservée). Sans preuve, écart indéterminé et validation non acquise ; jamais « FDM sûrement » ni correction des dates pour faire passer l’oracle. La collecte d’une telle attribution doit être qualifiée à l’admission si nécessaire. Les notes hors cible ne bénéficient d’aucune exemption.

Relais `scripts/relay.py` : entrée commune HTTP locale, amont stdio, Streamable HTTP (JSON ou événements) ou SSE legacy. Un amont stdio/SSE reste vivant pendant la reconnexion client. Aucun argument original modifié, ajouté ou reconstruit. L’adaptateur déclare les outils de mutation effectifs et les champs de lecture/path d’après le catalogue figé. En T5–T7b, retenir la première requête mutante déjà construite, saisir dans l’éditeur isolé, confirmer les bytes disque, snapshot H, transmettre la requête originale et prendre le premier état avant toute réparation. Un refus CAS puis une reconstruction est autorisé ; une perte temporaire réparée reste un incident.

**Apply différé T5–T7b :** le relais observe la première variation disque pendant pending et peut clore cette observation sur le statut terminal effectivement relu par l’agent (outils/champ/états déclarés dans l’adaptateur). Il bloque une nouvelle mutation tant que la première n’est pas réglée ou observée : aucune réparation sans snapshot préalable. Succès différé T6, refus différé sans changement T7 et effet différé T8 sont éprouvés sur le factice. Le mapping des schémas particuliers des candidats reste un gate d’admission ; une forme inconnue est une injection non qualifiée, jamais une perte attribuée au candidat. La préparation n’installe aucun candidat.

En T8, le portillon de réponse est fermé avant réponse amont ; un observateur disque indépendant ferme seulement la connexion client dès l’effet complet observé. Backend et Obsidian restent vivants. Trace dispatch → réponse retenue → effet disque → coupure → reconnexion, snapshots coupure/final, réponse initiale non délivrée. Le même agent reprend avec son historique et un message neutre « réponse perdue, issue inconnue ». Lecture sûre et statut/recovery sont tous acceptés ; pas de clé d’idempotence imposée aux autres.

Retouches T5–T7b : **méthode CDP dans l’éditeur QUALIFIÉE**, preuves `preuves/qualification-editeur.json`, FDM actif. Le script autonome `scripts/retouche-editeur.mjs` accepte port, identité coffre, note, texte et position UTF-16, remplacement optionnel ; confirme l’éditeur puis l’égalité exacte sur disque avant de rendre la main. Il n’écrit pas le fichier par filesystem. Documentation : `scripts/RETOUCHE-EDITEUR.md`. C’est une « retouche saisie dans l’éditeur d’Obsidian (saisie simulée par un script, pas par une personne) ». Pas une action humaine réelle, ni une simulation de clavier physique. En T5, seule la création de la note vide passe par l’API Obsidian ; son contenu passe par l’éditeur. Chaque injection doit refaire sa preuve de sauvegarde ; une pause ne vaut jamais barrière. Si une retouche n’est pas fiable avant le premier essai, la tâche concernée est non jouable pour tous (C5).

Tests de l’outillage : `python -X utf8 scripts/test_kit.py`, serveur factice écrit dans ce kit, sans installation ni candidat. Les traces avant/après, RPC et verdicts sont conservées. Succès T1–T8 sur stdio, HTTP et SSE ; négatifs : mauvaise note, mauvaise fixture, masque métier indu, relecture non prouvée, faux succès, mauvaise chronologie, arguments altérés, réponse prétendument perdue mais livrée, perte temporaire, coupure sans effet, entier chaîne/booléen, doublon YAML, champ perdu, doublon d’événement, perte humaine, autre note modifiée, suffixe de création. Ces tests ne sont pas des scores de serveur réel. Échecs de développement conservés dans les preuves privées et décrits dans le journal.

Verdicts : REUSSI_VERIFIE, PROTEGE_NON_ACCOMPLI, ECHEC_FONCTIONNEL, EFFET_NON_VOULU, NON_SUPPORTE, ECHEC_INSTALLATION, NON_EXECUTE_ENVIRONNEMENT, INJECTION_INVALIDE. Les trois derniers états d’admission/non-exécution sont attribués par le contrôleur, pas déduits d’un disque inchangé. La présence d’un fichier ne prouve aucun journal durable. Les oracles n’évaluent pas l’honnêteté rédactionnelle hors du JSON ; un juge aveugle partiel utilise des traces anonymisées et une grille séparée.

## 6. Admission, budgets et limites

Avant mesure : installation locale et empreintes des dix candidats et dépendances, 30 min maximum de prise en main chacun sur corpus distinct ; catalogues, adaptateurs, fiches, fournisseur/options client et exclusions techniques publiés. Préconditions réelles utilisées quand exposées. Une création réussie en T4 n’atteste pas l’exclusivité T5. Aucun candidat privé à la place d’Optimike public 3.13.0. Aucun tuning après score : correction = autre version/série.

Isolation : profil Obsidian sous runtime du run, caches/logs/env/client propres, un coffre et un candidat actifs. Jamais profil quotidien, ports 27123/27124, configuration globale, service durable ou firewall. Admission par nonce lu via **le chemin candidat**, et preuve coffre/port/PID. Pour Storks, sa CLI doit prouver la bonne instance ; un témoin REST seul ne suffit pas. Doute = aucune écriture. Ports proposés REST HTTP 27341, HTTPS 27342, CDP 27346, natif 27344 ; vérifier libres à l’instant du lancement. Le verrou partagé `VERROU-OBSIDIAN-TEST.txt` doit être pris atomiquement, propriétaire/heure/ports écrits, libéré à l’arrêt de l’instance. Un verrou occupé impose l’attente, jamais sa suppression par un autre agent.

Seuil **préparation** de cette reprise : arrêt propre si marge d’engagement < **1,5 Gio**, surveillance chaque seconde, aucun programme de Mike fermé. Ce seuil ne remplace pas les seuils de **campagne** C5 : ≥4 Gio de marge ET ≥4 Gio de RAM disponible avant chaque démarrage ; arrêt de nouveaux départs/mutations sous 2 Gio de marge ou 2 Gio de RAM disponible. Un seul agent lourd pendant la campagne. État préservé à l’arrêt ; cellule coupée = NON_EXECUTE_ENVIRONNEMENT, pas défaut fonctionnel attribué d’office.

Budget : 5 min par cellule, reprise T8 comprise, hors retouche planifiée jusqu’à 60 s. Maximum cellules 15 h 50 pour 190, plus gestes UI et admissions ; complet le 24 non garanti. L’ordre de lancement explicite du 23/10 remplace la date prévisionnelle du 24/10 du brouillon ; campagne après G1 et publication des amendements. Tout arrêt et toute reprise sont horodatés ; manquants visibles, aucune répétition sélective. Une mauvaise cible, écriture hors bac, perte imprévue ou doute d’isolation arrête immédiatement ; diagnostic et amendement public avant reprise. Hors périmètre : crash OS/disque/électrique, Sync, réseau partagé, toutes les courses CPU et arrêt du backend.

## 7. Résultats et publication

Par cellule : candidat/version/artefact, tâche/répétition, dates UTC, hashes prompt/fixture/adaptateur, admission, outils, chemins, temps mural et temps hors attente, appels, tokens/coût si disponibles (sinon NA), interventions setup/geste planifié/confirmation/réparation séparées, mémoire, changements, conflit, première mutation, reprise et état final. Deux strates courant T1–T4 / incidents T5–T7b et T8, numérateurs et dénominateurs, non-admis et non-joués visibles. Toute aide de Mike est comptée. Pas de moyenne arbitraire fabriquant un vainqueur.

Paquet public par liste blanche : ce protocole et journal, code neuf et tests, prompts, 190 cellules, corpus synthétique, empreintes commerciales, résultats de qualification factice/UI et masquage sans chemins privés. Ni archive commerciale, ni clé, ni profil, ni originaux privés. `scripts/redact.py` teste secrets nommés, Bearer, IDs privés UUID, emails et chemins personnels, y compris JSON imbriqué et échappé ; mesures/hash/Unicode conservés. Originaux séparés et intacts. Le masquage de secrets ne prouve pas un aveuglement complet : mécanismes/outils peuvent identifier un candidat.

Le gel V1 a été publié et vérifié sur clone frais (e3477a8). L’amendement v1.1 est préparé par `scripts/publish_v11.py`, puis un seul commit est poussé au même dépôt `optimikelabs/obsidian-mcp-comparatif`, sous l’autorisation explicite de Mike et la décision C5. Aucun nouveau dépôt ni autre publication. Le script PUBLICATION.ps1 et l’archive V1 restent des artefacts historiques du gel initial. Publication horodatée effective exigée avant admission et mesures ; un hash privé n’est pas une préinscription. Droit de réponse mainteneurs : 7 jours calendaires après mise à disposition des traces publiques ; même fenêtre pour tous, aucun contact envoyé par le kit. Réponse tardive en annexe ou nouvelle série, jamais effacement de l’essai initial.

## 8. Journal des changements du brouillon vers V1

- 23/10, C5 : H01 exclu pour archivage ; dix candidats C01–C10 conservés.
- 23/10, C5 : 240 → 160 cellules, deux séries annoncées, ordre filtré r2/r3 ; seules tâches réellement répétées trois fois fondent une phrase de résultat.
- 23/10, C5 : agent Codex CLI gpt-6.1-sol high, serviceTier default ; G1 avant comparatif ; autonomie de lancement accordée, revue C5 avant publication maintenue.
- 23/10, reprise Mike : seuil de préparation 1,5 Gio ; campagne inchangée (4 Gio départ / 2 Gio arrêt).
- 23/10, qualification : archive contrôlée et extraite, manifeste 749 fichiers, fixtures, prompts et 160 cellules produits ; aucun candidat installé.
- 23/10, précision C5/G1 AMENDEMENT-1 : CDP + saisie dans l’éditeur avec sauvegarde par Obsidian ; script autonome et preuve disque qualifiés ; verrou libéré pour G1.
- 23/10, outillage : oracles/factice/relais éprouvés stdio, HTTP, SSE ; correction de CRLF dans le factice, d’un appel require non disponible dans le renderer et d’une fermeture SSE bloquante. Aucun score candidat utilisé pour ces corrections.
- 23/10, transparence : attribution FDM et règlement d’apply différé T5–T7b restent des gates d’admission explicites ; aucune qualification de candidat présumée. Corpus synthétique distinct de l’environnement commercial, pas d’équivalence générale revendiquée.
- 23/10, opérationnel : CLI observée 0.160.1, Obsidian exécutable 1.13.7, Node 24.17.0, Python 3.12.10, PyYAML 6.0.3 ; configuration fournisseur/artefacts/catalogues à sceller à l’admission. Paquet préparé et masquage éprouvé ; aucune publication lancée.

Sources normatives : AMENDEMENTS-C5-AVANT-CAMPAGNE.md, puis DECISIONS-C5.md. Sources documentaires candidats : captures du brouillon datées du 23/10 ; descriptions non transformées en preuve runtime. Amendement ou écart ultérieur : conserver cette version et publier le delta **avant** toute cellule affectée.

## Journal v1.1 — amendements C5 avant campagne

- Préparation applicative identique, issue de G1 amendement 2, avant B0 ; aucun champ de date écrit par l’agent.
- T7b après lecture et avant premier plan/écriture ; 30 cellules ajoutées en série 2 ; total 190 (80 + 110).
- Mode documenté de chaque serveur ; Obsidian ouvert pour tous lors des retouches T5/T6/T7/T7b.
- Limites déclarées : un seul agent Codex ; corpus commercial Margelle vendu par l’auteur ; corpus synthétique publié mais non rejoué en campagne ; T1–T4 non répétés ; aucun contact préalable avec les mainteneurs. Trois répétitions n’établissent aucun taux de risque rare.
- Seuil utilisateur du 23/10 : 4 Gio engagement et RAM avant départ ; aucun nouveau départ sous 2 Gio sur l’un ou l’autre. Aucun programme de Mike fermé.
- Le gel e3477a8 demeure accessible. Ce delta, ses tests et le manifeste 190 sont publiés ensemble avant les admissions. Aucun résultat candidat à cette étape.

## Amendement d’instrumentation à l’admission — avant toute cellule

Le catalogue C02 retourne, pour read_note, deux composantes natives : fm (propriétés) et content (corps), sans sérialisation originale du frontmatter. Le mapping conserve séparément les propriétés typées et le hash du corps effectivement reçu par MCP ; l’oracle les compare au YAML et au corps du snapshot disque. Aucun contenu de réponse n’est inventé depuis le disque. Les différences de format restent contrôlées sur les snapshots. read_note_lines permet aussi une lecture brute complète ; les deux formes sont autorisées. Cette règle de mapping est disponible pour tous les candidats qui exposent une forme équivalente. Une forme inconnue reste non prouvée.

T7b exige que cette projection de lecture initiale soit égale à B0 et qu’une réponse de lecture correspondante soit réellement enregistrée avant le premier plan/écriture. Témoins factices : type de propriété erroné, corps erroné, réponse non reçue et divergence entre preuve initiale et réponse ; aucun de ces cas n’est accepté.

Incidents de préparation avant mesure : un premier bac C02 n’a pas atteint l’état daté sous 60 s ; aucun serveur candidat n’y était lancé. La méthode attend maintenant la sauvegarde disque, vérifie la fiche active et exécute la commande FDM seulement si les dates manquent. L’identifiant de Margelle Hub est elysia-os (nom Margelle Hub), identifié par son manifest ; désactivation identique dans toutes les copies. C01 est marqué à revalider dans cette configuration commune. Aucun score candidat n’a été acquis ni corrigé. Les essais et journaux initiaux restent conservés.
