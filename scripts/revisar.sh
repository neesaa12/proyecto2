#!/usr/bin/env bash
# Revisa archivos con el subagente de solo lectura sin abrir la interfaz de OpenCode.
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "Uso: $0 ARCHIVO [ARCHIVO...]" >&2
  exit 2
fi

if [[ -n "${OPENCODE_BIN:-}" ]]; then
  opencode_bin="$OPENCODE_BIN"
elif command -v opencode >/dev/null 2>&1; then
  opencode_bin="opencode"
elif [[ -x /c/OpenCode/opencode.exe ]]; then
  opencode_bin="/c/OpenCode/opencode.exe"
else
  echo "Error: no se encuentra opencode. Define OPENCODE_BIN con su ruta." >&2
  exit 127
fi

archivos=()
for ruta in "$@"; do
  if [[ ! -f "$ruta" ]]; then
    echo "Error: no existe el archivo '$ruta'." >&2
    exit 2
  fi
  archivos+=("$ruta")
done

mensaje="Revisa los archivos indicados usando únicamente el subagente 'revisor'. "
mensaje+="No modifiques archivos, no ejecutes comandos y no delegues en otros agentes. "
mensaje+="Para cada problema, indica el nombre del archivo y cómo corregirlo. "
mensaje+="Si no encuentras problemas, dilo explícitamente. Archivos:"
for ruta in "${archivos[@]}"; do
  mensaje+=" $ruta"
done

"$opencode_bin" run --agent revisor --archived "$mensaje"
