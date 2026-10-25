# Conception du projet Bullet Journal

## Entrées (niveau 1)

```
Entry (abstraite)
  attributs : id, name, description, created_at, log_date
  méthode abstraite : symbol()
      ├── Task    + state (TaskState), origin_id
      │           méthodes : complete(), abandon()
      ├── Event   + event_date, event_time (optionnelle)
      └── Note    (rien de plus)

TaskState (Enum) : TODO, DONE, MIGRATED, SCHEDULED, ABANDONED

BujoError (mère)
  ├── EntryNotFoundError
  ├── EmptyNameError
  ├── InvalidDateError
  └── InvalidTransitionError
```

Règle de transitions : seule une tâche `TODO` peut changer d'état.
`DONE`, `MIGRATED`, `SCHEDULED` et `ABANDONED` sont des états finaux.
Toute tentative de modification lève `InvalidTransitionError`.


## Journal (niveau 1)

```
Journal
  attributs privés : _entries (dictionnaire {id: entrée}), _next_id (compteur)
  add_task(name, description) / add_event(...) / add_note(...)
  get_entry(entry_id)       -> lève EntryNotFoundError si l'id n'existe pas
  complete_task(entry_id)   -> passe la tâche à DONE
  abandon_task(entry_id)    -> passe la tâche à ABANDONED
  delete_entry(entry_id)
  pending_tasks()           -> liste des tâches à l'état TODO
```

Choix de conception :
- Un dictionnaire `{id: entrée}` : on retrouve une entrée directement par son identifiant, sans parcourir une liste.
- Un compteur `_next_id` : on ajoute 1 à chaque nouvelle entrée, donc deux entrées n'ont jamais le même id.
- `_entries` est privé : on n'y touche que par les méthodes du journal (encapsulation).
- Les vérifications sont dans les classes : `Task` refuse les transitions interdites, `Journal` refuse les ids inconnus.


## Architecture des fichiers

```
bujo/
├── bujo/
│   ├── __init__.py
│   ├── exceptions.py       BujoError et ses filles
│   ├── models.py           TaskState, Entry, Task, Event, Note
│   ├── journal.py          Journal (niveau 1)
│   └── logging_config.py   configuration de logging (2 fichiers)
├── tests/
│   ├── test_models.py
│   └── test_journal.py
├── docs/
├── logs/
├── .github/workflows/ci.yml
├── requirements.txt
├── README.md
└── .gitignore
```

Niveau 2 : ajout de `bujo/pages.py` (DailyLog, MonthlyLog).
Dépendances : exceptions <- models <- journal ; logging_config utilisé par journal.
Les tests se lancent avec `python -m pytest`.