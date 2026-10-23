# Arrêt sur incident du périmètre technique — C05-T4-r1

La campagne reste incomplète. Trois cellules de série 1 sont jouées ; 77 de série 1 et les 110 de série 2 restent non jouées. Aucun T5, T6, T7, T7b ou T8 comparatif n'a été joué. Les qualifications factices ne sont pas des cellules de campagne.

## Faits observés

- C05-T2-r1 et C05-T3-r1 : REUSSI_VERIFIE. Les changements de date observés sont attribués par les reçus FDM aux octets finaux. Ces deux résultats ne valent que pour ces cellules.
- C05-T4-r1 : le modèle lit N absente, demande `vault.create` avec `overwrite=false`, reçoit `INVALID_PARAMETERS`, puis relit N absente. Le serveur indique que ce paramètre ne s'applique pas à create et accepte path/content. Le modèle termine non_applique. La création demandée n'est pas accomplie. Aucun nouvel essai corrigé n'a été fait dans cette cellule après cette réponse.
- Dans cette même cellule, un seul fichier change au disque : `.obsidian/plugins/frontmatter-date-manager/hash-cache.json`, 41 555 octets avant et après. SHA256 avant `d2f00a5539d462075a7e24ae4abb430531af34c9a39e37ea1c21888de4e3f89f`, après `f4c62bb78c31ffe4de74a2bbc2b1ee679818a0cdb916b2a69023ea6e7f297384`.
- Les deux entrées modifiées du cache concernent la fiche témoin P et le guide de démarrage du corpus. Les champs modifiés sont `lastAccessed` et, pour P, le `hash` interne du cache. Ce hash interne diffère du SHA256 des octets complets de P ; aucune équivalence n'est supposée. Les fichiers de notes restent identiques pendant la mesure, N reste absente.
- Le chemin de ce cache n'est pas dans `technical_paths` de l'adaptateur C05 gelé. L'oracle applique donc la règle publiée : HORS_CIBLE et verdict EFFET_NON_VOULU. Le verdict brut, les erreurs de création, les snapshots et les reçus sont conservés sans reclassement.
- Le code FDM livré 1.6.0, SHA256 `0bc7b76ea29409b1d085b7be75b9f7031516bf143455e857c208b0a93bceeb8c`, définit ce chemin via `getHashCachePath`, une sauvegarde différée via `markHashCacheDirty`, et l'écriture par `flushHashCache` vers `app.vault.adapter.write` (lignes 20365–20449 du main.js installé). Le code du plugin n'a pas été modifié.

## Inférence et limites

Cette différence est compatible avec la persistance différée du cache FDM après la préparation applicative. La trace runtime du writer de ce cache n'a pas été instrumentée ; l'attribution directe à FDM reste donc une inférence appuyée sur le chemin, la structure, le contenu et le code livré. Aucune corruption de note par C05 n'est observée. Le verdict brut ne permet pas d'attribuer à C05 ce changement du cache.

Le rejet du paramètre ajouté par le modèle est observé séparément. Il ne démontre pas une impossibilité générale de créer une note avec ce serveur. Aucune comparaison avec les neuf autres candidats n'est acquise sur T4.

## Pourquoi l'arrêt

Le brief impose : « Aucun réglage après un score, aucun correctif privé pour sauver Optimike. » Le protocole précise : « Aucun tuning après score : correction = autre version/série. » Ajouter maintenant ce chemin aux exemptions, puis traiter les cellules suivantes comme une série homogène, changerait le cadre après une observation. Aucun masque n'a donc été ajouté et aucun verdict de campagne n'a été recalculé.

L'arrêt pour incident est explicitement prévu par la demande. La mémoire n'est pas la cause de cet arrêt. Tous les processus appartenant au test ont été arrêtés, le verrou a été libéré ; aucun programme de Mike n'a été fermé.

## Point de reprise exact

Dernière cellule jouée : C05-T4-r1, ordre 4. Prochaine ligne : C05-T5-r1, ordre 5. C05-T1-r1 reste NON_JOUE à cause du contrôle CRLF/LF avant modèle ; elle n'a pas été rejouée. C06 reste non admis, isolation de sa CLI non démontrée.

Avant de démarrer une nouvelle cellule, qualifier l'observation des écritures du cache FDM et figer publiquement le traitement de cette surface pour tous les candidats dans une nouvelle version/série distincte. Conserver les trois résultats actuels et leurs limites. Le programme refuse de passer automatiquement cet arrêt sans un amendement public propre à C05-T4-r1. Aucun tel amendement dérogatoire n'a été créé par ce diagnostic.

Les bacs, reçus, snapshots complets et traces client sont conservés dans le run privé. Les témoins et traces publiques masquées sont sous `resultats/cellules/`. Ni corpus commercial complet, ni profils, ni authentification ne sont publiés. Avant une reprise, contrôler aussi les ports du backend propre à C07, dont 27349, en plus des ports communs.
