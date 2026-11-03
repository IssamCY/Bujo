"""Tests de la configuration de la journalisation."""

from bujo.logging_config import setup_logging


def test_cree_les_deux_fichiers(tmp_path):
    """setup_logging crée debug.log et errors.log dans le dossier donné."""
    setup_logging(tmp_path)
    assert (tmp_path / "debug.log").exists()
    assert (tmp_path / "errors.log").exists()


def test_debug_recoit_tout_errors_seulement_les_erreurs(tmp_path):
    """Les messages DEBUG vont dans debug.log, les ERROR dans les deux."""
    logger = setup_logging(tmp_path)
    logger.debug("message de debug")
    logger.error("message d'erreur")
    contenu_debug = (tmp_path / "debug.log").read_text(encoding="utf-8")
    contenu_errors = (tmp_path / "errors.log").read_text(encoding="utf-8")
    assert "message de debug" in contenu_debug
    assert "message d'erreur" in contenu_debug
    assert "message de debug" not in contenu_errors
    assert "message d'erreur" in contenu_errors


def test_pas_de_doublon_si_appel_repete(tmp_path):
    """Appeler setup_logging deux fois n'ajoute pas de gestionnaires."""
    setup_logging(tmp_path)
    logger = setup_logging(tmp_path)
    assert len(logger.handlers) == 2
