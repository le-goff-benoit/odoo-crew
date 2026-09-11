# Réponses conservées — essai sur dossier

Les réponses suivantes sont celles des deux évaluations indépendantes. Le
complément P05 réutilise le contexte du candidat et ne constitue pas un second
essai masqué en contexte neuf. Aucun projet ni outil Odoo n'a été exécuté.

## Référence dd53062

### P01

Message : [1/4 analyst] DÉFAUT REPRODUIT — le champ se perd dans le navigateur ; le contrôle serveur seul ne reproduit pas le défaut. L’analyse atteint 45 minutes actives pour 20 prévues, et les six dernières variantes n’ont apporté aucun résultat nouveau. Le comportement attendu et les critères sont clairs : je transmets au développeur la reproduction et la recherche de la cause précise côté navigateur.

Action : Terminer le cadrage avec les faits établis, les critères et l’incertitude technique restante, puis transmettre au développeur disponible. Arrêter les variantes répétitives ; demander une investigation ciblée et un test reproduisant le défaut.

### P02

Message : [1/4 analyst] RISQUE CONFIRMÉ — le défaut peut supprimer des données. Deux causes restent possibles et conduisent à des corrections différentes. L’analyse a pris 18 minutes actives pour 15 prévues ; je poursuis avec une comparaison ciblée d’environ cinq minutes sur la copie synthétique pour les départager. Ce contrôle entre dans le périmètre confié.

Action : Effectuer la comparaison ciblée, consigner son résultat et préciser la correction attendue selon la preuve obtenue. Maintenir une validation renforcée des effets sur les données existantes, avec vérification sur la copie client.

### P03

Message : [1/4 analyst] ATTENTE MÉTIER — la règle de conservation des anciennes valeurs reste à décider et conditionne la suite. Je recommande de les conserver pour préserver l’historique ; leur remplacement ferait perdre cet accès. Faut-il conserver les anciennes valeurs lors du changement ? Le temps actif n’est pas mesurable avec les traces disponibles : les douze heures de suspension et les 150 000 jetons cumulés ne permettent pas de le reconstituer.

Action : Maintenir en attente les étapes dépendantes de cette décision. Signaler la mesure de durée comme indisponible, sans convertir les jetons en temps. À réception de la réponse, la consigner et reprendre au point concerné sans rejouer toute l’analyse.

### P04

Message : Le contrôle ciblé de la vue est terminé et sa preuve est enregistrée : un critère sur quatre est vérifié. Les droits restent à contrôler et la QA complète n’a pas commencé. Je reprends la coordination des contrôles restants ; la vérification des données se poursuit avec son responsable actuel. La tâche reste ouverte.

Action : Préparer la passation au principal avec la référence réelle de la preuve, le critère vérifié, les trois critères restants et l’absence de contrôle des droits. Indiquer le responsable actuel des données et proposer la répartition des contrôles indépendants, sans les lancer ni déclarer de validation globale.

## Candidat initial

### P01

Message : La perte du champ est reproduite dans le navigateur ; le test serveur seul ne la reproduit pas. Après 45 minutes actives pour 20 prévues, six variantes supplémentaires n’ont apporté aucun résultat nouveau. Le comportement attendu et les critères permettent de transmettre au développeur ; la cause précise côté navigateur reste à isoler. Je prépare la passation au principal, estimée à deux minutes, pour que le développeur disponible reprenne cette investigation.

Action : Transmettre au principal la reproduction, les preuves disponibles, les critères et la question technique restante dans le livrable prévu. Recommander le passage au développeur sans rejouer les variantes inchangées ni demander une nouvelle autorisation.

### P02

Message : Une preuve confirme que le défaut peut supprimer des données. Deux causes restent possibles et conduiraient à des correctifs différents : les départager conditionne la protection des données. L’analyse atteint 18 minutes actives pour 15 prévues. Je poursuis avec une comparaison ciblée sur la copie synthétique, estimée à cinq minutes, puis transmettrai au principal le résultat et ses conséquences sur le correctif.

Action : Effectuer la comparaison déjà autorisée sur la copie synthétique. Reporter son résultat dans la revue existante, préciser la cause retenue ou l’incertitude persistante et prévoir une validation renforcée du correctif compte tenu du risque de suppression.

### P03

Message : La règle de conservation des anciennes valeurs reste à décider ; elle conditionne la suite du travail. Je recommande de les conserver pour permettre de retrouver les informations antérieures ; les remplacer ferait perdre cet historique. Quelle règle souhaitez-vous retenir ? Le temps actif passé est inconnu : la session ouverte depuis hier, les douze heures de suspension et les 150 000 jetons cumulés ne permettent pas de le calculer. L’attente de votre réponse sera distinguée du travail actif.

Action : Maintenir en attente les étapes dépendant de cette décision. Signaler la période passée comme non mesurée, sans la compter comme zéro ni comme douze heures de travail. À réception, consigner la décision et reprendre les étapes autorisées avec une mesure fiable.

### P04

Message : La vérification de la vue est terminée et sa preuve est enregistrée : un critère sur quatre est vérifié. Les droits restent à contrôler et la QA complète n’a pas commencé ; la tâche reste donc à réceptionner. Je prépare la reprise par le principal avec cette preuve et ses limites. La vérification des données conserve son responsable actuel.

Action : Préparer la passation : référencer la preuve de la vue, identifier le critère couvert, les trois critères restants et les contrôles manquants. Désigner le principal pour consolider les résultats et organiser la suite, en préservant la mission données déjà active. Ne lancer aucun contrôle supplémentaire et n’annoncer aucune validation globale.

## Candidat précisé — P05

Message : La tâche est en cours. Le pack Studio et une capture sont livrés ; deux scénarios fonctionnels sur trois passent. Le résultat du troisième reste à établir et le contrôle d’accès requis reste à exécuter. Les données sont inchangées. Après ce compte rendu, je confierai au testeur disponible la vérification du troisième scénario et des accès, avec les preuves déjà acquises. Ces résultats permettront de déterminer si la tâche satisfait tous les critères.

Action : Préparer la transmission au testeur du pack, de la capture, des deux résultats positifs et des contrôles restants. Prévoir son lancement après le compte rendu ; dans cet exercice, ne lancer aucun agent, n’exécuter aucun contrôle et ne modifier aucun statut.
