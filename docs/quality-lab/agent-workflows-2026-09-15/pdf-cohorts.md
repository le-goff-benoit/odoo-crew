# W03 — Cohortes PDF et comptabilité, calibration du 16 septembre 2026

**Calibration runtime synthétique, pas qualification des agents.** Aucun appel
LLM, projet client, base réelle ni modification des sources Odoo. Le runner
existant exécute les installations et tests réels dans des conteneurs jetables.

## Contrat explicite du témoin

Chaque pièce contient quatre lignes comptables de facture :

| Ligne | Montant | Marqueur technique explicite | Attendu dans le PDF |
|---|---:|---|---|
| Prestation | 7 | oui | présente, car non nulle |
| Forfait convenu | 42 | non | présente |
| Explication gratuite | 0 | non | présente |
| Marqueur technique masque | 0 | oui | absente |

Le total reste 49, et les quatre lignes restent en base. Le champ synthétique
`lab_technical_zero` indique la nature de la ligne : aucun forfait ou caractère
technique n'est déduit du montant ou du nom. L'héritage QWeb masque seulement la
combinaison **marqueur technique + sous-total nul**.

Trois cohortes passent par le rendu PDF véritable puis `pdftotext` :

| Cohorte | Type et date | Destinataire | Utilisateur de facturation | Titre attendu |
|---|---|---|---|---|
| Actuelle | facture, date courante du runtime | français | anglais | Facture |
| Historique | facture, 3 février 2020 | français | anglais | Facture |
| Avoir | avoir client, date courante du runtime | anglais | français | Credit Note |

L'utilisateur appartient à `account.group_account_invoice`, sans groupe
administrateur système. L'appel utilise son identité et sa langue ; le titre
prouve que la langue du destinataire reste appliquée, y compris dans le sens
inverse sur l'avoir.

Avant le rendu, les pièces sont comptabilisées et les écritures différées sont
vidées. Pendant le rendu, toute opération ORM `create`, `write` ou `unlink` sur
`account.move` et `account.move.line` fait échouer le contrôle ; les DML SQL
usuels sur ces tables sont également interceptés. Après le rendu et un nouveau
flush, les snapshots SQL de **toutes les colonnes** des pièces et lignes sont
identiques. Cette instrumentation de test ne remplace pas des droits d'accès.

## Résultats finaux

Dans le tableau, chaque résumé est `[échecs, erreurs, méthodes de test]` ; les
sous-tests par cohorte peuvent produire plusieurs échecs dans une même méthode.

| Série | Témoin | Mutants | Durée témoin / mutants | Nettoyage vérifié |
|---|---|---|---|---|
| 19.0 | [[0, 0, 3]] | [[5, 0, 3]] | 146.809 s / 104.992 s | oui |
| 18.0 | [[0, 0, 1]] | [[3, 0, 1]] | 146.778 s / 99.903 s | oui |

Sur 19.0, le runner conserve aussi les parcours stock et formulaire : les cinq
échecs attendus correspondent à stock, trois cohortes PDF et formulaire. Sur
18.0, seul le parcours PDF est lancé : les trois cohortes refusent la suppression
de toutes les lignes de sous-total nul. Aucun crash ou erreur technique ne
constitue la preuve d'un mutant détecté. Les essais mutants finaux n'émettent
aucun marqueur `WORKFLOW_PASS`.

La première passe était également correctement classée par le résumé de tests,
mais un marqueur PDF positif pouvait être émis après des échecs de `subTest`.
Ce marqueur a été conditionné à la réussite des trois cohortes, puis les deux
séries ont été intégralement rejouées. Les preuves ci-dessous proviennent de la
passe finale ; aucune correction métier n'a été nécessaire.

Deux tests déterministes supplémentaires calibrent les assertions : suppression
explicative, apparition de ligne technique, mauvaise langue, et reconnaissance
des écritures SQL comptables. **Ces mutations supplémentaires sont testées au
niveau des assertions ; seul le filtre global des zéros est muté dans le runtime
PDF.** Les neuf tests préexistants du banc passent également.

## Preuves et reproduction

- [Résultats Odoo 19.0](evidence/pdf/19.0/result.json),
  [empreintes des sources, journaux et PDF](evidence/pdf/19.0/SHA256.json).
- [Résultats Odoo 18.0](evidence/pdf/18.0/result.json),
  [empreintes des sources, journaux et PDF](evidence/pdf/18.0/SHA256.json).
- Les dossiers `witness/` et `mutants/` sous chaque série conservent les trois
  textes extraits et un extrait court des contrôles. Les PDF binaires et journaux
  complets sont dans les archives locales indiquées par `archive.json`.

```bash
python3 scripts/odoo_bench_workflows.py run --output /tmp/pdf-cohorts-new-19
python3 scripts/odoo_bench_workflows.py run --invoice18 --output /tmp/pdf-cohorts-new-18
python3 -m unittest discover -s tests/laboratoire -p test_pdf_cohort_oracle.py -v
```

Le briefing a identifié la série avant les lectures de code ; les cibles
réutilisables de l'héritage QWeb ont été vérifiées dans les sources 18.0 et 19.0,
puis confirmées par les deux installations. Les oracles restent dans le module
`workflow_oracle`, séparés du module candidat `workflow_case`. Aucun oracle n'a
été présenté à un agent dans cette campagne sans modèle.

## Limites

Trois cohortes synthétiques ne représentent pas toutes les factures historiques.
Cette passe ne couvre pas les taxes, devises multiples, avoirs partiels,
configurations multi-sociétés, mises en page client ni comparaison visuelle de
pagination. Elle valide les branches décrites dans les deux séries testées ; elle
ne qualifie aucun modèle, profil d'agent ou développement client réel.
