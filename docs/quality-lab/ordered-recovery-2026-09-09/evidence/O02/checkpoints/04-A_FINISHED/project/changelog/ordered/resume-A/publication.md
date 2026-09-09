# Publication A après reprise

La première réception indépendante, antérieure à cette reprise, est conservée dans `reception-A/review-A.json` et sa provenance native dans `native-provenance.json`. Le flow avait déjà reçu `module_task_gate → pass` et attendait `journal_task`, sans claim actif.

Nouvelle opération : claim par `codex-resume-A`, puis `publish-memory` par API publique du pack figé. Les deux cibles, initialement à leur base, sont désormais exactement identiques aux drafts approuvés. La commande a réussi (code 0), sans conflit, sans nouvelle réception et sans exécution Odoo. Trace : `/tmp/odoo-ordered-recovery-20260909/O02/resume.log`.

Contrôle après publication : intégrité des sources A, contrat A, preuve A, drafts, bases, périmètre documentaire A et reçu initial ; identité exacte des deux cibles aux drafts. Tous les contrôles sont vrais. Aucune autre demande ni pièce B modifiée.
