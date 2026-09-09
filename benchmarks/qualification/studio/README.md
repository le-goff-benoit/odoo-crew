# Précondition RPC du cas N03

Le premier parcours complet du 9 septembre 2026 a révélé une fixture
incomplète : `N03_seed.py` créait le modèle manuel et ses champs, sans aucun
accès au modèle. L'utilisateur synthétique `admin` pouvait administrer les
champs mais recevait `AccessError` en créant une demande via XML-RPC.
Le contrat exigeait des scénarios RPC et interdisait de modifier les droits.
Cette incohérence du banc ne devait pas être réparée par l'agent évalué.

Amendement : la fixture crée désormais **avant la demande** une ACL CRUD pour
le groupe interne, identifiée par `studio_customization.lab_seed_access`.
Le champ demandé n'est pas créé par la fixture. Les décisions D-22, le code
du correcteur, le modèle, l'effort et le budget restent inchangés. L'essai
initial reste conservé et ne peut être déclaré conforme après coup.

```bash
python3 benchmarks/qualification/studio/preflight.py /tmp/n03-preflight-neuf
```

Ce préflight utilise le véritable `Lab` natif dans une stack dédiée ; aucun
modèle n'est appelé. Il authentifie admin, crée/lit/modifie/supprime une demande
sur les champs existants, contrôle l'ACL et son identifiant stable et confirme
l'absence de `x_studio_needs_review`. Les résultats et identités sont conservés,
puis les ressources dédiées sont nettoyées et contrôlées par label.

Le préflight établit la précondition du prochain essai. Il ne valide pas la
réalisation du champ calculé ni le pack que l'agent produira ensuite, et ne
constitue pas une qualification générale de la sécurité Studio.

## QA indépendante du pack livré

```bash
python3 benchmarks/qualification/studio/pack_qa.py /chemin/pack.json /tmp/n03-pack-qa-neuf
```

Le rejeu natif a exercé deux fois son script de construction, mais n'a pas
appliqué le pack exporté deux fois. Ce contrôle indépendant applique donc
**le pack livré inchangé** sur une nouvelle copie : première création, seconde
application sans modification, mêmes champs et XML-ID, ACL préexistante inchangée,
puis bornes et dépendances vérifiées via RPC. Le protocole conserve l'empreinte
du pack avant exécution ; aucun appel de modèle et aucune réparation du pack.

Ce résultat qualifie l'artefact. Il ne devient pas rétroactivement une preuve
que l'agent natif avait effectué les deux applications demandées.
