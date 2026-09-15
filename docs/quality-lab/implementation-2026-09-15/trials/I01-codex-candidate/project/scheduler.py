def ready(tasks, active_locks):
    """Return ready pending task ids without claiming or changing tasks."""
    by_id = {}
    for task in tasks:
        task_id = task['id']
        if task_id in by_id:
            raise ValueError('duplicate task id: %s' % task_id)
        if task['status'] not in {'pending', 'running', 'received'}:
            raise ValueError('unknown task status: %s' % task['status'])
        by_id[task_id] = task

    for task in tasks:
        for dependency in task['deps']:
            if dependency not in by_id:
                raise ValueError('missing dependency: %s' % dependency)

    for mode in active_locks.values():
        if mode not in {'read', 'write'}:
            raise ValueError('unknown lock mode: %s' % mode)

    # Validate the complete graph, rather than only the pending portion.
    visiting = set()
    visited = set()

    def visit(task_id):
        if task_id in visiting:
            raise ValueError('dependency cycle detected')
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in by_id[task_id]['deps']:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in by_id:
        visit(task_id)

    current_cache = {}

    def dependency_is_current(task_id):
        """Whether this task and its entire prerequisite chain is current."""
        if task_id not in current_cache:
            task = by_id[task_id]
            current_cache[task_id] = (
                task['status'] == 'received'
                and task['proof_current']
                and all(dependency_is_current(dep) for dep in task['deps'])
            )
        return current_cache[task_id]

    def conflicts_with_lock(task):
        return (
            any(resource in active_locks for resource in task['writes'])
            or any(active_locks.get(resource) == 'write' for resource in task['reads'])
        )

    return sorted(
        task_id
        for task_id, task in by_id.items()
        if task['status'] == 'pending'
        and all(dependency_is_current(dep) for dep in task['deps'])
        and not conflicts_with_lock(task)
    )
