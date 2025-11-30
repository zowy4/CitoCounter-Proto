"""
main.py - Ejecutable Principal de CitoCounter Proto v1.1 (CLI OPTIMIZADO)

MEJORAS v1.1:
- ✅ Argumentos de línea de comandos (argparse)
- ✅ Manejo moderno de rutas (pathlib)
- ✅ Procesamiento por lotes activado
- ✅ No necesitas editar código para cambiar parámetros

USO BÁSICO:
    python main.py                                    # Usa imagen por defecto
    python main.py data/raw/paciente_045.jpg          # Analiza una imagen específica
    python main.py --sigma1 2.0 --sigma2 4.0          # Experimenta con parámetros
    python main.py data/raw --lote --no-gui           # Procesa carpeta completa

ARGUMENTOS DISPONIBLES:
    ruta              Imagen o carpeta a analizar
    --lote            Procesar todas las imágenes de una carpeta
    --sigma1 FLOAT    Valor de sigma1 para DoG (default: 3.0)
    --sigma2 FLOAT    Valor de sigma2 para DoG (default: 5.0)
    --ruido           Activar reducción de ruido extra
    --no-contraste    Desactivar mejora de contraste CLAHE
    --no-gui          No mostrar ventanas (útil para lotes)
    --bitacora ID     Registrar en bitácora con ID específico

PIPELINE:
    1. Cargar imagen del microscopio
    2. Preprocesamiento (gris + mejora de contraste)
    3. Aplicar filtro DoG
    4. Análisis y clasificación (regla del 3x)
    5. Visualización y generación de reportes
"""

import argparse
import sys
import csv
from pathlib import Path
from datetime import datetime
import cv2

# Importar módulos del proyecto
from src.preprocessing import preprocesar_imagen, verificar_calidad_imagen
from src.dog_filter import aplicar_filtro_dog, calcular_sigmas_optimas
from src.analysis import analizar_nucleos, generar_reporte_estadistico
from src.visualization import (
    crear_panel_comparativo,
    dibujar_estadisticas_en_imagen,
    guardar_imagen_resultado,
    mostrar_ventanas_analisis,
    crear_vista_deteccion
)


# ============================================================================
# CONFIGURACIÓN POR DEFECTO
# ============================================================================

DEFAULT_IMAGEN = "data/raw/image.png"
DEFAULT_SIGMA1 = 3.0
DEFAULT_SIGMA2 = 5.0
ARCHIVO_BITACORA = "bitacora_experimentos.csv"


# ============================================================================
# FUNCIONES DE BITÁCORA
# ============================================================================

