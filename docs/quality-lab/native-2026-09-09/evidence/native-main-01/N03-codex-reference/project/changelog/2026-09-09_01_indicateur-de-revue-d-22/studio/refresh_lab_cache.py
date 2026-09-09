"""Maintenance du banc seulement, exécutée par /bridge/labctl shell."""

# En 19.0 ici, ir.model.access invalide 'stable' alors que _get_allowed_models
# utilise le cache par défaut. Invalider les caches, sans modifier les droits.
env.registry.clear_cache()
env.registry.signal_changes()
env.cr.commit()
print('D22_CACHE_REFRESHED')
