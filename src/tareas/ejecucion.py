"""Ejecución de las acciones configuradas."""

import shutil
from collections.abc import Callable
from pathlib import Path

from tareas import ia
from tareas.config import Accion


class ErrorEjecucion(Exception):
    """Error al ejecutar una acción."""


def _archivos(directorio: Path, patron: str, etiqueta: str) -> list[Path]:
    try:
        return sorted(ruta for ruta in directorio.glob(patron) if ruta.is_file())
    except (OSError, ValueError, NotImplementedError) as exc:
        raise ErrorEjecucion(
            f"{etiqueta}: patrón '{patron}' no válido o no legible: {exc}"
        ) from exc


def _destino(accion: Accion, directorio: Path) -> Path:
    if not accion.destino:
        raise ErrorEjecucion(f"{accion.id}: falta el campo 'destino'.")
    return directorio / accion.destino


def _copiar(accion: Accion, directorio: Path, simular: bool) -> list[str]:
    if not directorio.is_dir():
        raise ErrorEjecucion(
            f"{accion.id}: no existe el directorio de trabajo '{directorio}'."
        )
    destino = _destino(accion, directorio)
    mensajes: list[str] = []
    archivos = _archivos(directorio, accion.patron, accion.id)
    if not archivos:
        mensajes.append(
            f"{accion.id}: ningún archivo coincide con '{accion.patron}' "
            f"en '{directorio}'."
        )
        return mensajes

    for archivo in archivos:
        objetivo = destino / archivo.name
        if objetivo.exists():
            mensajes.append(f"{accion.id}: ya existe '{objetivo}', no se sobrescribe.")
            continue
        if simular:
            mensajes.append(f"{accion.id}: copiaría '{archivo}' -> '{objetivo}'.")
            continue
        try:
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copy2(archivo, objetivo)
        except OSError as exc:
            raise ErrorEjecucion(
                f"{accion.id}: no se puede copiar '{archivo}': {exc.strerror or exc}"
            ) from exc
        mensajes.append(f"{accion.id}: copiado '{archivo}' -> '{objetivo}'.")
    return mensajes


def _crear_indice(accion: Accion, directorio: Path, simular: bool) -> list[str]:
    if not accion.origen:
        raise ErrorEjecucion(
            f"{accion.id}: la operación crear_indice necesita 'origen'."
        )
    origen = directorio / accion.origen
    objetivo = _destino(accion, directorio)
    if not origen.is_dir():
        raise ErrorEjecucion(
            f"{accion.id}: no existe el directorio de origen '{origen}'."
        )

    lineas: list[str] = []
    for archivo in _archivos(origen, accion.patron, accion.id):
        if archivo.resolve() == objetivo.resolve():
            continue
        lineas.append(archivo.relative_to(origen).as_posix())

    mensajes = [f"{accion.id}: {len(lineas)} archivos para el índice."]
    if objetivo.exists():
        mensajes.append(f"{accion.id}: ya existe '{objetivo}', no se sobrescribe.")
        mensajes.extend(f"  {linea}" for linea in lineas)
        return mensajes

    if simular:
        mensajes.append(
            f"{accion.id}: escribiría '{objetivo}' con {len(lineas)} líneas."
        )
        mensajes.extend(f"  {linea}" for linea in lineas)
        return mensajes

    try:
        objetivo.parent.mkdir(parents=True, exist_ok=True)
        objetivo.write_text(
            "\n".join(lineas) + ("\n" if lineas else ""), encoding="utf-8"
        )
    except OSError as exc:
        raise ErrorEjecucion(
            f"{accion.id}: no se puede escribir '{objetivo}': {exc.strerror or exc}"
        ) from exc
    mensajes.append(f"{accion.id}: índice escrito en '{objetivo}'.")
    mensajes.extend(f"  {linea}" for linea in lineas)
    return mensajes


def _aplicar_ia(
    accion: Accion,
    directorio: Path,
    simular: bool,
    verbo: str,
    consulta: Callable[[str], str],
) -> list[str]:
    if not directorio.is_dir():
        raise ErrorEjecucion(
            f"{accion.id}: no existe el directorio de trabajo '{directorio}'."
        )
    origen = directorio / accion.origen if accion.origen else directorio
    if not origen.is_dir():
        raise ErrorEjecucion(
            f"{accion.id}: no existe el directorio de origen '{origen}'."
        )

    archivos = _archivos(origen, accion.patron, accion.id)
    if not archivos:
        return [
            f"{accion.id}: ningún archivo coincide con '{accion.patron}' "
            f"en '{origen}'."
        ]

    mensajes: list[str] = []
    for archivo in archivos:
        nombre = archivo.relative_to(origen)
        if simular:
            mensajes.append(
                f"{accion.id}: enviaría el texto de '{nombre}' al modelo para {verbo}."
            )
            continue
        try:
            texto = archivo.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ErrorEjecucion(
                f"{accion.id}: no se puede leer '{nombre}' como texto UTF-8."
            ) from exc
        try:
            resultado = consulta(texto)
        except ia.ErrorIA as exc:
            raise ErrorEjecucion(f"{accion.id}: {exc}") from exc
        mensajes.append(f"{accion.id}: {nombre}")
        mensajes.append(f"  {resultado}")
    return mensajes


def _mostrar_resumen(accion: Accion, directorio: Path, simular: bool) -> list[str]:
    return _aplicar_ia(accion, directorio, simular, "resumir", ia.mostrar_resumen)


def _mostrar_tema(accion: Accion, directorio: Path, simular: bool) -> list[str]:
    return _aplicar_ia(
        accion, directorio, simular, "clasificar por tema", ia.mostrar_tema
    )


MANEJADORES: dict[str, Callable[[Accion, Path, bool], list[str]]] = {
    "copiar": _copiar,
    "crear_indice": _crear_indice,
    "mostrar_resumen": _mostrar_resumen,
    "mostrar_tema": _mostrar_tema,
}


def ejecutar_accion(
    accion: Accion, directorio: Path, simular: bool = False
) -> list[str]:
    manejador = MANEJADORES.get(accion.operacion)
    if manejador is None:
        raise ErrorEjecucion(
            f"{accion.id}: operación desconocida '{accion.operacion}'."
        )
    return manejador(accion, Path(directorio), simular)
