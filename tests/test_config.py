"""Pruebas de lectura y validación de acciones.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tareas.config import (
    Accion,
    ErrorConfiguracion,
    leer_acciones,
    validar_acciones,
)

from conftest import datos_acciones, escribir_acciones


def test_validar_acciones_devuelve_cada_accion_con_sus_campos() -> None:
    acciones = validar_acciones(datos_acciones())

    assert len(acciones) == 5
    assert all(isinstance(accion, Accion) for accion in acciones)
    assert [accion.id for accion in acciones] == [
        "reunir-apuntes",
        "reunir-capturas",
        "crear-indice",
        "resumir-apunte",
        "clasificar-apunte",
    ]
    assert acciones[2].origen == "entregar"
    assert acciones[2].destino == "entregar/indice.txt"


def test_operaciones_ia_aceptan_solo_campos_base() -> None:
    datos = [
        {"id": "a", "operacion": "mostrar_resumen", "patron": "*.txt"},
        {"id": "b", "operacion": "mostrar_tema", "patron": "*.txt"},
    ]

    acciones = validar_acciones(datos)

    assert [accion.operacion for accion in acciones] == [
        "mostrar_resumen",
        "mostrar_tema",
    ]
    assert todas_las_acciones_ia_no_tienen_rutas(acciones)


def todas_las_acciones_ia_no_tienen_rutas(acciones: list[Accion]) -> bool:
    return all(accion.origen is None and accion.destino is None for accion in acciones)


def test_operaciones_ia_aceptan_origen_opcional() -> None:
    datos = [
        {
            "id": "a",
            "operacion": "mostrar_resumen",
            "patron": "*.txt",
            "origen": "temas",
        }
    ]

    accion = validar_acciones(datos)[0]

    assert accion.origen == "temas"
    assert accion.destino is None


def test_operaciones_ia_rechazan_el_campo_destino() -> None:
    datos = [
        {
            "id": "a",
            "operacion": "mostrar_tema",
            "patron": "*.txt",
            "destino": "salida.txt",
        }
    ]

    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones(datos)

    assert "el campo 'destino' no es admitido" in str(info.value)


def test_operacion_desconocida_se_senala_por_su_nombre() -> None:
    datos = [{"id": "a", "operacion": "resumir", "patron": "*.txt"}]

    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones(datos)

    assert "operación desconocida 'resumir'" in str(info.value)


def test_campo_obligatorio_ausente_se_senala() -> None:
    datos = [{"id": "a", "operacion": "copiar", "patron": "*.pdf"}]

    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones(datos)

    assert "falta el campo 'destino'" in str(info.value)


def test_campo_vacio_se_rechaza() -> None:
    datos = [{"id": "a", "operacion": "copiar", "patron": "   ", "destino": "salida"}]

    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones(datos)

    assert "el campo 'patron' no puede estar vacío" in str(info.value)


def test_campo_no_texto_se_rechaza() -> None:
    datos: list[dict[str, Any]] = [
        {"id": "a", "operacion": "copiar", "patron": 123, "destino": "salida"}
    ]

    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones(datos)

    assert "el campo 'patron' no puede estar vacío" in str(info.value)


def test_origen_opcional_vacio_tambien_se_rechaza() -> None:
    datos = [
        {
            "id": "a",
            "operacion": "mostrar_resumen",
            "patron": "*.txt",
            "origen": "",
        }
    ]

    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones(datos)

    assert "el campo 'origen' no puede estar vacío" in str(info.value)


def test_ids_repetidos_se_rechazan() -> None:
    datos = [
        {"id": "igual", "operacion": "copiar", "patron": "*.pdf", "destino": "a"},
        {"id": "igual", "operacion": "copiar", "patron": "*.png", "destino": "b"},
    ]

    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones(datos)

    assert "el id 'igual' está repetido" in str(info.value)


def test_elemento_que_no_es_objeto_se_rechaza() -> None:
    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones([["no soy un objeto"]])

    assert "Acción 1: debe ser un objeto JSON" in str(info.value)


def test_la_raziz_del_json_debe_ser_una_lista() -> None:
    with pytest.raises(ErrorConfiguracion) as info:
        validar_acciones({"id": "a"})

    assert "debe contener una lista de acciones" in str(info.value)


def test_leer_acciones_falla_si_no_existe_el_fichero(tmp_path: Path) -> None:
    with pytest.raises(ErrorConfiguracion) as info:
        leer_acciones(tmp_path / "acciones.json")

    assert "No se encuentra el fichero acciones.json" in str(info.value)


def test_leer_acciones_detecta_json_mal_formado(tmp_path: Path) -> None:
    ruta = tmp_path / "acciones.json"
    ruta.write_text("[{'id': 'a'}]", encoding="utf-8")

    with pytest.raises(ErrorConfiguracion) as info:
        leer_acciones(ruta)

    assert "JSON mal formado en acciones.json" in str(info.value)
    assert "línea" in str(info.value)


def test_leer_acciones_detecta_fichero_no_utf8(tmp_path: Path) -> None:
    ruta = tmp_path / "acciones.json"
    ruta.write_bytes(b"[\xff]")

    with pytest.raises(ErrorConfiguracion) as info:
        leer_acciones(ruta)

    assert "no está codificado en UTF-8" in str(info.value)


def test_leer_acciones_acepta_una_ruta_explicita(tmp_path: Path) -> None:
    ruta = tmp_path / "otro-nombre.json"
    ruta.write_text(
        json.dumps(datos_acciones(), ensure_ascii=False), encoding="utf-8"
    )

    acciones = leer_acciones(ruta)

    assert len(acciones) == 5
    assert acciones[-1].operacion == "mostrar_tema"
