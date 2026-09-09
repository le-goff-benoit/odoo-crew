# Clôture d'une release — recette complète et livrables

Une release de changelog regroupe les tâches d'une même livraison. Pendant qu'il est
ouverte, chaque tâche n'a reçu qu'une QA proportionnée. **La clôture est le
moment où tout est rejoué, une fois, sur l'état exact qui partira** : base
neuve, suite complète, tours, désinstallation, mise à niveau sur la copie du
client et documentation métier `doc.md`. Les guides DOCX/PDF et la communication sont facultatifs, sur demande explicite. C'est un acte de l'humain — cette
commande ne se lance pas toute seule en fin de `/odoo-new`.

Réponds en français. La release à clôturer suit cette consigne ; sans précision,
c'est la release ouverte du projet courant.

Cette commande suit le même graphe persistant que `/odoo-new`. Après le
briefing, ouvre un run `--kind close`, enregistre le nœud `briefing`, puis suis
`odoo_flow.py ready` jusqu'à `release_closed` ou `release_blocked`. L'agent
principal est le seul à mettre à jour l'état et à écrire les livrables
partagés. La recette technique reste un nœud unique tant que
`odoo-recette.sh` écrit un seul `recette.md` et partage le stack ; ne simule
pas du parallélisme au prix de bases ou de fichiers concurrents.

```bash
FLOW=$(python3 ~/.odoo19-agents/scripts/odoo_flow.py start <racine> \
  --kind close --id cloture-<release>)
python3 ~/.odoo19-agents/scripts/odoo_flow.py status "$FLOW"
python3 ~/.odoo19-agents/scripts/odoo_flow.py claim "$FLOW" briefing
python3 ~/.odoo19-agents/scripts/odoo_flow.py complete "$FLOW" briefing \
  --outcome close --evidence <sortie-du-briefing>
```

## Étape 0 — Situer et vérifier que la release est clôturable

```bash
python3 ~/.odoo19-agents/scripts/odoo_briefing.py <racine_du_projet>
RELEASE=$(~/.odoo19-agents/scripts/odoo-release.sh current <racine>)
~/.odoo19-agents/scripts/odoo-release.sh points "$RELEASE"
~/.odoo19-agents/scripts/odoo-release.sh modules "$RELEASE"      # modules touchés depuis l'ouverture
~/.odoo19-agents/scripts/odoo-release.sh changed "$RELEASE"      # fichiers, pour le tableau « Fichiers »
git -C <racine> status --short                           # fichiers non suivis dont le code dépend ?
```

Annonce : **projet, série, release, points (réalisés / à faire), tickets de
support traités, modules touchés, copie client disponible ou non.**

Lis `effort.json` et `docs/EFFORT.md`. Estime seulement le travail de clôture
encore à venir s'il manque à la prévision ; ne reconstruis pas celle des tâches
terminées. Mesure recette, reprises et consolidation avec `odoo_effort.py start`
puis `stop` par tâche et rôle, sur la session réelle de l'exécutant. Les anciennes
mesures indisponibles sont une réserve de bilan, sans bloquer une QA verte.

Les points `[support #NNNN]` font partie de la livraison : une réponse, une
réparation de données confirmée ou une correction de code. Leur diagnostic est
dans `support/` ; le test `test_support_NNNN.py` fait partie de la suite jouée
par la recette.

Un point encore « à faire » n'empêche pas la clôture : il est marqué
**différé** dans `demande.md` (« Décisions de périmètre ») et retiré de la
livraison. Un point « configuration » (le standard couvrait le besoin) est
livré comme tel : la configuration à faire est décrite dans le README.

Un `__init__.py` qui importe un fichier non suivi par git est un arrêt
immédiat : ce qui part en production est le commit, pas le répertoire.

### Version avant recette

Prépare les versions une seule fois avant les tests :
`python3 ~/.odoo19-agents/scripts/odoo_release_guard.py prepare "$RELEASE" --module <chemin_relatif_module>`.
`versions.json` conserve départ et cible ; si le projet a déjà choisi une version
nouvelle, elle est conservée. Un code modifié ensuite invalide la preuve concernée.

## Étape 1 — Recette complète, module par module

```bash
export ODOO_ADDONS_DIR=<répertoire contenant les modules>
~/.odoo19-agents/scripts/odoo-recette.sh <module> --release "$RELEASE" [--db <copie_client>]
```

