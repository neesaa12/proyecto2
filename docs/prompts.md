# Prompts clave del proyecto CLI Tareas

## Commit 4 · Planificar la primera versión de la CLI

> Para el commit 4, prepara el plan para `tareas --help`, `tareas version` y `tareas listar`. Como todavía no existe `acciones.json`, `listar` debe mostrar «Todavía no hay acciones configuradas». Yo escribiré ese archivo a mano más adelante. Deja la validación para otro commit y enséñame el plan antes de editar.

## Commit 8 · Crear pruebas automáticas

> Empezamos el commit 8. Lee la implementación real y crea al menos 28 pruebas útiles con pytest. Usa tmp_path para los ficheros y un proveedor simulado para la IA. Todas las pruebas deben funcionar sin internet, sin clave y sin leer mi .env.
>
> Cubre ayuda, versión, listado, validación del JSON, copia, índice, simulación sin escrituras, destinos existentes y conservación de originales ante un fallo. Para la IA cubre resumen, clasificación, credenciales ausentes, fallo de red y que --simular nunca invoque al proveedor.
>
> Ejecuta uv run pytest -q. Al terminar, dame una lista por archivo que explique qué comportamiento protege cada prueba y qué comprueba cada assert, para que yo los pueda auditar. Deja GitHub Actions para el commit 9 y el commit de Git en mis manos.

## Commit 9 · Ejecutar las pruebas en tres sistemas

> Empezamos el commit 9. Crea un flujo de GitHub Actions que ejecute las pruebas con uv y pytest en Windows, Ubuntu y macOS en cada push y pull request. Usa la versión de Python del proyecto y las dependencias de uv.lock. Las pruebas deben funcionar sin los datos de la IA del centro.
>
> Crea también scripts/revisar.sh para ejecutar el subagente revisor de solo lectura mediante opencode run sin abrir la interfaz. Comprueba la sintaxis con la versión instalada y explica cómo probar el script. Enséñame los cambios y deja el commit en mis manos.