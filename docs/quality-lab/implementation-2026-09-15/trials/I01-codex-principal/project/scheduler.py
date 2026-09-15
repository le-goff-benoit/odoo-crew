def ready(tasks, active_locks):
    """Return ready pending task ids without claiming or changing tasks."""
    by_id = {}
    for task in tasks:
        task_id = task['id']
        if task_id in by_id:
            raise ValueError(f'Duplicate task id: {task_id}')
        if task['status'] not in ('pending', 'running', 'received'):
            raise ValueError(f"Unknown task status: {task['status']}")
        by_id[task_id] = task

    for mode in active_locks.values():
        if mode not in ('read', 'write'):
            raise ValueError(f'Unknown lock mode: {mode}')

    dependents = {task_id: [] for task_id in by_id}
    remaining = {}
    for task_id, task in by_id.items():
        remaining[task_id] = len(task['deps'])
        for dep in task['deps']:
            if dep not in by_id:
                raise ValueError(f'Missing dependency: {dep}')
            dependents[dep].append(task_id)

    # Process dependencies first, without recursion or changes to input lists.
    queue = [task_id for task_id, count in remaining.items() if count == 0]
    dependencies_current = dict.fromkeys(by_id, True)
    processed = 0
    while queue:
        task_id = queue.pop()
        task = by_id[task_id]
        processed += 1
        current = (dependencies_current[task_id]
                   and task['status'] == 'received' and task['proof_current'])
        for child in dependents[task_id]:
            dependencies_current[child] &= current
            remaining[child] -= 1
            if remaining[child] == 0:
                queue.append(child)

    if processed != len(by_id):
        raise ValueError('Dependency cycle')

    return sorted(
        task_id for task_id, task in by_id.items()
        if task['status'] == 'pending' and dependencies_current[task_id]
        and not any(resource in active_locks for resource in task['writes'])
        and not any(active_locks.get(resource) == 'write'
                    for resource in task['reads'])
    )
