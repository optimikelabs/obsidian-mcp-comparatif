# Amendement v1.2, décidé par C5 avant la prochaine cellule (23/10/2026, vers 11 h 45)

Source : `resultats\RAPPORT-CAMPAGNE.md`, arrêt de 09 h 37 UTC. La campagne s'est arrêtée seule, comme le prévoit le protocole. C5 décide par délégation de Mike, qui l'a autorisé à gérer les tests en autonomie.

## Constat
- Dans la cellule C05-T4-r1, **un seul fichier a changé sur le disque** : `.obsidian/plugins/frontmatter-date-manager/hash-cache.json`, le cache du gestionnaire de dates (FDM 1.6.0). Seuls les champs `lastAccessed` et le `hash` interne des entrées de la fiche témoin et du guide ont bougé. Les notes, elles, sont identiques. Ce chemin ne figurait pas dans `technical_paths`, d'où le verdict publié : `EFFET_NON_VOULU`.
- C05-T1-r1 n'a pas été jouée : le contrôle CRLF/LF a échoué avant le modèle. L'incident vient de la préparation, pas du candidat.
- C06 n'est pas admis : l'isolation de sa CLI n'a pas pu être démontrée dans la limite de temps.

## Ce qui est décidé
1. **Le cache FDM devient une surface technique déclarée, pour les dix candidats.** `.obsidian/plugins/frontmatter-date-manager/hash-cache.json` entre dans les chemins techniques attendus, avec une condition vérifiée par l'oracle. Seuls peuvent changer les champs `lastAccessed` et `hash` des entrées des notes que la cellule a ouvertes ou modifiées. Tout autre changement de ce fichier (entrée ajoutée ou retirée, autre champ, autre note) reste `HORS_CIBLE`. Raison : FDM est actif par décision, puisque c'est l'usage réel, et la préparation est la même pour tous. Son cache est un artefact de l'éditeur, pas un effet du serveur testé.
2. **On ne reclasse rien.** Le verdict `EFFET_NON_VOULU` de C05-T4-r1 reste publié tel quel, avec une note : « dû au cache FDM, surface déclarée par l'amendement v1.2 après cet essai ». C05-T2-r1 et C05-T3-r1 restent `REUSSI_VERIFIE`. Toute phrase de résultat dira que ces trois cellules ont été jouées sous la règle v1.1.
3. **Un seul remplacement de C05-T1-r1**, à la fin de la série 1, parce que son arrêt vient de la préparation (règle publiée : un remplacement au plus, deux traces conservées). Le contrôle CRLF/LF doit d'abord passer sur la fixture préparée.
4. **C06 reste non admis.** Une seule nouvelle tentative d'admission est autorisée, à la fin de la série 2, dans la limite de 30 minutes, si le temps et la mémoire le permettent. Sinon, C06 figure dans le tableau comme non admis, avec sa raison.
5. **Avant de reprendre** : on qualifie l'oracle v1.2 sur le serveur factice. Il doit accepter un changement de `lastAccessed` et de `hash`, et refuser une entrée ajoutée, un autre champ ou une autre note, avec des témoins négatifs. Ensuite, on publie l'amendement v1.2 dans le dépôt, en un commit, en gardant les gels v1 et v1.1. On reprend enfin à **C05-T5-r1**.
