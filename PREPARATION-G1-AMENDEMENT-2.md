# G1 : amendement 2, avant de rejouer les cellules M et la cellule C de Claude (décision de C5, 23/10/2026, vers 6 h 10)

## Constat de la reprise (`RAPPORT.md`, validé par Opus comme constat partiel)
- **M-Codex-1 n'est pas jouée de façon valide**, pour deux raisons :
  - la chaîne MCP 3.13.0 et Atomic Write Bridge 0.8.1 refuse de planifier sur la fiche Margelle telle que livrée (`FORBIDDEN`, `atomic_write_creation_property_missing`), parce que la fiche n'a pas encore de propriété `création` ;
  - la retouche qualifiée refuse une fiche en CRLF, puisque l'éditeur la montre en LF.
- **C-Codex-1 est valide** : sans MCP, Codex a relu le passage concurrent, conservé la retouche et demandé un nouvel accord. La fiche est identique octet pour octet.
- **Les cellules Claude ne sont pas jouées**, parce que le quota du compte C4 était épuisé (429). Il est revenu depuis 6 h.

## Ce qui change, pour toutes les cellules à rejouer
**Préparation applicative, identique pour chaque cellule et avant B0** : dans l'instance Obsidian isolée, on ouvre la fiche et on lance la commande native `editor:save-file`. Obsidian normalise alors les fins de ligne, et le gestionnaire de dates du coffre (FDM, livré avec Margelle) renseigne `création` et `modification`. Si les dates sont encore absentes après cette sauvegarde, on lance la commande livrée `frontmatter-date-manager:update-timestamps-current-file`. Le B0 est pris **après** cette préparation, qui est consignée dans les reçus.

**Pourquoi c'est représentatif** : chez un acheteur, la fiche d'un projet est créée ou ouverte dans Obsidian, et FDM la date à la première sauvegarde. Une fiche fabriquée par un script, sans dates et en CRLF, ne correspond à aucun usage réel. C'est aussi la préparation qu'a reçue C-Codex-1. **On ne recycle aucun diagnostic** : M-Codex-1 est rejouée de zéro, avec une copie neuve.

## Ce qu'on rejoue
**M-Codex-1, M-Claude-1, C-Claude-1**, dans l'ordre gelé, avec le compte C4 pour Claude Code, isolé comme au chantier A. **C-Codex-1 est conservée telle quelle.** Le protocole gelé ne change pas sur les critères, les versions, l'ordre ou le scénario.

## Ce que le rapport doit dire en plus
Le refus `atomic_write_creation_property_missing` est une **limite opérationnelle du MCP** sur une note sans date de création : par exemple une note créée hors d'Obsidian ou importée. Le rapport la décrit à part, comme un constat à transmettre à Mike, qui est l'auteur du MCP. Ce n'est pas un résultat G1. Le premier tour de M-Codex-1 n'a appelé aucun outil MCP de lui-même : ce fait est conservé, car il nourrit la décision sur une consigne produit du type « passer par le MCP quand il est branché ».
