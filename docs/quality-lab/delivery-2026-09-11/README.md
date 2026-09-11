# Gmail à la clôture — 11 septembre 2026

Référence : `782f50a420b7301cd8646a295b0c01aabacf502e`. Aucun transport Gmail,
accord de message ou paramétrage À/Cc/Cci du projet à cette révision. Demande
explicite : préparer à la clôture, présenter le texte et les PJ, puis envoyer
après accord dans le terminal, sans passer par un bouton Gmail.

## Contrat et essais

Les essais sont déterministes, sans appels de modèles ni emails réels. Projets,
destinataires, pièces et identifiants Google sont fictifs ; transport et trousseau
sont simulés. Le vrai garde de clôture est utilisé sur un projet jetable.

- 27 tests dédiés : MIME avec/sans PJ, Cc/Cci et Cci seuls ; stockage privé ;
  cohérence expéditeur ; contrôle du sceau ; PJ remplacée ; texte/destinataires
  modifiés ; ancienne décision ; absence de confirmation ; concurrence ;
  résultat réseau inconnu ; refus de relance ; symlinks ; injection d'en-têtes
  et de séquences terminal ; état altéré ; erreurs du trousseau sans détail secret.
- OAuth simulé de bout en bout : navigateur système, PKCE, state, retour boucle
  locale, endpoints fixes malgré un client JSON hostile, mauvais compte,
  permissions trop larges, persistance des jetons uniquement dans le trousseau.
- Contre-épreuve de course : désactivation du projet pendant le renouvellement
  du jeton. Le second contrôle avant transmission refuse l'envoi ; le transport
  n'est pas appelé. Les octets envoyés restent ceux du message préparé.
- Non-régression Crew : 281 tests ; graphe valide, 59 nœuds / 129 arêtes.
- Génération isolée et parité Claude/Codex contrôlées (30 fichiers, blocs de
  routage conservés) ; validation du skill de clôture.
- Tricorder : scénario Electron de saisie À/Cc/Cci, persistance isolée par projet,
  conservation de saisie à l'actualisation, aide de connexion et aperçu du message.
  Aucune écriture client ni accès au trousseau par le cockpit. Recette du paquet
  et autres parcours documentés dans son `QA.md`.

## Décision et limites

Implémentation adoptée localement, consigne d'accord humain ajoutée comme choix
explicite de l'utilisateur. Le garde mécanique atteste la version et la déclaration
d'accord, **pas l'identité humaine de l'auteur du fichier**. Aucune campagne native
Claude/Codex n'a mesuré la fidélité comportementale de cette nouvelle consigne.

L'email est activé projet par projet, non par défaut. Les données restent hors Git.
Le compte Google n'est pas encore connecté : consentement réel, règles Workspace,
disponibilité du trousseau et premier envoi témoin restent à contrôler avec l'humain.
Un état d'envoi incertain est bloqué, jamais relancé automatiquement ; sa résolution
nécessite de vérifier Gmail. La première version conserve l'archive privée sans
purge automatique. Aucun push, email réel ou test en production n'est effectué.

## Rejouer

```bash
python3 -m unittest tests.pilotage.test_odoo_delivery -v
python3 scripts/odoo_flow.py validate
python3 -m unittest discover -s tests -v
./build.sh --output-root /chemin/jetable
```

Installation des profils uniquement après ces contrôles : `./build.sh`.
Retour à la référence possible par restauration ciblée des sources puis génération,
sans modifier les données des projets ou effacer les archives d'envoi.
