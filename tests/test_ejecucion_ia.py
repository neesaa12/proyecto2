"""Pruebas de resumen y clasificación con un proveedor simulado."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from tareas import ia
from tareas.cli import app
from tareas.config import Accion
from tareas.ejecucion import ErrorEjecucion, ejecutar_accion

from conftest import datos_acciones, escribir_acciones, instantanea


def accion_ia(
    operacion: str, *, patron: str = "*.txt", origen: str | None = None
) -> Accion:
    return Accion(
        id="accion-ia",
        operacion=operacion,
        patron=patron,
        origen=origen,
    )


def test_resumen_muestra_el_resultado_y_envia_el_texto_al_proveedor(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    archivo = tmp_path / "apunte.txt"
    archivo.write_text("contenido del apunte", encoding="utf-8")

    mensajes = ejecutar_accion(accion_ia("mostrar_resumen"), tmp_path)

    assert proveedor_ia == [("mostrar_resumen", "contenido del apunte")]
    assert any("accion-ia: apunte.txt" in mensaje for mensaje in mensajes)
    assert any("resumen simulado" in mensaje for mensaje in mensajes)
    assert archivo.read_bytes() == "contenido del apunte".encode("utf-8")


def test_clasificacion_muestra_el_tema_y_envia_el_texto_al_proveedor(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    archivo = tmp_path / "apunte.txt"
    archivo.write_text("tema del apunte", encoding="utf-8")

    mensajes = ejecutar_accion(accion_ia("mostrar_tema"), tmp_path)

    assert proveedor_ia == [("mostrar_tema", "tema del apunte")]
    assert any("accion-ia: apunte.txt" in mensaje for mensaje in mensajes)
    assert any("tema simulado" in mensaje for mensaje in mensajes)
    assert archivo.read_bytes() == "tema del apunte".encode("utf-8")


def test_simulacion_no_invoca_al_proveedor_ni_modifica_el_arbol(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    (tmp_path / "apunte.txt").write_text("no leer", encoding="utf-8")
    antes = instantanea(tmp_path)

    mensajes = ejecutar_accion(accion_ia("mostrar_resumen"), tmp_path, True)

    assert proveedor_ia == []
    assert any("enviaría el texto" in mensaje for mensaje in mensajes)
    assert any("apunte.txt" in mensaje for mensaje in mensajes)
    assert instantanea(tmp_path) == antes


def test_simulacion_por_cli_no_pide_clave_ni_llama_al_proveedor(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    proveedor_ia: list[tuple[str, str]],
) -> None:
    datos = [
        datos for datos in datos_acciones() if datos["operacion"] == "mostrar_resumen"
    ]
    escribir_acciones(tmp_path, datos)
    monkeypatch.chdir(tmp_path)
    archivo = tmp_path / "apunte.txt"
    archivo.write_text("no debe enviarse", encoding="utf-8")

    def prohibido(*args: object, **kwargs: object) -> None:
        raise AssertionError("La simulación intentó preparar credenciales o red")

    monkeypatch.setattr(ia, "leer_configuracion", prohibido)
    monkeypatch.setattr(ia, "crear_cliente", prohibido)

    resultado = runner.invoke(
        app,
        [
            "ejecutar",
            "resumir-apunte",
            "--directorio",
            str(tmp_path),
            "--simular",
        ],
    )

    assert resultado.exit_code == 0
    assert "apunte.txt" in resultado.output
    assert "enviaría" in resultado.output
    assert proveedor_ia == []
    assert archivo.read_text(encoding="utf-8") == "no debe enviarse"


def test_fallo_de_red_del_proveedor_conserva_el_original(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archivo = tmp_path / "apunte.txt"
    archivo.write_text("texto intacto", encoding="utf-8")
    llamadas: list[str] = []

    def fallar(texto: str, configuracion: Any = None) -> str:
        llamadas.append(texto)
        raise ia.ErrorIA("No se puede conectar con el centro.")

    monkeypatch.setattr(ia, "mostrar_resumen", fallar)

    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(accion_ia("mostrar_resumen"), tmp_path)

    assert llamadas == ["texto intacto"]
    assert "No se puede conectar con el centro." in str(info.value)
    assert archivo.read_text(encoding="utf-8") == "texto intacto"


def test_fallo_de_red_por_cli_da_error_claro_sin_traceback(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    datos = [
        datos for datos in datos_acciones() if datos["operacion"] == "mostrar_resumen"
    ]
    escribir_acciones(tmp_path, datos)
    monkeypatch.chdir(tmp_path)
    archivo = tmp_path / "apunte.txt"
    archivo.write_text("texto intacto", encoding="utf-8")

    def fallar(texto: str, configuracion: Any = None) -> str:
        raise ia.ErrorIA("No se puede conectar con el centro.")

    monkeypatch.setattr(ia, "mostrar_resumen", fallar)

    resultado = runner.invoke(
        app, ["ejecutar", "resumir-apunte", "--directorio", str(tmp_path)]
    )

    assert resultado.exit_code == 1
    assert isinstance(resultado.exception, SystemExit) or resultado.exception is None
    assert "No se puede conectar con el centro." in resultado.output
    assert "Traceback" not in resultado.output
    assert archivo.read_text(encoding="utf-8") == "texto intacto"


def test_archivo_no_utf8_no_llama_al_proveedor_y_conserva_sus_bytes(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    archivo = tmp_path / "apunte.txt"
    archivo.write_bytes(b"\xff\xfe")

    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(accion_ia("mostrar_resumen"), tmp_path)

    assert "no se puede leer" in str(info.value)
    assert proveedor_ia == []
    assert archivo.read_bytes() == b"\xff\xfe"


def test_sin_origen_la_busqueda_parte_de_la_carpeta_de_trabajo(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    (tmp_path / "raiz.txt").write_text("de la raiz", encoding="utf-8")
    subcarpeta = tmp_path / "temas"
    subcarpeta.mkdir()
    (subcarpeta / "interno.txt").write_text("del subdirectorio", encoding="utf-8")

    ejecutar_accion(accion_ia("mostrar_resumen"), tmp_path)

    assert proveedor_ia == [("mostrar_resumen", "de la raiz")]


def test_con_origen_opcional_la_busqueda_parte_del_subdirectorio(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    subcarpeta = tmp_path / "temas"
    subcarpeta.mkdir()
    (subcarpeta / "apunte.txt").write_text("del tema", encoding="utf-8")

    mensajes = ejecutar_accion(
        accion_ia("mostrar_resumen", origen="temas"), tmp_path
    )

    assert proveedor_ia == [("mostrar_resumen", "del tema")]
    assert any("accion-ia: apunte.txt" in mensaje for mensaje in mensajes)


def test_sin_archivos_coincidentes_no_llama_al_proveedor(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    mensajes = ejecutar_accion(accion_ia("mostrar_tema"), tmp_path)

    assert any("ningún archivo coincide" in mensaje for mensaje in mensajes)
    assert proveedor_ia == []


def test_directorio_de_trabajo_inexistente_no_llama_al_proveedor(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(accion_ia("mostrar_resumen"), tmp_path / "no-existe")

    assert "no existe el directorio de trabajo" in str(info.value)
    assert proveedor_ia == []


def test_origen_inexistente_no_llama_al_proveedor(
    tmp_path: Path, proveedor_ia: list[tuple[str, str]]
) -> None:
    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(accion_ia("mostrar_tema", origen="no-existe"), tmp_path)

    assert "no existe el directorio de origen" in str(info.value)
    assert proveedor_ia == []


def test_proveedor_real_sin_credenciales_avisa_del_protocolo_y_no_lee_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archivo = tmp_path / "apunte.txt"
    archivo.write_text("texto intacto", encoding="utf-8")

    def prohibido(*args: object, **kwargs: object) -> None:
        raise AssertionError("La operación intentó leer credenciales o abrir red")

    monkeypatch.setattr(ia, "leer_configuracion", prohibido)
    monkeypatch.setattr(ia, "crear_cliente", prohibido)

    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(accion_ia("mostrar_resumen"), tmp_path)

    assert "Falta el protocolo del centro" in str(info.value)
    assert archivo.read_text(encoding="utf-8") == "texto intacto"
