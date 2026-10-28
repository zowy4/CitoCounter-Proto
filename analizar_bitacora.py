"""
analizar_bitacora.py - Herramienta de Análisis de Experimentos

Este script lee bitacora_experimentos.csv y genera estadísticas útiles
para el análisis de resultados (BM5) y justificación de parámetros.

USO:
    python analizar_bitacora.py

REQUISITOS:
    pip install pandas matplotlib (opcional)
"""

import csv
import os
from collections import defaultdict


def leer_bitacora(archivo="bitacora_experimentos.csv"):
    """Lee el archivo CSV de bitácora."""
    if not os.path.exists(archivo):
        print(f"❌ No se encontró el archivo: {archivo}")
        return []
    
    experimentos = []
    with open(archivo, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            experimentos.append(fila)
    
    return experimentos


def analizar_parametros(experimentos):
    """Analiza la distribución de parámetros usados."""
    print("\n" + "=" * 70)
    print("  ANÁLISIS DE PARÁMETROS")
    print("=" * 70)
    
    sigmas1 = []
    sigmas2 = []
    
    for exp in experimentos:
        try:
            s1 = float(exp['Sigma1'])
            s2 = float(exp['Sigma2'])
            sigmas1.append(s1)
            sigmas2.append(s2)
        except:
            continue
    
    if sigmas1:
        print(f"\n📊 SIGMA1:")
        print(f"   Mínimo:  {min(sigmas1):.2f}")
        print(f"   Máximo:  {max(sigmas1):.2f}")
        print(f"   Promedio: {sum(sigmas1)/len(sigmas1):.2f}")
        
        print(f"\n📊 SIGMA2:")
        print(f"   Mínimo:  {min(sigmas2):.2f}")
        print(f"   Máximo:  {max(sigmas2):.2f}")
        print(f"   Promedio: {sum(sigmas2)/len(sigmas2):.2f}")


def analizar_resultados(experimentos):
    """Analiza los resultados de detección."""
    print("\n" + "=" * 70)
    print("  ANÁLISIS DE RESULTADOS")
    print("=" * 70)
    
    total_celulas = []
    porcentajes_riesgo = []
    
    for exp in experimentos:
        try:
            tc = int(exp['Total_Celulas_Detectadas'])
            pr = float(exp['Porcentaje_Riesgo'])
            if tc > 0:  # Solo experimentos válidos
                total_celulas.append(tc)
                porcentajes_riesgo.append(pr)
        except:
            continue
    
    if total_celulas:
        print(f"\n📊 CÉLULAS DETECTADAS:")
        print(f"   Mínimo:  {min(total_celulas)}")
        print(f"   Máximo:  {max(total_celulas)}")
        print(f"   Promedio: {sum(total_celulas)/len(total_celulas):.1f}")
        
        print(f"\n📊 PORCENTAJE DE RIESGO:")
        print(f"   Mínimo:  {min(porcentajes_riesgo):.1f}%")
        print(f"   Máximo:  {max(porcentajes_riesgo):.1f}%")
        print(f"   Promedio: {sum(porcentajes_riesgo)/len(porcentajes_riesgo):.1f}%")


def encontrar_mejor_experimento(experimentos):
    """Identifica el experimento con mejor precisión estimada."""
    print("\n" + "=" * 70)
    print("  MEJOR EXPERIMENTO")
    print("=" * 70)
    
    mejor = None
    mejor_precision = 0
    
    for exp in experimentos:
        prec_str = exp.get('Precision_Estimada', '')
        if '/' in prec_str:
            try:
                correctos, total = prec_str.split('/')
                precision = int(correctos) / int(total)
                if precision > mejor_precision:
                    mejor_precision = precision
                    mejor = exp
            except:
                continue
    
    if mejor:
        print(f"\n🏆 ID: {mejor['ID_Prueba']}")
        print(f"   Imagen: {mejor['Imagen_Usada']}")
        print(f"   Sigma1: {mejor['Sigma1']}")
        print(f"   Sigma2: {mejor['Sigma2']}")
        print(f"   Precisión: {mejor['Precision_Estimada']} ({mejor_precision*100:.1f}%)")
        print(f"   Observaciones: {mejor['Observaciones_Cualitativas'][:60]}...")
    else:
        print("\n⚠️  No hay experimentos con precisión estimada aún.")
        print("   💡 Completa la columna 'Precision_Estimada' manualmente después de cada prueba.")


def listar_imagenes_procesadas(experimentos):
    """Lista todas las imágenes que se han procesado."""
    print("\n" + "=" * 70)
    print("  IMÁGENES PROCESADAS")
    print("=" * 70)
    
    imagenes = defaultdict(int)
    for exp in experimentos:
        img = exp.get('Imagen_Usada', '')
        if img:
            imagenes[img] += 1
    
    if imagenes:
        print()
        for img, count in sorted(imagenes.items()):
            print(f"   • {img:30s} ({count} prueba{'s' if count > 1 else ''})")
    else:
        print("\n⚠️  No hay imágenes registradas.")


def generar_recomendaciones(experimentos):
    """Genera recomendaciones basadas en los experimentos."""
    print("\n" + "=" * 70)
    print("  RECOMENDACIONES")
    print("=" * 70)
    
    n_experimentos = len(experimentos)
    
    if n_experimentos == 0:
        print("\n📝 Aún no hay experimentos registrados.")
        print("   Ejecuta: python main.py")
        return
    
    if n_experimentos < 5:
        print(f"\n📝 Solo tienes {n_experimentos} experimento(s).")
        print("   💡 Realiza al menos 5-10 pruebas para tener datos significativos.")
    
    # Verificar campos vacíos
    campos_vacios = 0
    for exp in experimentos:
        if not exp.get('Precision_Estimada') or not exp.get('Calidad_DoG'):
            campos_vacios += 1
    
    if campos_vacios > 0:
        print(f"\n📝 Hay {campos_vacios} experimento(s) con campos incompletos.")
        print("   💡 Completa manualmente:")
        print("      - Precision_Estimada (X/Y)")
        print("      - Calidad_DoG (Excelente/Buena/Regular/Mala)")
        print("      - Observaciones_Cualitativas")
    
    if n_experimentos >= 10:
        print(f"\n✅ ¡Excelente! Tienes {n_experimentos} experimentos.")
        print("   💡 Ya puedes:")
        print("      - Graficar Sigma1 vs. Precisión")
        print("      - Identificar parámetros óptimos")
        print("      - Escribir la sección de Resultados (BM5)")


def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("  CitoCounter Proto - Análisis de Bitácora")
    print("  Herramienta para BM5 (Análisis de Resultados)")
    print("=" * 70)
    
    experimentos = leer_bitacora()
    
    if not experimentos:
        print("\n⚠️  No se encontraron experimentos en la bitácora.")
        print("\n💡 Ejecuta primero: python main.py")
        return
    
    print(f"\n📊 Total de experimentos registrados: {len(experimentos)}")
    
    # Análisis
    analizar_parametros(experimentos)
    analizar_resultados(experimentos)
    encontrar_mejor_experimento(experimentos)
    listar_imagenes_procesadas(experimentos)
    generar_recomendaciones(experimentos)
    
    print("\n" + "=" * 70)
    print()


if __name__ == "__main__":
    main()
