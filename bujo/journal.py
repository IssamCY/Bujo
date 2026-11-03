"""Journal : gestion des entrées (niveau 1)."""

import logging
from datetime import date, time

from bujo.exceptions import EntryNotFoundError
from bujo.models import Entry, Event, Note, Task, TaskState

logger = logging.getLogger(__name__)


class Journal:
    """Journal qui range les entrées et les retrouve par identifiant."""

    def __init__(self) -> None:
        """Crée un journal vide."""
        self._entries: dict[int, Entry] = {}
        self._next_id = 1

    def add_task(self, name: str, description: str = "",
                 log_date: date | None = None) -> Task:
        """Ajoute une tâche à faire et la retourne."""
        task = Task(self._next_id, name, description, log_date)
        self._register(task)
        return task

    def add_event(self, name: str, event_date: date, description: str = "",
                  event_time: time | None = None,
                  log_date: date | None = None) -> Event:
        """Ajoute un événement et le retourne."""
        event = Event(self._next_id, name, event_date, description,
                      event_time, log_date)
        self._register(event)
        return event

    def add_note(self, name: str, description: str = "",
                 log_date: date | None = None) -> Note:
        """Ajoute une note et la retourne."""
        note = Note(self._next_id, name, description, log_date)
        self._register(note)
        return note

    def get_entry(self, entry_id: int) -> Entry:
        """Retourne l'entrée ; lève EntryNotFoundError si elle n'existe pas."""
        if entry_id not in self._entries:
            logger.error("Entrée introuvable : id=%d", entry_id)
            raise EntryNotFoundError(
                f"Aucune entrée avec l'identifiant {entry_id}"
            )
        return self._entries[entry_id]

    def complete_task(self, entry_id: int) -> None:
        """Termine la tâche correspondant à l'identifiant."""
        self._get_task(entry_id).complete()

    def abandon_task(self, entry_id: int) -> None:
        """Abandonne la tâche correspondant à l'identifiant."""
        self._get_task(entry_id).abandon()

    def delete_entry(self, entry_id: int) -> None:
        """Supprime l'entrée ; lève EntryNotFoundError si elle n'existe pas."""
        self.get_entry(entry_id)
        del self._entries[entry_id]
        logger.info("Entrée supprimée : id=%d", entry_id)

    def pending_tasks(self) -> list[Task]:
        """Retourne les tâches à faire, dans l'ordre de création."""
        pending = []
        for entry in self._entries.values():
            if isinstance(entry, Task) and entry.state == TaskState.TODO:
                pending.append(entry)
        logger.debug("%d tâche(s) à faire", len(pending))
        return pending

    def _register(self, entry: Entry) -> None:
        """Range l'entrée et prépare l'identifiant suivant."""
        self._entries[entry.id] = entry
        self._next_id += 1
        logger.info("Entrée ajoutée : id=%d, type=%s, nom=%s",
                    entry.id, type(entry).__name__, entry.name)

    def _get_task(self, entry_id: int) -> Task:
        """Retourne la tâche ; lève EntryNotFoundError si ce n'en est pas."""
        entry = self.get_entry(entry_id)
        if not isinstance(entry, Task):
            logger.error("L'entrée %d n'est pas une tâche", entry_id)
            raise EntryNotFoundError(
                f"L'entrée {entry_id} n'est pas une tâche"
            )
        return entry
