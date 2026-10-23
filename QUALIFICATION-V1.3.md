# Qualification de l’amendement v1.3

Le 23 octobre 2026, avant C05-T6-r1. Aucun résultat candidat dans cette qualification.

## Correction et indépendance des cellules historiques

prepare fournit les cibles N/P à tous les nouveaux bacs. Le relais ne marque l’injection faite qu’après la réussite vérifiée du crochet ; en cas d’échec, il ferme définitivement la barrière des mutations et préparations, consigne INJECTION_INVALIDE et arrête le client. Aucun argument candidat ni oracle de score n’est modifié.

C05-T2-r1, T3-r1 et T4-r1 n’ont déclenché aucun crochet : zéro intervention d’éditeur, aucun instantané humain, aucun événement d’injection. Ils ne dépendaient donc ni de cfg.N ni de cfg.P. Les cinq result.json historiques sont préservés à l’octet. Voir preuves/v13-audit-cellules.json et preuves/v13-resultats-preserves.json.

## Témoins observés

- 17 contrôles v1.3 passent sur le serveur factice : pour T5, T6, T7 et T7b, positif, N absent, P absent, crochet en échec ; plus arrêt du client sans invocation de modèle. Pour les négatifs : aucune mutation transmise, deuxième requête et préparation bloquées, disque inchangé.
- 4 positifs supplémentaires passent avec le vrai éditeur Obsidian isolé et le serveur factice. Pour chaque tâche : configuration N/P issue de prepare, retouche UI automatisée, sauvegarde disque observée, instantané humain présent, événement ui_disk_verified avant dispatch. Ce n’est pas une intervention humaine réelle. FDM actif ; copies Margelle isolées, Hub désactivé, aucun candidat installé dans ces bacs.
- 106 contrôles de régression passent : 57 T1–T8 (5 groupes), 30 T7b, 19 schémas natifs. T8 ne passe par aucun crochet UI ni cfg.N/P : sa preuve est effet disque → coupure de réponse → reconnexion. Témoins négatifs : réponse prétendument perdue mais livrée, absence de portillon, état de coupure sans effet, événement dupliqué.
- Codex CLI 0.160.1 a le même SHA-256 que dans C05-T5-r1. Le modèle n’est pas réinvoqué pour cette vérification ; sa disponibilité sera contrôlée en cellule, avec arrêt sans substitution.

Preuves : preuves/tests-injection-v13.json, preuves/tests-injection-v13-ui.json, preuves/tests-factice.json, preuves/tests-t7b.json, preuves/tests-native-mappings.json, preuves/v13-code-qualifie.json et preuves/v13-client-preserve.json. Les snapshots publics ne contiennent que les trois notes témoins ; inventaires complets et empreintes conservés, contenu commercial hors témoins exclu.

## Anomalie secondaire conservée

Le controller.jsonl du positif UI T6 contient un fragment tronqué à la ligne 2. L’original n’a pas été réparé : copie exacte controller-original.jsonl.txt et hash publiés. Les gates mémoire complets, événements du relais, snapshots et reçu d’arrêt sont valides. Les quatre arrêts d’instances et libérations de leurs verrous sont établis dans preuves/v13-ui-sortie.json. La cause de concurrence d’écriture du journal est une hypothèse ; aucun correctif supplémentaire du journal n’est appliqué dans cet amendement. Cette anomalie ne touche ni l’injection ni un résultat candidat.

## Reprise

Publication v1.3 en un commit avant C05-T6-r1. Gels v1/v1.1 conservés ; PROTOCOLE-V1.2-GELE.md est la copie exacte du protocole public précédent après le même masquage. C05-T5-r1 reste INJECTION_INVALIDE, défaut du banc d’essai ; aucun reclassement. Les remplacements uniques T1/T5 restent après la série 1 et dans des dossiers distincts ; la nouvelle tentative C06 reste après la série 2. Le verrou partagé reste prioritaire, sans forçage, même après la fin estimée du créneau produit.
