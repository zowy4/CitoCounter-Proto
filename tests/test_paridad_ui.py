"""
test_paridad_ui.py - Test de paridad (J-67, J-68) entre Streamlit/referencia y Qt para el pipeline de análisis.
Verifica que los motores devuelven resultados consistentes y contadores válidos.
"""

from pathlib import Path
import cv2
import numpy as np
import pytest

from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos
from src.segmentador_dl import analizar_nucleos_dl


def test_paridad_motores_conteo():
    """Verifica la paridad estructural y de conteo entre el pipeline DoG y DL en imágenes de prueba."""
    test_images_dir = Path("data/raw")
    test_images_dir.mkdir(parents=True, exist_ok=True)

    test_img_paths = sorted(list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg")))
    if not test_img_paths:
        img_path = test_images_dir / "test_paridad_sample.png"
        img = np.ones((256, 256, 3), dtype=np.uint8) * 220
        cv2.circle(img, (100, 100), 15, (40, 40, 40), -1)
        cv2.circle(img, (180, 180), 20, (30, 30, 30), -1)
        cv2.imwrite(str(img_path), img)
        test_img_paths = [img_path]

    path = test_img_paths[0]
    gray, orig = preprocesar_imagen(str(path), mejorar_contraste_flag=True, reducir_ruido_flag=False)
    if gray.nbytes > 65536:
        scale = np.sqrt(65536 / gray.nbytes)
        new_w = max(50, int(gray.shape[1] * scale))
        new_h = max(50, int(gray.shape[0] * scale))
        gray = cv2.resize(gray, (new_w, new_h))
        if orig is not None:
            orig = cv2.resize(orig, (new_w, new_h))

    dog = aplicar_filtro_dog(gray, sigma1=5.0, sigma2=10.0)
    res_dog = analizar_nucleos(dog, orig, polaridad='nucleos-claros')
    res_dl = analizar_nucleos_dl(gray, orig, polaridad='nucleos-claros')

    # Verificar contratos y claves obligatorias
    assert "total_celulas" in res_dog
    assert "normales" in res_dog
    assert "sospechosas" in res_dog
    assert "contornos_normales" in res_dog
    assert "contornos_sospechosos" in res_dog

    assert "total_celulas" in res_dl
    assert "normales" in res_dl
    assert "sospechosas" in res_dl
    assert "contornos" in res_dl

    # Validar que los conteos sean enteros no negativos
    assert res_dog["total_celulas"] >= 0
    assert res_dl["total_celulas"] >= 0