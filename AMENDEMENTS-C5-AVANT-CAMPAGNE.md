# Amendements au gel, décidés par C5 avant la première cellule (23/10/2026, vers 7 h 10)

Origine : la préparation G1 (`mcp-optimike\G1\AMENDEMENT-2.md`) et les relectures de l'article d'optimike.net (`article-optimike\RELECTURES.md` : nemesis, lignes 67, 106 et 120). Aucune cellule n'est jouée. Ces amendements sont **publiés dans le dépôt `optimikelabs/obsidian-mcp-comparatif`, avant la première cellule**. Le gel `e3477a8` reste conservé. C5 décide ici en tant que chef de projet global, par délégation de Mike.

## Retenus
1. **Préparation applicative identique pour tous** (leçon de G1). Avant B0, on ouvre la fixture dans l'instance Obsidian isolée et on lance `editor:save-file`. Si les dates de création manquent ensuite, on lance la commande FDM livrée. Raison : c'est l'usage réel, la préparation est la même pour les dix candidats, et une note restée sans date ne reflète aucun usage.
2. **Une tâche de plus, T7b, pour tester le point faible d'Optimike** (nemesis, V1). Dans T6 et T7, la retouche tombe toujours après le plan, dans la fenêtre que couvre le contrôle d'Optimike. T7b place la retouche **entre la lecture de l'agent et sa première écriture**, ou son plan pour Optimike. Optimike ne compare pas la note à la version que l'agent a lue ; c'est donc exactement le cas que T7b vérifie. T7b s'ajoute en série 2, en trois répétitions pour les dix candidats, soit 30 cellules de plus. **Le plan passe à 190 cellules.** L'oracle et le relais de T7b sont écrits et testés sur le serveur factice avant la première cellule, comme les autres.
3. **Le mode de fonctionnement documenté de chaque serveur.** Un serveur qui travaille sur les fichiers sans Obsidian est joué dans ce mode, si c'est sa documentation. Pour T5 à T7b, Obsidian est ouvert pour tout le monde, puisque la retouche se fait dans son éditeur. Ce point est déclaré.

## Non retenus pour cette campagne, et dits comme limites dans le dépôt et dans l'article
- **Un second agent** (Claude Code). Il doublerait les cellules, et le budget de la journée ne le permet pas. Ce sera une série suivante, annoncée d'avance si Mike la veut.
- **Le corpus libre, rejoué en plus du coffre Margelle.** Le corpus synthétique est publié pour qu'un tiers le rejoue, mais il ne fait pas partie de cette campagne. Le biais est dit : le test se joue sur le coffre que vend l'auteur.
- **Des répétitions de T1 à T4.** Une seule répétition, comme décidé ; ces tâches servent à l'admission et à la description.
- **Prévenir les mainteneurs avant le test.** Ce serait un contact public sous le nom de Mike : c'est sa décision. On garde le droit de réponse après les résultats, déjà prévu au protocole.

## Pour l'agent de la campagne
Publie ces amendements, ainsi que l'amendement de préparation, en un seul commit au dépôt, avec le gel conservé. Ensuite seulement, lance les admissions. Mets à jour `PROTOCOLE-V1.md` en v1.1, avec son journal de changements, ainsi que le manifeste des cellules, qui passe à 190.
