_VALID_STATUSES = {'pending', 'running', 'received'}
_VALID_LOCK_MODES = {'read', 'write'}


def ready(tasks, active_locks):
    """Return ready pending task ids without claiming or changing tasks."""
    by_id = {}
    for task in tasks:
        task_id = task['id']
        if task_id in by_id:
            raise ValueError(f'duplicate task id: {task_id}')
        by_id[task_id] = task

    for task in tasks:
        if task['status'] not in _VALID_STATUSES:
            raise ValueError(f'unknown status: {task["status"]}')
        for dep_id in task['deps']:
            if dep_id not in by_id:
                raise ValueError(f'missing dependency: {dep_id}')

    for mode in active_locks.values():
        if mode not in _VALID_LOCK_MODES:
            raise ValueError(f'unknown lock mode: {mode}')

    _check_no_cycles(by_id)

    result = []
    for task in tasks:
        if task['status'] != 'pending':
            continue
        if not _deps_satisfied(task, by_id):
            continue
        if _blocked_by_locks(task, active_locks):
            continue
        result.append(task['id'])

    return sorted(result)


def _check_no_cycles(by_id):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {task_id: WHITE for task_id in by_id}

    def visit(task_id):
        color[task_id] = GRAY
        for dep_id in by_id[task_id]['deps']:
            if color[dep_id] == GRAY:
                raise ValueError('cycle detected in dependencies')
            if color[dep_id] == WHITE:
                visit(dep_id)
        color[task_id] = BLACK

    for task_id in by_id:
        if color[task_id] == WHITE:
            visit(task_id)


def _deps_satisfied(task, by_id):
    seen = set()
    stack = list(task['deps'])
    while stack:
        dep_id = stack.pop()
        if dep_id in seen:
            continue
        seen.add(dep_id)
        dep = by_id[dep_id]
        if dep['status'] != 'received' or not dep['proof_current']:
            return False
        stack.extend(dep['deps'])
    return True


def _blocked_by_locks(task, active_locks):
    for resource in task['writes']:
        if resource in active_locks:
            return True
    for resource in task['reads']:
        if active_locks.get(resource) == 'write':
            return True
    return False
