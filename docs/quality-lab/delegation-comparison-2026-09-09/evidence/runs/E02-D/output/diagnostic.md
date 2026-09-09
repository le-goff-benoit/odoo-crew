# SYN-42 — Diagnostic support, 2026-09-09

## Demande originale

> Le montant reste à 30 quand je passe le prix de 10 à 12 pour une quantité de 3. C'est apparu après notre modification du calcul stocké. Merci de diagnostiquer, proposer un contournement et préparer la suite, sans modifier le module ni réparer de données pour l'instant. Nous vendons aussi des lignes gratuites ; il faut les conserver.

Source conservée : [demande.md](../demande.md).

## Verdict et portée

**Bug custom : dépendance de calcul stocké incomplète.** Série 19.0 établie par le briefing offline. Le montant lit le prix, mais sa déclaration de dépendances ne cite que la quantité. Le changement du seul prix laisse donc un montant stocké périmé.

La cause est étayée par le code local, le fonctionnement du moteur Odoo 19.0 et une trace synthétique fournie. Aucune reproduction Odoo n'a été exécutée dans cette intervention. Aucune base client, version déployée ou donnée réelle n'a été consultée. Le moment d'apparition après modification est rapporté par le ticket ; aucun historique de déploiement ne permet de dater le défaut.

## Preuves

| Pièce | Constat | Ce qu'elle établit |
|---|---|---|
| `project/lab_qualification/models.py:11` | `amount` est calculé et stocké | Le montant dépend du déclenchement du recalcul |
| Même fichier, ligne 20 | `@api.depends("quantity")` | Seule la quantité est déclarée |
| Même fichier, ligne 23 | Le calcul utilise quantité et prix unitaire | Le prix lu manque aux dépendances |
| Même fichier, lignes 16–18 et 25–26 | Quantités négatives interdites ; confirmation sans interdiction de prix zéro | La gratuité ne doit pas être bloquée |
| `pieces/orm-trace.jsonl`, séquence 1 | L7 confirmée, quantité 3, prix 10, montant 30 après flush/relecture | État initial cohérent |
| Même trace, séquence 2 | Écriture du seul prix 12, montant toujours 30 | Défaut observé dans la pièce fournie |
| Même trace, séquence 3 | Réécriture de quantité 3, montant 36 | Déclenchement cohérent avec la dépendance déclarée |
| Même trace, séquence 4 | FREE-2 confirmée, quantité 2, prix 0, montant 0 | Exemple synthétique conforme à D-17 |
| `pieces/decisions.md` et mémoire initiale | D-17 acquise, SYN-11 clos, aucune permission de recalcul production | Périmètre métier et limites d'intervention |
| `pieces/dependencies-source.md` | Explication du lien dépendances/recalcul | Corroborée par lecture des sources ci-dessous |

Sources locales consultées en lecture seule par le relecteur indépendant :

- `/home/blegoff/odoo-sources/19.0/odoo/orm/decorators.py:244–271` : déclaration des dépendances dans `_depends`.
- `/home/blegoff/odoo-sources/19.0/odoo/orm/fields.py:590–598` : collecte des dépendances des méthodes de calcul.
- `/home/blegoff/odoo-sources/19.0/odoo/orm/registry.py:637–650` : construction des déclencheurs inverses.
- `/home/blegoff/odoo-sources/19.0/odoo/orm/models.py:6754–6757` et `6801–6826` : notification des modifications et préparation du recalcul stocké.

Le code et la trace suffisent à expliquer le symptôme par le custom. Les données d'entrée 3 et 12 sont cohérentes : ce n'est pas une erreur arithmétique de saisie. Aucun élément fourni ne met en cause les droits ou une configuration. Ces pistes ne sont pas auditées sur une base réelle. Le standard suit les dépendances déclarées ; aucun bug standard n'est établi. Un écart de déploiement reste non vérifiable hors ligne.

## Impact et contournement

Une ligne affectée est démontrée dans la trace : L7, avec un écart de 6 (36 attendu, 30 stocké). FREE-2 fournit un contrôle de gratuité conforme. Le nombre de lignes, d'utilisateurs et la période affectés en situation réelle sont inconnus. Toute modification du prix seul peut laisser un montant périmé dans le modèle fourni. Aucun lien avec une facture ou une écriture comptable réelle n'est établi.

Gravité : **majeur**, car un montant métier peut être faux et le contrôle manuel est nécessaire. La validation d'une ligne présentant cet écart doit être suspendue jusqu'à traitement du montant.

