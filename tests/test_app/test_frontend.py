from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mathwizard.app.frontend import mount_frontend


def test_health_wins_over_frontend(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>spa</html>", encoding="utf-8")

    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"message": "OK"}

    mount_frontend(app, dist)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"message": "OK"}


def test_mount_frontend_serves_index_and_spa_fallback(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>spa</html>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")

    app = FastAPI()
    mount_frontend(app, dist)
    client = TestClient(app)

    home = client.get("/")
    spa = client.get("/practice/derivatives", headers={"accept": "text/html"})
    asset = client.get("/assets/app.js")
    missing_asset = client.get("/assets/missing.js")

    assert home.status_code == 200
    assert "spa" in home.text
    assert spa.status_code == 200
    assert "spa" in spa.text
    assert asset.status_code == 200
    assert asset.text == "console.log(1)"
    assert missing_asset.status_code == 404


def test_mount_frontend_skips_missing_directory(tmp_path: Path) -> None:
    app = FastAPI()
    mount_frontend(app, tmp_path / "missing")
    client = TestClient(app)

    assert client.get("/").status_code == 404
