"""Journal : entrées, Daily/Monthly Logs, signifiants et migration."""

import logging
from datetime import date, time, timedelta

from bujo.exceptions import (
    EntryNotFoundError,
    InvalidDateError,
    InvalidTransitionError,
    LogNotFoundError,
)
from bujo.models import Entry, Event, Note, Signifier, Task, TaskState
from bujo.pages import (
    DailyLog,
    MonthlyLog,
    month_start,
    next_month,
    to_day,
)

logger = logging.getLogger(__name__)

# Une page du journal : un Daily Log ou un Monthly Log.
Page = DailyLog | MonthlyLog


class Journal:
    """Journal qui range les entrées dans des logs et les retrouve par id.

    Chaque entrée appartient à exactement un log : un Daily Log (une
    journée) ou un Monthly Log (un mois). Les entrées sont indexées par
    identifiant, car deux entrées peuvent avoir le même nom (et une tâche
    migrée réapparaît sous le même nom d'un jour à l'autre).
    """

    def __init__(self) -> None:
        """Crée un journal vide."""
        self._entries: dict[int, Entry] = {}
        self._next_id = 1
        # Les logs sont indexés par leur date : le jour pour un Daily Log,
        # le premier jour du mois pour un Monthly Log.
        self._daily_logs: dict[date, DailyLog] = {}
        self._monthly_logs: dict[date, MonthlyLog] = {}
        # Associe l'id d'une entrée au log qui la contient : on retrouve
        # sa page directement, sans chercher dans tous les logs.
        self._homes: dict[int, Page] = {}

    # ------------------------------------------------------------------
    # Ajout d'entrées
    # ------------------------------------------------------------------

    def add_task(self, name: str, description: str = "",
                 log_date: date | None = None,
                 signifier: Signifier | None = None) -> Task:
        """Ajoute une tâche à faire dans le Daily Log du jour et la retourne.

        Sans log_date, le jour est aujourd'hui.
        """
        task = Task(self._next_id, name, description, log_date,
                    signifier=signifier)
        self._register(task, self._daily_log(task.log_date))
        return task

    def add_monthly_task(self, name: str, description: str = "",
                         month: date | None = None,
                         signifier: Signifier | None = None) -> Task:
        """Ajoute une tâche à faire dans le Monthly Log du mois.

        Seuls l'année et le mois de « month » comptent ; sans month, le mois
        est le mois en cours. La date du log de la tâche est le premier
        jour du mois. Retourne la tâche créée.
        """
        first = month_start(month if month is not None else date.today())
        task = Task(self._next_id, name, description, first,
                    signifier=signifier)
        self._register(task, self._monthly_log(first))
        return task

    def add_event(self, name: str, event_date: date, description: str = "",
                  event_time: time | None = None,
                  log_date: date | None = None,
                  signifier: Signifier | None = None) -> Event:
        """Ajoute un événement dans le Daily Log du jour et le retourne.

        L'événement apparaît aussi dans le calendrier du Monthly Log du
        mois de sa date (voir render_monthly_log).
        """
        event = Event(self._next_id, name, event_date, description,
                      event_time, log_date, signifier)
        self._register(event, self._daily_log(event.log_date))
        return event

    def add_note(self, name: str, description: str = "",
                 log_date: date | None = None,
                 signifier: Signifier | None = None) -> Note:
        """Ajoute une note dans le Daily Log du jour et la retourne."""
        note = Note(self._next_id, name, description, log_date,
                    signifier=signifier)
        self._register(note, self._daily_log(note.log_date))
        return note

    # ------------------------------------------------------------------
    # Consultation et modification d'une entrée
    # ------------------------------------------------------------------

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

    def set_signifier(self, entry_id: int,
                      signifier: Signifier | None) -> None:
        """Met un signifiant sur l'entrée (None pour le retirer).

        Lève EntryNotFoundError si l'entrée n'existe pas et
        InvalidSignifierError si le signifiant n'existe pas.
        """
        entry = self.get_entry(entry_id)
        entry.signifier = signifier
        logger.info("Signifiant de l'entrée %d : %s", entry_id,
                    signifier.value if signifier else "aucun")

    def delete_entry(self, entry_id: int) -> None:
        """Supprime l'entrée ; lève EntryNotFoundError si elle n'existe pas.

        Un log devenu vide disparaît du journal.
        """
        self.get_entry(entry_id)
        del self._entries[entry_id]
        home = self._homes.pop(entry_id)
        home.remove(entry_id)
        self._drop_if_empty(home)
        logger.info("Entrée supprimée : id=%d", entry_id)

    def pending_tasks(self) -> list[Task]:
        """Retourne les tâches à faire, dans l'ordre de création."""
        pending = []
        for entry in self._entries.values():
            if isinstance(entry, Task) and entry.state == TaskState.TODO:
                pending.append(entry)
        logger.debug("%d tâche(s) à faire", len(pending))
        return pending

    # ------------------------------------------------------------------
    # Daily Logs et Monthly Logs
    # ------------------------------------------------------------------

    def get_daily_log(self, day: date) -> DailyLog:
        """Retourne le Daily Log du jour ; lève LogNotFoundError sinon."""
        day = to_day(day)
        if day not in self._daily_logs:
            logger.error("Daily Log introuvable : %s", day)
            raise LogNotFoundError(f"Aucun Daily Log pour le {day}")
        return self._daily_logs[day]

    def get_monthly_log(self, month: date) -> MonthlyLog:
        """Retourne le Monthly Log du mois ; lève LogNotFoundError sinon."""
        first = month_start(month)
        if first not in self._monthly_logs:
            logger.error("Monthly Log introuvable : %s", first)
            raise LogNotFoundError(
                f"Aucun Monthly Log pour {first:%m/%Y}"
            )
        return self._monthly_logs[first]

    def daily_logs(self) -> list[DailyLog]:
        """Retourne tous les Daily Logs, du plus ancien au plus récent."""
        return [self._daily_logs[day] for day in sorted(self._daily_logs)]

    def monthly_logs(self) -> list[MonthlyLog]:
        """Retourne tous les Monthly Logs, du plus ancien au plus récent."""
        return [self._monthly_logs[month]
                for month in sorted(self._monthly_logs)]

    # ------------------------------------------------------------------
    # Migration et planification
    # ------------------------------------------------------------------

    def migrate_task(self, entry_id: int, target: date | None = None) -> Task:
        """Migre une tâche à faire et retourne sa nouvelle copie.

        La tâche d'origine passe à l'état « migrée » et reste dans son log ;
        une nouvelle tâche « à faire » (même nom, même description, même
        signifiant, origin_id = id d'origine) est écrite dans le log cible.

        - Tâche d'un Daily Log : target est le jour d'arrivée (par défaut
          le lendemain). Il doit être postérieur au jour du log.
        - Tâche d'un Monthly Log : seuls l'année et le mois de target
          comptent (par défaut le mois suivant). Ce mois doit être
          postérieur au mois du log.

        Lève InvalidTransitionError si l'entrée n'est pas une tâche à faire,
        InvalidDateError si la cible est invalide et EntryNotFoundError
        si l'id est inconnu. En cas d'erreur, rien n'est modifié.
        """
        task = self._get_movable_task(entry_id, "migrée")
        home = self._homes[entry_id]
        # Ordre voulu : 1) vérifier la cible, 2) changer l'état (peut être
        # refusé), 3) créer le log et la copie. Ainsi une migration refusée
        # ne modifie rien, pas même en créant un log vide.
        if isinstance(home, DailyLog):
            destination = self._target_day(home, target)
            task.migrate()
            destination_log: Page = self._daily_log(destination)
        else:
            destination = self._target_month(home, target)
            task.migrate()
            destination_log = self._monthly_log(destination)
        return self._copy_task(task, destination, destination_log)

    def migrate_day(self, source: date,
                    target: date | None = None) -> list[Task]:
        """Migre toutes les tâches à faire d'un Daily Log vers un autre jour.

        Retourne les nouvelles tâches. Si le jour n'a pas de log, il n'y
        a rien à migrer : la liste retournée est vide. Lève InvalidDateError
        si le jour cible n'est pas postérieur au jour source (rien n'est
        alors modifié).
        """
        day = to_day(source)
        log = self._daily_logs.get(day)
        if log is None:
            logger.info("Rien à migrer : aucun Daily Log le %s", day)
            return []
        destination = self._target_day(log, target)
        migrated = [self.migrate_task(task.id, destination)
                    for task in log.pending_tasks()]
        logger.info("Migration du %s vers le %s : %d tâche(s)",
                    day, destination, len(migrated))
        return migrated

    def migrate_month(self, source: date,
                      target: date | None = None) -> list[Task]:
        """Migre toutes les tâches à faire d'un Monthly Log vers un autre mois.

        Retourne les nouvelles tâches. Sans target, le mois d'arrivée est le
        mois suivant. Si le mois n'a pas de log, la liste retournée est
        vide. Lève InvalidDateError si le mois cible n'est pas postérieur
        au mois source (rien n'est alors modifié).
        """
        first = month_start(source)
        log = self._monthly_logs.get(first)
        if log is None:
            logger.info("Rien à migrer : aucun Monthly Log en %s",
                        f"{first:%m/%Y}")
            return []
        destination = self._target_month(log, target)
        migrated = [self.migrate_task(task.id, destination)
                    for task in log.pending_tasks()]
        logger.info("Migration de %s vers %s : %d tâche(s)",
                    f"{first:%m/%Y}", f"{destination:%m/%Y}", len(migrated))
        return migrated

    def schedule_task(self, entry_id: int, month: date) -> Task:
        """Planifie une tâche à faire sur un mois futur et retourne sa copie.

        La tâche d'origine passe à l'état « planifiée » ; une nouvelle
        tâche « à faire » est écrite dans le Monthly Log du mois choisi,
        qui doit être postérieur au mois de la tâche d'origine.

        Mêmes erreurs que migrate_task.
        """
        task = self._get_movable_task(entry_id, "planifiée")
        first = month_start(month)
        if first <= month_start(task.log_date):
            logger.error("Planification refusée : %s n'est pas après %s",
                         f"{first:%m/%Y}", f"{task.log_date:%m/%Y}")
            raise InvalidDateError(
                "Le mois de planification doit être postérieur au mois "
                "de la tâche"
            )
        task.schedule()
        return self._copy_task(task, first, self._monthly_log(first))

    # ------------------------------------------------------------------
    # Affichage
    # ------------------------------------------------------------------

    def render_daily_log(self, day: date) -> str:
        """Retourne le Daily Log du jour en rapid logging.

        Un jour sans entrée s'affiche comme un log vide (pas d'erreur).
        """
        day = to_day(day)
        log = self._daily_logs.get(day)
        if log is None:
            log = DailyLog(day)
        return log.render()

    def render_monthly_log(self, month: date) -> str:
        """Retourne le Monthly Log du mois en rapid logging.

        Le calendrier liste les événements du mois, même si aucune tâche
        n'a été écrite dans le Monthly Log.
        """
        first = month_start(month)
        log = self._monthly_logs.get(first)
        if log is None:
            log = MonthlyLog(first)
        events = [e for e in self._entries.values() if isinstance(e, Event)]
        return log.render(events)

    # ------------------------------------------------------------------
    # Méthodes privées
    # ------------------------------------------------------------------

    def _daily_log(self, day: date) -> DailyLog:
        """Retourne le Daily Log du jour, après l'avoir créé si besoin."""
        if day not in self._daily_logs:
            self._daily_logs[day] = DailyLog(day)
            logger.info("Daily Log créé : %s", day)
        return self._daily_logs[day]

    def _monthly_log(self, first: date) -> MonthlyLog:
        """Retourne le Monthly Log du mois, après l'avoir créé si besoin."""
        if first not in self._monthly_logs:
            self._monthly_logs[first] = MonthlyLog(first)
            logger.info("Monthly Log créé : %s", f"{first:%m/%Y}")
        return self._monthly_logs[first]

    def _drop_if_empty(self, log: Page) -> None:
        """Retire du journal un log qui n'a plus aucune entrée."""
        if len(log) > 0:
            return
        if isinstance(log, DailyLog):
            del self._daily_logs[log.day]
        else:
            del self._monthly_logs[log.month]
        logger.info("Log vide supprimé : %s", log.title())

    def _register(self, entry: Entry, log: Page) -> None:
        """Range l'entrée dans le log et prépare l'identifiant suivant."""
        log.add(entry)
        self._entries[entry.id] = entry
        self._homes[entry.id] = log
        self._next_id += 1
        logger.info("Entrée ajoutée : id=%d, type=%s, nom=%s",
                    entry.id, type(entry).__name__, entry.name)

    def _copy_task(self, task: Task, log_date: date, log: Page) -> Task:
        """Écrit dans le log une copie « à faire » de la tâche et la retourne.

        La copie garde le nom, la description et le signifiant ; son
        origin_id permet de remonter à la tâche d'origine.
        """
        copy = Task(self._next_id, task.name, task.description, log_date,
                    origin_id=task.id, signifier=task.signifier)
        self._register(copy, log)
        return copy

    def _get_task(self, entry_id: int) -> Task:
        """Retourne la tâche ; lève EntryNotFoundError si ce n'en est pas."""
        entry = self.get_entry(entry_id)
        if not isinstance(entry, Task):
            logger.error("L'entrée %d n'est pas une tâche", entry_id)
            raise EntryNotFoundError(
                f"L'entrée {entry_id} n'est pas une tâche"
            )
        return entry

    def _get_movable_task(self, entry_id: int, action: str) -> Task:
        """Retourne la tâche à migrer ou à planifier.

        Seule une tâche peut l'être : migrer une note ou un événement est
        une transition interdite (InvalidTransitionError).
        """
        entry = self.get_entry(entry_id)
        if not isinstance(entry, Task):
            logger.error("L'entrée %d (%s) ne peut pas être %s",
                         entry_id, type(entry).__name__, action)
            raise InvalidTransitionError(
                f"Seule une tâche peut être {action} "
                f"(entrée {entry_id} : {type(entry).__name__})"
            )
        return entry

    @staticmethod
    def _target_day(home: DailyLog, target: date | None) -> date:
        """Retourne le jour d'arrivée d'une migration ; vérifie qu'il suit."""
        if target is None:
            return home.day + timedelta(days=1)
        day = to_day(target)
        if day <= home.day:
            logger.error("Migration refusée : le %s n'est pas après le %s",
                         day, home.day)
            raise InvalidDateError(
                "Le jour cible doit être postérieur au jour du log"
            )
        return day

    @staticmethod
    def _target_month(home: MonthlyLog, target: date | None) -> date:
        """Retourne le mois d'arrivée d'une migration ; vérifie qu'il suit."""
        if target is None:
            return next_month(home.month)
        first = month_start(target)
        if first <= home.month:
            logger.error("Migration refusée : %s n'est pas après %s",
                         f"{first:%m/%Y}", f"{home.month:%m/%Y}")
            raise InvalidDateError(
                "Le mois cible doit être postérieur au mois du log"
            )
        return first
