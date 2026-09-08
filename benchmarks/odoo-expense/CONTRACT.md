# S-02 — notes de frais synthétiques, cas réservé de transfert

Odoo 19.0, modèle `quality_case.expense`. Un enregistrement est une demande de
remboursement d'un seul montant strictement positif, comparé à deux décimales.
`action_pay` peut passer `state` de `draft` à `paid` sans approbation jusqu'à
250 inclus ; au-delà, il faut l'accord d'un autre utilisateur du groupe
`quality_case.group_approver`. Le créateur (`create_uid`) ne peut pas approuver
sa propre demande, même s'il possède ce groupe.

`approved` et `state` ne peuvent être forgés par create/write, ni leurs valeurs
par défaut. L'autorisation est vérifiée côté serveur et suit les règles de
société en appel direct. Une hausse du montant par rapport au montant
immédiatement précédent invalide l'accord ; une baisse le conserve ; une
réécriture identique le conserve. Changer de société invalide l'accord.

Le modèle, ses ACL et sa règle de société sont fournis. Écrire seulement
`models/expense.py`. Ces règles sont les arbitrages explicites du banc fictif,
pas une recommandation comptable ni un besoin de client réel.

L'oracle teste six comportements. Deux mutants (borne déplacée et
approbation de sa propre demande) ont été détectés. Son premier résultat sur
un candidat a révélé une exigence indue du test : `ValidationError` était
imposé alors qu'un `AccessError` bloquait correctement le paiement. Le contrôle
porte désormais sur l'absence de paiement ; les codes candidats restent intacts.
B13 sert de transfert pour les consignes RPC, pas de preuve sur la comptabilité
réelle d'Odoo. Après étude de ces résultats, il n'est plus un cas réservé pour
une prochaine itération de réglage.
