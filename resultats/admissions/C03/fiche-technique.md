C03 — mcp-obsidian 0.2.3 (MarkusPfundstein)

Python stdio vers REST 5.5.2. obsidian_get_file_contents retourne un texte JSON encodant le fichier entier ; chemin filepath. obsidian_put_content crée ou remplace entièrement ; obsidian_append_content ajoute ; obsidian_patch_content cible heading/block/frontmatter (operation/target_type/target/content). Pas de ifMatch dans le schéma observé, ni statut durable exposé. Relecture complète après mutation ou réponse perdue. Les outils de lecture/recherche de notes sont autorisés ; aucun autre serveur de secours.
