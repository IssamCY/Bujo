# Bujo : bibliothèque Python de Bullet Journal

Projet ING1 GIA, CY Tech. Bibliothèque qui modélise un Bullet Journal :
tâches, événements et notes, avec cycle de vie des tâches, journalisation
(`logging`) et tests (`pytest`).

## Installation

```bash
conda create -n bujo python=3.12
conda activate bujo
pip install -r requirements.txt
```

## Exemple d'utilisation

```python
from bujo.journal import Journal

journal = Journal()
courses = journal.add_task("Faire les courses", "Lait, pain")
journal.add_task("Rendre le rapport")
journal.add_note("Idée", "Créer un jeu en Python")

journal.complete_task(courses.id)

for task in journal.pending_tasks():
    print(task)      # • Rendre le rapport
print(courses)       # × Faire les courses
```

Un scénario complet est fourni : `python demo.py`. Il génère aussi les
fichiers de logs dans `logs/`.

## Fonctionnalités (niveau 1)

- trois types d'entrées : tâche, événement, note
- identifiant unique pour chaque entrée
- cycle de vie des tâches : à faire, terminée, migrée, planifiée, abandonnée
  (seule une tâche à faire peut changer d'état)
- ajouter, terminer, abandonner, supprimer, lister les tâches à faire
- exceptions personnalisées (`BujoError` et ses filles)
- journalisation dans deux fichiers : `logs/debug.log` (tout) et
  `logs/errors.log` (erreurs uniquement)

## Symboles (rapid logging)

| Symbole | Signification |
|---|---|
| `•` | tâche à faire |
| `×` | tâche terminée |
| `>` | tâche migrée |
| `<` | tâche planifiée |
| `~` | tâche abandonnée |
| `○` | événement |
| `-` | note |

## Tests et qualité

```bash
python -m pytest
flake8 bujo tests
```

Une intégration continue (GitHub Actions) lance ces vérifications à chaque
envoi.

## Structure du dépôt

```
bujo/        le package (exceptions, models, journal, logging_config)
tests/       les tests pytest
docs/        glossaire et conception
logs/        fichiers de logs produits par demo.py
demo.py      scénario de démonstration
```

## Équipe

À COMPLÉTER : prénoms et noms des deux membres.

## Sources

À COMPLÉTER : les pages et vidéos consultées sur la méthode Bullet Journal,
et ce que vous en avez retenu, avec vos propres mots.
