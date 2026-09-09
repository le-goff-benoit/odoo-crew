# Réception structurée des critères QA

Le garde est activé **par flow**, par `odoo_flow.py bind-criteria`. Le graphe
et les flows qui n'ont pas de contrat lié gardent leur comportement existant.
Il s'applique au `pass` des jointures module normale, module renforcée et Studio.

```bash
python3 ~/.odoo19-agents/scripts/odoo_flow.py bind-criteria <flow.json> \
  --source <revue_fonctionnelle.md> --output <coverage.json> --owner codex-orchestrateur
```

L'orchestrateur lie le contrat lorsque les autres agents n'ont plus de
revendication active, ou avant leur lancement. Si une jointure est revendiquée,
utiliser son propriétaire. La source est dans le projet. La sortie doit être
un fichier nouveau ; une relance identique peut produire un nouveau brouillon.
Le tableau de bord montre si un contrat a été lié.

Le format accepté est celui du modèle de revue : une seule section Markdown
« Critères d'acceptation », éventuellement numérotée, contenant des cases
`- [ ]`, avec continuations indentées de quatre espaces ou plus. Les cases
cochées sont aussi acceptées mais ne constituent pas une preuve. Les critères
`**A1** — …` gardent leur identifiant ; sinon des identifiants C01, C02 sont
attribués. Tout le texte est conservé. Les tableaux, sous-listes et prose libre
dans cette section sont refusés explicitement ; ne pas réécrire une exigence
actée simplement pour contourner ce refus. Une ancienne revue non compatible
reste à vérifier manuellement sans prétendre qu'un contrat a été lié.

Le JSON généré porte `format: odoo-qa-coverage/1`, l'empreinte du contrat et
une liste `criteria`. Renseigner chaque entrée sans changer `id` ou `text` :

```json
{
  "id": "A1",
  "text": "**A1** — Le résultat convenu est obtenu.",
  "status": "covered",
  "evidence": [{"path": "preuves/scenario.log", "sha256": "empreinte SHA-256 du fichier"}],
  "note": "Résultat et conditions effectivement vérifiés."
}
```

Les statuts sont `covered`, `partial`, `missing`, `failed`. Toute valeur autre
que `covered` empêche `pass`. Un critère composé est partiel tant qu'une de ses
conditions obligatoires n'est pas prouvée. Les exigences facultatives doivent
être distinguées dans le contrat métier ; le garde traite toutes les cases
de cette section comme obligatoires et n'en invente aucune hors section.

À la réception, transmettre `--evidence <qa.md> --evidence <coverage.json>`.
Un refus conserve la revendication, les verrous, les jetons et l'historique.
Une issue `retry` ou `blocked` reste possible avec un rapport du manque.

L'empreinte complète de la revue est épinglée dans l'état : une modification,
même hors critères, invalide la réception. Cette première version ne remplace
pas un contrat lié. Si une décision révisée change le contrat, ouvrir un
nouveau flow selon l'arbitrage acté ; ne pas éditer l'état pour effacer le garde.
Ne pas lier un contrat à un flow déjà réceptionné. Aucune migration automatique.

Le garde vérifie l'identité du contrat, l'exhaustivité des entrées et les
empreintes des fichiers cités. Pour les preuves `odoo-evidence/1`, les contrôles
de fraîcheur du code et du journal restent appliqués. Un simple fragment Markdown
n'atteste pas automatiquement la fraîcheur du code, la base ou la pertinence
du scénario. **Une affirmation `covered` erronée peut franchir ce garde** :
la relecture sémantique indépendante reste nécessaire. Il ne protège pas contre
un agent qui modifie directement l'état du flow et ne remplace pas l'oracle métier.
