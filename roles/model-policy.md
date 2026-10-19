## Un agent, plusieurs compétences

Par défaut, le principal applique lui-même les rôles utiles dans sa session.
Leur nom décrit une compétence ou une phase, pas un sous-agent à créer.
La délégation exige une demande explicite de l'utilisateur, même si un outil
de sous-agents est disponible. Les procédures historiques de délégation ne
s'activent qu'après cette demande. Sans délégation, annoncer les auto-relectures
comme non indépendantes ; ne jamais contourner un garde indépendant déjà lié.

## Modèle par rôle

L'orchestrateur conserve le modèle principal et fixe critères, contrôles et
frontières avant délégation. Quota faible ne change ni modèle ni exigences.
Les rôles héritent du principal ; analyse ambiguë, QA décisionnelle, finance,
droits et données existantes y restent.

Tout changement explicite se résout avec `python3 ~/.odoo19-agents/scripts/odoo_models.py
<codex|claude> <rôle> --risk <normal|high> --principal <modèle-session>`.
Politique : `~/.odoo19-agents/workflows/model-policy.json`. `--candidate` signifie
essai local borné, pas qualification. Aucun repli silencieux si indisponible.
Détails et résultats des essais : `~/.odoo19-agents/docs/MODELS.md`.

Contrat : fournisseur, modèle et effort demandés ; résultat : valeurs observées
ou « non retournée ». Un candidat reste expérimental sans comparaison avec cas
inédit et délai jusqu'à réception, reprises comprises. La QA reste entière ;
le sous-agent retourne au principal, sans lancer son successeur.
