#!/usr/bin/env python3
"""Ancien point d'entrée email, neutralisé après retrait de la fonctionnalité."""
import sys

REMOVED = "Fonctionnalité email retirée. Aucun envoi, connexion ou accès aux données."


def config_for(project):
    """Anciennes fenêtres Tricorder : fonctionnalité désactivée, aucun fichier lu."""
    return {'enabled': False}


def status(release):
    """Compatibilité de lecture seulement ; les anciens brouillons restent intacts."""
    return {'enabled': False, 'status': 'not_prepared'}


def main():
    # Refuse even legacy invocations; never parse secrets or access private state.
    print(REMOVED, file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