def registrar_en_bitacora(id_prueba, ruta_imagen, sigma1, sigma2, resultados, observaciones=""):
    """
    Registra automáticamente los resultados en la bitácora de experimentación.
    
    Esto asegura trazabilidad para justificar parámetros en la tesis (BM5).
    """
    from src.analysis import AREA_PROMEDIO_NUCLEO_NORMAL, FACTOR_RIESGO, AREA_MINIMA_NUCLEO
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_actual = datetime.now().strftime("%H:%M")
    
    # Crear entrada de bitácora
    nueva_fila = [
        id_prueba,
        fecha_actual,
        hora_actual,
        ruta_imagen.name if isinstance(ruta_imagen, Path) else str(ruta_imagen),
        sigma1,
        sigma2,
        AREA_PROMEDIO_NUCLEO_NORMAL,
        FACTOR_RIESGO,
        AREA_MINIMA_NUCLEO,
        resultados.get('total_celulas', 0),
        resultados.get('normales', 0),
        resultados.get('sospechosas', 0),
        f"{resultados.get('porcentaje_riesgo', 0.0):.1f}",
        "",  # Falsos positivos (manual)
        "",  # Falsos negativos (manual)
        "",  # Precisión estimada (manual)
        observaciones,
        "",  # Calidad DoG (manual)
        "",  # Ajuste siguiente (manual)
        "Sistema"  # Responsable
    ]
    
    # Escribir en CSV
    try:
        with open(ARCHIVO_BITACORA, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(nueva_fila)
        print(f"   ✅ Resultados registrados en bitácora: {id_prueba}")
    except Exception as e:
        print(f"   ⚠️  No se pudo escribir en bitácora: {e}")


def obtener_siguiente_id_prueba():
    """
    Genera el siguiente ID de prueba secuencial (T-001, T-002, etc.).
    """
    try:
        with open(ARCHIVO_BITACORA, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            if len(lineas) <= 1:  # Solo header
                return "T-001"
            ultima_linea = lineas[-1]
            ultimo_id = ultima_linea.split(',')[0]
            if ultimo_id.startswith('T-'):
                numero = int(ultimo_id.split('-')[1]) + 1
                return f"T-{numero:03d}"
    except:
        pass
    return "T-001"


# ============================================================================
# FUNCIÓN PRINCIPAL DE PROCESAMIENTO
# ============================================================================

def procesar_una_imagen(ruta_imagen, args):
    """
    Procesa una sola imagen dada su ruta (Path object).
    
    Args:
        ruta_imagen (Path): Ruta de la imagen a procesar
        args: Argumentos de línea de comandos
    
    Returns:
        dict: Resultados del análisis (o None si hubo error)
    """
    
    print(f"\n📂 Procesando: {ruta_imagen.name}")
    
    # 1. VERIFICACIÓN DE EXISTENCIA
    if not ruta_imagen.exists():
        print(f"❌ ERROR: No se encontró el archivo: {ruta_imagen}")
        return None
    
    # 2. PREPROCESAMIENTO
    print("   [1/5] Preprocesando...")
    try:
        imagen_gris, imagen_original = preprocesar_imagen(
            str(ruta_imagen),  # OpenCV necesita string
            mejorar_contraste_flag=not args.no_contraste,  # Doble negación: por defecto es True
            reducir_ruido_flag=args.ruido
        )
        
        # Verificar calidad (opcional, solo warning)
        metricas = verificar_calidad_imagen(imagen_gris)
        if not metricas['es_aceptable']:
            print(f"   ⚠️  Calidad sospechosa: {', '.join(metricas['advertencias'])}")
    
    except Exception as e:
        print(f"❌ Error al cargar imagen: {e}")
        return None
    
    # 3. FILTRO DOG
    print(f"   [2/5] Aplicando filtro DoG (σ1={args.sigma1}, σ2={args.sigma2})...")
    try:
        imagen_dog = aplicar_filtro_dog(imagen_gris, sigma1=args.sigma1, sigma2=args.sigma2)
    except Exception as e:
        print(f"❌ Error en filtro DoG: {e}")
        return None
    
    # 4. ANÁLISIS
    print("   [3/5] Analizando núcleos...")
    try:
        resultados = analizar_nucleos(imagen_dog, imagen_original)
        print(generar_reporte_estadistico(resultados))
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return None
    
    # 5. VISUALIZACIÓN Y GUARDADO
    print("   [4/5] Generando visualizaciones...")
    try:
        # Preparar imágenes
        imagen_con_stats = dibujar_estadisticas_en_imagen(
            resultados['imagen_procesada'], resultados
        )
        
        panel = crear_panel_comparativo(
            {
                'original': imagen_original,
                'gris': imagen_gris,
                'dog': imagen_dog,
                'resultado': imagen_con_stats
            },
            {
                'original': 'Original',
                'gris': 'Gris (CLAHE)',
                'dog': f'DoG (σ1={args.sigma1}, σ2={args.sigma2})',
                'resultado': 'Detección'
            }
        )
        
        # Guardar (usando pathlib para crear carpetas si no existen)
        carpeta_salida = Path("data/results")
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        
        nombre_base = ruta_imagen.stem  # Nombre sin extensión
        ruta_salida = carpeta_salida / f"PANEL_{nombre_base}.png"
        
        cv2.imwrite(str(ruta_salida), panel)
        print(f"   💾 Resultados guardados en: {ruta_salida}")
        
        # Mostrar ventanas solo si NO estamos en modo lote o si se pide explícitamente
        if not args.lote and not args.no_gui:
            mostrar_ventanas_analisis({
                "Panel Comparativo": panel
            })
    
    except Exception as e:
        print(f"⚠️  Error en visualización/guardado: {e}")
    
    # 6. REGISTRO EN BITÁCORA
    if args.bitacora:
        print("   [5/5] Registrando en bitácora...")
        registrar_en_bitacora(
            args.bitacora,
            ruta_imagen,
            args.sigma1,
            args.sigma2,
            resultados,
            observaciones=f"CLI: {' '.join(sys.argv[1:])}"
        )
    
    return resultados


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que maneja argumentos CLI y ejecuta el pipeline.
    """
    
    # --- CONFIGURACIÓN DE ARGUMENTOS (CLI) ---
    parser = argparse.ArgumentParser(
        description="CitoCounter Proto v1.1 - Análisis Celular con DoG + Regla del 3x",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:
  # Analizar imagen por defecto
  python main.py
  
  # Analizar imagen específica
  python main.py data/raw/paciente_045.jpg
  
  # Experimentar con parámetros DoG
  python main.py --sigma1 2.0 --sigma2 4.0
  
  # Procesar carpeta completa (modo lote)
  python main.py data/raw --lote --no-gui
  
  # Registrar en bitácora
  python main.py --bitacora T-003
  
Para más información, consulta README.md
        """
    )
    
    # Argumento posicional: La imagen o carpeta
    parser.add_argument(
        "ruta",
        nargs='?',
        default=DEFAULT_IMAGEN,
        help="Ruta a la imagen o carpeta a analizar"
    )
    
    # Argumentos opcionales (flags)
    parser.add_argument(
        "--lote",
        action="store_true",
        help="Procesar todas las imágenes de la carpeta especificada"
    )
    
    parser.add_argument(
        "--sigma1",
        type=float,
        default=DEFAULT_SIGMA1,
        help=f"Valor de Sigma 1 para DoG (default: {DEFAULT_SIGMA1})"
    )
    
    parser.add_argument(
        "--sigma2",
        type=float,
        default=DEFAULT_SIGMA2,
        help=f"Valor de Sigma 2 para DoG (default: {DEFAULT_SIGMA2})"
    )
    
    parser.add_argument(
        "--ruido",
        action="store_true",
        help="Activar reducción de ruido adicional (bilateral filter)"
    )
    
    parser.add_argument(
        "--no-contraste",
        action="store_true",
        help="Desactivar mejora de contraste CLAHE"
    )
    
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="No mostrar ventanas emergentes (útil para modo lote)"
    )
    
    parser.add_argument(
        "--bitacora",
        type=str,
        default=None,
        help="ID de prueba para registrar en bitácora (ej: T-003). Si no se especifica, usa auto-incremento"
    )
    
    args = parser.parse_args()
    
    # Auto-generar ID de bitácora si no se especifica
    if args.bitacora is None:
        args.bitacora = obtener_siguiente_id_prueba()
    
    # Convertir ruta a Path object
    ruta_entrada = Path(args.ruta)
    
    # --- BANNER DE INICIO ---
    print("=" * 70)
    print("  🔬 CitoCounter Proto v1.1 - CLI Optimizado")
    print(f"  📋 Modo: {'PROCESAMIENTO LOTE' if args.lote else 'IMAGEN INDIVIDUAL'}")
    print(f"  ⚙️  Parámetros DoG: σ1={args.sigma1}, σ2={args.sigma2}")
    print(f"  🔧 Preprocesamiento: CLAHE={'OFF' if args.no_contraste else 'ON'}, Ruido={'ON' if args.ruido else 'OFF'}")
    print(f"  📊 Bitácora: {args.bitacora}")
    print("=" * 70)
    
    # --- PROCESAMIENTO ---
    if args.lote:
        # ====================================================================
        # MODO CARPETA (LOTE)
        # ====================================================================
        if not ruta_entrada.is_dir():
            print(f"\n❌ Error: {ruta_entrada} no es una carpeta válida.")
            print("\n💡 INSTRUCCIONES:")
            print("   1. Verifica que la ruta sea correcta")
            print("   2. Usa --lote solo para carpetas con imágenes")
            return
        
        # Buscar todas las imágenes
        extensiones = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']
        archivos = []
        for ext in extensiones:
            archivos.extend(list(ruta_entrada.glob(ext)))
        
        if not archivos:
            print(f"\n⚠️  No se encontraron imágenes en {ruta_entrada}")
            print(f"   Extensiones buscadas: {', '.join(extensiones)}")
            return
        
        print(f"\n📁 Encontradas {len(archivos)} imágenes en {ruta_entrada}")
        
        # Procesar cada imagen
        resultados_totales = []
        for i, archivo in enumerate(archivos, 1):
            print(f"\n{'='*70}")
            print(f"Imagen {i}/{len(archivos)}")
            print(f"{'='*70}")
            
            # Generar ID único para cada imagen en lote
            id_lote = f"{args.bitacora}-{i:02d}"
            args_copia = argparse.Namespace(**vars(args))
            args_copia.bitacora = id_lote
            
            resultado = procesar_una_imagen(archivo, args_copia)
            if resultado:
                resultados_totales.append(resultado)
        
        # Resumen final del lote
        print("\n" + "=" * 70)
        print("📊 RESUMEN DEL PROCESAMIENTO LOTE")
        print("=" * 70)
        print(f"Total de imágenes procesadas: {len(resultados_totales)}/{len(archivos)}")
        
        if resultados_totales:
            total_celulas = sum(r['total_celulas'] for r in resultados_totales)
            total_sospechosas = sum(r['sospechosas'] for r in resultados_totales)
            print(f"Total de células detectadas: {total_celulas}")
            print(f"Total de células sospechosas: {total_sospechosas}")
            print(f"Promedio de riesgo: {(total_sospechosas/total_celulas*100 if total_celulas > 0 else 0):.1f}%")
        
        print("=" * 70)
    
    else:
        # ====================================================================
        # MODO INDIVIDUAL
        # ====================================================================
        if not ruta_entrada.exists():
            print(f"\n❌ ERROR: No se encontró la imagen en {ruta_entrada}")
            print("\n💡 INSTRUCCIONES:")
            print("   1. Coloca tus imágenes de microscopio en la carpeta data/raw/")
            print("   2. Verifica que la ruta y el nombre del archivo sean correctos")
            print(f"   3. Extensiones válidas: .jpg, .jpeg, .png, .tif, .tiff")
            return
        
        resultado = procesar_una_imagen(ruta_entrada, args)
        
        if resultado:
            print("\n" + "=" * 70)
            print("✅ PROCESAMIENTO COMPLETADO")
            print("=" * 70)
            print(f"Total células: {resultado['total_celulas']}")
            print(f"Riesgo: {resultado['porcentaje_riesgo']:.1f}%")
            print("=" * 70)


if __name__ == "__main__":
    main()
