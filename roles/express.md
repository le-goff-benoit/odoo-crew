# Correctif Odoo express — changement local, contrôlé et livrable

Traite une petite correction Odoo dont le résultat attendu est déjà explicite.
Le flux reste piloté par l'orchestrateur principal et ne délègue pas ses étapes :
son intérêt est de réduire le coût de coordination tout en conservant les
contrôles qui rendent le changement livrable.

## Qualification

Commence par `odoo_briefing.py`, puis ouvre un flow de type `express` :

```bash
FLOW=$(python3 ~/.odoo19-agents/scripts/odoo_flow.py start <projet> \
  --kind express --id <identifiant-court>)
```

Le flux express convient lorsque toutes ces conditions sont remplies :

- le module et la zone à modifier existent déjà ;
- le résultat est précis et localisé ;
- le changement est réversible et reçoit un test ciblé proportionné ;
- il ne crée ni modèle, ni champ, ni droit, ni dépendance, ni migration ;
- il ne change aucun calcul comptable, fiscal, de paiement ou de QR, aucune
  donnée existante et aucun contenu légal.

Une retouche de présentation d'un document financier reste admissible si les
montants, règles et données demeurent strictement inchangés. Dès que la portée
s'étend ou qu'une décision fonctionnelle manque, termine la qualification par
l'issue `full` et poursuis avec `/odoo-new` depuis la revue fonctionnelle. Le
travail et les constats déjà produits sont conservés.

## Réalisation

Travaille dans un worktree propre créé depuis la branche distante cible lorsque
le répertoire courant contient des modifications. Ne mélange jamais les travaux
déjà présents dans le projet.

Effectue la modification minimale, ajoute ou adapte le test qui observe le
comportement demandé et mets à jour la documentation réellement concernée. Pour
une série d'ajustements liés, complète la même entrée de changelog express ; ne
crée pas un dossier par itération visuelle. Respecte les conventions de release
du projet et incrémente la version du module avant une livraison immédiate si
la plateforme en dépend.

## Contrôles

Exécute au minimum :

1. `git diff --check` ;
2. le lint Odoo limité aux fichiers touchés ;
3. l'installation ou la mise à jour du module ;
4. le test ciblé du comportement ;
5. pour un PDF ou un écran, le rendu correspondant lorsque l'apparence est le
   motif de la correction.

Deux reprises au maximum sont admises. Une QA encore rouge est consignée puis
arrête la livraison. N'annonce jamais comme exécuté un rendu ou un test absent.

## Mémoire et livraison

Ajoute une entrée de quinze lignes maximum à `JOURNAL.md`. Le compte rendu donne
le comportement livré, le commit, la version et les contrôles réellement verts.

Prépare toujours un commit propre. Pousse vers la branche demandée seulement si
l'utilisateur a explicitement demandé de pousser, déployer ou travailler « en
express » avec livraison. Après le push, relis la référence distante et vérifie
qu'elle correspond au commit local. Une production Odoo reste soumise aux règles
de confirmation de `odoo_instance.py`.
