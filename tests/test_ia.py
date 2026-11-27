"""Pruebas del proveedor aislado: configuración, TLS y mensajes sin protocolo."""

from __future__ import annotations

import ssl
from pathlib import Path
from typing import Any

import httpx
import pytest

from tareas import ia


def _configurar_obligatorias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAREAS_IA_URL", "https://centro.invalid")
    monkeypatch.setenv("TAREAS_IA_MODELO", "modelo-de-prueba")
    monkeypatch.setenv("TAREAS_IA_CLAVE", "clave-de-prueba")


def test_leer_configuracion_sin_variables_nombra_los_tres_datos() -> None:
    with pytest.raises(ia.ErrorIA) as info:
        ia.leer_configuracion()

    mensaje = str(info.value)
    assert "TAREAS_IA_URL" in mensaje
    assert "TAREAS_IA_MODELO" in mensaje
    assert "TAREAS_IA_CLAVE" in mensaje


def test_leer_configuracion_con_solo_url_pide_modelo_y_clave(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAREAS_IA_URL", "https://centro.invalid")

    with pytest.raises(ia.ErrorIA) as info:
        ia.leer_configuracion()

    assert "TAREAS_IA_MODELO" in str(info.value)
    assert "TAREAS_IA_CLAVE" in str(info.value)
    assert "TAREAS_IA_URL" not in str(info.value)


def test_leer_configuracion_usa_valores_por_defecto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configurar_obligatorias(monkeypatch)

    configuracion = ia.leer_configuracion()

    assert configuracion.url == "https://centro.invalid"
    assert configuracion.modelo == "modelo-de-prueba"
    assert configuracion.clave == "clave-de-prueba"
    assert configuracion.timeout == ia.TIEMPO_ESPERA_POR_DEFECTO
    assert configuracion.ca is None


def test_leer_configuracion_respeta_timeout_y_ca(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _configurar_obligatorias(monkeypatch)
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", "12.5")
    monkeypatch.setenv("TAREAS_IA_CA", str(tmp_path))

    configuracion = ia.leer_configuracion()

    assert configuracion.timeout == 12.5
    assert configuracion.ca == str(tmp_path)


def test_leer_configuracion_rechaza_timeout_no_numerico(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _configurar_obligatorias(monkeypatch)
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", "mucho")

    with pytest.raises(ia.ErrorIA) as info:
        ia.leer_configuracion()

    assert "debe ser un número de segundos" in str(info.value)


@pytest.mark.parametrize("valor", ["0", "-3"])
def test_leer_configuracion_rechaza_timeout_no_positivo(
    monkeypatch: pytest.MonkeyPatch, valor: str
) -> None:
    _configurar_obligatorias(monkeypatch)
    monkeypatch.setenv("TAREAS_IA_TIMEOUT", valor)

    with pytest.raises(ia.ErrorIA) as info:
        ia.leer_configuracion()

    assert "mayor que cero" in str(info.value)


def test_crear_cliente_rechaza_ca_inexistente(tmp_path: Path) -> None:
    configuracion = ia.ConfiguracionIA(
        url="https://centro.invalid",
        modelo="modelo",
        clave="clave",
        timeout=30,
        ca=str(tmp_path / "no-existe.pem"),
    )

    with pytest.raises(ia.ErrorIA) as info:
        ia.crear_cliente(configuracion)

    assert "No se encuentra el certificado CA" in str(info.value)


def test_crear_cliente_usa_capath_para_un_directorio_de_ca(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    RealContexto = ssl.create_default_context
    visto: dict[str, Any] = {}

    def crear_contexto(**kwargs: Any) -> ssl.SSLContext:
        visto.update(kwargs)
        return RealContexto()

    monkeypatch.setattr(ia.ssl, "create_default_context", crear_contexto)
    configuracion = ia.ConfiguracionIA(
        url="https://centro.invalid",
        modelo="modelo",
        clave="clave",
        timeout=30,
        ca=str(tmp_path),
    )

    cliente = ia.crear_cliente(configuracion)
    cliente.close()

    assert visto == {"capath": str(tmp_path)}
    assert isinstance(cliente, httpx.Client)


def test_crear_cliente_usa_cafile_para_un_archivo_de_ca(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    ruta_ca = tmp_path / "ca.pem"
    ruta_ca.write_bytes(b"certificado de prueba")
    RealContexto = ssl.create_default_context
    visto: dict[str, Any] = {}

    def crear_contexto(**kwargs: Any) -> ssl.SSLContext:
        visto.update(kwargs)
        return RealContexto()

    monkeypatch.setattr(ia.ssl, "create_default_context", crear_contexto)
    configuracion = ia.ConfiguracionIA(
        url="https://centro.invalid",
        modelo="modelo",
        clave="clave",
        timeout=30,
        ca=str(ruta_ca),
    )

    cliente = ia.crear_cliente(configuracion)
    cliente.close()

    assert visto == {"cafile": str(ruta_ca)}
    assert isinstance(cliente, httpx.Client)


def test_mostrar_resumen_sin_protocolo_no_inventa_la_peticion() -> None:
    with pytest.raises(ia.ErrorIA) as info:
        ia.mostrar_resumen("texto de prueba")

    mensaje = str(info.value)
    assert "mostrar_resumen" in mensaje
    assert "Falta el protocolo del centro" in mensaje
    assert "No voy a inventarlos" in mensaje


def test_mostrar_tema_sin_protocolo_no_inventa_la_peticion() -> None:
    with pytest.raises(ia.ErrorIA) as info:
        ia.mostrar_tema("texto de prueba")

    mensaje = str(info.value)
    assert "mostrar_tema" in mensaje
    assert "Falta el protocolo del centro" in mensaje


def test_comprobar_con_configuracion_explicita_no_lee_entorno_ni_red(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ClienteFalso:
        def __enter__(self) -> "ClienteFalso":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    def prohibido(*args: object, **kwargs: object) -> None:
        raise AssertionError("comprobar() intentó leer el entorno o crear un cliente real")

    monkeypatch.setattr(ia, "leer_configuracion", prohibido)
    monkeypatch.setattr(ia, "crear_cliente", lambda config: ClienteFalso())
    configuracion = ia.ConfiguracionIA(
        url="https://centro.invalid",
        modelo="modelo-explicito",
        clave="clave-secreta",
        timeout=7,
    )

    mensajes = ia.comprobar(configuracion)

    assert len(mensajes) == 4
    assert "modelo-explicito" in mensajes[0]
    assert "7 s" in mensajes[1]
    assert "bundle de certificados por defecto" in mensajes[2]
    assert "falta el protocolo" in mensajes[3]
    assert all("clave-secreta" not in mensaje for mensaje in mensajes)
