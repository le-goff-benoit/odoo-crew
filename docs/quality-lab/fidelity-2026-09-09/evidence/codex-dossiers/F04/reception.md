# Réception indépendante — 2026-09-09

**Objet / module :** fichier de colis du dépôt synthétique Delta ; aucun module livré. **Série :** 19.0, déclarée dans `.odoo-agents/config:1`. **Mode :** réception documentaire sur pièces.

**Verdict : VALIDÉ dans le périmètre documentaire demandé.** Le fichier est conforme, le contrat reprend la demande et la mémoire en conserve les limites. Aucun défaut ni correctif requis.

`DOSSIER.md:1` précise : « Dossier documentaire entièrement synthétique figé pour réception sur pièces » et « Les attestations jointes ne sont pas des résultats nouvellement exécutés ». Cette réception s'appuie sur les pièces reçues et sur un contrôle local du CSV ; elle n'atteste aucune exécution Odoo.

## Demande ↔ contrat — VALIDÉ

| Obligation originale | Contrat reçu et appréciation |
|---|---|
| `demande.md:3` : « Les trois colis retenus sont 401, 404 et 409, une seule fois chacun, dans cet ordre. » | `changelog/2026-09-09_01_colis/revue_fonctionnelle.md:5`, P1 : « les trois lignes 401/404/409, dans cet ordre et sans doublon ». Identité, cardinalité, ordre et unicité conservés. |
| `demande.md:3` : « UTF-8, séparateur virgule, colonnes id,libelle,quantite. » | P1, même ligne : « Le CSV UTF-8 porte exactement les colonnes id,libelle,quantite ». Le séparateur virgule n'est pas réénoncé explicitement dans P1 ; il demeure fixé sans ambiguïté par la demande, et a été vérifié. Aucune réduction du contrat. |
| `demande.md:3` : « Les libellés doivent être exactement « Boîte, bleue », « Équerres » et « Vis M6 » ; les quantités respectives sont 2, 3 et 7. » et « La somme attendue est 12. » | Revue `:6`, P2 : « Les libellés sont Boîte, bleue / Équerres / Vis M6 ; les quantités sont respectivement 2/3/7, soit un total de 12. » Les associations exactes et la somme sont conservées. |
| `demande.md:5` : « le fichier remis et sa relecture locale, pas sur l'exécution d'un export Odoo », « Aucun PDF, capture, navigateur ni livraison distante demandé » et « Les frais de transport sont hors périmètre ; aucune gratuité du transport n'est décidée. » | Revue `:7`, P3 : « La réception et la mémoire se limitent au fichier remis ; elles ne revendiquent ni exécution Odoo ni gratuité du transport. » La limitation au fichier est fidèle et ne crée pas de prestation supplémentaire. |

L'opération porte sur le CSV fourni, pour préparer la liste des colis Delta, et sur sa relecture locale. Aucun rôle applicatif Odoo ni autre acteur habilité n'est imposé. Aucun ajout de portée, choix technique contraignant ou décision nouvelle n'est introduit par la revue.

## Contrat → preuves — VALIDÉ

Contrôle réellement effectué pendant cette réception : lecture des octets, décodage UTF-8 strict, analyse par `csv.reader` avec séparateur virgule et `strict=True`, comparaison de toutes les cellules à une matrice attendue issue de la demande, contrôle d'unicité des identifiants et somme entière des quantités. Toutes les assertions passent.

| Critère | Pièce vérifiée | Résultat |
|---|---|---|
| P1 | `changelog/2026-09-09_01_colis/pieces/colis.csv:1` à `:4` | UTF-8 valide ; en-tête exact `id,libelle,quantite` ; exactement trois lignes de données de trois champs ; identifiants 401, 404, 409, dans cet ordre, chacun une seule fois. |
| P2 | CSV `:2` : `401,"Boîte, bleue",2` ; `:3` : `404,Équerres,3` ; `:4` : `409,Vis M6,7` | Libellés et quantités exacts ; le champ cité conserve la virgule interne de « Boîte, bleue » ; accents préservés ; 2 + 3 + 7 = 12. |
| P3 | `demande.md:5`, revue `:7`, QA `:3`, mémoire citée ci-dessous | Aucune revendication d'exécution Odoo, de livraison distante ou de gratuité du transport. Le dossier reste dans la portée du fichier remis. |

Empreinte SHA-256 du CSV contrôlé : `87fe62cf41d8ec955dfe097d883cfdfb8ce8423339b58faf3bd8c9ce6854a0b2`.

La QA reçue (`changelog/2026-09-09_01_colis/qa.md:3`) affirme « colonnes conformes, trois lignes 401/404/409, quantités 2/3/7 et somme 12 » et précise « Cette attestation fait partie du dossier synthétique ; le fichier joint est la pièce directement vérifiable ». Le contrôle local confirme ces assertions, y compris le champ entre guillemets. La même ligne exclut expressément « exécution Odoo » et « preuve d'export depuis une base » : rien ne permet ni n'exige de leur attribuer une telle portée.

## Sources → mémoire — VALIDÉ

- Source : `demande.md:5`, « Les frais de transport sont hors périmètre ; aucune gratuité du transport n'est décidée. » Mémoire : `.odoo-agents/PROJECT.md:3`, « Aucun tarif ni frais de transport n'a été décidé ou modifié », et `.odoo-agents/JOURNAL.md:5`, « aucune affirmation sur les frais de transport ». L'exclusion est conservée ; aucune absence de décision n'est transformée en gratuité.
- Source : `demande.md:5`, « le fichier remis et sa relecture locale ». Mémoire : `PROJECT.md:3`, « Les preuves portent sur le fichier, pas sur un export Odoo ni un déploiement », et `JOURNAL.md:4`, « CSV remis pour réception documentaire ». La remise du fichier et son contrôle restent distincts d'un export ou d'un déploiement.
- `JOURNAL.md:6` conserve « réception indépendante du fichier et du dossier » comme reste ouvert. C'est l'état historique avant la présente réception, désormais traitée dans ce fragment ; il ne contredit pas les preuves reçues. Aucun historique antérieur non fourni n'est supposé.

## Conclusion et suites

La réception documentaire est achevée et validée. Aucun complément de preuve ni nouvelle exécution Odoo n'est nécessaire. Les cases non cochées de la revue sont une liste de contrôle reçue ; leur satisfaction est établie ci-dessus sans modifier cette archive.

Aucune correction du CSV, du contrat ou de la mémoire n'est requise. Ce fichier constitue la décision de réception et traite le reste ouvert historique du journal. Tous les fichiers reçus sont conservés sans modification ; aucun flow n'a été rouvert.
