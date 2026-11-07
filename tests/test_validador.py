import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validador import validar_registro, procesar  # noqa: E402

OK = {"nombre": "Ana", "correo": "ana@example.com", "telefono": "3101234567", "edad": "25"}


class TestValidador(unittest.TestCase):
    def test_registro_valido(self):
        self.assertEqual(validar_registro(OK), [])

    def test_correo_invalido(self):
        self.assertIn("correo inválido", validar_registro({**OK, "correo": "ana@example"}))

    def test_telefono_invalido(self):
        self.assertIn("teléfono inválido", validar_registro({**OK, "telefono": "12345"}))

    def test_edad_no_numerica(self):
        self.assertIn("edad no numérica", validar_registro({**OK, "edad": "abc"}))

    def test_edad_fuera_de_rango(self):
        self.assertTrue(any("fuera de rango" in e for e in validar_registro({**OK, "edad": "17"})))

    def test_procesar_csv_de_ejemplo(self):
        r = procesar(Path(__file__).resolve().parent.parent / "data" / "usuarios.csv")
        self.assertEqual(r["total"], 8)
        self.assertEqual(r["validos"], 2)


if __name__ == "__main__":
    unittest.main()
