# Fragment QA d'exécution renforcée — frais de préparation (D-02)

Base `lab_qa`, séparée de la copie client.

| Contrôle | Commande | Résultat |
|---|---|---|
| Installation base neuve + tests ciblés | `labctl qa lab_rental --quick --fresh --tags /lab_rental:TestPreparationFee` | `install=ok` · **0 failed, 0 error of 10 tests** · ⏱ 15s |
| Mise à jour sur base existante + tests ciblés | `labctl qa lab_rental --quick --update --tags /lab_rental:TestPreparationFee` | `update=ok` · **0 failed, 0 error of 10 tests** · ⏱ 4s |
| Logs | analyse `labctl qa` | ERROR/CRITICAL 0 · tests ignorés 0 · WARNING liés à `lab_rental` 0 |

Ligne de recette conservée dans `qa_runtime.txt` :
`RECETTE module=lab_rental db=lab_qa install=ok update=n.a. tests="0 failed, 0 error(s) of 10 tests" errors=0 failed=0 skipped=0 warnings=0 total=15s`

10 tests exécutés, 10 verts. Les dix méthodes couvrent : borne 3/4/7 jours (Q1), prêts à 4 et
10 jours (Q2), enregistrement vide, forfait indépendant du tarif, franchissement du seuil et
bascule location→prêt sur champ stocké, et non-retour de D-01 (forfait fixe, non proportionnel).

**Verdict de la voie : VERT.**
