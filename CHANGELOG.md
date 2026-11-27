# Changelog

Cambios destacables de `tareas`. El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa versionado semántico.

## [1.0.0] - 2026-11-27

Primera versión 1.0.0. Incluye lo que ya se puede usar desde la línea de comandos.

### Añadido

- **CLI en español** (`d92e97a`, `7440481`): `tareas --help`, `tareas version`, `tareas validar`, `tareas listar`, `tareas comprobar-ia` y `tareas ejecutar ID --directorio RUTA`. Los fallos se explican con mensajes en español, sin traceback y con código de salida distinto de cero.
- **Acciones configurables** (`3dbb7fa`): `acciones.json` es una lista de acciones escritas a mano, cada una con un `id` único. El fichero de ejemplo trae cinco acciones: reunir apuntes PDF, reunir capturas PNG, crear un índice, resumir un apunte y clasificarlo por tema.
- **Validación de `acciones.json`** (`cafdcce`, `e6fae92`): `tareas validar` detecta JSON mal formado, campos ausentes o vacíos, campos no admitidos, operaciones desconocidas e identificadores repetidos. Cuando todo está correcto, indica cuántas acciones se han leído.
- **Acciones locales sin conexión** (`cafdcce`): `copiar` reúne archivos según un patrón en una carpeta de destino sin sobrescribir los que ya existen; `crear_indice` genera un índice ordenado de rutas relativas. La opción `--simular` muestra qué haría cada acción sin escribir ficheros ni crear carpetas.
- **Acciones con IA preparadas** (`7440481`, `e6fae92`): `mostrar_resumen` y `mostrar_tema` leen archivos de texto y muestran el resultado en la terminal, sin modificar los originales. La configuración se toma de variables de entorno (URL, modelo, clave, tiempo de espera y CA opcional); la clave no aparece en pantalla ni en errores.
- **Cliente HTTP seguro** (`7440481`): HTTPX 0.28 con TLS activo, tiempo de espera configurable y certificado CA opcional mediante `ssl.create_default_context`; nunca se usa `verify=False`. `tareas comprobar-ia` revisa la configuración local, crea el cliente y explica qué falta, sin abrir conexión ni revelar credenciales.
- **Pruebas y automatización** (`e6fae92`, `5041cea`): cobertura de la CLI, la validación, la ejecución local, la ejecución IA simulada y la configuración sin credenciales y sin red. Un flujo de GitHub Actions ejecuta `uv sync --locked --dev` y `uv run pytest -q` en Ubuntu, Windows y macOS.
