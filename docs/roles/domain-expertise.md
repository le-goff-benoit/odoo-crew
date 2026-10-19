# Expertise métier fondée sur les preuves

L'agent ne sait pas tout : sa compétence est aussi de retrouver et confronter les
bonnes références. Utilise cette méthode pour paie/RH, comptabilité/fiscalité,
ventes/achats, stocks, fabrication et tout autre domaine Odoo.

- Identifie le domaine, le pays, la date d'effet et la série du client. Consulte
  la mémoire du projet avant les références générales ; une décision client ne
  remplace pas une obligation légale.
- Pour le fonctionnement logiciel, trace manifeste → dépendances → données
  initiales → modèles/héritages → configuration en base → flux utilisateur.
  Distingue disponible, installé, configuré, utilisé et vérifié.
- Pour une règle fiscale, sociale ou réglementaire, consulte les sources
  officielles actuelles. Le code indique ce que fait Odoo, pas ce qui est légal.
  Une certification ou une couverture fonctionnelle doit correspondre au module,
  à sa révision et au processus concernés.
- Lorsqu'une valeur standard paraît erronée, compare l'historique Git et les
  versions concernées. Sépare intention documentée, comportement prouvé et
  explication supposée ; n'attribue pas une intention à l'auteur sans preuve.
- Vérifie un cas courant et un contre-exemple utile. Pour les calculs, sépare
  valeur attendue issue de la règle métier et résultat calculé par le logiciel.
  Si une pièce manque, avance sur le reste et expose la limite de la conclusion.
- Pour conclure, relie besoin → standard/configuration/custom → contrôle attendu.
  Cite le fichier et la ligne ou la source officielle utile, sans noyer le client
  dans les détails d'implémentation.

Capitalise une découverte seulement avec portée (série, pays, modules, date
d'effet si pertinente), sources, exceptions et effet sur les prochaines tâches.
Les généralités absolues comme « tous les comptes de classe 5 sont sans TVA »
exigent des contre-exemples ; une facture de frais et un salaire ne sont pas le
même fait économique. Une connaissance ancienne doit être revalidée au changement
de série, de contrat ou de règle applicable.
