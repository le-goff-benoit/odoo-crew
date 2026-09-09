# Revue indépendante — suivi des minutes et coûts IA

Verdict : **favorable sur le périmètre testé, après corrections du principal**. 16 contrôles indépendants passent. Aucun fichier du référentiel modifié par le relecteur. Tous les projets sous ce dossier sont synthétiques, avec `changelog/R/README.md`. Aucun client, secret, modèle ou API utilisé.

Rejouer : `python3 /tmp/odoo-effort-review-20260909/explore.py`. Le script ne détruit que ses propres projets synthétiques dans ce dossier. Les horodatages de `now()` sont contrôlés pour rendre les intervalles reproductibles ; le parseur de sessions et les traitements d'effort ne sont pas simulés.

## Défauts établis et contre-épreuves

| Cas | Comportement initial | Résultat après correction |
|---|---|---|
| Deux tours Codex terminés, un seul avec durée | `odoo_usage.py:_codex/read_usage` donnait `complete=true, active_seconds=9` ; bilan déclarait 0,15 min complètes et comparaison possible malgré la seconde durée inconnue | Durée globale et écart inconnus ; `time_complete=false` |
| Coût déclaré Claude avec chronomètre | `odoo_effort.py:stop` remplaçait le coût par null malgré 1 USD au départ et 3 USD à la fin | Coût déclaré de 2 USD conservé |
| Périmètre sans plan | `odoo_effort.py:contracts/check_report` renvoyaient `{}` ; modification de `demande.md` non détectée | Bilan périmé refusé, `scope_changed=true` |
| Modèle connu seulement après start | `odoo_effort.py:stop` exigeait l'égalité avec le modèle initial absent | Modèle unique final conservé |
| Deux dates de tarifs représentant le même instant UTC | `odoo_effort.py:rates`, anciennes lignes 325–328 : clé construite avec texte de date, deux prix contradictoires acceptés | Second prix refusé après normalisation UTC |

`results-before-fixes.json` conserve les résultats rouges natifs. Les scripts ont changé pendant cette revue ; les empreintes de la version réellement contre-éprouvée sont dans `review.json`.

Deux risques relevés par lecture ont été corrigés avant la première reproduction : identités absentes des mesures timer et absence de rattachement à la révision applicable. Je n'en revendique pas de résultat rouge exécuté. Les contrôles courants prouvent le refus de la même réponse sous timer puis session enfant, ainsi que la présence du rattachement de révision.

## Autres contrôles exécutés

- Import de fenêtres adjacentes : 20 + 20 jetons, total 40 ; chevauchement refusé.
- Contexte parent hérité suivi d'une frontière native enfant : seuls les 20 jetons de l'enfant sont conservés.
- Reprise d'une session dédiée : même identifiant, une entrée, une révision historique, 18 secondes et 40 jetons ; réimport idempotent.
- Révision partielle d'estimation : rôle QA conservé ; estimation initiale intacte.
- Coût cache natif : 1 000 entrées dont 600 lues au cache et 100 écrites, 200 sorties ; valorisation synthétique 0,00885 USD conforme au calcul des catégories sans double compte.
- Intégration `required_artifacts` de release guard : altération de chacun des quatre exports refusée. Modification du contenu de demande avec plan : fraîcheur refusée, périmètre changé visible.
- CLI native `odoo_usage.py read` et CLI effort `report/check` exécutées avec succès ; exports JSON égaux.

## Utilisabilité et limites

Les rôles et `docs/EFFORT.md` expliquent la séquence init → estimate → start/stop ou import → report et les reprises, la distinction minutes cumulées/délai et les coûts techniques facultatifs. La révision partielle et le rattachement au départ rendent désormais leurs promesses cohérentes avec le script. Aucune conversion commerciale ou en temps humain trouvée.

La revue ne constitue pas une validation de tous les formats historiques Codex/Claude. Elle utilise des JSONL natifs synthétiques, pas de traces privées. La découverte du chemin réel d'une session de sous-agent n'a pas été essayée ; les commandes exigent sa fourniture explicite.

Le cycle complet seal/check avec chaîne de preuves de QA n'a pas été exécuté ; seule l'intégration des artefacts d'effort et de leur fraîcheur a été éprouvée. Une durée native partielle est désormais entièrement inconnue, ce qui évite une comparaison fausse mais perd le sous-total de secondes connues. Les fenêtres, modèles mixtes et tarifs indisponibles restent volontairement conservateurs. Aucun tarif synthétique de cette revue ne doit servir à valoriser une consommation réelle.
