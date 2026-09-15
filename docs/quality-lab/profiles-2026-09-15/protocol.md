# Protocole figé avant correction — 15 septembre 2026

Référence : `4c6738c60c959fd1ceac7d24d6949d96909b6ab2`. Les profils de
référence se reconstruisent depuis ce commit ; le candidat sera une copie
figée de l'arbre courant, empreintée avant le premier appel. Les résultats ne
servent pas à réécrire rétroactivement les critères.

## Hypothèses et limites

- Une entrée courte et des procédures chargées selon le mode réduisent le
  contexte effectivement lu sans perdre les invariants, notamment les exceptions.
- Une sélection de sections doit garder les décisions, leur provenance et un
  index des omissions ; elle ne résout pas les contradictions métier.
- Les modèles candidats sont expérimentaux ; aucun changement du principal.
- Jusqu'à **24 appels natifs au total**, relances et incidents inclus. Au plus
  deux appels simultanés, timeout 600 s par appel, aucune répétition cachée.
  Codex Astra/Terra et Claude Opus/Sonnet, effort demandé medium ; valeur
  effective seulement si retournée. Aucun repli de modèle.

## Comparaisons

1. Profils avant/après : même modèle principal, deux cas synthétiques de
   passation et réception, un témoin positif et un défaut documentaire tenu
   à l'écart des ajustements. Outils et lectures des références autorisés.
   Ordre avant/après alterné selon fournisseur. Huit appels prévus.
2. Exécution : profil candidat identique, principal contre modèle candidat sur
   deux tâches synthétiques avec vrais outils ; au moins un cas inédit.
   Huit appels prévus. Oracles conservés hors du sandbox. Une qualification
   documentaire ne qualifie pas le développement Odoo.
3. Huit appels de réserve au maximum pour incident identifié ou contre-épreuve
   après correction ; un échec critique n'est jamais moyenné avec un succès.

## Réception

Comparer par cas/fournisseur : obligations respectées, preuves et lectures,
commandes réellement jouées, temps jusqu'au retour, jetons/cache observables,
reprises et temps de correction du principal. Un résultat sans réception ne
mesure pas le délai jusqu'à livraison. Signaler toute métrique non observable.
Les tests, documents et politiques restent identiques entre variantes.

Adoption du profil compact seulement si les contre-épreuves ne perdent aucun
invariant critique ; mesurer entrée **et références effectivement chargées**.
La cible indicative de contexte est 25–35 %, jamais un motif pour supprimer
une protection. Un candidat plus léger n'est adopté que sans échec critique
et avec gain de délai jusqu'à réception démontré ; sinon expérimental.
Les contrôles déterministes et Odoo synthétiques sont une couche distincte,
sans appel payant dans la CI. Aucun projet client dans les fixtures ou rapports.
