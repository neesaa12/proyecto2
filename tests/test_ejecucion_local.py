"""Pruebas de las acciones locales: copiar y crear índice."""

from __future__ import annotations

from pathlib import Path

import pytest

from tareas.config import Accion
from tareas.ejecucion import ErrorEjecucion, ejecutar_accion

from conftest import instantanea


def test_copiar_crea_el_destino_y_no_toca_el_original(tmp_path: Path) -> None:
    original = tmp_path / "apunte.pdf"
    original.write_bytes(b"contenido original")

    mensajes = ejecutar_accion(
        Accion(
            id="reunir-apuntes",
            operacion="copiar",
            patron="*.pdf",
            destino="entregar/apuntes",
        ),
        tmp_path,
    )

    copia = tmp_path / "entregar" / "apuntes" / "apunte.pdf"
    assert any("copiado" in mensaje for mensaje in mensajes)
    assert copia.read_bytes() == b"contenido original"
    assert original.read_bytes() == b"contenido original"


def test_copiar_no_sobrescribe_un_destino_existente(tmp_path: Path) -> None:
    original = tmp_path / "apunte.pdf"
    original.write_bytes(b"nuevo")
    destino = tmp_path / "entregar" / "apuntes" / "apunte.pdf"
    destino.parent.mkdir(parents=True)
    destino.write_bytes(b"viejo")

    mensajes = ejecutar_accion(
        Accion(
            id="reunir-apuntes",
            operacion="copiar",
            patron="*.pdf",
            destino="entregar/apuntes",
        ),
        tmp_path,
    )

    assert any("ya existe" in mensaje and "no se sobrescribe" in mensaje for mensaje in mensajes)
    assert destino.read_bytes() == b"viejo"
    assert original.read_bytes() == b"nuevo"


def test_copiar_sin_coincidencias_no_crea_el_destino(tmp_path: Path) -> None:
    mensajes = ejecutar_accion(
        Accion(
            id="reunir-apuntes",
            operacion="copiar",
            patron="*.pdf",
            destino="entregar/apuntes",
        ),
        tmp_path,
    )

    assert any("ningún archivo coincide" in mensaje for mensaje in mensajes)
    assert not (tmp_path / "entregar").exists()


def test_copiar_con_fallo_no_modifica_el_original(tmp_path: Path) -> None:
    original = tmp_path / "apunte.pdf"
    original.write_bytes(b"intacto")
    (tmp_path / "entregar").write_bytes(b"archivo que bloquea la carpeta")

    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(
            Accion(
                id="reunir-apuntes",
                operacion="copiar",
                patron="*.pdf",
                destino="entregar",
            ),
            tmp_path,
        )

    assert "no se puede copiar" in str(info.value)
    assert original.read_bytes() == b"intacto"
    assert (tmp_path / "entregar").read_bytes() == b"archivo que bloquea la carpeta"


def test_copiar_en_simulacion_no_escribe_nada(tmp_path: Path) -> None:
    (tmp_path / "apunte.pdf").write_bytes(b"original")
    antes = instantanea(tmp_path)

    mensajes = ejecutar_accion(
        Accion(
            id="reunir-apuntes",
            operacion="copiar",
            patron="*.pdf",
            destino="entregar/apuntes",
        ),
        tmp_path,
        True,
    )

    assert any("copiaría" in mensaje for mensaje in mensajes)
    assert instantanea(tmp_path) == antes
    assert not (tmp_path / "entregar").exists()


def test_indice_escribe_la_lista_ordenada_y_excluye_el_propio_indice(
    tmp_path: Path,
) -> None:
    origen = tmp_path / "entregar"
    origen.mkdir()
    (origen / "b.txt").write_bytes(b"b")
    (origen / "a.txt").write_bytes(b"a")

    mensajes = ejecutar_accion(
        Accion(
            id="crear-indice",
            operacion="crear_indice",
            patron="**/*",
            origen="entregar",
            destino="entregar/indice.txt",
        ),
        tmp_path,
    )

    indice = origen / "indice.txt"
    assert any("índice escrito" in mensaje for mensaje in mensajes)
    assert indice.read_text(encoding="utf-8") == "a.txt\nb.txt\n"
    assert (origen / "a.txt").read_bytes() == b"a"
    assert (origen / "b.txt").read_bytes() == b"b"


def test_indice_no_sobrescribe_un_indice_existente(tmp_path: Path) -> None:
    origen = tmp_path / "entregar"
    origen.mkdir()
    (origen / "a.txt").write_bytes(b"a")
    indice = origen / "indice.txt"
    indice.write_text("contenido anterior\n", encoding="utf-8")

    mensajes = ejecutar_accion(
        Accion(
            id="crear-indice",
            operacion="crear_indice",
            patron="**/*",
            origen="entregar",
            destino="entregar/indice.txt",
        ),
        tmp_path,
    )

    assert any("ya existe" in mensaje and "no se sobrescribe" in mensaje for mensaje in mensajes)
    assert indice.read_text(encoding="utf-8") == "contenido anterior\n"


def test_indice_con_fallo_no_modifica_los_originales(tmp_path: Path) -> None:
    origen = tmp_path / "entregar"
    origen.mkdir()
    (origen / "a.txt").write_bytes(b"intacto")
    (origen / "bloqueado").write_bytes(b"archivo que bloquea la carpeta")

    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(
            Accion(
                id="crear-indice",
                operacion="crear_indice",
                patron="**/*",
                origen="entregar",
                destino="entregar/bloqueado/indice.txt",
            ),
            tmp_path,
        )

    assert "no se puede escribir" in str(info.value)
    assert (origen / "a.txt").read_bytes() == b"intacto"
    assert (origen / "bloqueado").read_bytes() == b"archivo que bloquea la carpeta"
    assert not (origen / "bloqueado" / "indice.txt").exists()


def test_indice_en_simulacion_no_escribe_nada(tmp_path: Path) -> None:
    origen = tmp_path / "entregar"
    origen.mkdir()
    (origen / "a.txt").write_bytes(b"a")
    antes = instantanea(tmp_path)

    mensajes = ejecutar_accion(
        Accion(
            id="crear-indice",
            operacion="crear_indice",
            patron="**/*",
            origen="entregar",
            destino="entregar/indice.txt",
        ),
        tmp_path,
        True,
    )

    assert any("escribiría" in mensaje for mensaje in mensajes)
    assert instantanea(tmp_path) == antes
    assert not (origen / "indice.txt").exists()


def test_indice_sin_origen_falla_con_mensaje_claro(tmp_path: Path) -> None:
    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(
            Accion(
                id="crear-indice",
                operacion="crear_indice",
                patron="**/*",
                destino="indice.txt",
            ),
            tmp_path,
        )

    assert "necesita 'origen'" in str(info.value)


def test_operacion_desconocida_falla_en_el_motor(tmp_path: Path) -> None:
    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(
            Accion(id="rara", operacion="inventada", patron="*"), tmp_path
        )

    assert "operación desconocida 'inventada'" in str(info.value)


def test_directorio_de_trabajo_inexistente_falla(tmp_path: Path) -> None:
    with pytest.raises(ErrorEjecucion) as info:
        ejecutar_accion(
            Accion(
                id="copiar",
                operacion="copiar",
                patron="*.pdf",
                destino="entregar",
            ),
            tmp_path / "no-existe",
        )

    assert "no existe el directorio de trabajo" in str(info.value)
