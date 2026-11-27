"""Interfaz de línea de comandos del proyecto tareas."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import typer
from typer import core as typer_core
from typer import rich_utils
from typer._click import decorators as click_decorators
from typer._click import formatting as click_formatting

from tareas import __version__
from tareas.config import ErrorConfiguracion, leer_acciones, ruta_acciones
from tareas.ejecucion import ErrorEjecucion, ejecutar_accion

_TRADUCCIONES = {
    "Arguments": "Argumentos",
    "Options": "Opciones",
    "Commands": "Comandos",
    "Error": "Error",
    "Aborted.": "Abortado.",
    "[required]": "[obligatorio]",
    "Show this message and exit.": "Muestra este mensaje y sale.",
    "Try [blue]'{command_path} {help_option}'[/] for help.": (
        "Prueba [blue]'{command_path} {help_option}'[/] para obtener ayuda."
    ),
}


def _traducir(mensaje: str) -> str:
    return _TRADUCCIONES.get(mensaje, mensaje)


def _configurar_ayuda_en_espanol() -> None:
    """Traduce los rótulos fijos que Typer/Click generan en inglés."""
    # Algunas cadenas se resuelven al importar y otras al renderizar la ayuda.
    typer_core._ = _traducir
    rich_utils._ = _traducir
    rich_utils.ARGUMENTS_PANEL_TITLE = _traducir("Arguments")
    rich_utils.OPTIONS_PANEL_TITLE = _traducir("Options")
    rich_utils.COMMANDS_PANEL_TITLE = _traducir("Commands")
    rich_utils.ERRORS_PANEL_TITLE = _traducir("Error")
    rich_utils.ABORTED_TEXT = _traducir("Aborted.")
    rich_utils.REQUIRED_LONG_STRING = _traducir("[required]")
    rich_utils.RICH_HELP = _traducir(
        "Try [blue]'{command_path} {help_option}'[/] for help."
    )

    escribir_uso_original = click_formatting.HelpFormatter.write_usage

    def escribir_uso(self, prog, args="", prefix=None):
        args = (
            args.replace("[OPTIONS]", "[OPCIONES]")
            .replace("COMMAND", "COMANDO")
            .replace("[ARGS]", "[ARGUMENTOS]")
        )
        return escribir_uso_original(
            self, prog, args, "Uso: " if prefix is None else prefix
        )

    click_formatting.HelpFormatter.write_usage = escribir_uso

    ayuda_opcion_original = click_decorators.help_option

    def ayuda_opcion(param_decls):
        def decorar(comando):
            ayuda_opcion_original(param_decls)(comando)
            comando.params[-1].help = _traducir("Show this message and exit.")
            return comando

        return decorar

    click_decorators.help_option = ayuda_opcion


_configurar_ayuda_en_espanol()

app = typer.Typer(
    help="Gestiona tus tareas desde la línea de comandos.",
    no_args_is_help=True,
    add_completion=False,
)


def _fallar_configuracion(exc: ErrorConfiguracion) -> None:
    for mensaje in exc.mensajes:
        typer.echo(f"Error: {mensaje}", err=True)
    raise typer.Exit(code=1)


@app.command("version")
def version() -> None:
    """Muestra la versión del proyecto."""
    typer.echo(__version__)


@app.command("validar")
def validar() -> None:
    """Comprueba que acciones.json cumple el esquema documentado."""
    try:
        acciones = leer_acciones()
    except ErrorConfiguracion as exc:
        _fallar_configuracion(exc)
    typer.echo(f"acciones.json es válido: {len(acciones)} acciones.")


@app.command("listar")
def listar() -> None:
    """Muestra los identificadores de las acciones configuradas."""
    if not ruta_acciones().is_file():
        typer.echo("Todavía no hay acciones configuradas")
        return
    try:
        acciones = leer_acciones()
    except ErrorConfiguracion as exc:
        _fallar_configuracion(exc)
    for accion in acciones:
        typer.echo(accion.id)


@app.command("ejecutar")
def ejecutar(
    identificador: str = typer.Argument(..., help="Identificador de la acción."),
    directorio: Path = typer.Option(
        ..., "--directorio", help="Carpeta de trabajo para entradas y salidas."
    ),
    simular: bool = typer.Option(
        False, "--simular", help="Muestra qué haría sin escribir nada."
    ),
) -> None:
    """Ejecuta una acción por su identificador."""
    try:
        acciones = leer_acciones()
    except ErrorConfiguracion as exc:
        _fallar_configuracion(exc)

    accion = next((item for item in acciones if item.id == identificador), None)
    if accion is None:
        typer.echo(f"Error: no existe la acción '{identificador}'.", err=True)
        raise typer.Exit(code=1)

    try:
        mensajes = ejecutar_accion(accion, directorio, simular)
    except ErrorEjecucion as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    for mensaje in mensajes:
        typer.echo(mensaje)
