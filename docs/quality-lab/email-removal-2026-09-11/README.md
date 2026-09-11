# Retrait de l’intégration email

Décision explicite de l’utilisateur, 11 septembre 2026 : abandon du parcours email.
Référence : Crew `782f50a420b7301cd8646a295b0c01aabacf502e`, Tricorder
`bf5393abc55abdf8c6e8d1a3023a56a2fca7fbe6`, avec ajouts locaux jusqu’à la 0.2.4.
Le résultat attendu est une absence de fonctionnalité, pas un gain comportemental.

## Retrait et compatibilité

- Tricorder 0.2.5 : plus de section email, éditeur, connexion ou paramètres destinataires.
- API renderer/IPC et actions du catalogue retirées ; plus de lecture du stockage email.
- Transports Gmail/SMTP retirés ; ancien `odoo_delivery.py` refuse toutes les commandes.
- Deux fonctions de lecture inertes renvoient « désactivé » aux anciennes fenêtres.
- Rôle canonique de clôture sans préparation/envoi automatique, profils reconstruits.
- Brouillons, configurations et secrets conservés, sans lecture ni révocation implicite.
- Documentation de fonctionnement mise à jour ; rapports email antérieurs historiques.

## Preuves et incidents

Les anciens parcours démontraient encore la présence des écrans/API. Le nouveau
test Electron vérifie leur absence même avec des données email synthétiques
préexistantes, puis conserve leurs octets après navigation et actualisation.
Deux nouveaux tests catalogue refusent les anciennes actions et interdisent le
chargement du helper email. Quatre tests Crew remplacent les 41 tests du service retiré :
CLI refusé, API d’envoi absente, données préservées et import d’une demande EML.
Le nombre de tests diminue parce que le service correspondant a été supprimé.
Résultat : 263 tests Crew, 54 Python + 11 JavaScript Tricorder et six parcours
Electron sur sources verts. Les builds isolé et actif, la parité et le skill
de clôture sont validés.

Pendant l’intervention, la fenêtre installée 0.2.4 appelait encore `config_for` :
son absence a causé l’erreur signalée par l’utilisateur. Ajout des lectures
inertes `config_for`/`status`, sans stockage ni transport ; ancien catalogue
installé recontrôlé sur NECA : chargement réussi, email désactivé, panneau absent.
Cette compatibilité ne réintroduit pas l’envoi. Une première assertion de test
supposait à tort `odoo_mail.py --help` disponible ; remplacement par un vrai
fichier EML synthétique, rendu textuel vérifié.
Le premier parcours NECA attendait un chronomètre ouvert alors que le registre
avait évolué : assertion alignée sur les entrées running du registre réel,
sans modifier celui-ci. Le parcours rejoué vérifie l’absence correcte du bloc.

Contrôles : suite Crew, graphe, build isolé puis actif et parité Claude/Codex ;
suite Tricorder, six parcours Electron dont NECA en lecture seule et application
empaquetée. Résultats finaux et paquet : `odoo-tricorder/QA.md`.
Aucune campagne LLM ni connexion/envoi Gmail. Aucun changement de données client,
installation de paquet ou publication GitHub. Les anciennes sources non commitées
ont une sauvegarde privée locale avant retrait ; les preuves historiques restent consultables.
