#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Check if we're on PythonAnywhere
    if 'PYTHONANYWHERE_SITE' in os.environ:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hangout_streak.settings_prod')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hangout_streak.settings_dev')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
