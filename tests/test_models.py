"""Tests des modèles (niveau 1)."""

from datetime import date

import pytest

from bujo.exceptions import (
    EmptyNameError,
    InvalidDateError,
    InvalidTransitionError,
)
from bujo.models import Entry, Event, Note, Task, TaskState


def test_entry_est_abstraite():
    """On ne peut pas créer directement une Entry."""
    with pytest.raises(TypeError):
        Entry(1, "Test")


def test_nom_vide_refuse():
    """Un nom vide ou fait d'espaces lève EmptyNameError."""
    with pytest.raises(EmptyNameError):
        Task(1, "   ")


def test_tache_creee_a_faire():
    """Une nouvelle tâche est à faire, avec le symbole •."""
    tache = Task(1, "Courses", "Lait, pain")
    assert tache.state == TaskState.TODO
    assert tache.symbol() == "•"
    assert str(tache) == "• Courses"


def test_complete_termine_la_tache():
    """complete() fait passer la tâche à DONE."""
    tache = Task(1, "Courses")
    tache.complete()
    assert tache.state == TaskState.DONE
    assert tache.symbol() == "×"


def test_abandon_abandonne_la_tache():
    """abandon() fait passer la tâche à ABANDONED."""
    tache = Task(1, "Rénover la cuisine")
    tache.abandon()
    assert tache.state == TaskState.ABANDONED


def test_transition_interdite():
    """Terminer une tâche abandonnée est interdit et ne change rien."""
    tache = Task(1, "Courses")
    tache.abandon()
    with pytest.raises(InvalidTransitionError):
        tache.complete()
    assert tache.state == TaskState.ABANDONED


def test_double_complete_interdit():
    """Terminer deux fois la même tâche est interdit."""
    tache = Task(1, "Courses")
    tache.complete()
    with pytest.raises(InvalidTransitionError):
        tache.complete()


def test_state_en_lecture_seule():
    """On ne peut pas modifier state directement (encapsulation)."""
    tache = Task(1, "Courses")
    with pytest.raises(AttributeError):
        tache.state = TaskState.DONE


def test_evenement_valide():
    """Un événement garde sa date et a le symbole ○."""
    evenement = Event(1, "Partiel", date(2026, 12, 10))
    assert evenement.event_date == date(2026, 12, 10)
    assert evenement.event_time is None
    assert evenement.symbol() == "○"


def test_evenement_date_invalide():
    """Une date qui n'est pas de type date lève InvalidDateError."""
    with pytest.raises(InvalidDateError):
        Event(1, "Partiel", "2026-12-10")


def test_note_symbole():
    """Une note a le symbole -."""
    note = Note(1, "Idée", "Faire un jeu")
    assert note.symbol() == "-"
    assert str(note) == "- Idée"
