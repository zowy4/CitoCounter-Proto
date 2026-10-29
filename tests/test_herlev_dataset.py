import csv
import tempfile
import unittest
from pathlib import Path

from src.herlev_dataset import (
    CAMPOS_CSV_CELULAS,
    MAX_MASCARA_BYTES,
    MAX_TAMANO_DAT_BYTES,
    cargar_poligono_dat,
    cargar_poligonos_citoplasma,
    cargar_poligonos_nucleo,
    guardar_csv_celulas,
    mapear_elementos_a_grupo_por_prefijo,
    poligonos_a_registros,
    propagar_splits_por_grupo,
    rasterizar_mascara,
)


class HerlevDatasetTests(unittest.TestCase):
    def _crear_imagen_y_anotaciones(self, raiz: Path) -> Path:
        imagen = raiz / "001.bmp"
        imagen.touch()
        (raiz / "001_nuc02.dat").write_text(
            "4, 5\n6, 5\n6, 7\n",
            encoding="utf-8",
        )
        (raiz / "001_nuc01.dat").write_text(
            "1, 2\n3, 2\n3, 4\n",
            encoding="utf-8",
        )
        (raiz / "001_cyt01.dat").write_text(
            "0, 1\n4, 1\n4, 5\n",
            encoding="utf-8",
        )
        return imagen

    def test_cargar_poligono_dat_lee_coordenadas_csv(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "poligono.dat"
            ruta.write_text("1,2\n3.5,4\n5,6\n", encoding="utf-8")

            poligono = cargar_poligono_dat(ruta)

        self.assertEqual(poligono, [(1.0, 2.0), (3.5, 4.0), (5.0, 6.0)])

    def test_cargar_poligono_dat_ignora_lineas_vacias(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "poligono.dat"
            ruta.write_text("1,2\n\n3,4\n5,6\n", encoding="utf-8")

            poligono = cargar_poligono_dat(ruta)

        self.assertEqual(len(poligono), 3)

    def test_cargar_poligono_dat_rechaza_archivo_vacio(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "vacio.dat"
            ruta.touch()

            with self.assertRaisesRegex(ValueError, "vacío"):
                cargar_poligono_dat(ruta)

    def test_cargar_poligono_dat_rechaza_coordenada_malformada(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "invalido.dat"
            ruta.write_text("1,2\nno-numero,4\n5,6\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "línea 2"):
                cargar_poligono_dat(ruta)

    def test_cargar_poligono_dat_rechaza_valores_no_finitos(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "no-finito.dat"
            ruta.write_text("1,2\nNaN,4\n5,6\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "no finita"):
                cargar_poligono_dat(ruta)

    def test_cargar_poligono_dat_rechaza_menos_de_tres_vertices(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "corto.dat"
            ruta.write_text("1,2\n3,4\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "tres vértices"):
                cargar_poligono_dat(ruta)

    def test_cargar_poligono_dat_rechaza_archivo_mayor_al_limite(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "grande.dat"
            ruta.write_bytes(b"0" * (MAX_TAMANO_DAT_BYTES + 1))

            with self.assertRaisesRegex(ValueError, "excede el límite"):
                cargar_poligono_dat(ruta)

    def test_cargar_poligono_dat_rechaza_ruta_inexistente(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "no-existe.dat"

            with self.assertRaises(FileNotFoundError):
                cargar_poligono_dat(ruta)

    def test_cargar_poligonos_nucleo_lee_archivos_en_orden(self):
        with tempfile.TemporaryDirectory() as directorio:
            imagen = self._crear_imagen_y_anotaciones(Path(directorio))

            poligonos = cargar_poligonos_nucleo(imagen)

        self.assertEqual(len(poligonos), 2)
        self.assertEqual(poligonos[0][0], (1.0, 2.0))
        self.assertEqual(poligonos[1][0], (4.0, 5.0))

    def test_cargar_poligonos_citoplasma_lee_archivo_correspondiente(self):
        with tempfile.TemporaryDirectory() as directorio:
            imagen = self._crear_imagen_y_anotaciones(Path(directorio))

            poligonos = cargar_poligonos_citoplasma(imagen)

        self.assertEqual(len(poligonos), 1)
        self.assertEqual(poligonos[0][0], (0.0, 1.0))

    def test_cargar_poligonos_rechaza_imagen_sin_anotaciones(self):
        with tempfile.TemporaryDirectory() as directorio:
            imagen = Path(directorio) / "002.bmp"
            imagen.touch()

            with self.assertRaisesRegex(FileNotFoundError, "No se encontraron"):
                cargar_poligonos_nucleo(imagen)

    def test_cargar_poligonos_rechaza_imagen_inexistente(self):
        with tempfile.TemporaryDirectory() as directorio:
            imagen = Path(directorio) / "no-existe.bmp"

            with self.assertRaises(FileNotFoundError):
                cargar_poligonos_nucleo(imagen)

    def test_rasterizar_mascara_retorna_union_binaria_uint8(self):
        poligonos = [
            [(1, 1), (3, 1), (3, 3), (1, 3)],
            [(2, 2), (4, 2), (4, 4), (2, 4)],
        ]

        mascara = rasterizar_mascara(poligonos, (6, 6))

        self.assertEqual(mascara.shape, (6, 6))
        self.assertEqual(mascara.dtype.name, "uint8")
        self.assertEqual(set(mascara.ravel().tolist()), {0, 255})
        self.assertEqual(int((mascara > 0).sum()), 14)

    def test_rasterizar_mascara_sin_poligonos_retorna_mascara_vacia(self):
        mascara = rasterizar_mascara([], (4, 5))

        self.assertEqual(mascara.shape, (4, 5))
        self.assertEqual(mascara.dtype.name, "uint8")
        self.assertEqual(int(mascara.sum()), 0)

    def test_rasterizar_mascara_recorta_poligono_parcialmente_exterior(self):
        poligono = [[(-2, -2), (2, -2), (2, 2), (-2, 2)]]

        mascara = rasterizar_mascara(poligono, (4, 4))

        self.assertEqual(int((mascara > 0).sum()), 9)
        self.assertTrue((mascara[0:3, 0:3] == 255).all())

    def test_rasterizar_mascara_poligono_fuera_de_imagen_no_pinta(self):
        poligono = [[(10, 10), (12, 10), (12, 12), (10, 12)]]

        mascara = rasterizar_mascara(poligono, (4, 4))

        self.assertEqual(int(mascara.sum()), 0)

    def test_rasterizar_mascara_rechaza_poligono_vacio(self):
        with self.assertRaisesRegex(ValueError, "al menos tres pares"):
            rasterizar_mascara([[]], (4, 4))

    def test_rasterizar_mascara_rechaza_poligono_de_un_punto(self):
        with self.assertRaisesRegex(ValueError, "al menos tres pares"):
            rasterizar_mascara([[(1, 1)]], (4, 4))

    def test_rasterizar_mascara_rechaza_coordenadas_no_finitas(self):
        with self.assertRaisesRegex(ValueError, "no finitas"):
            rasterizar_mascara(
                [[(0, 0), (2, 0), (float("inf"), 2)]],
                (4, 4),
            )

    def test_rasterizar_mascara_rechaza_dimensiones_invalidas(self):
        for dimensiones in ((0, 4), (-1, 4), (4,), (4, 4.5), (True, 4)):
            with self.subTest(dimensiones=dimensiones):
                with self.assertRaisesRegex(ValueError, "dimensiones"):
                    rasterizar_mascara([], dimensiones)

    def test_rasterizar_mascara_rechaza_dimensiones_excesivas(self):
        with self.assertRaisesRegex(ValueError, "excede el límite"):
            rasterizar_mascara([], (MAX_MASCARA_BYTES + 1, 1))

    def test_poligonos_a_registros_convierte_cajas_y_conserva_clasificacion(self):
        poligonos = [
            [(1.2, 2.2), (4.1, 2.2), (4.1, 5.1), (1.2, 5.1)],
            [(8, 8), (9, 8), (9, 9), (8, 9)],
        ]

        registros = poligonos_a_registros(
            poligonos,
            (12, 12),
            clasificacion="Dyskeratotic",
        )

        self.assertEqual(list(registros[0]), list(CAMPOS_CSV_CELULAS))
        self.assertEqual(
            registros,
            [
                {
                    "Cell_ID": "1",
                    "X": "1",
                    "Y": "2",
                    "Width": "4",
                    "Height": "4",
                    "Classification": "Dyskeratotic",
                    "Notes": "",
                },
                {
                    "Cell_ID": "2",
                    "X": "8",
                    "Y": "8",
                    "Width": "2",
                    "Height": "2",
                    "Classification": "Dyskeratotic",
                    "Notes": "",
                },
            ],
        )

    def test_poligonos_a_registros_recorta_caja_a_dimensiones(self):
        registros = poligonos_a_registros(
            [[(-2, -2), (2, -2), (2, 2), (-2, 2)]],
            (4, 4),
            clasificacion="Dyskeratotic",
        )

        self.assertEqual(
            (registros[0]["X"], registros[0]["Y"],
             registros[0]["Width"], registros[0]["Height"]),
            ("0", "0", "3", "3"),
        )

    def test_poligonos_a_registros_rechaza_poligono_fuera_de_imagen(self):
        with self.assertRaisesRegex(ValueError, "queda fuera de la imagen"):
            poligonos_a_registros(
                [[(10, 10), (12, 10), (12, 12), (10, 12)]],
                (4, 4),
                clasificacion="Dyskeratotic",
            )

    def test_poligonos_a_registros_sin_poligonos_retorna_lista_vacia(self):
        self.assertEqual(
            poligonos_a_registros([], (4, 4), clasificacion="Dyskeratotic"),
            [],
        )

    def test_poligonos_a_registros_rechaza_clasificacion_vacia(self):
        with self.assertRaisesRegex(ValueError, "etiqueta fuente no vacía"):
            poligonos_a_registros([], (4, 4), clasificacion=" ")

    def test_poligonos_a_registros_rechaza_dimensiones_invalidas(self):
        with self.assertRaisesRegex(ValueError, "dimensiones"):
            poligonos_a_registros([], (4, 0), clasificacion="Dyskeratotic")

    def test_guardar_csv_celulas_escribe_esquema_existente(self):
        with tempfile.TemporaryDirectory() as directorio:
            salida = Path(directorio) / "cells.csv"
            registros = poligonos_a_registros(
                [[(1, 1), (3, 1), (3, 3), (1, 3)]],
                (5, 5),
                clasificacion="Dyskeratotic",
            )

            guardar_csv_celulas(salida, registros)

            with salida.open(newline="", encoding="utf-8") as archivo:
                lector = csv.DictReader(archivo)
                self.assertEqual(tuple(lector.fieldnames or ()), CAMPOS_CSV_CELULAS)
                filas = list(lector)
            self.assertEqual(filas, registros)

    def test_guardar_csv_celulas_no_sobrescribe_salida_existente(self):
        with tempfile.TemporaryDirectory() as directorio:
            salida = Path(directorio) / "cells.csv"
            salida.write_text("contenido previo", encoding="utf-8")
            contenido_original = salida.read_text(encoding="utf-8")

            with self.assertRaises(FileExistsError):
                guardar_csv_celulas(salida, [])

            self.assertEqual(salida.read_text(encoding="utf-8"), contenido_original)

    def test_guardar_csv_celulas_rechaza_campos_inesperados(self):
        with tempfile.TemporaryDirectory() as directorio:
            salida = Path(directorio) / "cells.csv"

            with self.assertRaisesRegex(ValueError, "exactamente las columnas"):
                guardar_csv_celulas(salida, [{"unexpected": "value"}])

            self.assertFalse(salida.exists())

    def test_propagar_splits_por_grupo_mantiene_juntos_elementos_relacionados(self):
        resultado = propagar_splits_por_grupo(
            {
                "train": ["origen-a"],
                "val": ["origen-b"],
                "test": ["origen-c"],
            },
            {
                "origen-a": "origen-a",
                "crop-a-1": "origen-a",
                "crop-a-2": "origen-a",
                "origen-b": "origen-b",
                "crop-b-1": "origen-b",
                "origen-c": "origen-c",
                "crop-c-1": "origen-c",
            },
        )

        self.assertEqual(
            resultado,
            {
                "train": ["crop-a-1", "crop-a-2", "origen-a"],
                "val": ["crop-b-1", "origen-b"],
                "test": ["crop-c-1", "origen-c"],
            },
        )

    def test_propagar_splits_por_grupo_rechaza_fuga_entre_splits(self):
        with self.assertRaisesRegex(ValueError, "más de un split"):
            propagar_splits_por_grupo(
                {"train": ["origen-a"], "test": ["origen-a"]},
                {"origen-a": "origen-a", "crop-a": "origen-a"},
            )

    def test_propagar_splits_por_grupo_rechaza_elemento_sin_asignacion(self):
        with self.assertRaisesRegex(ValueError, "no está asignado"):
            propagar_splits_por_grupo(
                {"train": ["origen-a"]},
                {"origen-a": "origen-a", "crop-b": "origen-b"},
            )

    def test_propagar_splits_por_grupo_rechaza_grupo_sin_elementos(self):
        with self.assertRaisesRegex(ValueError, "sin elementos asociados"):
            propagar_splits_por_grupo(
                {"train": ["origen-a", "origen-b"]},
                {"origen-a": "origen-a"},
            )

    def test_propagar_splits_por_grupo_conserva_splits_vacios(self):
        self.assertEqual(
            propagar_splits_por_grupo(
                {"train": ["origen-a"], "val": []},
                {"origen-a": "origen-a"},
            ),
            {"train": ["origen-a"], "val": []},
        )

    def test_mapear_elementos_a_grupo_usa_prefijo_de_origen_mas_largo(self):
        resultado = mapear_elementos_a_grupo_por_prefijo(
            ["origen-1", "origen-10_crop"],
            ["origen-1", "origen-10"],
        )

        self.assertEqual(
            resultado,
            {"origen-1": "origen-1", "origen-10_crop": "origen-10"},
        )

    def test_mapear_elementos_a_grupo_rechaza_elemento_sin_origen(self):
        with self.assertRaisesRegex(ValueError, "No se encontró grupo"):
            mapear_elementos_a_grupo_por_prefijo(["desconocido"], ["origen-1"])

    def test_mapear_elementos_a_grupo_rechaza_grupos_repetidos(self):
        with self.assertRaisesRegex(ValueError, "deben ser únicos"):
            mapear_elementos_a_grupo_por_prefijo(
                ["ab_crop"],
                ["ab", "ab"],
            )


if __name__ == "__main__":
    unittest.main()