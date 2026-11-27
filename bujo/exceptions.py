"""Exceptions personnalisées de la bibliothèque."""


class BujoError(Exception):
    """Exception de base de la bibliothèque bujo."""


class EntryNotFoundError(BujoError):
    """Aucune entrée ne correspond à l'identifiant demandé."""


class EmptyNameError(BujoError):
    """Le nom d'une entrée ne peut pas être vide."""


class InvalidDateError(BujoError):
    """La date fournie n'est pas valide."""


class InvalidTransitionError(BujoError):
    """Changement d'état interdit pour une tâche."""


class LogNotFoundError(BujoError):
    """Aucun log (Daily Log ou Monthly Log) ne correspond à la date."""


class InvalidSignifierError(BujoError):
    """Le signifiant fourni n'existe pas (priorité ou idée seulement)."""
