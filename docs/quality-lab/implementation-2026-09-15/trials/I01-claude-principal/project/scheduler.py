"""Ordonnancement en lecture seule : expose les tâches pending prêtes à être prises."""

_STATUSES = frozenset(('pending', 'running', 'received'))
_LOCK_MODES = frozenset(('read', 'write'))


def _index(tasks):
    """Valide le graphe et renvoie {id: tâche} sans toucher aux entrées."""
    by_id = {}
    for task in tasks:
        identifier = task['id']
        if identifier in by_id:
            raise ValueError('identifiant dupliqué : ' + identifier)
        if task['status'] not in _STATUSES:
            raise ValueError('statut inconnu : ' + str(task['status']))
        by_id[identifier] = task
    for task in tasks:
        for dep in task['deps']:
            if dep not in by_id:
                raise ValueError('dépendance absente : ' + str(dep) + ' requise par ' + task['id'])
    return by_id


def _reject_cycles(by_id):
    """Parcours en profondeur itératif sur tout le graphe, composantes non pending incluses."""
    WHITE, GREY, BLACK = 0, 1, 2
    colour = dict.fromkeys(by_id, WHITE)
    for root in by_id:
        if colour[root] != WHITE:
            continue
        stack = [(root, iter(by_id[root]['deps']))]
        colour[root] = GREY
        while stack:
            node, deps = stack[-1]
            advanced = False
            for dep in deps:
                if colour[dep] == GREY:
                    raise ValueError('cycle de dépendances passant par : ' + dep)
                if colour[dep] == WHITE:
                    colour[dep] = GREY
                    stack.append((dep, iter(by_id[dep]['deps'])))
                    advanced = True
                    break
            if not advanced:
                colour[node] = BLACK
                stack.pop()


def _satisfied(identifier, by_id, cache):
    """Toutes les dépendances transitives sont-elles reçues avec une preuve à jour ?

    Parcours post-ordre itératif : le graphe est acyclique à ce stade, et chaque
    tâche visitée est mémorisée pour être réutilisée par ses autres descendantes.
    """
    stack = [(identifier, False)]
    while stack:
        node, expanded = stack.pop()
        if node in cache:
            continue
        if expanded:
            cache[node] = all(
                by_id[dep]['status'] == 'received'
                and by_id[dep]['proof_current']
                and cache[dep]
                for dep in by_id[node]['deps']
            )
            continue
        stack.append((node, True))
        for dep in by_id[node]['deps']:
            if dep not in cache:
                stack.append((dep, False))
    return cache[identifier]


def _lock_free(task, active_locks):
    """Écrire exige une ressource libre ; lire ne bute que sur un verrou write."""
    for resource in task['writes']:
        if resource in active_locks:
            return False
    for resource in task['reads']:
        if active_locks.get(resource) == 'write':
            return False
    return True


def ready(tasks, active_locks):
    """Return ready pending task ids without claiming or changing tasks."""
    for mode in active_locks.values():
        if mode not in _LOCK_MODES:
            raise ValueError('mode de verrou inconnu : ' + str(mode))
    by_id = _index(tasks)
    _reject_cycles(by_id)
    cache = {}
    return sorted(
        identifier
        for identifier, task in by_id.items()
        if task['status'] == 'pending'
        and _satisfied(identifier, by_id, cache)
        and _lock_free(task, active_locks)
    )
