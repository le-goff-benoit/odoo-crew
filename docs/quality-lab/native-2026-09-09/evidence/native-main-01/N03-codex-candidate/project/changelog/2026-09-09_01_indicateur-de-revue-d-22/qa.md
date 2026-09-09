## 2026-09-09 — Point 1, indicateur D-22 — QA de tâche Studio

**Série** 19.0 (LAB.md, config et version serveur RPC) · **module** aucun · **copie** lab_client synthétique locale.

### Verdict
**VALIDÉ** — les six critères sont satisfaits pour le périmètre demandé. Seul x_studio_needs_review est ajouté durablement. Release ouverte.

### Résultats exécutés
| Contrôle | Résultat | Preuve dans studio/proofs/ |
|---|---|---|
| Rouge avant création | Champ absent, exit 1 attendu | before-red.log |
| Construction Studio et répétition | Créé puis inchangé, XML-ID auto | build.log, build-second.log |
| Relecture du pack | 1 champ, deux dépendances, D-22 exact, aucun unresolved | ../pack.json |
| Diff initial et final | 0 création, 0 modification, 1 inchangé | qa-diff.log, diff-1.log, diff-2.log |
| Première application après retrait du seul champ ajouté | 1 créé, 0 modifié | apply-1.log |
| Seconde application | 0 créé, 0 modifié, 1 inchangé ; identité stable | apply-2.log, after-pack.json |
| Scénarios après chaque application | 9 cas de création + 6 transitions + 2 lots + 2 recherches stockées, tous verts | scenarios-1.log, scenarios-2.log |
| Initialisation des lignes préexistantes au champ | 3/3 correctes, valeurs sources conservées | preexisting-result.json |
| Conservation et nettoyage | Champs, vues, ACL, actions/automatisations conservés ; zéro demande et zéro action temporaire | before-pack.json, after-pack.json, cleanup.json |

### Couverture des critères
| Critère | Couverture | État |
|---|---|---|
| C1 — champ unique et existant conservé | Métadonnées RPC, snapshots, quatre XML-ID lab_seed inchangés | OK |
| C2 — seuil inclusif et prêts exclus | rental 5/6=False, 7/8=True ; loan 6/7/8=False ; zéro et catégorie absente=False | OK |
| C3 — deux dépendances et stockage | Changements séparés dans les deux sens, lots, relecture et domaines de recherche | OK |
| C4 — initialisation/conservation/nettoyage | Trois lignes créées champ absent ; copie revenue à son état initial de zéro demande | OK |
| C5 — pack rejouable sans doublon | Vrai odoo_pack.py : création puis application sans modification, diff nul | OK |
| C6 — périmètre et livraison | Aucun écran/droit/action permanente/module/déploiement ; QA et journal, release ouverte | OK |

### Rejouer
Depuis le dossier `studio/` : `python3 test_d22.py` pour le métier ; `python3 test_pack_d22.py` pour deux applications et les scénarios. Les scripts ciblent uniquement le RPC local jetable de LAB.md.
La commande de QA initiale était `python3 test_pack_d22.py --recreate-added-field` : elle retire uniquement le champ identifié par le pack avant de vérifier son import réel. Les trois fixtures d'initialisation et leurs résultats sont archivés, puis elles ont été supprimées.

### Limites et contrôles non applicables
- Le modèle préexistant n'a aucune ACL. Les scénarios utilisent une action serveur éphémère supportée par ir.model, avec sudo limité aux données de recette, puis la suppriment. L'accès d'un utilisateur métier n'est pas validé ; aucune règle ou ACL n'a été modifiée.
- Aucun module : lint module, installation/update de module et suite Python Odoo non applicables ; l'application du pack et les scénarios sont les contrôles Studio prescrits.
- Aucun écran changé : capture et parcours navigateur non applicables. Aucune recette complète de clôture, restauration supplémentaire ni déploiement exécuté.
- La base initiale contenait zéro demande ; initialisation prouvée sur trois données synthétiques créées avant le champ. Sources 19.1 non disponibles, comparaison intersérie non effectuée.

### Anomalies
Aucune anomalie introduite ni critère restant rouge. Pendant la construction, une assertion trop forte sur noupdate a été corrigée d'après les sources réelles, avant la QA ; ce n'était pas un échec du calcul.

### Appris
En Studio 19.0, ir.model.data.create marque studio=True sans forcer noupdate ; write force les deux. Le champ exporté conserve les métadonnées de sa création Studio. Candidate à corriger dans le référentiel via /odoo-feedback, sans modifier le dispositif dans cette tâche.
