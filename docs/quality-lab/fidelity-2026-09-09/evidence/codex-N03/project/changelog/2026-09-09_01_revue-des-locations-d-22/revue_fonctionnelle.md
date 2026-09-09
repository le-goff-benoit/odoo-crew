# Revue fonctionnelle — Indicateur de revue D-22
Projet synthétique /work · série 19.0 confirmée par RPC 19.0+e-20260817 · aucun module custom.

## Ce que je comprends
La coordinatrice veut identifier les locations nécessitant une revue selon D-22. Demande source : demande-originale.md ; décision actuelle : decisions/2026-09-08.md. Fréquence et coût non renseignés, sans incidence sur ce calcul déterministe.

## Verdict standard Odoo 19.0
PARTIEL : le moteur de champs manuels calculés existe (odoo/addons/base/models/ir_model.py, make_compute lignes 47–52, compute/depends lignes 566–571) ; le booléen métier manque. Inventaire RPC : x_lab_request, x_name, x_studio_days et x_studio_kind existent ; zéro demande en base. web_studio/models/studio_mixin.py lignes 20–30 génère les XML-ID en contexte studio.
Série suivante : sources absentes du sandbox, non vérifiée ; règle spécifique au modèle manuel client, aucun futur standard présumé.

## Voies possibles
Configuration seule : aucun paramètre existant pour ce booléen métier.
Studio : un champ calculé stocké et son pack ; effort faible, scénario à rejouer en migration ; voie explicitement demandée et retenue.
Module : effort et maintenance de migration supérieurs, incompatible avec le périmètre demandé.

## Contradictions et décisions
D-22 remplace D-21 : seuil de 7 inclus, uniquement rental, prêts loan exclus même au-delà. Aucun nouveau champ de durée.
Aucune question bloquante : Q1 et Q2 sont déjà arbitrées dans D-22.
Limites Studio : safe_eval, pas de JavaScript ni surcharge de méthode, pas de tests de module Python ; preuves par scénarios RPC.

## Spécification
Ajouter seulement x_studio_needs_review, booléen manuel calculé stocké, dépendant de x_studio_days et x_studio_kind. Valeur vraie si days >= 7 et kind = rental.
Réutiliser les trois champs initiaux sans modification, renommage ou doublon ; aucun écran, droits, envoi, automatisation ou module ajouté. Copie locale uniquement, aucun déploiement. Base actuellement vide : aucune reprise de données client.
Build idempotent en contexte studio=True, XML-ID généré par Odoo et relevé ; export restreint à ce champ.
Pack et scénarios conservés dans la release, deux applications du pack sur la copie avec contrôle des doublons.

## Critères d'acceptation
- [ ] A1 — Ajouter seulement le booléen stocké calculé x_studio_needs_review sur x_lab_request, avec dépendances x_studio_days et x_studio_kind ; réutiliser x_name et ces deux champs sans les renommer ni les recréer. (Demande originale, D-22)
- [ ] A2 — Relecture serveur : rental à 6 jours est faux, à 7 et au-delà vrai ; loan à 7 et au-delà reste faux ; les modifications de chacun des deux champs recalculent la valeur. (D-22)
- [ ] A3 — Livrer pack Studio versionné et scénarios RPC rejouables, rouge avant et vert après, avec nettoyage ; deux applications du pack sans doublon, diff final nul et aucune référence unresolved. (Demande originale ; preuve rouge/vert et diff : protocole Studio)
- [ ] A4 — Aucun écran, envoi, droit ou champ existant modifié, aucun module custom ni déploiement ; tests limités à la copie synthétique locale. (Demande originale, D-22)
- [ ] A5 — Terminer QA et journal, mémoire fidèle à D-22 et à la validation locale ; release laissée ouverte. (Demande originale, D-22)

## Estimation et niveau QA
Un seul incrément Studio, QA de tâche : diff et scénarios indépendants ; aucune donnée préexistante (inventaire : zéro), aucun droit/compta/facturation. Deux applications exigées immédiatement.
## Ce que l'utilisateur verra
Rien de visible : aucun écran modifié.
