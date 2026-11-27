"""Pruebas de la interfaz de línea de comandos."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from tareas import __version__, ia
from tareas.cli import app

from conftest import datos_acciones, escribir_acciones


def test_ayuda_muestra_comandos_y_rotulos_en_espanol(runner: CliRunner) -> None:
    resultado = runner.invoke(app, ["--help"])

    assert resultado.exit_code == 0
    assert isinstance(resultado.exception, SystemExit) or resultado.exception is None
    assert "Uso:" in resultado.output
    assert "Comandos" in resultado.output
    assert "Opciones" in resultado.output
    assert "comprobar-ia" in resultado.output
    assert "ejecutar" in resultado.output
    assert "Muestra la versión del proyecto." in resultado.output


def test_sin_argumentos_muestra_la_ayuda(runner: CliRunner) -> None:
    resultado = runner.invoke(app, [])

    assert resultado.exit_code == 2
    assert "Uso:" in resultado.output
    assert "version" in resultado.output


def test_version_devuelve_la_version_del_paquete(runner: CliRunner) -> None:
    resultado = runner.invoke(app, ["version"])

    assert resultado.exit_code == 0
    assert resultado.output.strip() == __version__


def test_listar_muestra_los_cinco_identificadores_en_orden(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    escribir_acciones(tmp_path, datos_acciones())
    monkeypatch.chdir(tmp_path)

    resultado = runner.invoke(app, ["listar"])

    assert resultado.exit_code == 0
    assert resultado.output.splitlines() == [
        "reunir-apuntes",
        "reunir-capturas",
        "crear-indice",
        "resumir-apunte",
        "clasificar-apunte",
    ]


def test_listar_sin_fichero_avisa_en_lugar_de_fallar(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    resultado = runner.invoke(app, ["listar"])

    assert resultado.exit_code == 0
    assert "Todavía no hay acciones configuradas" in resultado.output


def test_listar_con_json_mal_formado_da_error_sin_traceback(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "acciones.json").write_text("{ mal", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    resultado = runner.invoke(app, ["listar"])

    assert resultado.exit_code == 1
    assert isinstance(resultado.exception, SystemExit) or resultado.exception is None
    assert "JSON mal formado" in resultado.output
    assert "Traceback" not in resultado.output


def test_validar_acepta_las_cinco_acciones(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    escribir_acciones(tmp_path, datos_acciones())
    monkeypatch.chdir(tmp_path)

    resultado = runner.invoke(app, ["validar"])

    assert resultado.exit_code == 0
    assert resultado.output.strip() == "acciones.json es válido: 5 acciones."


def test_validar_reune_varios_errores_y_sale_con_codigo_1(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    datos = [
        {"id": "x", "operacion": "inventada", "patron": "*.txt"},
        {
            "id": "x",
            "operacion": "mostrar_tema",
            "patron": "*.txt",
            "destino": "no-admitido",
        },
    ]
    escribir_acciones(tmp_path, datos)
    monkeypatch.chdir(tmp_path)

    resultado = runner.invoke(app, ["validar"])

    assert resultado.exit_code == 1
    assert isinstance(resultado.exception, SystemExit) or resultado.exception is None
    assert "operación desconocida 'inventada'" in resultado.output
    assert "el campo 'destino' no es admitido" in resultado.output
    assert "está repetido" in resultado.output
    assert "Traceback" not in resultado.output


def test_ejecutar_con_id_inexistente_avisa_sin_traceback(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    escribir_acciones(tmp_path, datos_acciones())
    monkeypatch.chdir(tmp_path)

    resultado = runner.invoke(
        app, ["ejecutar", "no-existe", "--directorio", str(tmp_path)]
    )

    assert resultado.exit_code == 1
    assert isinstance(resultado.exception, SystemExit) or resultado.exception is None
    assert "no existe la acción 'no-existe'" in resultado.output
    assert "Traceback" not in resultado.output


def test_comprobar_ia_sin_variables_explica_los_tres_datos_que_faltan(
    runner: CliRunner,
) -> None:
    resultado = runner.invoke(app, ["comprobar-ia"])

    assert resultado.exit_code == 1
    assert isinstance(resultado.exception, SystemExit) or resultado.exception is None
    assert "TAREAS_IA_URL" in resultado.output
    assert "TAREAS_IA_MODELO" in resultado.output
    assert "TAREAS_IA_CLAVE" in resultado.output
    assert "Exporta las variables" in resultado.output
    assert "Traceback" not in resultado.output


def test_comprobar_ia_con_solo_url_pide_modelo_y_clave(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TAREAS_IA_URL", "https://centro.invalid")

    resultado = runner.invoke(app, ["comprobar-ia"])

    assert resultado.exit_code == 1
    assert "TAREAS_IA_MODELO" in resultado.output
    assert "TAREAS_IA_CLAVE" in resultado.output
    assert "TAREAS_IA_URL" not in resultado.output
    assert isinstance(resultado.exception, SystemExit) or resultado.exception is None


def test_comprobar_ia_con_valores_no_muestra_la_clave_y_no_abre_red(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    class ClienteFalso:
        def __enter__(self) -> "ClienteFalso":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    creados: list[Any] = []

    def crear_cliente(configuracion: Any) -> ClienteFalso:
        creados.append(configuracion)
        return ClienteFalso()

    monkeypatch.setenv("TAREAS_IA_URL", "https://centro.invalid")
    monkeypatch.setenv("TAREAS_IA_MODELO", "modelo-de-prueba")
    monkeypatch.setenv("TAREAS_IA_CLAVE", "clave-secreta-de-prueba")
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", "12")
    monkeypatch.setattr(ia, "crear_cliente", crear_cliente)

    resultado = runner.invoke(app, ["comprobar-ia"])

    assert resultado.exit_code == 0
    assert len(creados) == 1
    assert "modelo-de-prueba" in resultado.output
    assert "12 s" in resultado.output
    assert "falta el protocolo" in resultado.output
    assert "clave-secreta-de-prueba" not in resultado.output
