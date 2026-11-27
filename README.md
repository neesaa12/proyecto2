# CLI de tareas

Herramienta de línea de comandos para preparar una entrega de clase. El proyecto define acciones locales para reunir apuntes y capturas y crear un índice, además de dos acciones que usan el modelo del centro: `mostrar_resumen` y `mostrar_tema`.

## Uso

Desde la raíz del proyecto se pueden ejecutar estos comandos:

- `uv run tareas --help` muestra la ayuda en español.
- `uv run tareas version` muestra la versión del proyecto.
- `uv run tareas validar` comprueba `acciones.json` y señala los errores encontrados.
- `uv run tareas listar` muestra los identificadores de las acciones configuradas.
- `uv run tareas ejecutar ID --directorio RUTA` aplica la acción indicada.
- `uv run tareas ejecutar ID --directorio RUTA --simular` muestra qué haría sin copiar ficheros, crear carpetas, escribir el índice ni enviar texto al modelo.
- `uv run tareas comprobar-ia` comprueba la configuración del proveedor IA sin revelar credenciales.

`acciones.json` se lee desde la raíz del proyecto. `--directorio` es la carpeta de trabajo: todas las rutas relativas del JSON (`origen` y `destino`) se resuelven dentro de ella. Los archivos de destino existentes no se sobrescriben; se omiten y se informa.

Identificadores actuales: `reunir-apuntes`, `reunir-capturas`, `crear-indice`, `resumir-apunte` y `clasificar-apunte`.

## Formato de acciones.json

El fichero contiene una lista de acciones. Cada acción tiene un `id` único y solo los campos admitidos por su operación.

| `operacion` | Campos admitidos |
| --- | --- |
| `copiar` | `id`, `operacion`, `patron`, `destino` |
| `crear_indice` | `id`, `operacion`, `patron`, `origen`, `destino` |
| `mostrar_resumen` | `id`, `operacion`, `patron`; `origen` es opcional |
| `mostrar_tema` | `id`, `operacion`, `patron`; `origen` es opcional |

| Campo | Significado |
| --- | --- |
| `id` | Nombre único que permite elegir la acción, como `reunir-apuntes`. |
| `operacion` | Trabajo que realizará la herramienta: `copiar`, `crear_indice`, `mostrar_resumen` o `mostrar_tema`. |
| `patron` | Regla para seleccionar archivos. Por ejemplo, `*.pdf`, `*.png`, `**/*` o `*.txt`. |
| `origen` | Carpeta donde empieza la búsqueda, relativa a `--directorio`. Es obligatorio en `crear_indice` y opcional en `mostrar_resumen` y `mostrar_tema`: si se omite, se busca en la propia carpeta `--directorio`. |
| `destino` | Carpeta de copias en `copiar`; ruta del fichero generado en `crear_indice`. No se usa en `mostrar_resumen` ni `mostrar_tema`. |

`tareas validar` detecta JSON mal formado, campos ausentes, valores vacíos, campos no admitidos, operaciones desconocidas e identificadores repetidos, y devuelve un código distinto de cero.

Las tres acciones locales funcionan sin conexión y sin credenciales del centro.

## Proveedor IA del centro

`mostrar_resumen` y `mostrar_tema` leen archivos de texto y muestran el resultado en la terminal precedido del `id` de la acción y del nombre del fichero. No escriben ficheros ni modifican los originales. En `--simular` solo se listan los ficheros que se enviarían; no se lee su contenido para envío y no se crea ninguna conexión.

La configuración local se declara en `.env.example`. Copia ese fichero a `.env`, rellena los valores y expórtalos en tu sesión antes de ejecutar:

```powershell
$env:TAREAS_IA_URL = "valor-de-la-clase"
$env:TAREAS_IA_MODELO = "valor-de-la-clase"
$env:TAREAS_IA_CLAVE = "tu-clave"
$env:TAREAS_IA_TIMEOUT = "30"
$env:TAREAS_IA_CA = "ruta-al-certificado-o-directorio"
```

El programa **no lee** `.env`; solo consulta variables de entorno. La clave nunca se muestra en pantalla ni en mensajes de error. `.env` ya está ignorado por Git.

- `TAREAS_IA_TIMEOUT` es opcional; si se deja vacío, el tiempo de espera es de 30 segundos.
- `TAREAS_IA_CA` es opcional. Si se configura, se crea un contexto SSL con `ssl.create_default_context(cafile=...)` o `capath=...` y se pasa a `httpx.Client(verify=ctx)`. La verificación TLS permanece activa; nunca se usa `verify=False`.
- Si faltan variables, hay un fallo de red o el centro rechaza la autenticación, la CLI muestra un mensaje en español y termina con código distinto de cero, sin traceback.

Las operaciones IA necesitan además el contrato técnico del centro: método HTTP, ruta, esquema del cuerpo de petición, campo donde enviar el texto y campo de respuesta con el resultado. Mientras ese contrato no se indique, la CLI no inventa la URL, el modelo ni el protocolo: `comprobar-ia` valida la configuración local y explica qué dato falta para poder enviar una petición de prueba.

## Acciones de la entrega

1. **Reunir apuntes.** Selecciona los PDF de la carpeta de trabajo y los copia a `entregar/apuntes`.
2. **Reunir capturas.** Selecciona las imágenes PNG de la carpeta de trabajo y las copia a `entregar/capturas`.
3. **Crear el índice.** Recorre `entregar` y escribe la lista de archivos en `entregar/indice.txt`. Las rutas se escriben en orden y relativas a `entregar`; el propio índice queda fuera de la lista.

Para definir otra acción local, se añade un objeto a la lista con un `id` nuevo y los campos de su operación. No hace falta cambiar el código Python.