Pour chaque module touché. Pour les points `[studio]` : copie fraîche du client,
`odoo_pack.py apply` puis `diff` à zéro, scénarios `studio/test_*.py`, second
`apply` sans changement ; résultat ajouté à `recette.md` à la main (le script
ne couvre que les modules). Le déploiement d'un pack (staging puis production,
`diff` avant `apply`, confirmation humaine en production) est « Reste à faire »,
jamais fait par la clôture. La copie du client est celle du briefing (base
restaurée sur le stack) ; si elle manque, restaure la sauvegarde
(`odoo-restore.sh`) ou, à défaut, demande-la — et écris la réserve.

Le script écrit `$RELEASE/recette.md` et rend 0 seulement si tout est vert. Lis le
tableau, pas les logs. Il signale aussi :

- **un module sans test** → réserve bloquante pour une release de code ;
- **une version de manifest qui n'a pas bougé** depuis l'ouverture alors que
  du code a changé → l'incrémenter maintenant (composante convenue avec le
  projet, lue dans le fichier), puis **relancer la recette** : la version
  livrée est celle qui a été testée.

Si un contrôle est rouge : **on ne clôture pas.** Applique le rôle
`~/.odoo19-agents/roles/qa-review.md` (mode release) pour localiser, puis
`roles/implementation.md` pour corriger, puis recette à nouveau. Deux reprises
au maximum ; au-delà, livre l'état réel et arrête.

## Étape 2 — Recette navigateur et captures

Applique `~/.odoo19-agents/roles/qa-review.md` § Étape 3 : chaque critère
d'acceptation de `revue_fonctionnelle.md` est couvert par un tour, un test HTTP
ou un scénario manuel rejoué **sur la copie du client**, rechargement et
contrôle serveur compris. Résultat dans `$RELEASE/tests_navigateur.md` (gabarit
`~/.odoo19-agents/docs/templates/changelog/tests_navigateur.md`). Sans
interface concernée, le fichier le dit explicitement, avec les contrôles
réellement exécutés.

Captures finales dans `$RELEASE/captures/`, numérotées dans l'ordre du parcours,
depuis la copie locale neutralisée — jamais la production.

## Étape 3 — Documentation métier et consolidation

Écris toujours `$RELEASE/doc.md` : résultat métier, actions de l'utilisateur,
conditions et droits utiles, effets sur les données existantes, mise en service,
limites et références. Décris uniquement les comportements livrés ; sépare ce
qui est validé localement de ce qui reste à déployer. Gabarit :
`docs/templates/changelog/doc.md`. Une copie de la spec n'est pas une documentation
utilisateur. Contrôle chaque affirmation contre les critères et les preuves.

Écris `$RELEASE/consolidation.md` : décisions devenues actuelles, règles remplacées,
questions encore ouvertes, connaissances mises à jour dans PROJECT/DECISIONS,
ou justification explicite d'absence de changement. Les journaux anciens restent
historiques, pas des instructions actuelles. Référence les sources des décisions.

Le guide Camptocamp DOCX/PDF et la communication sont produits seulement sur demande
explicite, pour cette release identifiée, maintenant ou après clôture. Leur absence
ne bloque pas la livraison ; aucun envoi ni déploiement n'est implicite.

## Étape 4 — README final, version, commit proposé

Ferme les mesures terminées, importe les consommations attribuables et lance
`odoo_effort.py report "$RELEASE"`. Référence `bilan-effort.md` dans le README :
prévu/réel par tâche et agent, reprises comprises, jetons et coût IA sourcé ou
calculé sur un tarif technique daté. Montre la couverture et les absences ;
un montant inconnu ne vaut pas zéro. Distingue les minutes d'agent cumulées,
la durée calendaire et les chevauchements, ainsi que coûts déclarés et calculés.
Régénère le bilan après les dernières mesures de clôture.

Réécris `$RELEASE/README.md` dans sa forme finale, d'après le gabarit
`~/.odoo19-agents/docs/templates/changelog/README.md` :

