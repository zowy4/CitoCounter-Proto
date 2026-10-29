import csv
import hashlib
import io
import struct
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import cv2
import numpy as np

from src.herlev_preparation import (
    _leer_dimensiones_bmp,
    main,
    preparar_dataset_herlev,
)


class HerlevPreparationTests(unittest.TestCase):
    def _crear_fixture(self, raiz: Path) -> tuple[Path, Path, Path]:
        fuente = raiz / "source"
        crops = fuente / "CROPPED"
        splits = raiz / "input_splits"
        fuente.mkdir()
        crops.mkdir()
        splits.mkdir()
        for ruta in (fuente / "source-a.bmp", crops / "source-a_crop-1.bmp"):
            self.assertTrue(
                cv2.imwrite(str(ruta), np.zeros((16, 16, 3), dtype=np.uint8))
            )
            (ruta.parent / f"{ruta.stem}_nuc01.dat").write_text(
                "2,2\n8,2\n8,8\n2,8\n",
                encoding="utf-8",
            )
        for split, image_ids in (
            ("train", ["source-a"]),
            ("val", []),
            ("test", []),
        ):
            with (splits / f"{split}.csv").open(
                "w", newline="", encoding="utf-8"
            ) as archivo:
                escritor = csv.DictWriter(
                    archivo,
                    fieldnames=("image_id", "image_name"),
                )
                escritor.writeheader()
                for image_id in image_ids:
                    escritor.writerow(
                        {"image_id": image_id, "image_name": f"{image_id}.bmp"}
                    )
        return fuente, splits, raiz

    def _hashes(self, directorio: Path) -> dict[str, str]:
        return {
            str(ruta.relative_to(directorio)): hashlib.sha256(
                ruta.read_bytes()
            ).hexdigest()
            for ruta in sorted(directorio.rglob("*"))
            if ruta.is_file()
        }

    def test_preparar_dataset_generates_deterministic_outputs_and_grouped_splits(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            fuente, splits, _ = self._crear_fixture(raiz)
            salida_uno = raiz / "prepared-one"
            salida_dos = raiz / "prepared-two"

            primero = preparar_dataset_herlev(
                fuente, splits, salida_uno, "Dyskeratotic"
            )
            segundo = preparar_dataset_herlev(
                fuente, splits, salida_dos, "Dyskeratotic"
            )

            self.assertEqual(primero, {
                "imagenes": 2,
                "celulas": 2,
                "train": 2,
                "val": 0,
                "test": 0,
            })
            self.assertEqual(primero, segundo)
            self.assertEqual(self._hashes(salida_uno), self._hashes(salida_dos))
            self.assertEqual(
                {ruta.name for ruta in (salida_uno / "cells").iterdir()},
                {"source-a_cells.csv", "source-a_crop-1_cells.csv"},
            )
            mascara = cv2.imread(
                str(salida_uno / "masks" / "source-a_mask.png"),
                cv2.IMREAD_UNCHANGED,
            )
            if mascara is None:
                self.fail("No se pudo leer la máscara generada.")
            self.assertEqual(mascara.shape, (16, 16))
            self.assertEqual(mascara.dtype, np.uint8)
            self.assertEqual(set(np.unique(mascara).tolist()), {0, 255})
            with (salida_uno / "cells" / "source-a_cells.csv").open(
                newline="", encoding="utf-8"
            ) as archivo:
                filas_celulas = list(csv.DictReader(archivo))
            self.assertEqual(len(filas_celulas), 1)
            self.assertEqual(filas_celulas[0]["Classification"], "Dyskeratotic")
            with (salida_uno / "splits" / "train.csv").open(
                newline="", encoding="utf-8"
            ) as archivo:
                filas = list(csv.DictReader(archivo))
            self.assertEqual(len(filas), 2)

    def test_preparar_dataset_no_sobrescribe_salida_existente(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            fuente, splits, _ = self._crear_fixture(raiz)
            salida = raiz / "prepared"
            salida.mkdir()
            marcador = salida / "keep.txt"
            marcador.write_text("original", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                preparar_dataset_herlev(fuente, splits, salida, "Dyskeratotic")

            self.assertEqual(marcador.read_text(encoding="utf-8"), "original")

    def test_preparar_dataset_rechaza_imagen_mayor_al_limite(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            fuente, splits, _ = self._crear_fixture(raiz)
            salida = raiz / "prepared"

            with self.assertRaisesRegex(ValueError, "excede el límite"):
                preparar_dataset_herlev(
                    fuente,
                    splits,
                    salida,
                    "Dyskeratotic",
                    max_archivo_imagen_bytes=1,
                )

            self.assertFalse(salida.exists())

    def test_leer_dimensiones_bmp_rechaza_cabecera_con_demasiados_pixeles(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "oversized.bmp"
            bmp_file_header = struct.pack("<2sIHHI", b"BM", 54, 0, 0, 40)
            dib_header_prefix = struct.pack("<iiHHII", 9000, 9000, 1, 24, 0, 0)
            ruta.write_bytes(bmp_file_header + dib_header_prefix)

            with self.assertRaisesRegex(ValueError, "exceden el límite"):
                _leer_dimensiones_bmp(ruta)

    def test_leer_dimensiones_bmp_rechaza_cabecera_invalida(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "invalid.bmp"
            ruta.write_bytes(b"not a BMP")

            with self.assertRaisesRegex(ValueError, "Cabecera BMP inválida"):
                _leer_dimensiones_bmp(ruta)

    def test_preparar_dataset_rechaza_manifiestos_con_solapamiento(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            fuente, splits, _ = self._crear_fixture(raiz)
            with (splits / "test.csv").open(
                "w", newline="", encoding="utf-8"
            ) as archivo:
                escritor = csv.DictWriter(
                    archivo,
                    fieldnames=("image_id", "image_name"),
                )
                escritor.writeheader()
                escritor.writerow(
                    {"image_id": "source-a", "image_name": "source-a.bmp"}
                )
            salida = raiz / "prepared"

            with self.assertRaisesRegex(ValueError, "un solo manifiesto"):
                preparar_dataset_herlev(fuente, splits, salida, "Dyskeratotic")

            self.assertFalse(salida.exists())

    def test_preparar_dataset_falla_sin_dejar_destino_parcial(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            fuente, splits, _ = self._crear_fixture(raiz)
            (fuente / "source-a_nuc01.dat").write_text(
                "malformed\n",
                encoding="utf-8",
            )
            salida = raiz / "prepared"

            with self.assertRaises(ValueError):
                preparar_dataset_herlev(fuente, splits, salida, "Dyskeratotic")

            self.assertFalse(salida.exists())
            self.assertEqual(
                {ruta.name for ruta in raiz.iterdir()},
                {"source", "input_splits"},
            )

    def test_main_cli_requiere_rutas_y_clasificacion(self):
        with self.assertRaises(SystemExit) as contexto:
            main([])

        self.assertEqual(contexto.exception.code, 2)

    def test_main_cli_escribe_salida_nueva_y_reporta_conteos(self):
        with tempfile.TemporaryDirectory() as directorio:
            raiz = Path(directorio)
            fuente, splits, _ = self._crear_fixture(raiz)
            salida = raiz / "cli-output"
            consola = io.StringIO()

            with redirect_stdout(consola):
                codigo = main(
                    [
                        "--source-dir",
                        str(fuente),
                        "--splits-dir",
                        str(splits),
                        "--output-dir",
                        str(salida),
                        "--classification",
                        "Dyskeratotic",
                    ]
                )

            self.assertEqual(codigo, 0)
            self.assertTrue((salida / "cells").is_dir())
            self.assertIn("imagenes: 2", consola.getvalue())
            self.assertIn("train: 2", consola.getvalue())


if __name__ == "__main__":
    unittest.main()
