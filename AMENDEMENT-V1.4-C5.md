# Amendement v1.4 — attribution FDM dans l’instantané jugé

Décision C5 du 23 octobre 2026, vers 16 h 50, après le diagnostic `63e83af`. Source complète : `DECISIONS-C5-20261023-1650.md`. Règle commune aux dix candidats, publiée avant C08-T7-r1.

## Périmètre et preuves

Dans l’instantané jugé, seuls les changements des clés création et modification attribués à FDM sont tolérés : format FDM 1.6.0 ; note créée ou modifiée par la cellule ou l’injection humaine ; heure compatible avec delayForNewFiles/minSecondsBetweenSaves, ou passage correspondant dans hash-cache.json. Tout autre changement reste jugé comme avant, notamment les autres propriétés, le corps, les autres notes, la première mutation et la correction humaine.

L’observateur enregistre l’appel natif de FDM, ses propriétés avant/après, le contenu résultant, l’empreinte, la version et l’heure. Une chaîne intermédiaire peut désormais établir l’attribution même quand la modification demandée change ensuite l’empreinte du fichier. L’oracle vérifie l’intégrité du contenu intermédiaire, les seules clés modifiées par FDM, leur valeur finale, la fenêtre de mesure et la chronologie du snapshot concerné. Les valeurs de dates suivent le format configuré ; les notes admissibles sont les cibles d’écriture ou d’injection de la tâche, jamais une simple autre note ouverte par l’éditeur. Les contrôles de contenu métier existants restent actifs.

Pour une date déjà présente, le temps observé doit satisfaire minSecondsBetweenSaves ; pour une note créée pendant la cellule, il doit satisfaire delayForNewFiles depuis sa création. À défaut, la branche cache exige le passage de cette note, pendant la fenêtre pertinente, avec le hash correspondant au contenu intermédiaire selon la projection de FDM 1.6.0. Un hash quelconque ou un accès à une autre note ne suffit pas. Les dates futures, preuves hors fenêtre et preuves provenant d’un autre writer sont refusées. Une date modifiée sans preuve recevable reste indéterminée et impose l’arrêt.

La règle est activée explicitement par `fdm_dates_policy: fdm-dates-v1.4`. Les cas sans cette politique gardent exactement leur comportement précédent. Le contrôleur fige les paramètres depuis B0 et fournit les observations ; le candidat ne fournit pas les preuves. En mode fichier avec Obsidian déjà fermé, la liste des observations FDM pendant la mesure est vide, sans exemption inventée. Le client, les prompts, les adaptateurs, la préparation, le délai de stabilisation et l’instantané jugé ne changent pas. Les observations après fermeture restent régies par la note de 16 h 35 et hors jugement.

## Qualification

`scripts/test_fdm_dates_v14.py` qualifie le changement sur le serveur factice HTTP, avec FDM simulé dans une fixture synthétique neuve. Aucun résultat de candidat réel n’est utilisé comme qualification positive.

- Chaîne FDM puis modification demandée : acceptée en v1.4, bloquée par v1.3.
- Autre clé, autre note, format non FDM, correction humaine écrasée : refusés dans quatre scénarios HTTP distincts.
- Preuve absente, mauvais writer/version/note/hash, preuve hors fenêtre, délai incompatible, date future et mauvais hash de cache : refusés.
- Passage de cache correspondant : accepté lorsque le délai seul n’est pas établi.

Quinze contrôles passent. Voir `preuves/tests-fdm-dates-v14.json` et ses cas rejouables. Les cas factices antérieurs sont également rejugés sans changement de politique. Les empreintes du code qualifié sont dans `preuves/v14-code-qualifie.json` ; le contrôleur refuse une divergence avant lancement.

## Équité et résultats conservés

Les quatorze cellules existantes ont été relues, dont les deux arrêts sans instantané jugé. L’oracle précédent est rejoué sur les entrées conservées, puis la règle v1.4 est examinée séparément, sans écrire dans les bacs ni remplacer les résultats. Preuve détaillée : `preuves/v14-audit-equite.json`.

**Liste des cellules dégradées uniquement par ce motif : C08-T6-r1.** Aucun autre ajout à la liste. C05-T4-r1 présente d’autres erreurs (cache hors cible selon sa règle initiale et cible absente) ; C08-T1-r1 échoue sur l’extrait de réponse. Les autres arrêts concernent la préparation, l’injection ou la fermeture, et les cellules réussies ou protégées conservent leur verdict.

C08-T6-r1 reste publiée telle quelle : `NON_EXECUTE_ENVIRONNEMENT`, avec la note « bloquée par l’oracle v1.3, chaîne FDM, amendement v1.4 ». La relecture contrefactuelle n’est pas un nouveau score. Un seul remplacement est autorisé en fin de série 1. Le registre contient désormais C05-T1-r1, C05-T5-r1, C08-T4-r1 et C08-T6-r1, sans doublon et avec les empreintes originales. Aucune cellule existante n’est rejouée ni effacée.

## Gel et reprise

Le protocole précédent est conservé octet pour octet dans `PROTOCOLE-V1.3-GELE.md`, l’oracle dans `scripts/oracles_v13.py`. Les gels v1/v1.1/v1.2 et les anciens résultats restent intacts. Cet amendement, sa qualification et son audit sont publiés ensemble avant reprise à C08-T7-r1.

Astra orchestre uniquement ; Codex CLI gpt-6.1-sol, high, serviceTier default reste le client de mesure, sans modèle de repli. Démarrage avec RAM disponible et marge d’engagement ≥ 4 Gio, arrêt sous 2 Gio. Verrou partagé jamais forcé, priorité au gel produit 1.0.7, aucun profil quotidien ni ports 27123/27124. Les remplacements restent en fin de série 1 ; nouvelle tentative C06 après la série 2.
