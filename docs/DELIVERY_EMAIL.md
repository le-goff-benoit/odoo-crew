# Email de clôture — fonctionnalité retirée

À la demande de l’utilisateur le 11 septembre 2026, l’intégration email a été
retirée de Tricorder 0.2.5 et des consignes de clôture Odoo Crew.

Il n’y a plus de connexion Gmail/SMTP/OAuth, de configuration des destinataires,
d’éditeur ou d’envoi dans le cockpit. Les agents ne préparent plus automatiquement
de message à la clôture. Ils peuvent toujours rédiger une communication comme
document sur demande, sans envoi.

L’ancien script `odoo_delivery.py` refuse toutes les commandes avec un message
de retrait, sans lire le stockage privé ni le trousseau. Deux fonctions de lecture
inertes renvoient « désactivé » aux fenêtres Tricorder 0.2.4 encore ouvertes ; elles
n’exposent ni message ni destinataire. Les transports ont été retirés.

## Données conservées

Les anciens brouillons, paramètres et justificatifs d’envoi dans
`~/.local/state/odoo-crew/delivery/` restent intacts et privés. Les secrets du
trousseau n’ont été ni lus ni supprimés. Ce retrait ne révoque pas les autorisations
du compte Google ; une révocation peut se faire séparément par son propriétaire.
Ne pas verser ces données dans un dépôt Git.

L’import des demandes reçues en `.eml` par `odoo_mail.py`, les fichiers du projet
et les documents clients restent disponibles. Aucun état ni livrable client n’a
été supprimé pour ce retrait.
