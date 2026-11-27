"""Fixtures comunes: sin red, sin clave y sin leer el fichero .env del usuario."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from tareas import ia

VARIABLES_IA = (
    "TAREAS_IA_URL",
    "TAREAS_IA_MODELO",
    "TAREAS_IA_CLAVE",
    "TAREAS_IA_TIMEOUT",
    "TAREAS_IA_CA",
)


@pytest.fixture(autouse=True)
def sin_credenciales(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cualquier prueba empieza sin variables del centro en el entorno."""
    for nombre in VARIABLES_IA:
        monkeypatch.delenv(nombre, raising=False)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def proveedor_ia(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    """Sustituye las dos consultas por funciones locales que registran su entrada."""
    llamadas: list[tuple[str, str]] = []

    def resumen(texto: str, configuracion: Any = None) -> str:
        llamadas.append(("mostrar_resumen", texto))
        return "resumen simulado"

    def tema(texto: str, configuracion: Any = None) -> str:
        llamadas.append(("mostrar_tema", texto))
        return "tema simulado"

    monkeypatch.setattr(ia, "mostrar_resumen", resumen)
    monkeypatch.setattr(ia, "mostrar_tema", tema)
    return llamadas


def datos_acciones() -> list[dict[str, str]]:
    """Cinco acciones válidas, con los nombres exactos del esquema."""
    return [
        {
            "id": "reunir-apuntes",
            "operacion": "copiar",
            "patron": "*.pdf",
            "destino": "entregar/apuntes",
        },
        {
            "id": "reunir-capturas",
            "operacion": "copiar",
            "patron": "*.png",
            "destino": "entregar/capturas",
        },
        {
            "id": "crear-indice",
            "operacion": "crear_indice",
            "patron": "**/*",
            "origen": "entregar",
            "destino": "entregar/indice.txt",
        },
        {
            "id": "resumir-apunte",
            "operacion": "mostrar_resumen",
            "patron": "*.txt",
        },
        {
            "id": "clasificar-apunte",
            "operacion": "mostrar_tema",
            "patron": "*.txt",
        },
    ]


def escribir_acciones(directorio: Path, datos: Any) -> Path:
    ruta = directorio / "acciones.json"
    ruta.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return ruta


def instantanea(raiz: Path) -> dict[str, str]:
    """Contenido completo de un árbol, para detectar escrituras inesperadas."""
    return {
        str(ruta.relative_to(raiz)).replace("\\", "/"): (
            "<directorio>" if ruta.is_dir() else ruta.read_bytes().hex()
        )
        for ruta in sorted(raiz.rglob("*"))
    }
