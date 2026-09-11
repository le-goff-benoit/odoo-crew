# Gmail SMTP et message corrigé avant accord

11 septembre 2026. Base Crew `782f50a420b7301cd8646a295b0c01aabacf502e` et
Tricorder `bf5393abc55abdf8c6e8d1a3023a56a2fca7fbe6`, avec les changements locaux
email/temps précédents conservés. Version Tricorder préparée : 0.2.4.

## Besoin et contrat

L’utilisateur demande SMTP par mot de passe d’application et souhaite modifier
l’email avant envoi, tout en donnant son accord dans le terminal. La préparation
existante OAuth est conservée. Le nouveau mode ne nécessite pas Google Cloud.

- Secret saisi dans Zenity par le helper Crew, stocké uniquement au trousseau.
- Aucun secret dans Electron, arguments de processus, configuration ou logs.
- TLS vérifié vers smtp.gmail.com:465, aucun repli en clair ou sur OAuth.
- Test de connexion limité à l’authentification : aucun message transmis.
- Brouillon éditable : objet, texte, À/Cc/Cci et PDF/DOCX de cette release.
- Destinataires du message indépendants des paramètres du projet.
- Une édition périmée échoue ; un brouillon corrigé n’est plus régénéré implicitement.
- Accord lié à la version exacte, au contexte de clôture, à la configuration et aux PJ.
- Tous les RCPT acceptés avant DATA ; Bcc reste uniquement dans l’enveloppe SMTP.
- Une réponse DATA positive signifie accepté par le serveur, pas livré au destinataire.
- Résultat incertain : statut unknown, aucune nouvelle tentative automatique.

## Essais et contre-épreuves

`python3 -m unittest discover -s tests -v` : 300 tests verts, dont 41 email
(27 précédents et 14 ajouts). Les transports, Zenity et le trousseau sont simulés.
Les tests couvrent aussi l’ancienne approbation, le conflit d’édition, la protection
contre régénération, le refus après changement de configuration pendant l’auth,
un destinataire refusé sans DATA, la perte de réponse DATA, l’authentification
refusée, l’absence de secret dans les erreurs et la fermeture de socket défaillante.
Un parcours CLI réel sur fixture reste dans cette suite, sans Gmail réel.

Tricorder : 52 tests Python + 11 JavaScript ; six parcours Electron.
Le parcours communication prépare une release synthétique avec le vrai garde,
édite/enregistre/relit le brouillon, normalise les destinataires, préserve les
paramètres projet, manipule les PJ et refuse une ancienne version par IPC.
Les saisies non enregistrées survivent à la fermeture du dialogue et à l’actualisation.
Le contenu ressemblant à du HTML reste du texte. Le renderer n’a pas de méthode send.
Le dialogue de connexion est annulé dans le parcours Electron ; aucun secret réel.
Les parcours NECA comparent les fichiers de release avant/après et restent en lecture seule.
Résultats du paquet et captures inspectées : `odoo-tricorder/QA.md`.

## Adoption et réserves

Changements : `scripts/odoo_smtp.py`, `odoo_delivery.py`, rôle canonique
`roles/release-close.md`, documentation et intégration du cockpit. Génération isolée
contrôlée avant reconstruction des profils actifs Claude/Codex ; pas d’édition
manuelle des profils générés. Guide utilisateur : [DELIVERY_EMAIL.md](../../DELIVERY_EMAIL.md).

Le corpus précédent ne couvrait ni SMTP ni édition : absence de fonctionnalités,
pas de taux de défaut LLM mesuré. Une assertion ajustée lors du développement
(champ enabled ajouté par le statut, absent du résultat de préparation) ne constitue
pas une campagne comparative. Aucun gain de comportement natif n’est revendiqué.
L’accord reste une décision humaine que l’orchestrateur doit transcrire honnêtement ;
le helper ne peut pas prouver sémantiquement qu’un humain a réellement approuvé.
La consigne exige une nouvelle présentation si la version a changé depuis la relecture.

La connexion réelle, les règles du compte Google et la réception d’un premier
message restent à valider avec l’utilisateur. Aucun envoi, accès Gmail réel,
installation du paquet ni publication GitHub dans cette intervention.
