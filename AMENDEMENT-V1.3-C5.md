# Amendement v1.3, décidé par C5 avant C05-T6-r1 (23/10/2026, vers 13 h 30)

Source : `kit\public\resultats\incidents\injection-ui-C05-T5-r1.json` et le commit public `623b963`. C5 décide par délégation de Mike, qui l'a autorisé à gérer les tests en autonomie.

## Constat
- **C05-T5-r1 : `INJECTION_INVALIDE`.** Le script d'injection dans l'interface (`scripts/ui_cdp.mjs`, ligne 22 : `const path=task==='T5'?cfg.N:cfg.P;`) lit `cfg.N` et `cfg.P` dans le `obsidian.json` créé par `campaign_runtime.prepare`. Or ce fichier ne contient ni l'un ni l'autre : le script a échoué (`TypeError`) avant la création « humaine ». Aucune note métier n'a changé.
- **Défaut secondaire :** le relais passe `injected` à vrai avant que le crochet d'interface ait réussi. Après l'erreur 503, une seconde requête qui modifie le coffre a été transmise sans nouvelle barrière. Le candidat a répondu `INVALID_PARAMETERS`, et aucune note n'a été créée ni perdue.
- **Ces deux défauts appartiennent au banc d'essai,** pas au candidat. Ils toucheraient les dix candidats de la même façon.

## Ce qui est décidé
1. **Deux corrections communes à tous les candidats.**
   - `prepare` écrit les cibles `N` et `P` attendues par `ui_cdp.mjs`, pour chaque tâche qui injecte dans l'interface.
   - Le relais ne marque l'injection faite qu'après la réussite vérifiée du crochet. Si le crochet échoue, il bloque toute requête qui modifie le coffre jusqu'à la fin de la cellule, et la cellule est classée `INJECTION_INVALIDE` sur-le-champ.
2. **Vérifier les cellules déjà jouées.** Liste les tâches qui utilisent `ui_cdp.mjs`, ou une autre injection. Montre ensuite, preuves à l'appui, que C05-T2-r1, T3-r1 et T4-r1 ne dépendaient pas de `cfg.N` ni de `cfg.P`.
   - Si l'une en dépendait, son verdict est marqué « injection non établie », et C5 tranche avant la reprise.
   - Sinon, leurs verdicts restent tels quels.
3. **Qualifier sur le serveur factice avant de reprendre**, pour chaque tâche qui injecte (T5 au minimum, et toutes celles relevées au point 2).
   - **Témoin positif :** l'injection a lieu, l'instantané « humain » est présent, et l'événement de vérification sur le disque (`ui_disk_verified`) est émis.
   - **Témoins négatifs :** si la cible manque, la cellule s'arrête avant toute modification par le candidat. Si le crochet échoue, aucune seconde requête de modification ne passe.
4. **On ne reclasse rien.** `INJECTION_INVALIDE` reste publié pour C05-T5-r1, avec cette note : « défaut du banc d'essai (cibles N/P absentes, relais), corrigé par l'amendement v1.3 ». Ce n'est pas un résultat du candidat.
5. **Un seul remplacement de C05-T5-r1**, à la fin de la série 1, après la qualification. C'est la même règle que pour C05-T1-r1 : un remplacement au plus, et les deux traces sont conservées.
6. **Publication.** Publie l'amendement v1.3 dans le dépôt, en un seul commit, en gardant les gels v1, v1.1 et v1.2. Reprends ensuite à **C05-T6-r1**. Les seuils mémoire, le verrou et la règle sur le modèle restent ceux de l'amendement v1.2. L'agent testé reste Codex CLI gpt-6.1-sol, effort high, serviceTier default.
