# Preuves QA synthétiques

- `real-qa-shell-02` : vrai script ancien contre corrigé, deux bases existantes
  vides dans un Compose jetable. Ancien : vert et zéro test. Corrigé : vert et
  douze tests réellement exécutés. 7,66 s / 8,37 s, un essai, sans conclusion de
  performance générale. L'essai 01 a échoué des deux côtés à cause d'un montage
  de filestore mal configuré ; il reste dans les résultats locaux, exclu de la
  comparaison. L'image utilise uid100/gid101, vérifier au lieu de supposer uid101.
- `runtime-oracle-strengthened-red` : trois assertions en échec dans la première
  référence après ajout des tests de valeurs RPC par défaut et politique inchangée.
- `runtime-strengthened-final` : référence corrigée, douze tests verts avec Studio ;
  trois mutants détectés. Le compteur de statistiques inclut le montage des classes :
  utiliser le bilan final de douze méthodes, pas les seize lignes statistiques.
- `tooling-checks-02` : 89 tests de l'outillage, code/log liés par empreintes.
  Les chemins absolus désignent les originaux locaux ; les copies de logs gardent
  les mêmes octets. La preuve est vérifiable sur le poste d'origine, pas portable
  comme attestation signée.
- `tooling-checks-04` : 90 tests après la reprise du correcteur et la préparation CI.
  `python312.log` : les mêmes 90 tests passent sous Python 3.12.3, sans sources
  Odoo ni réseau ; Git fourni en lecture seule.
- `build.log` : génération isolée conforme des vingt fichiers et deux blocs.

Ces traces ne contiennent que des fixtures synthétiques. Les sorties CLI brutes,
les authentifications et l'analyse contenant des informations client ne sont pas
exportées. Les empreintes de sources dans les campagnes renvoient à leur snapshot
local ; la référence finale est versionnée dans `benchmarks/odoo`.

- `tooling-final` / `python312-final.log` : 91 tests sur les deux versions Python.
- `development-final` : huit codes livraison réévalués sans modification avec
  les mêmes treize méthodes ; les sorties de référence Claude restent rejetées.
- `expense-final` : les deux codes de transfert passent six méthodes.
- `delivery-mutations-final` : trois mutants toujours détectés avec l'oracle final
  et Studio installé. `expense-mutants/final` : les deux mutants sont rejetés ;
  le statut `failed` du runner est attendu ici, car ces fichiers volontairement
  faux ont été fournis comme candidats. La référence reste verte.
