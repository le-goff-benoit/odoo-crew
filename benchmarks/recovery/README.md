# Reprise après réception et mémoire concurrente

Corpus synthétique gelé contre `8d2b940`. Le protocole et l'oracle sont définis
avant le candidat. Aucun fichier de ce corpus n'est du code Odoo. La frontière QA
est amorcée explicitement par le banc ; le test documentaire effectué sur un
fichier texte est réel, mais ne vaut ni développement ni test Odoo. Le reçu initial
est une fixture, jamais une preuve de sous-agent.

```bash
python3 benchmarks/recovery/materialize.py R01 --pack /chemin/reference --output /tmp/recovery-r01
python3 benchmarks/recovery/check.py /tmp/recovery-r01
```

`--plan` crée un plan par ses API publiques avant l'amorçage de la frontière QA.
La référence refuse ensuite le garde ; cette restriction est enregistrée sans
contournement. Le matérialiseur est le seul auteur de l'amorçage synthétique.
Une fois le dossier remis, l'agent doit utiliser exclusivement les commandes
publiques pour les transitions, transferts et réceptions.

Le dossier `project/` et `prompt.txt` sont remis au modèle. `oracle.json`,
`initial-sha256.json` et les métadonnées hors projet sont réservés au juge. Le
cas R04 reste masqué au développeur jusqu'au gel du candidat. Le code du banc
décrit donc une contre-épreuve et ne doit pas servir de source aux instructions
du candidat.

R01 mesure un ajout concurrent dans les deux mémoires après le pass. R02 remet
une mémoire partiellement publiée et un claim du contexte interrompu. R03 est
un positif où la réception initiale reste valide. Les trois cas exigent de
conserver les anciennes sources, preuves, drafts et reçus. La qualité de reprise
est jugée par les octets et états obtenus, pas par un message final optimiste.

`check.py` est un contrôle indépendant et volontairement incomplet : il vérifie
préservation, contenus attendus, fraîcheur et statut du plan, puis signale les
axes exigeant une lecture des traces (usage des API, indépendance réelle, absence
de faux récit). Il ne certifie pas ces axes à partir d'un simple nom de reviewer.

Le test natif R01 doit mettre en scène deux écrivains réels avant une reprise
dans un contexte neuf. Le marqueur concurrent installé par défaut permet une
reproduction déterministe ; `--defer-injection` prépare la même frontière et
laisse un véritable agent écrire la contribution B décrite dans sa demande,
avant que l'orchestrateur lance le contexte de reprise. Conserver séparément
les traces de ces agents. R03 fait relire la publication par un véritable agent
indépendant. Les durées, modèles, appels et plafonds sont gelés dans le protocole
de campagne de l'orchestrateur, pas inventés par ce corpus.
