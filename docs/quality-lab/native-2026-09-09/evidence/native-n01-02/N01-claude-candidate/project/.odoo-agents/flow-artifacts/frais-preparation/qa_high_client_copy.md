# Fragment QA renforcée — voie copie client (`lab_client`)

**Série** 19.0 · **module** `lab_rental` · base `lab_client` · 09/09/2026

Cette voie est **obligatoire** ici : la tâche modifie la valeur d'un champ **stocké** sur des
enregistrements déjà en base. C'est le seul contrôle qui voit la reprise de données.

## Préparation

La copie `lab_client` ne contenait **aucun** `lab.rental` (`select count(*) from lab_rental`
→ 0). Sept enregistrements représentatifs y ont été créés **avant** la modification du code,
donc avec les totaux de l'ancienne formule — sans cela, la reprise n'aurait rien eu à
reprendre et le contrôle aurait été vide de sens. Écritures autorisées sur cette copie
synthétique (LAB.md).

## Le fait qui a changé le périmètre

Première mise à jour du module (nouvelle formule, **version inchangée**) : les sept totaux
sont restés **strictement identiques**. Odoo ne recalcule pas un champ `store=True` dont
seul le corps du compute a changé. La revue fonctionnelle affirmait le contraire ; la mesure
l'a démentie et le périmètre a été corrigé (reprise + incrément de version).

## Avant / après la reprise `post-migrate 19.0.1.1.0`

Le log de mise à jour porte la ligne :
`odoo.modules.migration: module lab_rental: Running upgrade [19.0.1.1.0>] post-migrate`
et `latest_version` en base vaut bien `19.0.1.1.0`.

| id | Enregistrement | type | jours | tarif | avant | après | delta | attendu |
|---|---|---|---|---|---|---|---|---|
| 1 | Location 5 jours | rental | 5 | 10,00 | 50,00 | **62,00** | +12,00 | +12 ✅ |
| 2 | Location 4 jours (borne) | rental | 4 | 10,00 | 40,00 | **52,00** | +12,00 | +12 ✅ |
| 3 | Location 3 jours | rental | 3 | 10,00 | 30,00 | 30,00 | 0 | 0 ✅ |
| 4 | Location 4 jours tarif nul | rental | 4 | 0,00 | 0,00 | **12,00** | +12,00 | +12 ✅ |
| 5 | Prêt 10 jours | loan | 10 | 10,00 | 100,00 | 100,00 | 0 | 0 ✅ |
| 6 | Prêt 4 jours (borne) | loan | 4 | 10,00 | 40,00 | 40,00 | 0 | 0 ✅ |
| 7 | Location 0 jour | rental | 0 | 10,00 | 0,00 | 0,00 | 0 | 0 ✅ |

**3 enregistrements repris sur 7, +36,00 EUR au total.** Aucun prêt touché (Q2), aucune
location de moins de 4 jours touchée, la borne de 4 jours s'applique bien (Q1). Valeurs
relues **en SQL**, pas dans le cache de l'ORM.

## Idempotence

La fonction `migrate()` a été rejouée une seconde fois sur la même base : les sept totaux
sont inchangés (`preuves/copie_client_idempotence.txt`, `IDENTIQUE`). La reprise ne cumule
pas les frais.

## Effets de bord contrôlés

| Point | Résultat |
|---|---|
| Droits / `ir.model.access.csv` | inchangé, `git diff` vide |
| Comptabilité, facturation | aucun modèle comptable dans le périmètre ; `lab.rental` n'a aucun lien vers `account.*` |
| Vues, menus, actions | le module n'en contient aucun ; rien à casser |
| Erreurs à la mise à jour | 0 ERROR, 0 CRITICAL dans le log |

**Verdict de la voie : vert.**
