# Qualification des droits multi-sociétés

```bash
python3 scripts/odoo_qualify_rights.py --output /tmp/qualification-rights-nouveau
```

Prérequis : images locales `odoo-qa:19.0` et `postgres:16`, Docker disponible.
Le runner crée son réseau interne et ses bases, sans port publié ni montage
client. Ses conteneurs et son réseau sont supprimés puis leur absence vérifiée.
Le dossier de sortie doit être neuf ; ses protocoles, sources et oracles sont
copiés et empreintés avant exécution. Aucun fournisseur LLM n'est appelé.

Le témoin comporte un modèle synthétique, des ACL pour les utilisateurs internes
et une règle serveur globale qui limite les enregistrements aux sociétés actives.
Le mutant désactive uniquement cette règle, dans une base indépendante. Les
oracles ignorent la variante et vérifient toujours le même contrat sécurisé.

L'utilisateur possède uniquement la société A, sans privilège administrateur.
Les essais exécutent recherche, lecture directe et écriture sur B, écriture sur
A, puis imports autorisé et interdit avec la vraie méthode serveur `load`.
La même identité est authentifiée en XML-RPC. Les audits administrateur sont
séparés et servent exclusivement à vérifier les identifiants, valeurs et
l'absence de lignes étrangères créées malgré un refus.

La qualification du 9 septembre 2026 a accepté le témoin et détecté le mutant
sur les deux transports, Odoo `19.0-20260817`. Le mutant permet lecture,
écriture et import dans B, tout en conservant les opérations valides sur A.
Les premiers résultats ont aussi corrigé un défaut de l'oracle RPC : voir
[ORACLE_ERRATUM.md](ORACLE_ERRATUM.md). L'échec initial et sa réévaluation sont
conservés ; il ne s'agit pas d'un défaut des agents ni d'Odoo.

Portée : calibration réelle d'un modèle synthétique en 19.0. Ces essais ne
qualifient ni comptabilité, ni navigateur, ni portail, ni les autres séries.
Ils ne mesurent pas la capacité d'un agent à concevoir cette sécurité : le
modèle et les règles sont des témoins fixés par le banc.
