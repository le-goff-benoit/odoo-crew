# Mémoire partagée pendant la release — 15 septembre 2026

**Les outils et le parcours partagé sont livrés ; les essais natifs gardent un
échec et une réserve.** Aucun gain global de vitesse de release n'est déduit.

[Protocole préalable](../KNOWLEDGE-PROTOCOL.md) ·
[Utilisation](../../KNOWLEDGE.md) · [Résultats natifs](native-results.json) · [Relecture indépendante](independent-native.md).
Référence : `916ec52f04faf67fe05bb9e165eff6ad0722842a`.

## Ce qui est adopté

- Contributions sourcées publiées pendant les tâches, immuables et atomiques.
  La réception rend immédiatement son fragment mémoire disponible aux suivantes.
- Lecture de la mémoire exigée avant réception des plans `shared_memory` ;
  une lecture périmée ou des sources non vérifiées demandent une réconciliation.
- Documents originaux préservés, DOCX/XLSX/PDF extraits avec repères et limites ;
  aucune décision confirmée par extraction. Images à lire manuellement.
- Index AST/XML série/révision, cache standard séparé du custom ; aucune déduction
  de l'état installé en base. Sur Stock Community 19.0 : 182 fichiers et 2 775
  symboles, zéro erreur de parsing, index revérifié. Révision Community
  `8759429547e42e9f63b15a7c80475be46ef437e2`. Pas de tests runtime Odoo dans cette passe.
- Décisions liées aux tâches affectées, consolidation de clôture distincte des
  observations de déploiement et vue mémoire en lecture seule dans Tricorder.

## Avant/après et améliorations observées

Le même dossier K01 n'exposait pas l'exception du tableur dans le contexte de
référence. Elle est présente après, avec `Livraison!B9`. Le contexte passe de
545 à 2 067 caractères : **meilleure couverture, pas réduction de volume**.
K06 conserve sa règle et ajoute le repère documentaire (725 → 2 491 caractères).
[Mesures](context-comparison.json). Une première requête « société » ratait
« sociétés » : accents et pluriels simples sont maintenant rapprochés ; un test
de régression couvre cette correction. Les synonymes restent une limite.

Une première évaluation indépendante du parcours avait observé une ancienne
passation encore validée après arbitrage contraire. Correction : `affects_tasks`
et `impact_reason` obligatoires pour une décision acceptée dans une release
planifiée ; empreintes d'impact liées aux réceptions. La contre-épreuve de
72 commandes constate T02 périmée immédiatement, T01 toujours validée, T03 en
attente ; puis reprise/réception T02 et démarrage réel de T03.
[Rapport indépendant](independent-workflow.md) · [Reproduction synthétique](reproduce-workflow.py).

Le contrôle déterministe comprend témoins positifs et mutations : exception
absente, proposition confirmée à tort, déploiement inventé, citation absente,
source changée, pièce hors projet, extraction falsifiée, report et concurrence.
Les suites utilisent des projets temporaires, aucun appel modèle en CI.

## Quatre passages natifs, budget tenu

Les CLI natives utilisent des projets et homes isolés, profils générés et outils
du candidat figé. Aucun oracle n'est accessible au candidat. Les identités de
modèle sont demandées à effort medium ; Codex ne restitue pas son identité exacte
dans ces traces, Claude restitue `claude-opus-5` derrière l'alias `opus`.

| Cas | Fournisseur | Durée | Contrôles structurés | Réception indépendante |
|---|---|---:|---|---|
| K01, exception XLSX | Codex / Astra demandé | 59,215 s | Réussis | Accepté |
| K01, exception XLSX | Claude / Opus | 100,251 s | Report inventé | Refusé |
| K06, règle DOCX et proposition récente | Codex / Astra demandé | 56,458 s | Réussis | Accepté |
| K06, règle DOCX et proposition récente | Claude / Opus | 68,411 s | Réussis | Accepté avec réserves |

Tous conservent l'exception et ne déclarent aucun déploiement vérifié. Claude K01
assimile le mandat de passation à un report de T02 non attesté. Claude K06 décrit
une levée du report trop restrictive : un arbitrage pourrait aussi rejeter la
proposition et maintenir l'ancienne règle. Le mode d'emploi précise ces deux
distinctions ; la CLI `verify` signale désormais explicitement le `--file` manquant.

**Pas de nouvel appel après ces corrections**, pour respecter la borne de quatre.
La qualification native du comportement corrigé reste expérimentale. Les outils
sont couverts par tests et contre-épreuve indépendante ; aucune modification de
politique de modèle n'est justifiée par ces quatre dossiers. Les mesures de tokens
restent celles des transports dans le JSON, avec cache séparé, sans coût inventé.

Le candidat natif a été figé avant les corrections d'impact, de recherche lexicale,
de consolidation et de diagnostic CLI. [Empreintes du sous-ensemble pertinent](native-frozen-excerpt.json).
Les modifications ultérieures sont validées par la suite déterministe et la
contre-épreuve de parcours ; elles ne sont pas présentées comme rejouées en natif.
Les traces natives brutes et artefacts complets restent locaux ; seules les preuves
synthétiques utiles et verdicts sont publiés.

## Vérification de livraison

371 tests Crew (un ignoré : tomllib absent sur Python 3.10), graphe valide,
génération isolée puis installation locale : 35 fichiers et deux blocs
d’aiguillage identiques entre Claude/Codex. Validation des skills plan/start
réussie. Tricorder : 81 tests Python, 56 Node, 16 parcours Electron (un parcours
client réel ignoré) et paquet Debian 0.3.1 testé.
