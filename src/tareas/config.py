"""Lectura y validación de acciones.json."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OPERACIONES_CONOCIDAS = {"copiar", "crear_indice"}
CAMPOS_COMUNES = ("id", "operacion", "patron", "destino")
CAMPOS_EXTRA = {"crear_indice": ("origen",)}


@dataclass(frozen=True)
class Accion:
    id: str
    operacion: str
    patron: str
    destino: str
    origen: str | None = None


class ErrorConfiguracion(Exception):
    """Errores de lectura o validación del fichero de acciones."""

    def __init__(self, mensajes: list[str]) -> None:
        super().__init__("; ".join(mensajes))
        self.mensajes = mensajes


def ruta_acciones() -> Path:
    return Path.cwd() / "acciones.json"


def leer_acciones(ruta: Path | None = None) -> list[Accion]:
    ruta = ruta or ruta_acciones()
    if not ruta.is_file():
        raise ErrorConfiguracion([f"No se encuentra el fichero {ruta.name}."])
    try:
        datos: Any = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ErrorConfiguracion(
            [
                f"JSON mal formado en {ruta.name}: {exc.msg} "
                f"(línea {exc.lineno}, columna {exc.colno})."
            ]
        ) from exc
    except UnicodeDecodeError as exc:
        raise ErrorConfiguracion(
            [f"{ruta.name} no está codificado en UTF-8: {exc.reason}."]
        ) from exc
    except OSError as exc:
        raise ErrorConfiguracion(
            [f"No se puede leer {ruta.name}: {exc.strerror or exc}."]
        ) from exc
    return validar_acciones(datos, ruta.name)


def validar_acciones(
    datos: Any, nombre_fichero: str = "acciones.json"
) -> list[Accion]:
    if not isinstance(datos, list):
        raise ErrorConfiguracion(
            [f"{nombre_fichero} debe contener una lista de acciones."]
        )

    errores: list[str] = []
    acciones: list[Accion] = []
    vistos: set[str] = set()

    for indice, elemento in enumerate(datos, start=1):
        if not isinstance(elemento, dict):
            errores.append(f"Acción {indice}: debe ser un objeto JSON.")
            continue

        id_valor = elemento.get("id")
        etiqueta = f"Acción {indice}"
        if isinstance(id_valor, str) and id_valor.strip():
            etiqueta += f" ('{id_valor}')"

        operacion = elemento.get("operacion")
        campos = (
            CAMPOS_COMUNES + CAMPOS_EXTRA.get(operacion, ())
            if isinstance(operacion, str)
            else CAMPOS_COMUNES
        )

        datos_validos: dict[str, str] = {}
        for campo in campos:
            if campo not in elemento:
                errores.append(f"{etiqueta}: falta el campo '{campo}'.")
                continue
            valor = elemento[campo]
            if not isinstance(valor, str) or not valor.strip():
                errores.append(f"{etiqueta}: el campo '{campo}' no puede estar vacío.")
                continue
            datos_validos[campo] = valor

        if (
            isinstance(operacion, str)
            and operacion.strip()
            and operacion not in OPERACIONES_CONOCIDAS
        ):
            errores.append(f"{etiqueta}: operación desconocida '{operacion}'.")

        id_limpio = datos_validos.get("id")
        if id_limpio is not None:
            if id_limpio in vistos:
                errores.append(f"{etiqueta}: el id '{id_limpio}' está repetido.")
            else:
                vistos.add(id_limpio)

        if all(campo in datos_validos for campo in campos):
            acciones.append(
                Accion(
                    id=datos_validos["id"],
                    operacion=datos_validos["operacion"],
                    patron=datos_validos["patron"],
                    destino=datos_validos["destino"],
                    origen=datos_validos.get("origen"),
                )
            )

    if errores:
        raise ErrorConfiguracion(errores)
    return acciones
