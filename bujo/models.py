"""Modèles : états des tâches et entrées du journal."""

import logging
from abc import ABC, abstractmethod
from datetime import date, datetime, time
from enum import Enum

from bujo.exceptions import (
    EmptyNameError,
    InvalidDateError,
    InvalidTransitionError,
)

logger = logging.getLogger(__name__)


class TaskState(Enum):
    """États possibles d'une tâche."""

    TODO = "a_faire"
    DONE = "terminee"
    MIGRATED = "migree"
    SCHEDULED = "planifiee"
    ABANDONED = "abandonnee"


# Légende : symbole du rapid logging pour chaque état de tâche.
TASK_SYMBOLS = {
    TaskState.TODO: "•",
    TaskState.DONE: "×",
    TaskState.MIGRATED: ">",
    TaskState.SCHEDULED: "<",
    TaskState.ABANDONED: "~",
}


class Entry(ABC):
    """Entrée de base du journal (classe abstraite)."""

    def __init__(self, entry_id: int, name: str, description: str = "",
                 log_date: date | None = None) -> None:
        """Crée une entrée ; lève EmptyNameError si le nom est vide."""
        if name.strip() == "":
            logger.error("Création refusée : nom d'entrée vide")
            raise EmptyNameError("Le nom d'une entrée ne peut pas être vide")
        self.id = entry_id
        self.name = name.strip()
        self.description = description
        self.created_at = datetime.now()
        self.log_date = log_date if log_date is not None else date.today()

    @abstractmethod
    def symbol(self) -> str:
        """Retourne le symbole du rapid logging de l'entrée."""

    def __str__(self) -> str:
        """Retourne l'entrée sous la forme « symbole nom »."""
        return f"{self.symbol()} {self.name}"


class Task(Entry):
    """Tâche à accomplir, avec un état."""

    def __init__(self, entry_id: int, name: str, description: str = "",
                 log_date: date | None = None,
                 origin_id: int | None = None) -> None:
        """Crée une tâche à l'état « à faire »."""
        super().__init__(entry_id, name, description, log_date)
        self._state = TaskState.TODO
        self.origin_id = origin_id

    @property
    def state(self) -> TaskState:
        """Retourne l'état courant de la tâche (lecture seule)."""
        return self._state

    def symbol(self) -> str:
        """Retourne le symbole correspondant à l'état de la tâche."""
        return TASK_SYMBOLS[self._state]

    def complete(self) -> None:
        """Termine la tâche (seulement si elle est à faire)."""
        self._change_state(TaskState.DONE)

    def abandon(self) -> None:
        """Abandonne la tâche (seulement si elle est à faire)."""
        self._change_state(TaskState.ABANDONED)

    def _change_state(self, new_state: TaskState) -> None:
        """Change l'état ; lève InvalidTransitionError si c'est interdit."""
        if self._state != TaskState.TODO:
            logger.error("Transition interdite pour la tâche %d : %s -> %s",
                         self.id, self._state.value, new_state.value)
            raise InvalidTransitionError(
                f"Impossible de passer de {self._state.value} "
                f"à {new_state.value}"
            )
        logger.info("Tâche %d : %s -> %s",
                    self.id, self._state.value, new_state.value)
        self._state = new_state


class Event(Entry):
    """Événement qui a lieu à une date, et éventuellement à une heure."""

    def __init__(self, entry_id: int, name: str, event_date: date,
                 description: str = "", event_time: time | None = None,
                 log_date: date | None = None) -> None:
        """Crée un événement ; lève InvalidDateError si la date est fausse."""
        super().__init__(entry_id, name, description, log_date)
        if not isinstance(event_date, date):
            logger.error("Création refusée : date d'événement invalide (%r)",
                         event_date)
            raise InvalidDateError(
                "La date de l'événement doit être de type date"
            )
        self.event_date = event_date
        self.event_time = event_time

    def symbol(self) -> str:
        """Retourne le symbole d'un événement."""
        return "○"


class Note(Entry):
    """Note : une information à retenir, sans action ni date."""

    def symbol(self) -> str:
        """Retourne le symbole d'une note."""
        return "-"
