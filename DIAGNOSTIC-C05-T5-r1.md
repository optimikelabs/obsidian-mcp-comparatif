# Diagnostic C05-T5-r1 — injection UI invalide

Cette tentative sous v1.2 demeure **NON_JOUE / INJECTION_INVALIDE**. Aucun reclassement et aucun rejeu. La campagne compte toujours 3/80 cellules jouées en série 1 et 0/110 en série 2. Les trois cellules jouées l’ont été sous v1.1.

## Faits observés

La configuration effective du client et les métadonnées RPC indiquent Codex CLI 0.160.1, gpt-6.1-sol, effort high ; serviceTier default est confirmé par config/read. Le client se termine avec code 0, sans erreur fournisseur ni outil interdit. Astra reste l’orchestrateur.

Le relais retient la première demande de création (request_held, seq 8). Le hook T5 appelle ui_cdp.mjs. Celui-ci lit cfg.N, mais campaign_runtime.prepare ne fournit ni N ni P dans obsidian.json, contrairement à la configuration utilisée par ui_qualification.py. Le script passe donc un chemin undefined à l’API Obsidian. L’erreur observée est `TypeError: Cannot read properties of undefined (reading 'replace')` (relay_error, seq 9).

Aucun événement ui_disk_verified ni snapshot human n’existe. La note humaine n’est pas créée. Le relais avait déjà positionné injected=true ; la requête suivante est transmise (mutation_dispatch, seq 14) sans injection réussie. Le candidat la refuse : INVALID_PARAMETERS pour overwrite=false sur vault.create. La dernière relecture indique la note absente ; le client termine non_applique.

Le diff complet ne contient aucune note métier : seul hash-cache.json change dans les champs autorisés par v1.2. L’oracle conserve ses erreurs secondaires PREMIERE_MUTATION_PERTE et CIBLE_ABSENTE ; en l’absence d’injection humaine, elles ne constituent pas une preuve de perte de contenu humain ni une conclusion sur la protection du candidat.

## Arrêt et reprise

La mémoire n’est pas la cause. Les minima et la surveillance à la seconde sont conservés dans resultats/incidents/injection-ui-C05-T5-r1.json et le journal de cellule. L’instance possédée par le test a été arrêtée, le verrou libéré ; aucun programme de Mike fermé, bitnet non relancé.

Prochaine cellule ordonnée : **C05-T6-r1**, bloquée jusqu’à correction commune et qualification positive/négative du chemin UI et du comportement du relais après échec d’injection, puis amendement public. Aucun correctif du relais, du client ni des oracles n’a été appliqué après cette tentative. Le dossier C05-T5-r1 est conservé et ne sera pas rejoué implicitement.

C05-T1-r1 : remplacement réservé à la fin de série 1. C06 : nouvelle admission réservée à la fin de série 2. Les séries restent incomplètes, sans extrapolation ni classement.
