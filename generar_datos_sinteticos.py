"""
generar_datos_sinteticos.py - Generador de Metadatos Clínicos Sintéticos

Este script genera una base de datos clínica SINTÉTICA para proteger la privacidad
de pacientes reales mientras se mantiene realismo estadístico para la investigación.

PROPÓSITO:
- Cumplir con ética de investigación (anonimización)
- Proporcionar contexto clínico para validación del algoritmo
- Generar datos realistas basados en distribuciones estadísticas reales
- Permitir reproducibilidad del dataset

USO:
    python generar_datos_sinteticos.py

REQUISITOS:
    pip install pandas faker

SALIDA:
    CitoDataset_v1/metadata/clinical_data_synthetic.csv
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Intentar importar Faker, si no está instalado, usar generación básica
try:
    from faker import Faker
    USE_FAKER = True
    fake = Faker('es_MX')  # Datos en español de México
except ImportError:
    USE_FAKER = False
    print("⚠️  Faker no instalado. Usando generación básica.")
    print("   Para mejor calidad: pip install faker")


# ============================================================================
# CONFIGURACIÓN DEL DATASET
# ============================================================================

# Cantidad de registros a generar
CANTIDAD_MUESTRAS = 100  # Ajustar según el número de imágenes reales

# Distribuciones estadísticas basadas en literatura médica
DIAGNOSTICOS = {
    'NEGATIVO': 0.60,      # 60% de muestras normales
    'LSIL': 0.20,          # 20% lesiones de bajo grado
    'HSIL': 0.10,          # 10% lesiones de alto grado
    'ASC-US': 0.05,        # 5% células atípicas
    'INADECUADA': 0.05     # 5% muestras inadecuadas
}

CALIDAD_MUESTRA = [
    'Satisfactoria',
    'Limitada por inflamación',
    'Limitada por sangre',
    'Limitada por superposición celular',
    'Limitada por escasez celular'
]

METODO_TOMA = [
    'Convencional (Papanicolaou)',
    'Base Líquida (ThinPrep)',
    'Base Líquida (SurePath)'
]

ESTADOS_HORMONALES = [
    'Cíclica - Fase folicular',
    'Cíclica - Fase lútea',
    'Embarazo',
    'Post-menopáusica',
    'Pre-menárquica',
    'Lactancia'
]


def generar_id_sintetico():
    """Genera un ID sintético único."""
    if USE_FAKER:
        return fake.uuid4()[:8].upper()
    else:
        import uuid
        return str(uuid.uuid4())[:8].upper()


def generar_fecha_toma():
    """Genera una fecha realista en el último año."""
    if USE_FAKER:
        return fake.date_between(start_date='-1y', end_date='today')
    else:
        dias_atras = random.randint(0, 365)
        return (datetime.now() - timedelta(days=dias_atras)).date()


def generar_edad():
    """
    Genera edad con distribución normal centrada en 35 años.
    Refleja la distribución real de pacientes que se realizan Pap.
    """
    edad = int(random.gauss(35, 12))
    return max(18, min(75, edad))  # Limitar entre 18 y 75


def determinar_estado_hormonal(edad):
    """
    Determina estado hormonal basado en edad.
    Introduce correlaciones clínicamente realistas.
    """
    if edad < 18:
        return 'Pre-menárquica'
    elif edad < 25:
        return random.choice([
            'Cíclica - Fase folicular',
            'Cíclica - Fase lútea'
        ])
    elif edad < 45:
        weights = [0.35, 0.35, 0.15, 0.10, 0.05]
        return random.choices([
            'Cíclica - Fase folicular',
            'Cíclica - Fase lútea',
            'Embarazo',
            'Lactancia',
            'Post-menopáusica'
        ], weights=weights)[0]
    else:  # >45 años
        weights = [0.15, 0.15, 0.70]
        return random.choices([
            'Cíclica - Fase folicular',
            'Cíclica - Fase lútea',
            'Post-menopáusica'
        ], weights=weights)[0]


def determinar_vph(diagnostico, edad):
    """
    Determina resultado de VPH con correlación clínica realista.
    - HSIL/LSIL tienen mayor probabilidad de VPH+
    - Edad influye (pico en 20-30 años)
    """
    if diagnostico in ['HSIL', 'LSIL']:
        # 70-80% de lesiones son VPH positivas
        probabilidad_positivo = 0.75 if edad < 35 else 0.65
    elif diagnostico == 'ASC-US':
        probabilidad_positivo = 0.40
    else:
        # NEGATIVO o INADECUADA
        probabilidad_positivo = 0.15 if edad < 30 else 0.08
    
    return 'Positivo' if random.random() < probabilidad_positivo else 'Negativo'


def generar_dataset(cantidad=100):
    """
    Genera el dataset completo con metadatos sintéticos.
    
    Args:
        cantidad (int): Número de registros a generar
    
    Returns:
        pandas.DataFrame: Dataset con metadatos clínicos
    """
    
    print(f"🔬 Generando {cantidad} registros sintéticos...")
    
    dataset = []
    diagnosticos_list = list(DIAGNOSTICOS.keys())
    diagnosticos_weights = list(DIAGNOSTICOS.values())
    
    for i in range(1, cantidad + 1):
        # ID vinculado a la imagen (Ej. IMG_001)
        img_id = f"IMG_{i:03d}"
        
        # Generar edad con distribución realista
        edad = generar_edad()
        
        # Determinar estado hormonal correlacionado con edad
        estado_hormonal = determinar_estado_hormonal(edad)
        
        # Seleccionar diagnóstico (ponderado estadísticamente)
        diagnostico = random.choices(diagnosticos_list, weights=diagnosticos_weights)[0]
        
        # Calidad de muestra (satisfactoria en 80% de casos)
        calidad = random.choices(
            CALIDAD_MUESTRA,
            weights=[0.80, 0.08, 0.05, 0.04, 0.03]
        )[0]
        
        # Método de toma (convencional aún predomina en muchos centros)
        metodo = random.choices(
            METODO_TOMA,
            weights=[0.60, 0.25, 0.15]
        )[0]
        
        # Test de VPH (correlacionado con diagnóstico y edad)
        vph_test = determinar_vph(diagnostico, edad)
        
        # Generar registro completo
        registro = {
            'ID_Imagen': img_id,
            'ID_Paciente_Sintetico': generar_id_sintetico(),
            'Fecha_Toma': generar_fecha_toma(),
            'Edad': edad,
            'Estado_Hormonal': estado_hormonal,
            'Metodo_Toma': metodo,
            'Calidad_Muestra': calidad,
            'Diagnostico_Ref_Bethesda': diagnostico,
            'VPH_Test': vph_test,
            'Observaciones': ''  # Para completar manualmente si es necesario
        }
        
        dataset.append(registro)
        
        # Mostrar progreso cada 20 registros
        if i % 20 == 0:
            print(f"   Generados {i}/{cantidad} registros...")
    
    return pd.DataFrame(dataset)


def validar_coherencia(df):
    """
    Valida que los datos generados tengan coherencia clínica.
    """
    print("\n📊 Validando coherencia del dataset...")
    
    # Verificar distribución de diagnósticos
    distribucion = df['Diagnostico_Ref_Bethesda'].value_counts(normalize=True)
    print("\n   Distribución de diagnósticos:")
    for diag, prop in distribucion.items():
        print(f"   - {diag}: {prop*100:.1f}%")
    
    # Verificar correlación VPH-HSIL
    hsil_vph_pos = df[df['Diagnostico_Ref_Bethesda'] == 'HSIL']['VPH_Test'].value_counts()
    if 'Positivo' in hsil_vph_pos:
        print(f"\n   ✓ HSIL con VPH+: {hsil_vph_pos['Positivo']} de {hsil_vph_pos.sum()}")
    
    # Verificar rango de edades
    print(f"\n   Edad promedio: {df['Edad'].mean():.1f} años")
    print(f"   Rango de edad: {df['Edad'].min()}-{df['Edad'].max()} años")
    
    print("\n   ✅ Validación completada")


def main():
    """Función principal."""
    
    print("=" * 70)
    print("  CitoCounter Proto - Generador de Metadatos Sintéticos")
    print("  Protección de privacidad + Realismo estadístico")
    print("=" * 70)
    print()
    
    # Generar dataset
    df = generar_dataset(cantidad=CANTIDAD_MUESTRAS)
    
    # Validar coherencia
    validar_coherencia(df)
    
    # Crear directorio si no existe
    output_dir = 'CitoDataset_v1/metadata'
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar CSV
    output_path = os.path.join(output_dir, 'clinical_data_synthetic.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 Dataset guardado en: {output_path}")
    print(f"   Total de registros: {len(df)}")
    
    # Mostrar primeras filas como ejemplo
    print("\n📋 Primeras 5 filas del dataset:")
    print(df.head().to_string())
    
    print("\n" + "=" * 70)
    print("✅ GENERACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("📌 PRÓXIMOS PASOS:")
    print("   1. Revisar el archivo CSV generado")
    print("   2. Cuando obtengas imágenes reales del hospital:")
    print("      - Nómbralas como IMG_001.jpg, IMG_002.jpg, etc.")
    print("      - Ajusta manualmente las filas del CSV para que coincidan")
    print("      - Ejemplo: Si IMG_005.jpg tiene lesiones, asegura que su")
    print("        fila tenga Diagnostico_Ref_Bethesda = 'HSIL' o 'LSIL'")
    print("   3. Usa LabelImg para etiquetar las células en cada imagen")
    print()


if __name__ == "__main__":
    main()
