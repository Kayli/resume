"""doit tasks for this repository.

task_test: run mypy then pytest using the project's .venv python.
"""

def task_install():
    """Create .venv if missing and install requirements into it.

    This task is idempotent: it will run pip install when invoked. It marks
    the `.venv` directory as a target so doit can skip it when present.
    """
    return {
        'actions': [
            'python3 -m venv .venv || python -m venv .venv',
            '.venv/bin/python -m pip install --upgrade pip',
            '.venv/bin/pip install -r requirements.txt',
        ],
        'targets': ['.venv'],
        'uptodate': [False],
        'verbosity': 2,
        'doc': 'Create .venv and install requirements'
    }


def task_test():
    """Run static type checks (mypy) then unit tests (pytest).

    Depends on `install` so the virtual environment and tools are available.
    """
    return {
        'actions': [
            '.venv/bin/python -m mypy .',
            '.venv/bin/python -m pytest -q',
        ],
        'task_dep': ['install'],
        'verbosity': 2,
        'doc': 'Run mypy then pytest (uses .venv python)'
    }


def task_main():
    """Run main which will generate the resume PDF using the project's .venv.
    Named `main` to avoid colliding with doit's builtin `run` command.
    """
    return {
        'actions': [
            '.venv/bin/python main.py',
        ],
        'task_dep': ['install'],
        'verbosity': 2,
        'doc': 'Generate the resume PDF'
    }
