# Retouche dans l’éditeur Obsidian par CDP

**QUALIFIÉE le 23/10/2026** dans une instance Obsidian isolée, FDM 1.6.0 actif. Preuves : `../preuves/qualification-editeur.json`. T5 (création de texte dans une note ouverte), T6/T7 (remplacement dans l’éditeur), insertion début/fin Unicode, refus d’une précondition périmée sans écriture : contrôlés. Le verrou partagé a été libéré après arrêt du seul processus isolé appartenant au kit.

Le script autonome `retouche-editeur.mjs` fonctionne avec Node 24, sans installation et sans candidat MCP. Il lit le disque mais n’y écrit jamais ; `MarkdownView.editor.replaceRange` saisit le texte et Obsidian enregistre. Son succès exige ensuite l’égalité exacte du fichier sur disque. Une attente de 50 ms sert au sondage ; aucun délai seul ne vaut confirmation.

```powershell
node "<kit>\scripts\retouche-editeur.mjs" --port 27346 --vault "<chemin absolu du coffre isolé>" --note "Efforts/Projets/Note.md" --text "Texte à insérer" --position end
```

Paramètres : `--port` CDP, `--vault` identité attendue obligatoire, `--note` chemin relatif obligatoire, `--text` OU `--text-file` (UTF-8), `--position start|end|<offset UTF-16>`. Remplacement : ajouter `--delete-length <nombre d’unités UTF-16>`. Protection recommandée : `--expected-before-sha256 <hash du fichier attendu>`. `--timeout-ms` vaut 60000 par défaut. La note doit déjà exister et une seule page doit être exposée sur ce port. Le texte intégral de l’éditeur doit correspondre au disque avant la saisie. Les ports quotidiens 27123/27124 sont refusés. Sortie JSON sur stdout ; aucun fichier de preuve écrit par ce script. Code non nul : ne pas transmettre l’écriture concurrente.

Pour T5, `ui_cdp.mjs inject T5` crée la note vide avec l’API Obsidian, l’ouvre en mode source, puis saisit le texte dans l’éditeur. `ui_qualification.py inject --task T5` confirme le contenu disque avant de rendre la main. Le script autonome d’insertion n’a pas de fonction de création ou d’écriture filesystem.

Le lanceur de qualification `ui_qualification.py launch` prend atomiquement `VERROU-OBSIDIAN-TEST.txt`, réserve le port 27346 et utilise un profil sous `kit/runtime/ui/`. Si le verrou existe, il affiche VERROU_OCCUPE et ne lance rien. `stop` vérifie le PID et sa ligne de commande avant de l’arrêter, puis retire seulement son propre verrou. Le profil quotidien n’est ni lu ni modifié.

G1 peut réutiliser le script autonome avec **son propre port, son coffre et son verrou** ; il n’a pas à lancer le profil du kit. Chaque retouche doit être désignée comme « retouche saisie dans l’éditeur d’Obsidian (saisie simulée par un script, pas par une personne) ». Le script ne prouve ni l’admission d’un candidat, ni une protection de concurrence.
