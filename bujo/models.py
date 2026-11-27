"""Modèles : états des tâches et entrées du journal."""

import logging
from abc import ABC, abstractmethod
from datetime import date, datetime, time
from enum import Enum

from bujo.exceptions import (
    EmptyNameError,
    InvalidDateError,
    InvalidSignifierError,
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


class Signifier(Enum):
    """Signifiants : marques ajoutées devant le symbole d'une entrée."""

    PRIORITY = "priorite"
    IDEA = "idee"


# Légende : symbole du rapid logging pour chaque signifiant.
SIGNIFIER_SYMBOLS = {
    Signifier.PRIORITY: "*",
    Signifier.IDEA: "!",
}


class Entry(ABC):
    """Entrée de base du journal (classe abstraite)."""

    def __init__(self, entry_id: int, name: str, description: str = "",
                 log_date: date | None = None,
                 signifier: Signifier | None = None) -> None:
        """Crée une entrée.

        Lève EmptyNameError si le nom est vide, InvalidDateError si
        log_date n'est pas une date et InvalidSignifierError si le
        signifiant n'existe pas.
        """
        if name.strip() == "":
            logger.error("Création refusée : nom d'entrée vide")
            raise EmptyNameError("Le nom d'une entrée ne peut pas être vide")
        self.id = entry_id
        self.name = name.strip()
        self.description = description
        self.created_at = datetime.now()
        self.log_date = self._check_log_date(log_date)
        self._signifier: Signifier | None = None
        self.signifier = signifier

    @staticmethod
    def _check_log_date(log_date: date | None) -> date:
        """Retourne une date sans heure ; aujourd'hui si rien n'est donné."""
        if log_date is None:
            return date.today()
        if not isinstance(log_date, date):
            logger.error("Création refusée : date de log invalide (%r)",
                         log_date)
            raise InvalidDateError("La date du log doit être de type date")
        # Un datetime est aussi un date : on retire l'heure pour que deux
        # entrées du même jour tombent dans le même Daily Log.
        if isinstance(log_date, datetime):
            return log_date.date()
        return log_date

    @property
    def signifier(self) -> Signifier | None:
        """Retourne le signifiant de l'entrée (None s'il n'y en a pas)."""
        return self._signifier

    @signifier.setter
    def signifier(self, value: Signifier | None) -> None:
        """Change le signifiant ; None le retire."""
        if value is not None and not isinstance(value, Signifier):
            logger.error("Signifiant refusé : %r", value)
            raise InvalidSignifierError(
                "Le signifiant doit être Signifier.PRIORITY, "
                "Signifier.IDEA ou None"
            )
        self._signifier = value

    @abstractmethod
    def symbol(self) -> str:
        """Retourne le symbole du rapid logging de l'entrée."""

    def label(self) -> str:
        """Retourne « [signifiant] symbole nom », par exemple « * • Nom »."""
        if self._signifier is None:
            return f"{self.symbol()} {self.name}"
        mark = SIGNIFIER_SYMBOLS[self._signifier]
        return f"{mark} {self.symbol()} {self.name}"

    def __str__(self) -> str:
        """Retourne l'entrée en rapid logging (voir label)."""
        return self.label()


class Task(Entry):
    """Tâche à accomplir, avec un état."""

    def __init__(self, entry_id: int, name: str, description: str = "",
                 log_date: date | None = None,
                 origin_id: int | None = None,
                 signifier: Signifier | None = None) -> None:
        """Crée une tâche à l'état « à faire ».

        origin_id est l'identifiant de la tâche dont celle-ci est la
        copie après une migration ou une planification (None sinon).
        """
        super().__init__(entry_id, name, description, log_date, signifier)
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

    def migrate(self) -> None:
        """Marque la tâche comme migrée (seulement si elle est à faire)."""
        self._change_state(TaskState.MIGRATED)

    def schedule(self) -> None:
        """Marque la tâche comme planifiée (seulement si elle est à faire)."""
        self._change_state(TaskState.SCHEDULED)

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
                 log_date: date | None = None,
                 signifier: Signifier | None = None) -> None:
        """Crée un événement ; lève InvalidDateError si la date est fausse."""
        super().__init__(entry_id, name, description, log_date, signifier)
        if not isinstance(event_date, date):
            logger.error("Création refusée : date d'événement invalide (%r)",
                         event_date)
            raise InvalidDateError(
                "La date de l'événement doit être de type date"
            )
        if isinstance(event_date, datetime):
            event_date = event_date.date()
        self.event_date = event_date
        self.event_time = event_time

    def symbol(self) -> str:
        """Retourne le symbole d'un événement."""
        return "○"

    def time_text(self) -> str:
        """Retourne « à HH:MM » si l'événement a une heure, sinon rien."""
        if self.event_time is None:
            return ""
        return f" à {self.event_time:%H:%M}"

    def __str__(self) -> str:
        """Retourne l'événement avec son heure, et sa date si elle diffère.

        La date n'est rappelée que si l'événement n'a pas lieu le jour
        du log où il est écrit.
        """
        text = f"{self.label()}{self.time_text()}"
        if self.event_date != self.log_date:
            text += f" le {self.event_date:%d/%m/%Y}"
        return text


class Note(Entry):
    """Note : une information à retenir, sans action ni date."""

    def symbol(self) -> str:
        """Retourne le symbole d'une note."""
        return "-"
