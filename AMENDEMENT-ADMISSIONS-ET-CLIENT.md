# Amendement avant la première cellule — admissions, client et attribution

23 octobre 2026. Aucun score candidat acquis lors de cet amendement. Il complète la v1.1 publiée en `1e698f62401034c74dd70a1019146e45c8dc821f` ; le gel initial `e3477a8b02441f73ac3d22b19d78766428887bbd` reste conservé.

## Admissions

Neuf candidats admis : C01, C02, C03, C04, C05, C07, C08, C09, C10. C06 reste dans les 190 lignes : NON_EXECUTE_ENVIRONNEMENT, isolation de sa CLI non démontrée sur ce poste ; aucune commande CLI n'a été envoyée à une instance quotidienne. Ce n'est pas un résultat fonctionnel de Storks.

Les catalogues complets, adaptateurs, fiches et reçus sont sous `resultats/admissions/`. C01 a été revalidé sans Hub ; l'essai initial avec Hub est conservé. La première préparation C02 n'a pas stabilisé les dates sous 60 secondes ; son bac et la tentative suivante sont conservés. C08 a d'abord rencontré une erreur du parseur du contrôleur, corrigée avant toute cellule. C07 : le contrôleur a continué à interroger un statut déjà terminal, en lisant le mauvais champ, jusqu'à une réponse 429. Tous ces reçus restent publiés. Aucun quota produit n'a été relevé ; le contrôleur utilise désormais `phase`, `outcome` et `postflight.checkAfter`. Aucun de ces essais d'admission n'est une cellule comparative.

C08 est le paquet npm 2.0.1 observé, pas le tag GitHub 2.0.0. C09 expose réellement un remplacement dans le paquet 1.6.0. Les divergences de licence déclarées dans les fiches C09/C10 ne sont pas résolues ici ; aucun code de candidat n'est redistribué.

## Client commun qualifié sur factice

Codex CLI 0.160.1, gpt-6.1-sol, high, fournisseur openai, service_tier default. `config/read` exporte les options effectivement chargées ; les journaux de session confirment modèle, effort et sandbox read-only. Contexte initial vide et CODEX_HOME propre par cellule ; seule l'authentification du compte est copiée dans ce dossier privé, jamais publiée. Aucun changement de configuration globale.

Le premier essai factice échoue avec « code-mode host is disabled » : désactiver cet hôte rend les outils MCP inaccessibles sur cette version. L'hôte interne est donc actif, avec `code_mode=false`. Les traces du second essai montrent des appels MCP directs, sans outil eval, shell, navigateur ou autre serveur. Les capacités shell, browser, apps, plugins, agents, image, mémoire et skills sont désactivées. Un outil neutre d'attente est autorisé pour respecter un `checkAfter` ; il n'accède pas au coffre. Cette configuration est identique pour tous. Les outils MCP autorisés sont limités par `enabled_tools` au périmètre commun déclaré dans chaque adaptateur.

T2 factice : lecture, écriture conditionnelle, relecture et oracle acquis. T8 factice : effet disque, réponse retenue, coupure du client seulement, puis arrêt du processus client de mesure ; backend maintenu vivant. Relance de ce même client par son identifiant de session, historique conservé, message neutre « Réponse perdue, issue inconnue. Poursuis avec ton historique, établis l'issue puis termine la demande initiale. » Une lecture établit un ajout unique. Aucun résultat de candidat n'est inféré de ces qualifications.

Le relais initialise une fois la session amont pour acquérir le catalogue avant B0 ; il restitue cette réponse d’initialisation au client et garde cette session pendant T8. Les requêtes d’outils sont transmises avec leurs arguments originaux. Cette voie est qualifiée avec la reprise factice.

Budget commun : 300 secondes, reprise T8 comprise ; retouche planifiée exclue à concurrence de 60 secondes, avec durée publiée. Le contrôleur de mesure et l'agent du modèle sont distincts.

## Attribution des dates

FDM 1.6.0 est livré et reste actif. Un observateur en mémoire dans l'instance isolée entoure `app.fileManager.processFrontMatter`, transmet le callback natif sans assigner de date, puis enregistre le chemin, les valeurs avant/après, la pile attribuant l'appel au plugin, les octets sauvegardés et l'heure. Son code ne modifie ni les fichiers du plugin, ni ses réglages. La qualification réelle a observé une retouche éditeur suivie d'une mise à jour FDM, liée au SHA256 exact du fichier. L'observation ajoute une lecture et une étape asynchrone ; cela reste une limite instrumentale déclarée.

La preuve est désormais vérifiée contre le snapshot concerné : H, première mutation, coupure ou final. Pour T5, un frontmatter constitué seulement de dates attribuées peut entourer le corps humain strictement intact. Les différences de dates et de format restent exposées ; aucune exemption de note hors cible. Une date différente sans attribution valide donne NON_EXECUTE_ENVIRONNEMENT, avec les erreurs détaillées, sans réussite ni défaut du candidat inféré. Les 15 contrôles hypothétiques de dates sont des objets JSON en mémoire, pas des modifications de notes. Le détecteur d'effet T8 reconnaît le corps et les autres propriétés ; l'oracle exige ensuite séparément l'attribution exacte des dates du snapshot de coupure.

Les changements techniques de H sont admis seulement pour les chemins exacts déclarés avant lancement. Les autres notes sont toujours contrôlées, y compris une perte temporaire réparée avant la fin.

## Reçus techniques C08

Le journal C08 crée des noms de transaction dynamiques. Une liste littérale de ces noms ne peut donc pas exister avant l'appel. Exception déclarée à la règle de liste fixe : politique `c08-transactions-v1`, liée au `transaction_id` de la réponse native réellement observée. Elle valide chaque chemin exact, l'identifiant, le statut committed, l'unique cible autorisée, le type write/file, les etags et le hash du backup `0.bin`. Seuls ce manifest technique et son backup validés sont classés techniques. Pas de masque de dossier, de note Markdown ou de code. Tous les deltas restent visibles. Reçu absent ou artefact non qualifié : NON_EXECUTE_ENVIRONNEMENT ; note cachée ou autre cible : effet non voulu. Quinze contrôles factices positifs et négatifs sont publiés.

## Publication des mesures

Les originaux complets restent dans le run privé : snapshots de tous les fichiers, réponses amont, différences, état mémoire chaque seconde et traces client. La projection publique conserve les témoins synthétiques P/N/Q et les métadonnées complètes des différences. Elle omet les octets des autres fichiers du corpus commercial et leurs réponses de lecture, en conservant leur hash et leur taille ; elle ne redistribue pas le coffre, ses plugins, les profils ni l'authentification. Une reproduction complète sur Margelle nécessite donc un accès licite au corpus. Les qualificatifs factices sont rejugés après masquage.

Un bac neuf par cellule, ordre des 190 lignes conservé, aucune répétition sélective. Les cellules non jouées restent visibles. Aucun texte de conclusion ou de promotion produit n'est publié ici.
