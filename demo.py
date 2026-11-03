"""Démonstration de la bibliothèque bujo (génère les fichiers de logs)."""

from datetime import date, time

from bujo.exceptions import BujoError
from bujo.journal import Journal
from bujo.logging_config import setup_logging


def main() -> None:
    """Joue un petit scénario d'utilisation du journal."""
    setup_logging("logs")
    journal = Journal()

    courses = journal.add_task("Faire les courses", "Lait, pain")
    journal.add_task("Rendre le rapport")
    cuisine = journal.add_task("Rénover la cuisine")
    journal.add_note("Idée", "Créer un jeu en Python")
    journal.add_event("Partiel", date(2026, 12, 10), event_time=time(9, 0))

    journal.complete_task(courses.id)
    journal.abandon_task(cuisine.id)

    print("Tâches à faire :")
    for task in journal.pending_tasks():
        print(" ", task)

    # Quelques erreurs volontaires, pour remplir errors.log.
    try:
        journal.complete_task(courses.id)
    except BujoError as erreur:
        print("Erreur attendue :", erreur)

    try:
        journal.get_entry(999)
    except BujoError as erreur:
        print("Erreur attendue :", erreur)

    try:
        journal.add_task("   ")
    except BujoError as erreur:
        print("Erreur attendue :", erreur)


if __name__ == "__main__":
    main()
