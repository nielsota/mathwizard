from pathlib import Path

from fastapi import FastAPI


def mount_frontend(app: FastAPI, dist_dir: Path) -> None:
    if dist_dir.is_dir():
        app.frontend("/", directory=dist_dir, fallback="index.html")
