C02 — MCPVault 0.17.0

Serveur fichiers stdio, sans plugin Obsidian. read_note retourne fm (propriétés) et content (corps). read_note_lines permet la lecture brute intégrale depuis startLine=1 avec une borne couvrant le fichier, frontmatter compris. write_note : overwrite/append/prepend, frontmatter facultatif. patch_note remplace une chaîne exacte unique ; update_frontmatter conserve les propriétés en merge=true. Aucun jeton de révision ni statut durable établi. Relire après écriture et après une réponse perdue.
