"""Configuration de la journalisation : deux fichiers de logs."""

import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(log_dir: str | Path = "logs") -> logging.Logger:
    """Configure le logger « bujo » et crée les deux fichiers de logs.

    debug.log reçoit tous les messages (DEBUG et plus).
    errors.log ne reçoit que les messages ERROR et CRITICAL.
    """
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("bujo")
    logger.setLevel(logging.DEBUG)

    # Évite les doublons si la fonction est appelée plusieurs fois.
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(LOG_FORMAT)
    logger.addHandler(_file_handler(directory / "debug.log",
                                    logging.DEBUG, formatter))
    logger.addHandler(_file_handler(directory / "errors.log",
                                    logging.ERROR, formatter))
    return logger


def _file_handler(path: Path, level: int,
                  formatter: logging.Formatter) -> logging.FileHandler:
    """Crée un gestionnaire qui écrit dans un fichier à partir d'un niveau."""
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler
