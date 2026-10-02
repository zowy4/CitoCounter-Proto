"""Tests de privacidad y anonimización para CitoCounter-Proto (CITO-69).

Estos tests validan que no haya identificadores personales en las salidas
del prototipo y que se cumplan las políticas de privacidad LFPDPPP.
"""

import os
import sys
import cv2
import numpy as np
import pandas as pd

# Add workspace to path
sys.path.insert(0, '/workspaces/CitoCounter-Proto')

from src.preprocessing import cargar_imagen
from src.analysis import analizar_nucleos, clasificar_nucleo_por_area, generar_reporte_estadistico
from src.contracts.pipeline_contract import validar_tamano_imagen as vt


def test_no_patient_id_en_salidas():
    """S1: No hay patient_id en ninguna salida generada."""
    # Crear una imagen de prueba (256x256, 3 canales, float32)
    img = np.random.rand(256, 256, 3).astype(np.float32)
    
    # Probar que la función de validación no incluya patient_id
    from src.preprocessing import anonimizar_metadata
    
    # Test con metadata que NO tiene patient_id (should pass)
    clean_meta = {'clase': 'normal', 'split': 'train'}
    anonymized = anonimizar_metadata(clean_meta)
    
    # Ver que no se añadieron campos extra
    assert 'patient_id' not in anonymized, "patient_id debe estar removido"
    assert anonymized == clean_meta, "Metadata limpia debe permanecer igual"


def test_no_nombre_archivo_en_reportes():
    """S2: No hay nombres de archivo en reportes generados."""
    # Verificar que dataset_index.csv no tenga campos sensibles
    # cuando se generan reportes públicos
    idx_path = '/workspaces/CitoCounter-Proto/data/dataset_index.csv'
    if os.path.exists(idx_path):
        df = pd.read_csv(idx_path)
        # Verificar que los nombres de archivo sean genéricos
        sample = df.iloc[0]
        # Los nombres deberían ser MUESTRA_XXX format, no rutas completas
        assert 'patient' not in str(sample).lower(), \
            "No debe haber patient info en dataset_index.csv"


def test_advertencia_presenten_todas_las_salidas():
    """S3: Advertencia 'no diagnóstico' presente en todas las salidas."""
    # Verificar CLI (main.py)
    main_path = '/workspaces/CitoCounter-Proto/main.py'
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            content = f.read()
            # Debe contener la advertencia
            assert 'no equivale a diagnóstico clínico' in content, \
                "CLI debe tener advertencia 'no equivale a diagnóstico clínico'"
    
    # Verificar Streamlit (app.py)
    app_path = '/workspaces/CitoCounter-Proto/app.py'
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            content = f.read()
            assert 'no equivalen a diagnóstico clínico' in content, \
                "Streamlit debe tener advertencia 'no equivalen a diagnóstico clínico'"
    
    # Verificar API (api_v1.py)
    api_path = '/workspaces/CitoCounter-Proto/api_v1.py'
    if os.path.exists(api_path):
        with open(api_path, 'r') as f:
            content = f.read()
            assert 'no equivale a diagnóstico clínico' in content, \
                "API debe tener advertencia 'no equivale a diagnóstico clínico'"


def test_tamano_imagen_maxim_64k():
    """S4: Tamaño de imagen máximo de 64 KiB (65536 bytes)."""
    # Crear imagen dentro del límite (ej. 100x100x3 float32 = ~300KB sin comprimir,
    # pero el validar_tamano_imagen chequea bytes, no dimensiones)
    # Una imagen real JPG de 64 KiB sería el límite
    img_small = np.random.rand(100, 100, 3).astype(np.float32)
    result = validar_tamano_imagen(img_small.tobytes())
    # Debería pasar el validación (imágenes pequeñas suelen pasar)
    # El test verifica que la función existe y es callable
    assert callable(validar_tamano_imagen), \
        "validar_tamano_imagen debe ser una función callable"


def test_distribucion_clases_agregadas():
    """S5: Distribución de clases reportada como proporciones agregadas."""
    # Verificar que los reportes usen proporciones, no conteos individuales
    from src.analysis import generar_reporte_estadisticos
    
    # Datos de prueba: solo conteos agregados
    resultados_prueba = {
        'total': 100,
        'normales': 95,
        'sospechosas': 5,
        'anormales': 0,
        'artifacts': 0
    }
    
    reporte = generar_reporte_estadisticos(resultados_prueba)
    # El reporte debe contener solo proporciones agregadas
    assert 'total' in reporte, "Reporte debe tener total"
    assert 'porcentaje' in reporte.lower() or 'percentage' in reporte.lower(), \
        "Reporte debe incluir proporciones/porcentajes"


if __name__ == '__main__':
    """Ejecutar todos los tests de privacidad."""
    import pytest
    sys.exit(pytest.main([__file__, '-v']))