"""Tests para herlev_patches.py - Extracción de parches 256x256."""
import csv
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np

from src.herlev_patches import (
    PatchConfig,
    PatchInfo,
    aplicar_aumentacion,
    cargar_imagen_herlev,
    cargar_mascara_herlev,
    extraer_patch,
    generar_coordenadas_patch,
    generar_patch_id,
)


class HerlevPatchesTests(unittest.TestCase):
    """Pruebas unitarias para el pipeline de extracción de parches."""

    def test_cargar_imagen_herlev_returns_correct_array(self):
        """Verifica que la imagen se carga correctamente en escala de grises."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = Path(tmpdir) / "test_image.bmp"
            img_array = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
            cv2.imwrite(str(ruta), img_array)
            
            resultado = cargar_imagen_herlev(ruta)
            
            self.assertEqual(resultado.shape, (100, 100))
            self.assertEqual(resultado.dtype, np.uint8)

    def test_cargar_imagen_herlev_raises_on_missing_file(self):
        """Verifica que se lanza excepción para archivo inexistente."""
        with self.assertRaises(ValueError):
            cargar_imagen_herlev(Path("/nonexistent/image.bmp"))

    def test_cargar_mascara_herlev_returns_binary(self):
        """Verifica que la máscara se binariza correctamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ruta = Path(tmpdir) / "test_mask.png"
            mask = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
            cv2.imwrite(str(ruta), mask)
            
            resultado = cargar_mascara_herlev(ruta)
            
            unique_vals = set(np.unique(resultado).tolist())
            self.assertTrue(unique_vals.issubset({0, 255}))

    def test_generar_coordenadas_patch_yields_valid_positions(self):
        """Verifica que las coordenadas generadas son válidas para parches."""
        config = PatchConfig(patch_size=64, stride=32)
        
        coordenadas = list(generar_coordenadas_patch(100, 100, config))
        
        self.assertGreater(len(coordenadas), 0)
        for y, x in coordenadas:
            self.assertGreaterEqual(y, 0)
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(y + 64, 100)
            self.assertLessEqual(x + 64, 100)

    def test_extraer_patch_returns_correct_size(self):
        """Verifica que el parche extraído tiene el tamaño correcto."""
        img = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        config = PatchConfig(patch_size=64, stride=32)
        
        patch = extraer_patch(img, 32, 32, config)
        
        self.assertEqual(patch.shape, (64, 64))
        self.assertEqual(patch.dtype, np.uint8)

    def test_aplicar_aumentacion_original(self):
        """Verifica que la aumentación original no modifica la imagen."""
        img = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        
        result, rot, flip_h, flip_v = aplicar_aumentacion(img, "original")
        
        self.assertEqual(result.shape, img.shape)
        self.assertEqual(rot, 0)
        self.assertFalse(flip_h)
        self.assertFalse(flip_v)
        self.assertTrue(np.array_equal(result, img))

    def test_aplicar_aumentacion_rot90(self):
        """Verifica la aumentación rotación 90 grados."""
        img = np.arange(64 * 64, dtype=np.uint8).reshape(64, 64)
        
        result, rot, flip_h, flip_v = aplicar_aumentacion(img, "rot90")
        
        self.assertEqual(rot, 1)
        self.assertFalse(flip_h)
        self.assertFalse(flip_v)
        np.testing.assert_array_equal(result, np.rot90(img, k=1))

    def test_aplicar_aumentacion_flip_horizontal(self):
        """Verifica la aumentación flip horizontal."""
        img = np.arange(64 * 64, dtype=np.uint8).reshape(64, 64)
        
        result, rot, flip_h, flip_v = aplicar_aumentacion(img, "flip_horizontal")
        
        self.assertEqual(rot, 0)
        self.assertTrue(flip_h)
        self.assertFalse(flip_v)
        np.testing.assert_array_equal(result, np.fliplr(img))

    def test_aplicar_aumentacion_flip_vertical(self):
        """Verifica la aumentación flip vertical."""
        img = np.arange(64 * 64, dtype=np.uint8).reshape(64, 64)
        
        result, rot, flip_h, flip_v = aplicar_aumentacion(img, "flip_vertical")
        
        self.assertEqual(rot, 0)
        self.assertFalse(flip_h)
        self.assertTrue(flip_v)
        np.testing.assert_array_equal(result, np.flipud(img))

    def test_generar_patch_id_is_deterministic(self):
        """Verifica que el ID del parche es determinístico y único."""
        id1 = generar_patch_id("001", 0, 0, "original", 0)
        id2 = generar_patch_id("001", 0, 0, "original", 0)
        id3 = generar_patch_id("001", 10, 20, "rot90", 1)
        
        self.assertEqual(id1, id2)
        self.assertNotEqual(id1, id3)
        self.assertTrue(id1.startswith("patch_001"))

    def test_patch_dataclass_has_all_fields(self):
        """Verifica que PatchInfo contiene todos los campos requeridos."""
        info = PatchInfo(
            patch_id="patch_001_original",
            image_id="001",
            patch_x=0,
            patch_y=0,
            split="train",
            augmentation="original",
            rotation=0,
            flip_h=False,
            flip_v=False,
        )
        
        self.assertEqual(info.patch_id, "patch_001_original")
        self.assertEqual(info.image_id, "001")
        self.assertEqual(info.patch_x, 0)
        self.assertEqual(info.patch_y, 0)
        self.assertEqual(info.split, "train")
        self.assertEqual(info.augmentation, "original")


if __name__ == "__main__":
    unittest.main()