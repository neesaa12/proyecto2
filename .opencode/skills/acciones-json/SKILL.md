---
name: Esquema de acciones.json
description: Explica el esquema de acciones.json del proyecto tareas, los campos de cada operación y la regla de id único; úsalo al crear o revisar acciones.
---

# Esquema de `acciones.json`

El fichero es una lista de objetos. Cada objeto es una acción. No hay otros niveles ni propiedades adicionales.

## Campos comunes

| Campo | Tipo | Regla |
| --- | --- | --- |
| `id` | string | Obligatorio en toda acción y único en toda la lista. Permite elegir la acción, p. ej. `reunir-apuntes`. |
| `operacion` | string | Obligatorio. Valores admitidos: `copiar`, `crear_indice`, `mostrar_resumen` y `mostrar_tema`. |
| `patron` | string | Obligatorio. Regla glob para seleccionar archivos: `*.pdf`, `*.png`, `**/*`, `*.txt`. |

## Campos según la operación

| `operacion` | Campos admitidos | Qué hace |
| --- | --- | --- |
| `copiar` | `id`, `operacion`, `patron`, `destino` | Copia los archivos que coinciden con `patron` a la carpeta `destino`. No lleva `origen`. |
| `crear_indice` | `id`, `operacion`, `patron`, `origen`, `destino` | Recorre `origen` y escribe en `destino` la lista de archivos encontrados. |
| `mostrar_resumen` | `id`, `operacion`, `patron` | Envía al modelo del centro el texto de los archivos encontrados y muestra el resumen en la terminal. `origen` es opcional; no lleva `destino`. |
| `mostrar_tema` | `id`, `operacion`, `patron` | Envía al modelo del centro el texto de los archivos encontrados y muestra el tema en la terminal. `origen` es opcional; no lleva `destino`. |

`origen` es la carpeta, relativa a `--directorio`, desde la que se buscan los archivos. Es obligatorio en `crear_indice`; en `mostrar_resumen` y `mostrar_tema` se puede omitir y entonces se busca en la propia carpeta `--directorio`. `destino` es la carpeta de copias en `copiar` y la ruta del fichero generado en `crear_indice`.

Cualquier campo que no aparezca en la fila correspondiente es un error de validación.

## Regla de identificadores únicos

`id` no se puede repetir. Antes de proponer una acción nueva, lee `acciones.json` y comprueba que el `id` elegido no exista ya. Los ids actuales son `reunir-apuntes`, `reunir-capturas`, `crear-indice`, `resumir-apunte` y `clasificar-apunte`. Si falta un campo obligatorio, aparece un campo no admitido o se repite un `id`, señala qué acción hay que corregir.

## Ejemplos reales del fichero

```json
{
  "id": "reunir-apuntes",
  "operacion": "copiar",
  "patron": "*.pdf",
  "destino": "entregar/apuntes"
}
```

```json
{
  "id": "crear-indice",
  "operacion": "crear_indice",
  "patron": "**/*",
  "origen": "entregar",
  "destino": "entregar/indice.txt"
}
```

OpenCode no debe redactar estas acciones en nombre del usuario: solo puede explicar el esquema, comprobarlo y mostrar el texto para que el usuario lo escriba a mano.
