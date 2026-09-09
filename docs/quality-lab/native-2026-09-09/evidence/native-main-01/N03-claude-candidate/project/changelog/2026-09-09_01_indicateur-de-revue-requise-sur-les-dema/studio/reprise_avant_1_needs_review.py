"""Préalable de recette — crée des enregistrements AVANT l'ajout du champ.

À jouer une fois, avant `build_1_needs_review.py`, pour prouver C9 : un champ
calculé stocké ajouté sur un modèle déjà peuplé doit reprendre les
enregistrements existants. Ils sont relus puis supprimés par
`test_1_needs_review_orm.py`.

`/bridge/labctl shell changelog/<release>/studio/reprise_avant_1_needs_review.py`
"""
M = env["x_lab_request"].sudo()
ATTENDU = [
    ("reprise location 9 jours", "rental", 9),   # attendu vrai
    ("reprise location 2 jours", "rental", 2),   # attendu faux
    ("reprise prêt 20 jours", "loan", 20),       # attendu faux (prêt exclu)
]
M.search([("x_name", "like", "reprise")]).unlink()
for name, kind, days in ATTENDU:
    M.create({"x_name": name, "x_studio_kind": kind, "x_studio_days": days})
env.cr.commit()
print("PRÉALABLE OK — %d enregistrement(s) antérieur(s) en base"
      % M.search_count([("x_name", "like", "reprise")]))
