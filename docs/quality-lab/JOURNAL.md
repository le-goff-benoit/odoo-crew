# Journal de l’espace qualité

## 11 septembre 2026 — rendre l'investigation longue pilotable

- Demande : adopter les bilans utiles et publier Crew avec Tricorder 0.2.8.
- Consigne commune, passation analyste/développeur et contrat de délégation précisés.
- Référence dd53062 ; quatre cas sur dossier, dont longue recherche justifiée et veille.
- Ambiguïté « à réceptionner » relevée sur un retour partiel ; frontière précisée.
- Aucune promesse de gain, arrêt automatique, changement de modèle ou écriture client.
- Essais, contre-épreuve, contrôles et limites dans `progress-2026-09-11/README.md`.

## 11 septembre 2026 — retrait de l’intégration email

- Décision utilisateur : abandon du parcours email, pas une tentative d’améliorer son adoption.
- Retrait de la consigne canonique de clôture, des transports Gmail/SMTP et de l’interface Tricorder.
- Ancien CLI neutralisé ; fonctions de lecture inertes pour les fenêtres 0.2.4 encore ouvertes.
- Incident utilisateur config_for absent corrigé, ancien catalogue installé recontrôlé sur NECA en lecture seule.
- Données privées et trousseau conservés ; import des demandes EML inchangé.
- Tests de retrait et contre-épreuve EML ; aucun appel Gmail ou campagne modèle.
- Sources de transport sauvegardées hors des dépôts avant retrait ; aucune publication distante.

## 11 septembre 2026 — SMTP Gmail et correction de l’email

- Demande : mot de passe d’application, aperçu modifiable, envoi après accord terminal.
- Helper SMTP séparé du renderer : dialogue masqué, trousseau distinct OAuth, TLS vérifié.
- Préparation/édition avec version attendue ; correction humaine protégée contre régénération.
- Tous les destinataires acceptés avant DATA, Cci masqués, échec incertain sans relance.
- 41 tests email et 300 tests Crew verts ; transport, dialogue et trousseau simulés.
- Six parcours Tricorder, NECA en lecture seule ; preuves et limites dans le rapport SMTP.
- Consigne canonique de clôture ajustée et génération Claude/Codex contrôlée avant adoption locale.
- Aucun email réel, aucune campagne LLM payante ni changement de données client.

## 9 septembre 2026 — présentation et rangement

- Demande : README court et orienté chef de projet, bannière fournie, tests et essais plus faciles à trouver.
- Réalisé : présentation réduite de 1 404 à 501 mots ; cinq rôles, bénéfices et parcours de démarrage.
- Rangé : tests répartis en pilotage, outillage et laboratoire ; catalogue des scénarios et résultats classés par sujet.
- Conservé : détail du pilote dans benchmarks/PILOTE.md ; archives et preuves historiques inchangées.
- Vérifié : 251 tests toujours découverts et réussis ; 79 liens locaux valides ; image copiée à l’identique.
- Suite : ajouter les nouvelles campagnes à l’index et leurs tests dans le domaine correspondant.

## 11 septembre 2026 — publication demandée

- Demande explicite : pousser les changements et publier Crew/Tricorder sur GitHub.
- Livraison Crew datée v2026.09.11, synchronisée avec Tricorder v0.2.7.
- Notes dans docs/releases/2026.09.11.md ; tests, graphe et parité contrôlés.
- Aucun projet client, brouillon, identifiant ni paquet binaire ajouté au code source.

## 11 septembre 2026 — veille et compteurs indépendants

- Demande explicite : protéger les chronomètres à la veille/reprise et améliorer les jetons Claude/Codex.
- Reproduction rouge puis correction monotone/boottime, reboot sans durée inventée, lecture vivante sans écriture.
- Champs de jetons indépendants et dernière ligne JSONL en cours tolérée, corruption interne refusée.
- Coûts non extrapolés, anciens bilans vérifiables sans migration ; aucun client modifié.
- 271 tests, graphe valide, génération isolée puis active conforme ; protocole dans sleep-tokens-2026-09-11.
- Limite : durées natives sans trace de suspension inchangées ; veille simulée, pas de mise en veille du poste.

## 9 septembre 2026 — parcours visibles et commandes

- Demande : petits graphiques ASCII, commandes plus explicites et nouvelle bannière fournie.
- Réalisé : trois parcours (évolution, release, support), rôle de l’orchestrateur et tableau des huit commandes, avec les deux usages de feedback.
- Image : nouvelle bannière copiée à l’identique ; même lien depuis le README.
- Contrôles : liens et commandes confrontés au générateur et à l’aiguillage ; suite et génération vérifiées avant publication.

## 9 septembre 2026 — références rangées et exemple métier

- Demande : alléger la racine du dépôt et illustrer un développement Odoo avec le rôle et la conclusion de chaque agent.
- Rangé : installation dans docs, quatre références dans docs/reference, aiguillage dans roles ; README/AGENTS/CLAUDE conservés à la racine.
- Répercuté : liens, briefing, génération et profils ; index de documentation ajouté.
- Exemple : contrôle de référence d’achat à la confirmation d’une commande, scénario fictif dépliable ; aucune exécution Odoo revendiquée.
- Vérification : test rouge de lecture des leçons après déplacement, puis correction du chemin ; suite et build avant livraison.

## 10 septembre 2026 — flux Odoo express

- Demande : formaliser les corrections locales urgentes observées sur les rapports NECA.
- Réalisé : nouvelle commande `/odoo-express`, cinq nœuds orchestrateur et bascule vers `/odoo-new` lorsque le périmètre s'élargit.
- Limites : aucun schéma, droit, dépendance, migration, donnée existante ni calcul financier ; présentation financière admise si les montants restent inchangés.
- Livraison : worktree propre, test ciblé, lint, mise à jour, changelog groupé, journal et push seulement lorsqu'il est demandé.
- Vérification : 254 tests, parcours CLI complet, génération conforme de 30 profils/commandes et skill Codex validé.

## 11 septembre 2026 — mesurer avant le plan

- Demande : inclure le cadrage `/odoo-plan`, avant toute tâche ou release.
- Réalisé : registre de préparation projet, rattachement explicite unique, même moteur temps/jetons.
- Les passages futurs dédiés vont à leur tâche ; ni ventilation ni prévision rétroactive.
- Contrôles : 12 nouveaux tests, 283 tests Crew verts, lecteurs natifs Claude/Codex et concurrence.
- Graphe et génération isolée conformes ; adoption dans les profils partagés Claude/Codex.
- Preuves, contre-cas et limites : `docs/quality-lab/PREPARATION.md`.
