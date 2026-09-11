# Veille et compteurs partiels — protocole figé

Demande : exclure automatiquement les suspensions des chronomètres et conserver
les compteurs natifs connus de Claude et Codex. Aucun projet client modifié.
Référence : HEAD 782f50a, avec modifications locales antérieures conservées.

Empreintes initiales : `odoo_usage.py` 56a82de110cf64efc75b46f8ebf2b305b289fd6e1390a044a6e6da7d6f20b5ff ;
`odoo_effort.py` 65b5f5f4c21e9ed9657ec178ec449286ecc3d6ac84bbe878ac4932573787e3ce.

Reproductions : un chronomètre compte actuellement la nuit ; un cache absent
supprime les autres compteurs ; une dernière ligne JSONL en cours masque le relevé.
Correction ciblée : horloges Linux monotone/boottime et identité de démarrage,
compteurs indépendants, tolérance limitée à la dernière ligne non terminée.

Critères : 120 s éveillées + 8 h de veille donnent 120 s ; reprise après reboot
inconnue et non 8 h de travail ; coût non calculé avec cache inconnu ; aucune
addition de cumuls Codex ni des instantanés d'un même message Claude.
Contre-épreuves : corruption au milieu du JSONL, compteur régressif partiel,
ancienne mesure sans horloge. Cas réservé : horloge civile reculant pendant
deux suspensions ; le résultat ne dépend que des horloges du même démarrage.

Limite : une durée native historique sans preuve de suspension n'est pas
corrigée arbitrairement. Les nouveaux chronomètres locaux sont protégés ; leurs
attentes hors veille restent incluses. Aucun appel LLM requis par ces essais.

Sources : [horloges Linux](https://man7.org/linux/man-pages/man3/clock_gettime.3.html),
[cache Claude](https://platform.claude.com/docs/en/build-with-claude/prompt-caching),
[cache OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching).

## Résultat et adoption

- Référence rouge : 60 tests ciblés, 2 échecs et 4 erreurs (veille, reboot,
  delta partiel, cache Claude/Codex, dernière ligne). Sorties conservées dans
  la session d’exécution ; aucun essai LLM ni modification client.
- Correction : `scripts/odoo_usage.py`, `scripts/odoo_effort.py` et tests associés.
- Contre-épreuves et cas réservé verts : 300 s éveillées, 21 600 s de suspensions,
  aucune lecture de l’horloge civile ; ancien chronomètre sans borne inconnu.
- Compatibilité : bilan historique sans version de mesure vérifié sans réécriture.
- Suite complète : 271 tests ; graphe 59 nœuds/129 arêtes valide.
- Génération isolée puis active : 30 fichiers, deux blocs et pointeur conformes.
- Adoption locale des scripts, sans évolution des instructions de rôle dans
  cette itération. Les formats natifs supplémentaires et la collecte des
  sous-agents ne sont pas présentés comme implémentés.
