# Auto-relecture documentaire B-42

**Non indépendante**, par l'auteur dans la même conversation, imposée par LAB.md. Le garde exigeant une nouvelle conversation n'est pas activé. La couverture structurée du contrat reste obligatoire.

## Demande ↔ contrat
`decisions/current.md` : « uniquement sur les enregistrements de self en état draft appartenant à la société ACTIVE env.company » repris en A1, et non remplacé par allowed_company_ids. « sequence=100,200,... » repris en A2 ; somme excluant cancelled et date/id conservées. L'interdiction de modifier les émis est A3. Autorisation locale et droits inchangés sont A4/A6 et les bornes de la spec. Rouge/vert A5, idempotence A6, publication et release ouverte A7.
Ajouts techniques justifiés et explicités : absence de write au rejeu (renforce l'idempotence), pas d'arrondi arbitraire, contrôle write même sur valeur déjà correcte. Aucun écran/RPC imposé dans la demande, aucune substitution de canal.

## Contrat → preuves
Tests réels `TestRepair` : 5 échecs métier dans red.log ; mêmes méthodes 0 échec/erreur dans green.log. Le test mixed_selection exerce un issued sélectionné, un draft non sélectionné et une autre société accessible ; les snapshots relisent tous les champs protégés et lignes. Changement de société active, égalité de date/ID et contexte forgé sont exercés, pas seulement décrits.
La reprise copie porte sur les vrais IDs historiques sous UID 5 sans sudo. `repair-first.log` et `repair-second.log`, assertions intégrées et `replay-comparison.json` prouvent les deux transactions et la persistance ; zéro write instrumenté et write_date conservés. L'AccessError attendu sous UID 6 est capturé avec postconditions inchangées.
Le lint n'est pas entièrement vert : author préexistant absent. Son statut rouge est conservé dans la synthèse, séparé du diff sans nouvelle anomalie. Ce n'est pas un contrôle omis. Aucun test UI, RPC externe, désinstallation ou livraison revendiqué.

## Sources → mémoire
Les propositions complètes PROJECT/JOURNAL conservent les entrées historiques et ajoutent les résultats locaux précis, les émis/autres sociétés exclus, les droits testés, la dette de lint, le caractère non indépendant et l'absence de livraison. L'ancien « reste ouvert » du 14 septembre reste daté comme historique ; la nouvelle entrée établit la reprise réalisée.
Publication locale des propositions relues avant le pass pour satisfaire A7 (exigence de publication elle-même incluse au contrat) ; le nœud journal contrôlera leur identité et n'ajoutera pas de doublon. Aucun garde de réception indépendante/publication automatique activé. Ceci ne vaut pas clôture de release.

Conclusion : contrat technique et reprise satisfaits ; dette statique antérieure explicitement conservée. La réception du flow est recevable après contrôle des pièces publiées et de leurs empreintes.
