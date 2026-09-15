# Procédure — qa-runtime

Chargement conditionnel depuis le profil canonique. Les chemins `docs/…` et
`roles/…` sont relatifs à `~/.odoo19-agents/`.

## Étape 2 — Exécution réelle (Odoo local sous Docker)

Le stack vit dans `~/.odoo19-agents/stack/`, **dans la série du module**
(image `odoo-qa:<série>`, base par module `odoo_qa_<série>_<module>`). Ne
coupe jamais un service que tu n'as pas démarré : d'autres projets s'en servent.

**QA de tâche** — un seul chargement d'Odoo, base par module gardée chaude
d'une tâche à l'autre (installation si elle n'existe pas, mise à jour sinon,
tests ciblés dans le même passage) :

```bash
export ODOO_ADDONS_DIR=<répertoire contenant le module>
~/.odoo19-agents/scripts/odoo-test.sh <module> --quick --tags /<module>:<TestClasse>
```

**Point de contrôle** — la suite complète du module, base chaude, sans tours
(`odoo-test.sh <module> --quick`, deux à cinq minutes). Pas systématique : tu
le déclenches quand **l'un** de ces cas se présente, et tu le dis dans la ligne
d'état :

- le diff touche un fichier déjà modifié par un autre point de la release
  (`odoo-release.sh changed` le montre) ;
- un modèle partagé est concerné : `sale.order`, `account.move`,
  `stock.picking`, `project.task`, `res.partner`, ou tout modèle étendu par
  plusieurs fichiers du module ;
- c'est le troisième point de la release depuis le dernier contrôle ;
- la tâche est sensible (droits, compta, facturation, données existantes) —
  là, c'est la recette sur la copie du client, pas seulement la suite.

Sur Claude comme sur Codex, ce contrôle peut tourner pendant une tâche
indépendante si son code est figé et ses ressources séparées (checkout, base,
filestore, port et logs). Sinon, exécute-le séquentiellement. Reçois son résultat
avant une tâche qui le consomme et avant clôture. Une régression introduite doit
être corrigée ; une anomalie antérieure prouvée sur la base de la release reste
dans « Réserves », sans masquer le résultat rouge.

**Durées** — chaque étape d'`odoo-test.sh` affiche son temps (`⏱`) et la ligne
`RECETTE` les récapitule : annonce une durée réelle dans tes lignes d'état,
pas « quelques minutes ».

**QA de release** — une commande, tout le protocole, un tableau en sortie :

```bash
~/.odoo19-agents/scripts/odoo-recette.sh <module> --release changelog/<release> --risk <normal|high> --db <copie_client>
```

Elle enchaîne lint `--changed` depuis l'ouverture de la release, base neuve
(clonée en quelques secondes depuis une base **gabarit** par module où les
dépendances standard sont préinstallées ; le gabarit se reconstruit quand la
liste des dépendances du manifest change ; `--no-template` force une
installation intégrale), installation, `-u`, **suite complète** du module tours
compris, désinstallation, mise à niveau sur la copie du client, et écrit
`changelog/<release>/recette.md`. Elle signale un module sans test, une version de
manifest qui n'a pas bougé, et tout ce qui n'a pas été exécuté.

Ce que tu vérifies, dans les deux modes :

1. **Installation** sans erreur ni warning de vue (`ir.ui.view` est un défaut,
   pas du bruit). Un module « ignoré » par Odoo (`invalid module names`) est un
   échec : le script le détecte, ne le contourne pas.
2. **Mise à jour** — `-u` passe sur une base où le module est installé.
3. **Tests** — en mode tâche, ceux de la tâche ; en mode release, **toute la
   suite**. Un `skip` doit être justifié. Un test rouge antérieur à la release se
   prouve en rejouant la suite sur la base git de la release : il va dans
   « Réserves » avec cette preuve.
4. **Logs** — lis la ligne `RECETTE …` et les extraits d'erreurs que le script
   imprime. Va dans le log complet **seulement** pour localiser une erreur
   signalée, avec `grep -n`, jamais en le lisant d'un bloc.
5. **Mise à niveau sur la copie du client** (mode release, ou tâche sensible) :
   c'est le seul contrôle qui voit les vues héritées cassées par Studio, les
   données `noupdate` non reprises et les enregistrements existants qui
   violent une nouvelle contrainte.

Un module qui ne s'installe pas est un échec, quelle que soit la qualité du code.

---

## Étape 3 — Parcours utilisateur, captures et PDF (mode release)

Navigateur et moteur PDF sont **dans le conteneur** : l'image embarque Google
Chrome, wkhtmltopdf 0.12.6 (patched qt) et poppler-utils. Ne conclus jamais
« pas de navigateur disponible ». Sur le poste, `odoo_capture.py` (Playwright)
sert aux captures recadrées de la documentation.

Piège connu : un tour qui échoue sur une **erreur console d'un module
standard** (bundle JS, import `@account/...` introuvable) trahit un décalage
entre le paquet Odoo de l'image et les sources enterprise montées, pas un
défaut du module. Signale-le comme problème d'outillage.

```bash
~/.odoo19-agents/scripts/odoo-test.sh <module> --tours              # tours seuls
~/.odoo19-agents/scripts/odoo-shot.sh "/odoo/action-mod.action_x/3" --wait ".o_form_view" --full --out fiche.png
~/.odoo19-agents/scripts/odoo-pdf.sh mon_module.action_report_x 42 --out rapport.pdf --html
```

Trois pièges déjà traités par `odoo-pdf.sh` : `_render_qweb_pdf` retombe sur
du HTML en contexte de test ; sans serveur HTTP, le PDF sort nu (`NimbusSans`
au lieu de `Lato`) ; les bundles sont produits par le processus serveur.

En complément :

- Chaque critère d'acceptation est couvert par un tour, un test HTTP, ou un
  scénario manuel reproductible (URL, login, clics, attendu) écrit dans
  `tests_navigateur.md`. Ce qui n'est pas couvert, tu le dis.
- Le parcours se termine par un **rechargement** et un contrôle de la valeur
  **serveur** : un écran juste avec une base fausse est un défaut.
- Contrôle l'accès portail et les droits d'un utilisateur non-admin quand la
  fonctionnalité les concerne : le test en `admin` ne prouve rien sur les droits.
- Les captures finales vont dans `changelog/<release>/captures/`, la recette dans
  `changelog/<release>/tests_navigateur.md` (gabarits du skill `camptocamp-docs`).

---
