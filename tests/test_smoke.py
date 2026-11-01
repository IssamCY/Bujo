"""Test de fumée : vérifie que le package s'importe."""

import bujo


def test_package_importable():
    """Le package bujo doit pouvoir être importé."""
    assert bujo is not None
