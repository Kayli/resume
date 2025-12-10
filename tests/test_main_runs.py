import pytest


def test_main_runs_without_exception():
    """Ensure `main.main()` runs end-to-end without throwing when dependencies
    are patched. This prevents regressions where `main` expects dicts but
    code now returns DTOs.
    """
    # Run the real main to ensure it executes without raising.
    import main as app_main
    app_main.main()
