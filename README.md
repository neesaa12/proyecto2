# CLI de tareas

Herramienta de línea de comandos para preparar una entrega de clase. El proyecto define tres acciones: reunir los apuntes en PDF, reunir las capturas en PNG y crear un índice de la entrega.

## Uso

Desde la raíz del proyecto se pueden ejecutar estos comandos:

- `uv run tareas --help` muestra la ayuda en español.
- `uv run tareas version` muestra la versión del proyecto.
- `uv run tareas validar` comprueba `acciones.json` y señala los errores encontrados.
- `uv run tareas listar` muestra los identificadores de las acciones configuradas.
- `uv run tareas ejecutar ID --directorio RUTA` aplica la acción indicada.
- `uv run tareas ejecutar ID --directorio RUTA --simular` muestra qué haría sin copiar ficheros, crear carpetas ni escribir el índice.

`acciones.json` se lee desde la raíz del proyecto. `--directorio` es la carpeta de trabajo: todas las rutas relativas del JSON (`origen` y `destino`) se resuelven dentro de ella. Los archivos de destino existentes no se sobrescriben; se omiten y se informa.

Identificadores disponibles: `reunir-apuntes`, `reunir-capturas` y `crear-indice`.

## Formato de acciones.json

El fichero contiene una lista de acciones. Cada acción tiene un identificador único y describe qué ficheros usará y dónde dejará el resultado.

| Campo | Significado |
| --- | --- |
| `id` | Nombre único que permite elegir la acción, como `reunir-apuntes`. |
| `operacion` | Trabajo que realizará la herramienta: `copiar` o `crear_indice`. |
| `patron` | Regla para seleccionar archivos. Por ejemplo, `*.pdf` selecciona los que terminan en `.pdf`. |
| `origen` | Carpeta donde empieza la búsqueda. Solo la acción del índice la usa; en este proyecto es `entregar`. |
| `destino` | Carpeta donde se guardan las copias o ruta del archivo que se generará. |

`copiar` usa `id`, `operacion`, `patron` y `destino`. `crear_indice` usa además `origen`. `tareas validar` detecta JSON mal formado, campos ausentes o vacíos, operaciones desconocidas e identificadores repetidos, y devuelve un código distinto de cero.

## Acciones de la entrega

1. **Reunir apuntes.** Selecciona los PDF de la carpeta de trabajo y los copia a `entregar/apuntes`.
2. **Reunir capturas.** Selecciona las imágenes PNG de la carpeta de trabajo y las copia a `entregar/capturas`.
3. **Crear el índice.** Recorre `entregar` y escribe la lista de archivos en `entregar/indice.txt`. Las rutas se escriben en orden y relativas a `entregar`; el propio índice queda fuera de la lista.

Para definir otra acción de copia, se añade un objeto a la lista con un `id` nuevo, la operación `copiar`, el patrón que interesa y la carpeta de destino. No hace falta cambiar el código Python.
