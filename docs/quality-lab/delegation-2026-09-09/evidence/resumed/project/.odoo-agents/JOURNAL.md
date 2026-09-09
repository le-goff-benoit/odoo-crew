# Journal
## 2026-08-01 — Historique
**Appris** : Les durées négatives étaient anciennement permises pour des essais ; D-31 remplace cette tolérance.

## 2026-09-09 — D-31 : interdire les jours négatifs de location (`lab_rental`, 19.0)
**Demande** : contrainte SQL `days >= 0` sur `lab.rental`, zéro valide, `jours × tarif` inchangé.
**Fait** : reprise de la chaîne interrompue pendant les voies QA — trois revendications abandonnées
libérées avec motif puis réattribuées ; revue et code repris tels quels ; trois voies QA rejouées en
parallèle (statique, exécution, copie client) sur les bases reconstituées.
**Verdict** : VERT AVEC RÉSERVE — A1→A9 satisfaits, 6/6 tests (ciblés puis suite complète),
contrainte prouvée en base après `-u`. Détail : `changelog/2026-09-09_01_.../qa.md`.
**Appris** :
- Une contrainte CHECK posée sur une table portant une ligne violante n'est **pas** créée et l'`-u`
  se termine vert (`odoo/orm/registry.py:682-717`) : compter les lignes violantes avant, vérifier
  `pg_constraint` après — le code de sortie de la mise à niveau ne prouve rien. Reproduit sur la copie.
- Une preuve d'exécution ne survit pas à la base sur laquelle elle a été prise : après reconstitution
  de l'environnement, tout run antérieur est à rejouer, seules les preuves de forme (sources) tiennent.
- Le sha de `.base` d'une release ne résout pas dans une copie de dépôt : prévoir une délimitation du
  diff par recoupement plutôt que de conclure à l'absence de diff.
**Reste ouvert** : arbitrage des lignes `days < 0` d'une base réelle (mise à 0 ou suppression) → Luc Roy ;
`author` manquant au manifest (dette, lint rouge de ce seul fait) ; message vérifié à l'écran et version
du manifest à la clôture ; `NULL` sur `days` toujours accepté (hors D-31).
