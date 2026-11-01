"""Tests du journal (niveau 1)."""

from datetime import date

import pytest

from bujo.exceptions import (
    EmptyNameError,
    EntryNotFoundError,
    InvalidTransitionError,
)
from bujo.journal import Journal
from bujo.models import TaskState


def test_identifiants_uniques_et_croissants():
    """Chaque entrée reçoit un identifiant différent, à partir de 1."""
    journal = Journal()
    tache = journal.add_task("Courses")
    note = journal.add_note("Idée")
    evenement = journal.add_event("Partiel", date(2026, 12, 10))
    assert [tache.id, note.id, evenement.id] == [1, 2, 3]


def test_deux_taches_meme_nom_ids_differents():
    """Deux tâches de même nom restent distinctes grâce à l'id."""
    journal = Journal()
    premiere = journal.add_task("Appeler Paul")
    seconde = journal.add_task("Appeler Paul")
    assert premiere.id != seconde.id


def test_get_entry_retourne_l_entree():
    """get_entry retrouve l'entrée par son identifiant."""
    journal = Journal()
    tache = journal.add_task("Courses")
    assert journal.get_entry(tache.id) is tache


def test_get_entry_inconnue():
    """Un identifiant inconnu lève EntryNotFoundError."""
    journal = Journal()
    with pytest.raises(EntryNotFoundError):
        journal.get_entry(42)


def test_complete_task():
    """complete_task termine la tâche."""
    journal = Journal()
    tache = journal.add_task("Courses")
    journal.complete_task(tache.id)
    assert tache.state == TaskState.DONE


def test_abandon_task():
    """abandon_task abandonne la tâche."""
    journal = Journal()
    tache = journal.add_task("Courses")
    journal.abandon_task(tache.id)
    assert tache.state == TaskState.ABANDONED


def test_complete_task_deux_fois():
    """Terminer deux fois une tâche lève InvalidTransitionError."""
    journal = Journal()
    tache = journal.add_task("Courses")
    journal.complete_task(tache.id)
    with pytest.raises(InvalidTransitionError):
        journal.complete_task(tache.id)


def test_complete_task_id_inconnu():
    """Terminer une tâche inexistante lève EntryNotFoundError."""
    journal = Journal()
    with pytest.raises(EntryNotFoundError):
        journal.complete_task(42)


def test_complete_task_sur_une_note():
    """Une note n'est pas une tâche : l'opération est refusée."""
    journal = Journal()
    note = journal.add_note("Idée")
    with pytest.raises(EntryNotFoundError):
        journal.complete_task(note.id)


def test_delete_entry():
    """Une entrée supprimée n'est plus retrouvable."""
    journal = Journal()
    tache = journal.add_task("Courses")
    journal.delete_entry(tache.id)
    with pytest.raises(EntryNotFoundError):
        journal.get_entry(tache.id)


def test_delete_entry_inconnue():
    """Supprimer une entrée inexistante lève EntryNotFoundError."""
    journal = Journal()
    with pytest.raises(EntryNotFoundError):
        journal.delete_entry(42)


def test_id_non_reutilise_apres_suppression():
    """Un identifiant supprimé n'est jamais réattribué."""
    journal = Journal()
    premiere = journal.add_task("A")
    journal.delete_entry(premiere.id)
    seconde = journal.add_task("B")
    assert seconde.id == 2


def test_nom_vide_ne_consomme_pas_d_id():
    """Un ajout refusé ne fait pas avancer le compteur."""
    journal = Journal()
    with pytest.raises(EmptyNameError):
        journal.add_task("")
    assert journal.add_task("Courses").id == 1


def test_pending_tasks():
    """pending_tasks ne retourne que les tâches à faire."""
    journal = Journal()
    terminee = journal.add_task("Terminée")
    abandonnee = journal.add_task("Abandonnée")
    restante = journal.add_task("Restante")
    journal.add_note("Une note")
    journal.complete_task(terminee.id)
    journal.abandon_task(abandonnee.id)
    assert journal.pending_tasks() == [restante]
