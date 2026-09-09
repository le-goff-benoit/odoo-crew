# Laboratoire synthétique Odoo 19.0
Exécute la demande originale jusqu'au résultat prévu par /odoo-new, avec le vrai graphe et les profils figés du référentiel monté dans le sandbox. Projet /work modifiable, sources et référentiel en lecture seule. Aucun accès à un client ou une production. Toutes les écritures sur cette copie synthétique sont autorisées. Studio est installé, aucun module custom, aucun écran à modifier.

Toutes les commandes du projet se jouent par le wrapper hôte :
python3 /tmp/odoo-fidelity-20260909/codex_control.py bash -lc '<commande dans /work>'
Il monte le projet à /work et le référentiel à ~/.odoo19-agents, crée un /tmp privé à chaque appel et conserve les fichiers du projet et du home entre les appels. Ne stocke donc aucune preuve dans /tmp. Ne démarre pas Docker ou une autre stack. /bridge/labctl shell FICHIER.py permet un shell Odoo sur lab_client (env disponible, commit explicite pour conserver les écritures). Les appels Studio passent par les vrais scripts odoo_pack.py et XML-RPC. Les champs initiaux portent les XML-ID studio_customization.lab_seed_*.

Délègue les voies QA indépendantes à de vrais sous-agents dans une même vague quand les verrous sont compatibles. L'orchestrateur seul pilote le flow et fusionne les preuves ; les enfants écrivent des fragments isolés et ne délèguent pas. Les autres agents partagent le projet : aucun écrasement du travail d'autrui. Donne à chaque enfant son périmètre et ce wrapper. Utilise au plus deux enfants simultanés afin de conserver le slot du superviseur ; au plus huit enfants dans tout ce run.

RPC local : http://127.0.0.1:52795, base lab_client, admin/admin (identifiants jetables du banc).