Contournement immédiat sans écriture : calculer séparément quantité × prix et comparer avant d'utiliser ou valider le montant ; signaler les écarts au support. Le contrôle ne répare pas le champ stocké. Pour une ligne gratuite, le montant attendu reste zéro.

La trace montre que réécrire la même quantité déclenche le recalcul. Cela décrit une piste technique à tester sur copie locale, pas une consigne de réparation autorisée ici. Ne pas changer temporairement les quantités ni lancer de réécriture en masse. Aucun enregistrement n'a été modifié.

## Test rouge proposé — non exécuté

À préparer dans un futur `tests/test_support_syn42.py` sous Odoo 19.0, avec le modèle du module fourni et une `TransactionCase` :

1. Créer une ligne nommée L7, quantité 3, prix 10, état confirmé.
2. Appeler `env.flush_all()` puis `env.invalidate_all()` ; relire la ligne et vérifier quantité 3, prix 10, montant 30.
3. Écrire uniquement `unit_price = 12`. Ne pas écrire la quantité.
4. Refaire flush et invalidation, relire la ligne ; vérifier quantité 3, prix 12 et **montant 36**.
5. L'assertion finale est attendue rouge avec 30 selon le code et la trace. Il faut constater cet échec dans Odoo avant toute correction. Ne pas appeler directement la méthode de calcul, ce qui masquerait la dépendance manquante.

Non-régressions à prévoir ensuite :

- Modifier la quantité seule et vérifier le montant stocké après flush/relecture.
- Créer puis confirmer une ligne quantité 2, prix 0 : confirmation acceptée et montant 0 (D-17).
- Sur une ligne payante confirmée, passer uniquement le prix à 0 : montant recalculé à 0 et état confirmé conservé.
- Conserver quantité zéro en brouillon et le rejet d'une quantité négative. Ne pas modifier le bouton de SYN-11.

## Transmission

Classement fonctionnel : `bug custom`. Issue de diagnostic pour une correction limitée aux dépendances : `bug`, avec porte du test rouge **non franchie** car le test est seulement proposé. Aucun flow de livraison n'est ouvert dans cette épreuve.

Responsable immédiat : développeur avec le support, pour reproduire le rouge sur copie locale. Le diagnostic prépare la reprise par `/odoo-new`, sans prétendre avoir satisfait sa preuve d'entrée. Résultat attendu de la correction future : le changement du prix déclenche le recalcul stocké, les tests passent, la gratuité reste permise. Aucun patch n'est livré ici.

Les montants déjà périmés constituent un chantier distinct : après reproduction, inventorier et chiffrer les écarts sur une copie avant de proposer un recalcul. Ne pas supposer qu'une correction de dépendances répare tous les montants historiques. Si la suite inclut cette reprise de données ou touche effectivement facturation/comptabilité/droits, aiguiller en `bug_sensitive` vers l'analyste avant implémentation de ce périmètre. Toute éventuelle écriture de production nécessitera alors une décision explicite sur l'opération précise ; aucune demande d'autorisation n'est nécessaire pour rendre le présent diagnostic.

## Brouillon de réponse au client — non envoyé

Nous avons identifié une dépendance manquante dans le calcul personnalisé du montant.
Les pièces fournies montrent qu'un changement de prix peut laisser l'ancien montant affiché.
Pour 3 unités à 12, le montant attendu est 36, alors que la trace conserve 30.
En attendant, vérifiez quantité × prix avant d'utiliser le montant et signalez les écarts.
Les lignes offertes restent autorisées, même confirmées, avec un montant nul.
Nous préparons un test de reproduction avant la correction et l'examen des montants déjà enregistrés.
Aucune donnée n'a été modifiée ; la reproduction sur une copie et le délai de correction restent à établir.

## Contrôles réellement exécutés et limites

- Briefing : `python3 /tmp/odoo-delegation-comparison-20260909/reference/scripts/odoo_briefing.py /tmp/odoo-delegation-comparison-20260909/runs/E02-D/project --offline`.
- Lecture des entrées, mémoires, rôle support figé, code et sources locales indiquées ; relecture indépendante limitée au code et aux sources.
- Contrôle des empreintes des entrées et du projet, ainsi que du préfixe du journal initial : voir `execution-notes.md` et `input-sha256.json`.
- Aucun correctif, réparation, test Odoo, réseau métier, accès production, flow de livraison ou envoi de message au client.
