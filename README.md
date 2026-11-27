# CLI de tareas

Herramienta de línea de comandos para preparar una entrega de clase. El proyecto define tres acciones: reunir los apuntes en PDF, reunir las capturas en PNG y crear un índice de la entrega.

## Uso actual

Desde la carpeta del proyecto se pueden ejecutar estos comandos:

- `uv run tareas --help` muestra la ayuda.
- `uv run tareas version` muestra la versión del proyecto.
- `uv run tareas listar` es el comando de listado.

En el commit 5, las tres acciones quedan definidas en `acciones.json`. Su ejecución y el modo `--simular` se implementarán en el commit 6.

## Formato de acciones.json

El fichero contiene una lista de acciones. Cada acción tiene un identificador único y describe qué ficheros usará y dónde dejará el resultado.

| Campo | Significado |
| --- | --- |
| `id` | Nombre único que permite elegir la acción, como `reunir-apuntes`. |
| `operacion` | Trabajo que realizará la herramienta, como copiar archivos o generar un índice. |
| `patron` | Regla para seleccionar archivos. Por ejemplo, `*.pdf` selecciona los que terminan en `.pdf`. |
| `origen` | Carpeta donde empieza la búsqueda. La acción del índice usa `entregar` para recorrer sus subcarpetas. |
| `destino` | Carpeta donde se guardarán las copias o ruta del archivo que se generará. |

## Acciones de la entrega

1. **Reunir apuntes.** Selecciona los PDF de la carpeta de entrada y los copia a `entregar/apuntes`.
2. **Reunir capturas.** Selecciona las imágenes PNG de la carpeta de entrada y las copia a `entregar/capturas`.
3. **Crear el índice.** Recorre `entregar` y escribe la lista de archivos en `entregar/indice.txt`. El propio índice queda fuera de la lista.

Para definir otra acción de copia, se añade un objeto a la lista con un `id` nuevo, la operación `copiar`, el patrón que interesa y la carpeta de destino.