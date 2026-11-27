"""Pages du journal : Daily Logs et Monthly Logs (niveau 2)."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import date, datetime, time

from bujo.exceptions import InvalidDateError
from bujo.models import Entry, Event, Task, TaskState

logger = logging.getLogger(__name__)

MONTH_NAMES = (
    "janvier", "février", "mars", "avril", "mai", "juin", "juillet",
    "août", "septembre", "octobre", "novembre", "décembre",
)
DAY_NAMES = (
    "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche",
)
DAY_ABBREVIATIONS = ("lun", "mar", "mer", "jeu", "ven", "sam", "dim")

NO_ENTRY_TEXT = "(aucune entrée)"


def to_day(value: date) -> date:
    """Retourne un jour sans heure ; lève InvalidDateError sinon."""
    if not isinstance(value, date):
        logger.error("Date refusée : %r n'est pas une date", value)
        raise InvalidDateError(f"{value!r} n'est pas une date")
    # Un datetime est aussi un date : on retire l'heure.
    if isinstance(value, datetime):
        return value.date()
    return value


def month_start(value: date) -> date:
    """Retourne le premier jour du mois de la date donnée."""
    return to_day(value).replace(day=1)


def next_month(value: date) -> date:
    """Retourne le premier jour du mois qui suit celui de la date donnée."""
    first = month_start(value)
    if first.month == 12:
        return date(first.year + 1, 1, 1)
    return date(first.year, first.month + 1, 1)


class Log(ABC):
    """Page du journal (classe abstraite) : un ensemble d'entrées ordonnées.

    Les entrées sont gardées dans l'ordre où elles ont été écrites, comme
    sur une page de Bullet Journal remplie « au fil de l'eau ».
    """

    def __init__(self) -> None:
        """Crée une page vide."""
        self._entries: dict[int, Entry] = {}

    @property
    def entries(self) -> tuple[Entry, ...]:
        """Retourne les entrées de la page, dans l'ordre d'écriture."""
        return tuple(self._entries.values())

    def add(self, entry: Entry) -> None:
        """Écrit l'entrée à la suite de la page."""
        self._entries[entry.id] = entry

    def remove(self, entry_id: int) -> None:
        """Retire l'entrée de la page (sans effet si elle n'y est pas)."""
        self._entries.pop(entry_id, None)

    def tasks(self) -> list[Task]:
        """Retourne les tâches de la page, quel que soit leur état."""
        return [e for e in self._entries.values() if isinstance(e, Task)]

    def pending_tasks(self) -> list[Task]:
        """Retourne les tâches de la page qui sont encore à faire."""
        return [t for t in self.tasks() if t.state == TaskState.TODO]

    def __len__(self) -> int:
        """Retourne le nombre d'entrées de la page."""
        return len(self._entries)

    def __contains__(self, entry_id: object) -> bool:
        """Indique si l'entrée portant cet identifiant est sur la page."""
        return entry_id in self._entries

    @abstractmethod
    def title(self) -> str:
        """Retourne le titre de la page."""

    def render(self) -> str:
        """Retourne la page en rapid logging (une entrée par ligne)."""
        title = self.title()
        lines = [title, "=" * len(title)]
        if self._entries:
            lines.extend(str(entry) for entry in self._entries.values())
        else:
            lines.append(NO_ENTRY_TEXT)
        return "\n".join(lines)


class DailyLog(Log):
    """Journal d'un jour : entrées courtes, ajoutées au fil de l'eau."""

    def __init__(self, day: date) -> None:
        """Crée le Daily Log du jour donné (vide)."""
        super().__init__()
        self._day = to_day(day)

    @property
    def day(self) -> date:
        """Retourne le jour du log."""
        return self._day

    def title(self) -> str:
        """Retourne le titre, par exemple « Jeudi 26 novembre 2026 »."""
        day_name = DAY_NAMES[self._day.weekday()].capitalize()
        month_name = MONTH_NAMES[self._day.month - 1]
        return f"{day_name} {self._day.day} {month_name} {self._day.year}"


class MonthlyLog(Log):
    """Journal d'un mois : calendrier des événements et tâches du mois.

    Les entrées stockées dans la page sont les tâches du mois. Le
    calendrier, lui, est fourni au moment de l'affichage (voir render) :
    il est formé des événements dont la date tombe dans le mois.
    """

    def __init__(self, month: date) -> None:
        """Crée le Monthly Log du mois contenant la date donnée (vide)."""
        super().__init__()
        self._month = month_start(month)

    @property
    def month(self) -> date:
        """Retourne le premier jour du mois du log."""
        return self._month

    def title(self) -> str:
        """Retourne le titre, par exemple « Décembre 2026 »."""
        month_name = MONTH_NAMES[self._month.month - 1].capitalize()
        return f"{month_name} {self._month.year}"

    def calendar(self, events: Iterable[Event]) -> list[Event]:
        """Retourne les événements du mois, triés par date puis par heure.

        Un événement sans heure passe avant ceux de la même journée qui
        en ont une.
        """
        in_month = [e for e in events
                    if month_start(e.event_date) == self._month]
        return sorted(in_month,
                      key=lambda e: (e.event_date, e.event_time or time.min))

    def render(self, events: Iterable[Event] = ()) -> str:
        """Retourne le mois en rapid logging : calendrier puis tâches."""
        title = self.title()
        lines = [title, "=" * len(title), "Calendrier"]
        calendar = self.calendar(events)
        if calendar:
            for event in calendar:
                abbreviation = DAY_ABBREVIATIONS[event.event_date.weekday()]
                lines.append(f"  {event.event_date.day:>2} {abbreviation} "
                             f"{event.label()}{event.time_text()}")
        else:
            lines.append("  (aucun événement)")
        lines.append("Tâches du mois")
        if self._entries:
            lines.extend(f"  {entry}" for entry in self._entries.values())
        else:
            lines.append(f"  {NO_ENTRY_TEXT}")
        return "\n".join(lines)
