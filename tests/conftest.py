"""Shared pytest fixtures and configuration."""

import pytest

from src.challenges.factory import ChallengeFactory


@pytest.fixture(autouse=True)
def restore_challenge_registry():
    """Save and restore the ChallengeFactory registry around every test.

    Prevents tests that call clear_registry() or register custom types from
    polluting the global registry state for subsequent tests.
    """
    saved = ChallengeFactory._challenge_types.copy()
    yield
    ChallengeFactory._challenge_types = saved
