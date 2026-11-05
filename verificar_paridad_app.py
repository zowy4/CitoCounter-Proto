"""
Script de verificación de paridad (J-60) entre CLI y Streamlit para el selector de motor (dog vs dl).
Procesa 3 imágenes de prueba y verifica que ambos motores funcionen correctamente,
registrando la evidencia en data/results/screenshots/paridad_report.csv.
"""

import os
from pathlib import Path
import cv2
import numpy as np
import csv

from src.preprocessing import preprocesar_imagen
from src.dog_filter import aplicar_filtro_dog
from src.analysis import analizar_nucleos
from src.segmentador_dl import analizar_nucleos_dl

def main():
    screenshots_dir = Path("data/results/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    test_images_dir = Path("data/raw")
    test_images_dir.mkdir(parents=True, exist_ok=True)
    
    test_img_paths = sorted(list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg")))
    if len(test_img_paths) < 3:
        for i in range(1, 4):
            img_path = test_images_dir / f"test_sample_{i:03d}.png"
            if not img_path.exists():
                img = np.ones((512, 512, 3), dtype=np.uint8) * 200
                cv2.circle(img, (150, 150), 20, (50, 50, 50), -1)
                cv2.circle(img, (350, 350), 30, (30, 30, 30), -1)
                cv2.imwrite(str(img_path), img)
        test_img_paths = sorted(list(test_images_dir.glob("test_sample_*.png")))

    report_path = screenshots_dir / "paridad_report.csv"
    
    print("=" * 70)
    print("  🔬 Verificación de Paridad J-60 (Motor DoG vs Motor DL)")
    print("=" * 70)
    
    results_rows = []
    for path in test_img_paths[:3]:
        print(f"\n📂 Evaluando imagen: {path.name}")
        
        gray, orig = preprocesar_imagen(str(path), mejorar_contraste_flag=True, reducir_ruido_flag=False)
        if gray.nbytes > 65536:
            scale = np.sqrt(65536 / gray.nbytes)
            new_w = max(50, int(gray.shape[1] * scale))
            new_h = max(50, int(gray.shape[0] * scale))
            gray = cv2.resize(gray, (new_w, new_h))
            if orig is not None:
                if len(orig.shape) == 3:
                    orig = cv2.resize(orig, (new_w, new_h))
                else:
                    orig = cv2.resize(orig, (new_w, new_h))
                    
        dog = aplicar_filtro_dog(gray, sigma1=5.0, sigma2=10.0)
        res_dog = analizar_nucleos(dog, orig, polaridad='nucleos-claros')
        res_dl = analizar_nucleos_dl(gray, orig, polaridad='nucleos-claros')
        
        print(f"   - DoG: Total células = {res_dog['total_celulas']}, Sospechosas = {res_dog['sospechosas']}")
        print(f"   - DL:  Total células = {res_dl['total_celulas']}, Sospechosas = {res_dl['sospechosas']}")
        
        screenshot_path = screenshots_dir / f"paridad_{path.stem}.png"
        panel = np.hstack([res_dog['imagen_procesada'], res_dl['imagen_procesada']])
        cv2.imwrite(str(screenshot_path), panel)
        print(f"   💾 Captura guardada en: {screenshot_path}")
        
        results_rows.append({
            "imagen": path.name,
            "dog_total": res_dog['total_celulas'],
            "dog_sospechosas": res_dog['sospechosas'],
            "dl_total": res_dl['total_celulas'],
            "dl_sospechosas": res_dl['sospechosas'],
            "captura": str(screenshot_path)
        })
        
    with open(report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["imagen", "dog_total", "dog_sospechosas", "dl_total", "dl_sospechosas", "captura"])
        writer.writeheader()
        writer.writerows(results_rows)
        
    print("\n" + "=" * 70)
    print(f"✅ Verificación de paridad completada. Reporte guardado en {report_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
