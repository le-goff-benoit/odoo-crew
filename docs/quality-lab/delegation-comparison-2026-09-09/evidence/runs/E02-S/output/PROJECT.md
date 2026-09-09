# Projet synthétique E02
Série : 19.0. Module custom lab_qualification. Aucune production déclarée.
## Décisions actées
- D-17 : prix zéro autorisé pour les lignes gratuites, y compris confirmées. Décision acquise.
- Quantité zéro autorisée pour les brouillons ; quantité négative interdite.
- SYN-11 résolu : le libellé du bouton ne nécessite plus de changement ; ne pas rouvrir.
## Limites
Les pièces du banc sont synthétiques ; elles ne prouvent pas l'état d'une base client.

## SYN-42 — diagnostic du 2026-09-09
- Bug custom identifié dans les pièces fournies : amount est stocké et lit quantity et unit_price, mais seule quantity est déclarée dans les dépendances.
- Trace synthétique : 3 × 10 donne 30 ; le prix seul passe à 12 et le montant reste 30 ; une écriture explicite de quantity=3 donne 36.
- D-17 reste applicable : gratuité autorisée, y compris après confirmation. La correction doit couvrir aussi le passage d'un prix positif à zéro.
- Contournement immédiat : vérifier quantité × prix et suspendre l'usage des montants incohérents. La piste de réécriture de quantité est à vérifier sur copie, sans réparation autorisée aujourd'hui.
- Test rouge proposé dans output/diagnostic.md, non exécuté. Suite : développeur pour reproduction locale et correction du déclencheur, puis QA ; aucune reprise de développement effectuée ici.
- Les anciens montants peuvent nécessiter une reprise distincte : analyse préalable sur copie, comptage et preuve avant/après ; aucune autorisation de recalcul en production.
- Aucun accès client ni exécution Odoo. Impact réel et version déployée inconnus ; une seule ligne incohérente démontrée dans la trace synthétique.
