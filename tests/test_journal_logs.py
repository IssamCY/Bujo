"""Tests des messages de log émis par le journal et les modèles."""

import logging

import pytest

from bujo.exceptions import (
    EmptyNameError,
    EntryNotFoundError,
    InvalidTransitionError,
)
from bujo.journal import Journal


def test_ajout_logue_en_info(caplog):
    """Ajouter une entrée produit un message INFO."""
    journal = Journal()
    with caplog.at_level(logging.INFO, logger="bujo"):
        journal.add_task("Courses")
    assert "Entrée ajoutée" in caplog.text
    assert caplog.records[0].levelname == "INFO"


def test_suppression_logue_en_info(caplog):
    """Supprimer une entrée produit un message INFO."""
    journal = Journal()
    tache = journal.add_task("Courses")
    with caplog.at_level(logging.INFO, logger="bujo"):
        journal.delete_entry(tache.id)
    assert "Entrée supprimée" in caplog.text


def test_entree_introuvable_logue_en_error(caplog):
    """Un identifiant inconnu produit un message ERROR."""
    journal = Journal()
    with caplog.at_level(logging.ERROR, logger="bujo"):
        with pytest.raises(EntryNotFoundError):
            journal.get_entry(42)
    assert "Entrée introuvable" in caplog.text
    assert caplog.records[0].levelname == "ERROR"


def test_transition_interdite_logue_en_error(caplog):
    """Terminer deux fois une tâche produit un message ERROR."""
    journal = Journal()
    tache = journal.add_task("Courses")
    journal.complete_task(tache.id)
    with caplog.at_level(logging.ERROR, logger="bujo"):
        with pytest.raises(InvalidTransitionError):
            journal.complete_task(tache.id)
    assert "Transition interdite" in caplog.text


def test_nom_vide_logue_en_error(caplog):
    """Un nom vide produit un message ERROR."""
    journal = Journal()
    with caplog.at_level(logging.ERROR, logger="bujo"):
        with pytest.raises(EmptyNameError):
            journal.add_task("   ")
    assert "nom d'entrée vide" in caplog.text


def test_fonctionnement_normal_sans_erreur(caplog):
    """Un usage normal ne produit aucun message ERROR."""
    journal = Journal()
    with caplog.at_level(logging.DEBUG, logger="bujo"):
        tache = journal.add_task("Courses")
        journal.complete_task(tache.id)
        journal.pending_tasks()
    niveaux = [record.levelname for record in caplog.records]
    assert "ERROR" not in niveaux
