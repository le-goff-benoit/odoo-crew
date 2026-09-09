# Qualification versions et navigateur

Exécuter explicitement `python3 scripts/odoo_qualify_versions.py --output /tmp/nouveau-dossier`.
Prérequis locaux : Docker, images `postgres:16`, `odoo-qa:18.0` et `odoo-qa:19.0`.
Le lanceur ne télécharge ni ne construit d'image, ne monte aucune base cliente,
ne publie aucun port et ne modifie pas le banc natif partagé.
Le réseau Docker est interne et le home jetable porte un mode explicite
`1777` : le tmpfs sans mode hérite sinon des droits root `0750` de l'image et
empêche l'utilisateur Odoo de créer le profil Chrome.

Le protocole est figé dans `protocol.json` avant les essais : trois exécutions,
360 secondes maximum chacune. Les deux versions exécutent les mêmes quatre
tests ORM : zéro autorisé, création négative refusée, modification négative
refusée sans altérer l'enregistrement, confirmation de l'objet. Seule la
déclaration de contrainte SQL change selon la série.

En 19.0, `HttpCase.browser_js` ouvre réellement Chrome sur la fiche Odoo du
témoin, clique le bouton objet et attend le statut affiché « Confirmed ».
Après le retour du navigateur, le test invalide le cache ORM puis vérifie
le statut serveur et le montant. Le troisième essai reprend ce parcours et
attend volontairement « draft » côté serveur : il doit être rejeté.
Un HTTP 200 ou un navigateur skippé ne suffit jamais pour le verdict.
Le marqueur de clic doit provenir de la console `.browser`, pas de la copie
du code JavaScript affichée dans le log. `--browser-only` limite une reprise
après incident aux deux scénarios 19.0 et conserve les preuves précédentes.

Les formes sont vérifiées dans les sources locales en lecture seule :

- `18.0/odoo/addons/base/models/res_currency.py:51` : `_sql_constraints`.
- `19.0/odoo/addons/base/models/res_currency.py:49` : `models.Constraint`.
- `19.0/odoo/tests/common.py:2450` : contrat `browser_js` et signal de succès.
- `19.0/addons/web/static/src/views/fields/statusbar/statusbar_field.xml:39` :
  classe du statut sélectionné et attribut `data-value`.
- `19.0/addons/mrp/tests/test_order.py:5583` : URL réelle d'une fiche `/odoo/action-ID/ID`.

Chaque exécution conserve le briefing préalable, le module exact, le log
Odoo, les marqueurs métier et la décision d'oracle. Le bilan retient les IDs
d'images, durées et vérification du nettoyage. SHA256 couvre les preuves.
Le mot de passe PostgreSQL est une constante publique dédiée au réseau
jetable, sans lien avec un identifiant utilisateur.

Portée : un témoin synthétique par série, une seule exécution positive de
chaque scénario, UI administrateur en 19.0. Cela ne qualifie ni les droits,
ni les modules clients, ni la série 17.0 ou SaaS, ni la performance des agents.
