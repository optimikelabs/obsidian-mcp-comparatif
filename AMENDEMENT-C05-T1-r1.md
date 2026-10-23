# Incident de contrôle avant modèle — C05-T1-r1

23/10/2026, 09:15 UTC. Première cellule prévue, arrêt avant tout appel au modèle. Son état reste NON_JOUE / NON_EXECUTE_ENVIRONNEMENT. Aucun résultat de C05 n'est acquis. Le bac, le résultat brut et la trace d'assertion d'origine restent conservés ; la cellule ne sera pas rejouée dans cette campagne.

Le contrôleur comparait le hash des bytes du fichier prompt (CRLF sous Windows) au hash du manifeste, calculé en LF. T1 : raw `31ca7d249a482d0c2bf7a1d09f7f31d406e34559aa6bfa5b2cba3f24fe0ef024`, LF/manifeste `fa81a124b6b8d98c4d193201dad45fa41cceb31727890e93f53ea47416ff997f`. Le texte effectivement préparé pour le modèle était déjà lu en LF. Correction pour les cellules suivantes : comparer le SHA256 UTF-8 de ce texte LF au manifeste. Aucun prompt, manifeste ni intention n'est modifié.

L'instance Obsidian du test a été arrêtée et son verrou libéré ; aucun programme de Mike n'a été fermé.

La publication automatique de l'incident a ensuite échoué : l'ordre de deux chemins dans `technical_changes` variait entre processus Python. Le rejeu masqué d'un cas factice négatif C08 donnait le même verdict, les mêmes erreurs et les mêmes chemins, avec un ordre différent. La sortie de cette liste est maintenant triée ; les autres listes de chemins l'étaient déjà. Il s'agit d'une correction déterministe de sortie, pas d'un changement de verdict. Les preuves factices sont régénérées et rejugées après masquage avant la reprise. Aucun score candidat n'est corrigé.

Reprise après publication de cet amendement : C05-T2-r1, puis l'ordre restant du manifeste. `--after-incident C05-T1-r1` vérifie que l'amendement est présent sur le main distant avant de passer la ligne arrêtée. Aucune répétition sélective, aucun effacement de bac.

La comparaison T1 reste donc incomplète pour C05. Ce manque reste dans tous les tableaux et dénominateurs.

Précision de comptage avant tout appel de mesure : une cellule interrompue par l'environnement, une attribution non qualifiée ou une injection invalide reste NON_JOUE pour le comparatif, même si des appels partiels sont conservés. Une cellule achevée avec un échec fonctionnel ou un effet non voulu est JOUE. Les tableaux gardent les deux champs status/verdict et les reçus ; une tentative incomplète ne devient pas une mesure acquise.
