# Entrepôt Silex — recalcul des demandes en cours
<!-- odoo-agents:relevé fin -->
## Compréhension métier
Projet entièrement synthétique pour le banc.
## Décisions actées
Lire decisions/2026-09-08.md ; elle remplace les anciennes règles du journal.
- **D-12 (2026-09-08, Marc Colin) fait foi** : `action_recalculate` ne traite que les brouillons, en additionnant `quantity × price` des lignes non annulées. Un dossier validé est figé : ni recalculé, ni réécrit. Sélection mixte tolérée sans erreur. Pas de changement de droits.
- **D-11 (2026-08-01) est périmée** : elle demandait de recalculer aussi les validés. D-12 la rejette explicitement. Toute demande future de « reconstruire tous les dossiers » se confronte à D-12 avant d'être mise en œuvre.
- `snapshot_total` reste un champ stocké piloté par une action, **et non un champ calculé** : un compute se recalculerait aussi pour les validés, ce que D-12 interdit. C'est une photographie, pas un calcul — ne pas le « corriger » en `compute=`.
## Pièges connus
Ne pas confondre accord métier, validation sur copie et déploiement.
- « Strictement inchangé » pour un dossier validé signifie **aucune écriture** : filtrer l'état avant l'affectation, jamais après. Une réécriture à valeur identique déplacerait quand même `write_date`.
- `write_date` n'est pas une preuve de non-écriture dans un test unitaire (elle porte l'horodatage de la transaction) : utiliser un espion sur `write`. Elle n'est probante que sur la copie, entre deux transactions distinctes.
- La reprise ne tolère aucun arrondi que le contrat ne prévoit pas : l'écart de 0,004 de `LEGACY_FRACTION` était un vrai écart à corriger.
- Corriger le calcul ne corrige pas les valeurs déjà stockées : la reprise passe par `migrations/<version>/post-*.py`, ce qui **impose** d'incrémenter la version du manifest, même en cours de release.
- Le manifest n'a pas de clé `author` depuis l'origine : unique erreur de lint et 3 WARNING à l'installation, valeur à décider par le projet.
