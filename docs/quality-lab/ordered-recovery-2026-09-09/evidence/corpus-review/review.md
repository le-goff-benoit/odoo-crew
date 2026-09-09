# Revue indépendante du banc et de l’export natif

Verdict : **PASS avec limites déclarées**, aucun défaut bloquant du correcteur amendé identifié. Ce verdict porte sur le banc et ses preuves documentaires ; il ne certifie ni le runtime Odoo ni une promotion sans réserve.

## Correcteur, calibration et amendement

Calibration relancée dans un bac temporaire, sans réécrire le fichier du dépôt : **15/15 résultats attendus**. Le positif normal, le terminal public task_done et l’absence du champ optionnel de registre passent. Ordre inversé, trace absente, source modifiée, mémoire différente, retry, gate supplémentaire, reprise dans le contexte auteur et verrou orphelin sont refusés. Les trois cas réels ont été relus par check.py sans mutation : **O01/O02/O03 passent**, O03 représentant le refus attendu.

Les empreintes du gel initial, des quatre fichiers avant/après amendement et du diff concordent. Les quatre autres fichiers gelés restent identiques. L’amendement conserve l’exception initiale du registre, le verdict intermédiaire négatif sur task_done et la rétractation d’une annonce prématurée. Il répare deux hypothèses du juge, sans effacer les observations ni compter une fixture comme réception native. Il continue de refuser QA et retry superflus.

## Export et publication

Examen des métadonnées de **18 exports publics native-final** : aucun message entrant, système/développeur, message assistant analysis ou objet reasoning ; aucun last_agent_message dans task_complete. Toutes les empreintes d’exports correspondent aux manifests. Le v1 est conservé ; le nouvel export prend en charge phase=final_answer et n’ajoute que les métadonnées temporelles du terminal. Aucun accès aux sessions brutes ni lecture de contenu assistant analysis.

L’archive sélectionne les cas synthétiques, audits, amendement, exports et intégration locale ; elle exclut le checkout reference, les répertoires git, caches et distributions. Aucun lien symbolique trouvé dans ces arbres. Un contrôle sans affichage des valeurs sur **1 008 fichiers destinés à l’archive** ne trouve aucun motif de clé privée, jeton GitHub ou clé OpenAI à forte confiance. Aucun secret réel ou source client n’a été identifié dans les éléments inspectés. Cela reste une vérification ciblée : les appels/résultats d’outils sont recopiés, pas nettoyés arbitrairement, et le copieur d’archive ne constitue pas un filtre générique de confidentialité. Le mot de passe PostgreSQL public du bac synthétique est documenté comme tel.

## Mesures et limites

Les 18 snapshots de jetons correspondent exactement au dernier compteur cumulatif de leur thread public. Le script ne somme pas les compteurs successifs. Les sous-compteurs cached/reasoning ne doivent pas être ajoutés une seconde fois au total. La sélection nominative est bornée à cette campagne ; le root historique est explicitement hors mesure.

Au début de la revue, les durées étaient seulement agrégées et corpus_review manquait de la liste. Le parent a corrigé metrics.py pendant la revue : liste complétée, détail temporel par tour et maximum par tour. Le code corrigé a été relu ; **metrics.json demeure un snapshot préparatoire à régénérer après la terminaison des contextes**. Les followups sont alors distingués, la durée active exclut les attentes entre tours. Les métadonnées temporelles permettent d’apprécier les budgets sans confondre un thread réutilisé avec un tour unique.

La réserve de l’audit précédent est justifiée : puisque les messages entrants sont exclus et certaines enveloppes opaques, l’absence de consignes additionnelles n’est pas mesurée. Les PASS comportementaux et mécaniques ne valent pas certification intégrale de l’isolation des consignes. Cette limite n’est pas effacée par l’amendement.

Revue effectuée en lecture seule des scripts/projets ; seuls review.md et review.json sont produits. Les contrôles et empreintes détaillés figurent dans review.json.
