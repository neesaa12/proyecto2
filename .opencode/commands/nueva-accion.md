---
description: Guía al usuario para redactar a mano una nueva acción en acciones.json
---

Ayúdame a definir una acción nueva en `acciones.json` sin escribir ni modificar el fichero.

1. Carga la skill `acciones-json` si está disponible y usa su esquema como referencia.
2. Pregúntame con la herramienta de preguntas qué `operacion` quiero: `copiar` o `crear_indice`.
3. Según la operación, pregúntame solo los campos que corresponden:
   - `copiar`: `id`, `patron`, `destino`.
   - `crear_indice`: `id`, `patron`, `origen`, `destino`.
4. Antes de mostrar nada, lee `acciones.json` y comprueba que el `id` no esté repetido. Los ids actuales son `reunir-apuntes`, `reunir-capturas` y `crear-indice`. Si está repetido, avísame y pídeme otro.
5. Muéstrame el objeto JSON resultante en un bloque de código para que lo copie y lo añada yo a mano a la lista. No edites `acciones.json`, no ejecutes comandos para insertarlo y no escribas la acción en mi lugar.
6. Recuérdame que `origen` solo corresponde a `crear_indice` y que `destino` es una carpeta en `copiar` pero la ruta de un fichero en `crear_indice`.
