from mathwizard.settings import BootstrapSettings


def test_bootstrap_username_defaults_to_niels() -> None:
    settings = BootstrapSettings()

    assert settings.username == "niels"
    assert settings.password == "root"
