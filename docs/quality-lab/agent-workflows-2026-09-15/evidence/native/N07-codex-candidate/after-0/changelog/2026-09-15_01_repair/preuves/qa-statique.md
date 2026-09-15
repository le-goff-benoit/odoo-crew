# QA statique — N-17

Diff relu : modèle existant et trois fichiers de tests, tous visibles dans git diff (nouveaux tests déclarés en intention d'ajout). Aucune dépendance, ACL, vue ou donnée XML modifiée. git diff --check sans erreur. Le diff complet, tests inclus, est dans code.diff.
Ruff bloquant et conseils : verts sur tout le module, voir lint.log. Contrôles Odoo 19.0 complets puis --only-files : même unique erreur author absent du manifest. dette-manifest.txt établit le manifest strictement identique à HEAD ; la passe ciblée garde cette anomalie structurelle par conception. Aucun défaut dans les fichiers touchés. Lint global en échec antérieur explicitement conservé, pas présenté comme vert.
Revue : copy=False respecte le mécanisme ORM de 19.0 ; ordered_qty conservé ; zéro manuel explicite ; filtre état/manual ; reliquat ensure_one avant mutation, retour vide non positif, valeurs remises à zéro et état de source après création. Pas de sudo, SQL brut, nouvelles contraintes ou arrondi ajouté. Les tests importés vérifient des attentes numériques de N-17, dont zéro et fractions.
Risque données couvert par reprise.json/rejeu.json ; version 19.0.1.0.0 conservée jusqu'à clôture. Le module n'est ni commité ni déployé.
Verdict de tâche : aucun défaut introduit trouvé ; dette du manifest à conserver séparément. Relecture non indépendante selon LAB.md.