- résultat métier en une ligne, puis « Livraison » point par point (ce que
  l'utilisateur voit ou peut faire) ;
- **versions de départ et livrée lues dans les manifests** (`git show
  $(cat $RELEASE/.base):<module>/__manifest__.py` pour le départ) ;
- « Tickets de support » : un tableau numéro · symptôme · classement · issue,
  d'après `support/` ;
- « Fichiers » d'après `odoo-release.sh changed` ;
- « Validation » recopiée de `recette.md` — chaque ligne correspond à quelque
  chose qui a été exécuté ;
- « Réserves » : tout ce qui est rouge, partiel ou non exécuté, avec la cause.
  Jamais vide par oubli ; « Aucune » seulement si c'est vrai ;
- « Reste à faire » : déploiement, envoi, décision attendue.

`demande.md` : chaque demande d'origine y est, telle quelle ; les décisions de
périmètre (retenu / différé / hors périmètre) sont à jour.

Avant de retirer le marqueur, relie les contrôles à l'état testé avec
`odoo_evidence.py` (périmètres custom et dépendances concernés, `--module` pour
les tests Odoo). Une preuve verte peut être réutilisée sans rejouer sa commande
si code, environnement, données et périmètre restent identiques ; la relecture
indépendante et les critères métier restent nécessaires.

Écris aussi `controls.json` selon `docs/RELEASE_PLAN.md` : installation, update,
tests, copie client, navigateur et désinstallation, résultat et preuve de chacun.
Une non-applicabilité exige sa raison ; pas de dispense de copie à risque élevé.
La voie doit correspondre aux tâches effectivement livrées.

Scelle la clôture :
`python3 ~/.odoo19-agents/scripts/odoo_release_guard.py seal "$RELEASE" --scope <module> --proof <preuve_relative_projet>`.
Répète les options pour couvrir les modules/artefacts Studio livrés. Le contrôle
bloque les preuves périmées et les documents manquants. Il ne remplace pas la
relecture du sens métier. Puis retire le marqueur :

```bash
~/.odoo19-agents/scripts/odoo-release.sh close "$RELEASE"
```

Propose le **message de commit** de la release (`[TAG] module: sujet`, guide § 10 ;
un commit par release, corps = les points livrés). Tu ne commites, ne pousses et ne
déploies pas sans qu'on te le demande.

## Étape 5 — Capitaliser

1. **Journal** : une entrée de release dans `<projet>/.odoo-agents/JOURNAL.md`,
   quinze lignes au plus — les entrées de tâche existent déjà, celle-ci dit ce
   que la recette complète a révélé et ce qui part. Référence le bilan d'effort
   et les causes d'écart utiles aux futures tâches comparables ; aucune conversion
   en travail humain.
2. **`PROJECT.md`** : pièges durables, décisions actées, compréhension métier
   acquise pendant la release. Puis `odoo_project_scan.py <racine>` pour
   rafraîchir le relevé.
3. **Candidats à `LESSONS.md`** : ce qui dépasse ce projet. Compte les entrées
   de journal écrites depuis le dernier retex (`grep -c '^## 20' JOURNAL.md`
   contre la date `dernier-retex` en tête de `LESSONS.md`) : au-delà de dix,
   ou dès qu'une candidate est sérieuse, recommande `/odoo-feedback`.

## Compte-rendu final

```markdown
# Clôture — <titre de la release>

**Projet** <nom> · **série** <X.Y> · **release** `<dossier>` · **modules** <…> · version <a> → <b>

## Recette
<tableau de recette.md, un par module>

## Livrables
<README, tests_navigateur, captures (n), guide (pages), communication — chemins>

## Réserves
<ce qui n'est pas vert ou pas exécuté, et ce qui le lèverait>

## Reste à faire
- commit proposé : `[TAG] module: …`
- déploiement <production / staging>, communication à <contact>
- <n> entrée(s) de journal depuis le dernier retex — /odoo-feedback recommandé ou non
```

## Règles

- Une ligne d'état par étape, même forme que `/odoo-new`
  (`[1/5 recette] vertical_construction ✅ · vertical_construction_project_management ❌ 1 test → reprise`),
  et une annonce de durée avant chaque recette Docker. Aucune sortie d'outil brute.
- Emploie le mot du projet pour la release (`lot_label` de `.odoo-agents/config`).
- Ne clôture pas une release dont la recette est rouge ; dis pourquoi et arrête.
- Ne déclare jamais « testé » ce qui n'a pas été exécuté ; la réserve est un
  résultat légitime.
- La version livrée est celle qui a été testée : tout incrément de version
  après la recette impose de la rejouer.
- Ne lis pas les logs Odoo d'un bloc : `recette.md`, la ligne `RECETTE …`, et
  `grep -n` pour localiser.
