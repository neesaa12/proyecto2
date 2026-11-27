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
| `operacion` | string | Obligatorio. Valores usados en el proyecto: `copiar` o `crear_indice`. |
| `patron` | string | Obligatorio. Regla glob para seleccionar archivos: `*.pdf`, `*.png`, `**/*`. |
| `destino` | string | Obligatorio. En `copiar`, carpeta donde se guardan las copias. En `crear_indice`, ruta del fichero que se genera. |

## Campos según la operación

| `operacion` | Campos que lleva |
| --- | --- |
| `copiar` | `id`, `operacion`, `patron`, `destino`. No lleva `origen`. |
| `crear_indice` | `id`, `operacion`, `patron`, `origen`, `destino`. |

`origen` es un string que solo aparece en `crear_indice`: la carpeta desde la que empieza la búsqueda, p. ej. `entregar`.

## Regla de identificadores únicos

`id` no se puede repetir. Antes de proponer una acción nueva, lee `acciones.json` y comprueba que el `id` elegido no exista ya. Los ids actuales son `reunir-apuntes`, `reunir-capturas` y `crear-indice`. Si falta un campo obligatorio o se repite un `id`, señala qué acción hay que corregir.

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
