"""Tests des exceptions personnalisées."""

import pytest

from bujo.exceptions import (
    BujoError,
    EmptyNameError,
    EntryNotFoundError,
    InvalidDateError,
    InvalidSignifierError,
    InvalidTransitionError,
    LogNotFoundError,
)

TOUTES_LES_EXCEPTIONS = [
    EntryNotFoundError,
    EmptyNameError,
    InvalidDateError,
    InvalidTransitionError,
    LogNotFoundError,
    InvalidSignifierError,
]


def test_exceptions_derivent_de_bujo_error():
    """Chaque exception du projet peut être rattrapée via BujoError."""
    for exception_class in TOUTES_LES_EXCEPTIONS:
        with pytest.raises(BujoError):
            raise exception_class("message")


def test_message_conserve():
    """Le message passé à l'exception est bien conservé."""
    with pytest.raises(EmptyNameError) as info:
        raise EmptyNameError("nom vide")
    assert str(info.value) == "nom vide"
