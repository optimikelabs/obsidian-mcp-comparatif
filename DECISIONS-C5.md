# Test comparatif : décisions de C5 sur le brouillon (23/10/2026, vers 4 h 10)

C5 décide en tant que chef de projet global, par délégation de Mike (23/10, vers 3 h 45). Ces décisions sont prises **avant tout essai** : aucune cellule n'a été jouée et aucun score n'existe. Elles deviennent la version v1 du protocole, à geler.

## Ce qui est décidé
1. **Le panel reste entier : les dix candidats C01 à C10.** On ne retire aucun concurrent pour gagner du temps : ce serait le premier reproche fait à un auteur qui compare son propre outil. **H01, MCP Tools, est exclu** selon la règle « dépôt archivé ». La règle est ratifiée maintenant, avant toute observation.
2. **Le plan passe de 240 à 160 cellules, en deux séries annoncées d'avance.**
   - Série 1 : les 10 candidats sur les 8 tâches, une répétition chacun (80 cellules), dans l'ordre du brouillon pour r = 1.
   - Série 2 : les tâches T5 à T8 (collision, deux écritures distinctes, intentions incompatibles, réponse perdue), en répétitions 2 et 3 pour chaque candidat (80 cellules), dans l'ordre du brouillon pour r = 2 et r = 3, limité à ces tâches.
   - Raison : la question que le site posera porte sur ce qui arrive quand deux écritures se croisent ou qu'une réponse se perd. Ce sont les tâches qui demandent des répétitions. T1 à T4 (lire, modifier, propriété, création) servent à admettre et à décrire chaque serveur.
   - **Seules les cellules jouées en trois répétitions peuvent fonder une phrase de résultat.** Ce qui n'est pas joué est listé, sans extrapolation.
3. **L'agent est le même pour tous** : Codex CLI, `gpt-6.1-sol`, effort high, avec les mêmes options, dont `serviceTier: default`, par économie (consigne de Mike pour la nuit). Contexte neuf pour chaque cellule.
4. **L'ordre du 24/10.** G1 passe d'abord : il est plus petit et le site en a besoin. Le comparatif vient ensuite. Pendant le comparatif, aucun autre agent lourd ne tourne sur le poste. Les seuils mémoire du brouillon (≥ 4 Gio avant de démarrer, arrêt sous 2 Gio) sont retenus sans changement.
5. **Les retouches dans Obsidian (T5 à T7) sont automatisées** par l'interface et synchronisées au disque. Aucune pause arbitraire ne doit passer pour une course validée, selon la règle du brouillon. Si l'automatisation n'est pas fiable, la tâche est déclarée non jouable pour tous, avant le premier essai.

## Autorisation de Mike (23/10, vers 4 h 15)
« non codex lancera les tests sans ma présence, je vous autorise à le gérer en autonomie, je donne mon ok ». **La publication du gel et le lancement sont donc autorisés, sans attendre Mike.** Ordre retenu par C5 :
1. le kit est prêt (`kit\RAPPORT-KIT.md`) ;
2. C5 le relit en juge : panel, oracles, équité, masquage ;
3. Codex publie le gel dans un dépôt public sous `optimikelabs` ;
4. G1 ;
5. série 1 ;
6. série 2.

Un seul agent lourd à la fois ; seuils mémoire du protocole ; Codex en vitesse normale. Les résultats arrivent dans `test-comparatif\resultats\`. Toute phrase publique tirée des résultats (article d'optimike.net, page Margelle) passe d'abord par C5, puis par un contre-audit nemesis.

## Ce qui se prépare cette nuit (Codex, vitesse normale)
Le kit est construit dans `test-comparatif\kit\`, **sans installer aucun candidat et sans rien publier** : reconstruction du coffre Margelle 1.0.6 de référence, oracles scriptés et leurs tests négatifs sur un serveur factice, relais d'injection pour T6 à T8, manifeste des 160 cellules dans l'ordre, et paquet public prêt, avec masquage testé.
