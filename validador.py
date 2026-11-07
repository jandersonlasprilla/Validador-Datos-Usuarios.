"""Validador y analizador de datos de usuarios (CSV).

Lee un archivo CSV, valida cada registro, detecta duplicados y genera
un reporte en consola y en JSON. Usa solo la biblioteca estándar de Python.
"""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

REGEX_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
REGEX_TELEFONO = re.compile(r"^3\d{9}$")  # celular colombiano: 10 dígitos, empieza en 3
EDAD_MIN, EDAD_MAX = 18, 100


def validar_registro(fila: dict) -> list[str]:
    """Devuelve la lista de errores encontrados en un registro (vacía si es válido)."""
    errores = []
    if not fila.get("nombre", "").strip():
        errores.append("nombre vacío")
    if not REGEX_CORREO.match(fila.get("correo", "").strip()):
        errores.append("correo inválido")
    if not REGEX_TELEFONO.match(fila.get("telefono", "").strip()):
        errores.append("teléfono inválido")
    try:
        edad = int(fila.get("edad", ""))
        if not EDAD_MIN <= edad <= EDAD_MAX:
            errores.append(f"edad fuera de rango ({EDAD_MIN}-{EDAD_MAX})")
    except ValueError:
        errores.append("edad no numérica")
    return errores


def procesar(ruta_csv: Path) -> dict:
    """Valida todo el archivo y devuelve un diccionario con el resumen."""
    validos, invalidos, vistos = [], [], set()
    with ruta_csv.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            errores = validar_registro(fila)
            clave = (fila["correo"].strip().lower(), fila["telefono"].strip())
            if clave in vistos:
                errores.append("registro duplicado")
            vistos.add(clave)
            if errores:
                invalidos.append({"id": fila["id"], "errores": errores})
            else:
                validos.append(fila)

    ciudades = Counter(f["ciudad"] for f in validos)
    edades = [int(f["edad"]) for f in validos]
    return {
        "total": len(validos) + len(invalidos),
        "validos": len(validos),
        "invalidos": len(invalidos),
        "edad_promedio": round(sum(edades) / len(edades), 1) if edades else None,
        "usuarios_por_ciudad": dict(ciudades),
        "detalle_invalidos": invalidos,
    }


def imprimir_reporte(r: dict) -> None:
    print("=== REPORTE DE VALIDACIÓN ===")
    print(f"Total de registros : {r['total']}")
    print(f"Válidos            : {r['validos']}")
    print(f"Inválidos          : {r['invalidos']}")
    print(f"Edad promedio      : {r['edad_promedio']}")
    print("Usuarios por ciudad:", r["usuarios_por_ciudad"])
    print("\n--- Registros con errores ---")
    for item in r["detalle_invalidos"]:
        print(f"ID {item['id']}: {', '.join(item['errores'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida y analiza un CSV de usuarios.")
    parser.add_argument("archivo", type=Path, help="Ruta del archivo CSV")
    parser.add_argument("-o", "--salida", type=Path, default=Path("reporte.json"),
                        help="Archivo JSON de salida (por defecto: reporte.json)")
    args = parser.parse_args()

    resultado = procesar(args.archivo)
    imprimir_reporte(resultado)
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReporte guardado en {args.salida}")


if __name__ == "__main__":
    main()
