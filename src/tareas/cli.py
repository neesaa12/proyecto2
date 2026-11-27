"""Interfaz de línea de comandos del proyecto tareas."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import typer
from typer import core as typer_core
from typer import rich_utils
from typer._click import core as click_core
from typer._click import decorators as click_decorators
from typer._click import formatting as click_formatting

from tareas import __version__

_TRADUCCIONES = {
    "Arguments": "Argumentos",
    "Options": "Opciones",
    "Commands": "Comandos",
    "Error": "Error",
    "Aborted.": "Abortado.",
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


@app.command("version")
def version() -> None:
    """Muestra la versión del proyecto."""
    typer.echo(__version__)


@app.command("listar")
def listar() -> None:
    """Lista las acciones configuradas."""
    if not Path("acciones.json").exists():
        typer.echo("Todavía no hay acciones configuradas")
