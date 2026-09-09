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

## Rendu du verdict et de ses références

```bash
python3 ~/.odoo19-agents/scripts/odoo_flow.py qa-report <flow.json> module_high_gate \
  --coverage <coverage.json> --outcome blocked --output <nouveau-rapport-qa.md> \
  --owner codex-orchestrateur
```

La jointure doit être revendiquée par ce propriétaire et le contrat déjà lié.
Le rapport est créé sous le verrou du flow, dans un fichier neuf du projet.
Il affiche **VALIDÉ** pour `pass` et une couverture entière, **À REPRENDRE** pour
`retry`, **REFUSÉ** pour `blocked`. Il indique l'issue proposée : seule la commande
`complete` enregistre effectivement la transition. Les critères, leurs statuts,
les chemins et empreintes sont reproduits ; les notes libres et déclarations
globales de build ou d'environnement ne sont pas reprises.

Une couverture partielle est autorisée pour produire un rapport négatif. Le
format, le contrat et toutes les références présentes restent vérifiés. Un statut
`covered` exige toujours une preuve ; les statuts `partial`, `missing`, `failed`
peuvent n'en avoir aucune. Une preuve d'exécution en échec peut étayer un critère
non couvert, avec les contrôles habituels d'intégrité et de fraîcheur du code.

Le flow conserve l'empreinte du rapport, celle de sa couverture, le contrat,
l'issue, la jointure et le propriétaire. Quand ce rapport figure dans les preuves
de `complete`, tous ces liens sont revérifiés, ainsi que la fraîcheur des preuves
imbriquées. Une modification du texte généré, même mineure, exige un nouveau
rendu dans un fichier neuf. Pour `pass`, joindre aussi la couverture JSON.

Si un ancien `qa.md` contient plusieurs tâches, ajouter une référence au rapport
de réception de la tâche sans en paraphraser le verdict. Les flows historiques
gardent leur fonctionnement : le rendu est optionnel au niveau du moteur.
Une preuve périmée ne doit pas empêcher de constater l'échec : `retry` ou `blocked`
restent possibles avec un constat autonome, en omettant le rapport devenu périmé.
Le moteur ne cherche pas à interpréter les titres des anciens rapports libres.

Le rendu ne prouve ni la justesse d'un `covered`, ni un build, ni l'environnement
d'exécution sur la seule foi d'un fragment. Cette limitation déclarative reste
identique à celle de la réception structurée ; la relecture métier et les oracles
indépendants restent nécessaires.

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
