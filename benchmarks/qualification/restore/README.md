# Qualification de la restauration locale

```bash
python3 scripts/odoo_qualify_restore.py --output /tmp/qualification-restore-nouveau
```

Prérequis : Docker local, Compose, images déjà présentes `odoo-qa:19.0` et
`pgvector/pgvector:pg16`, `unzip`. Le dossier de sortie doit être neuf.
Aucun appel de modèle, aucun téléchargement d'image prévu.

Le lanceur copie **sans modification** `odoo-restore.sh` et ses dépendances
dans un paquet isolé. Une définition Compose propre remplace la stack habituelle :
projet `qualification-restore-<aléatoire>`, volumes neufs, réseau interne, aucun
port hôte ni source client montée. L'environnement n'hérite pas des variables
Compose, Docker distant ou Odoo du poste. Le restaurateur est toujours lancé
depuis cette copie et reçoit une cible `qualification_*` explicite.

Le protocole, le lanceur et les scripts ORM seed/check sont copiés avant tout
démarrage ; les copies des scripts ORM sont celles effectivement exécutées. Une vraie base Odoo 19.0 contenant
une pièce jointe stockée sur disque, un cron et un serveur SMTP synthétiques
produit le dump SQL et le ZIP. Les trois scénarios sont :

- restauration complète ;
- refus d'une archive sans dump ;
- refus de déclarer prête une restauration demandant un module inexistant.

Les octets de la pièce jointe sont relus via l'ORM, puis la neutralisation,
l'état du cron et du serveur SMTP, l'administrateur actif et l'URL locale sont
vérifiés. Une base voisine et son fichier sentinelle sont comparés après chaque
scénario. Les invariants sélectionnés de la base source sont également contrôlés.
Le mot de passe admin n'est pas authentifié par un RPC dans cette qualification.

`report.json` distingue succès, échec du contrat et incident d'exécution.
`events.json`, les sorties originales, l'identité des images et du restaurateur,
le ZIP, les fichiers Compose et `SHA256.json` sont conservés. Le nettoyage vise
uniquement le projet créé et vérifie ses conteneurs, volumes et réseau par label.
Le code de sortie final reste non nul si le nettoyage échoue.

Un échec de mise à jour laisse une base locale inspectable : ce comportement est
observé, sans présumer d'un rollback atomique. Le test ne couvre ni sauvegarde
client, ni paiement, ni entreprise, ni disque plein, ni toute forme d'archive
tronquée. Le protocole ne mesure pas la fiabilité d'autres séries Odoo.

Premier essai, le 9 septembre 2026 : trois scénarios conformes en 31,437 secondes,
aucune ressource résiduelle du projet. Les résultats détaillés sont versés par
l'orchestrateur dans le dossier de la campagne de qualification.

Après correction du gel des entrées, le second passage des trois scénarios
reste conforme en 44,298 secondes, sans ressource résiduelle.
