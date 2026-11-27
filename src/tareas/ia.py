"""Proveedor IA del centro, aislado de la ejecución local."""

from __future__ import annotations

import os
import ssl
from dataclasses import dataclass
from pathlib import Path

import httpx

VARIABLES_OBLIGATORIAS = ("TAREAS_IA_URL", "TAREAS_IA_MODELO", "TAREAS_IA_CLAVE")
TIEMPO_ESPERA_POR_DEFECTO = 30.0


class ErrorIA(Exception):
    """Error de configuración o comunicación con el centro."""


@dataclass(frozen=True)
class ConfiguracionIA:
    """Valores leídos del entorno del proceso; nunca del fichero .env."""

    url: str
    modelo: str
    clave: str
    timeout: float
    ca: str | None = None


def leer_configuracion() -> ConfiguracionIA:
    """Lee las variables de entorno y explica qué falta sin revelar valores."""
    valores = {
        nombre: (os.environ.get(nombre) or "").strip()
        for nombre in VARIABLES_OBLIGATORIAS
    }
    faltan = [nombre for nombre, valor in valores.items() if not valor]
    if faltan:
        raise ErrorIA(
            "Faltan datos del centro: " + ", ".join(faltan) + ". "
            "Exporta las variables antes de ejecutar el comando."
        )

    texto_timeout = (os.environ.get("TAREAS_IA_TIMEOUT") or "").strip()
    if texto_timeout:
        try:
            timeout = float(texto_timeout)
        except ValueError as exc:
            raise ErrorIA(
                "TAREAS_IA_TIMEOUT debe ser un número de segundos, p. ej. 30."
            ) from exc
        if timeout <= 0:
            raise ErrorIA("TAREAS_IA_TIMEOUT debe ser mayor que cero.")
    else:
        timeout = TIEMPO_ESPERA_POR_DEFECTO

    ca = (os.environ.get("TAREAS_IA_CA") or "").strip() or None
    return ConfiguracionIA(
        url=valores["TAREAS_IA_URL"],
        modelo=valores["TAREAS_IA_MODELO"],
        clave=valores["TAREAS_IA_CLAVE"],
        timeout=timeout,
        ca=ca,
    )


def crear_cliente(configuracion: ConfiguracionIA) -> httpx.Client:
    """Crea el cliente HTTPX con TLS activo y CA opcional."""
    opciones: dict[str, object] = {"trust_env": False}
    if configuracion.ca:
        ruta = Path(configuracion.ca)
        if not ruta.exists():
            raise ErrorIA(
                "No se encuentra el certificado CA indicado en TAREAS_IA_CA."
            )
        try:
            if ruta.is_dir():
                contexto = ssl.create_default_context(capath=str(ruta))
            else:
                contexto = ssl.create_default_context(cafile=str(ruta))
        except (OSError, ssl.SSLError) as exc:
            raise ErrorIA(
                "No se puede usar el certificado CA indicado en TAREAS_IA_CA."
            ) from exc
        opciones["verify"] = contexto

    return httpx.Client(timeout=httpx.Timeout(configuracion.timeout), **opciones)


def _sin_protocolo(operacion: str) -> ErrorIA:
    return ErrorIA(
        f"Falta el protocolo del centro para '{operacion}': necesito método HTTP, "
        "ruta, esquema del cuerpo de petición, campo donde enviar el texto y "
        "campo de respuesta con el resultado. No voy a inventarlos."
    )


def mostrar_resumen(
    texto: str, configuracion: ConfiguracionIA | None = None
) -> str:
    """Pide un resumen al centro cuando se conozca su protocolo."""
    raise _sin_protocolo("mostrar_resumen")


def mostrar_tema(texto: str, configuracion: ConfiguracionIA | None = None) -> str:
    """Pide el tema al centro cuando se conozca su protocolo."""
    raise _sin_protocolo("mostrar_tema")


def comprobar(configuracion: ConfiguracionIA | None = None) -> list[str]:
    """Comprueba la configuración local sin revelar credenciales."""
    config = configuracion or leer_configuracion()
    with crear_cliente(config):
        pass
    return [
        f"Configuración del centro leída; modelo '{config.modelo}'.",
        f"Tiempo de espera configurado: {config.timeout:g} s.",
        (
            "TLS verificado con la CA indicada en TAREAS_IA_CA."
            if config.ca
            else "TLS verificado con el bundle de certificados por defecto."
        ),
        "Cliente HTTPX creado; falta el protocolo del centro para una prueba de red.",
    ]
