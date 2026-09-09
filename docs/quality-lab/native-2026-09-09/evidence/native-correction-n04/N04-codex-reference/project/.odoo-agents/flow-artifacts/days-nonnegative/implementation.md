# Implémentation D-31 — Odoo 19.0
Ajout de models.Constraint CHECK(days >= 0) dans lab_rental/models/business.py ; calcul, champs, manifest, écrans et droits inchangés. Trois fichiers de tests ajoutés, quatre méthodes TestRentalDays.
Preuve rouge red.json/red.log : absence de CheckViolation sur create/write, pour rental et loan (4 sous-tests en échec).
Preuve verte green.json/green.log : installation/mise à jour QA OK, 4 méthodes exécutées, 0 échec/erreur/skip, 6 s.
Lint --changed : Ruff exécuté et vert, aucun conseil ; contrôle Odoo rouge uniquement pour author absent du manifest inchangé. baseline-lint.log reproduit cette dette sur la référence d4f00bfbaa29ce6b8c47939859d4a20b52c60390. Aucune anomalie nouvelle ; dette hors périmètre à conserver dans la QA, pas de faux lint vert.
