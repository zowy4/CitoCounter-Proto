"""
verificar_entorno.py - Script de Diagnóstico del Sistema

Ejecuta este script ANTES de la primera prueba para verificar que:
1. Todas las librerías están instaladas correctamente
2. La estructura de carpetas es correcta
3. Los archivos necesarios existen

USO:
    python verificar_entorno.py
"""

import sys
import os
from datetime import datetime


def imprimir_seccion(titulo):
    """Imprime una sección visual."""
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)


def verificar_python():
    """Verifica la versión de Python."""
    print(f"✓ Python {sys.version}")
    if sys.version_info < (3, 8):
        print("⚠️  ADVERTENCIA: Se recomienda Python 3.8 o superior")
        return False
    return True


def verificar_libreria(nombre, nombre_import=None):
    """Verifica que una librería esté instalada."""
    if nombre_import is None:
        nombre_import = nombre
    
    try:
        modulo = __import__(nombre_import)
        version = getattr(modulo, '__version__', 'desconocida')
        print(f"✓ {nombre} (versión {version})")
        return True
    except ImportError:
        print(f"✗ {nombre} NO INSTALADO")
        return False


def verificar_estructura_carpetas():
    """Verifica que existan las carpetas necesarias."""
    carpetas_requeridas = [
        "data",
        "data/raw",
        "data/ground_truth",
        "data/results",
        "src",
        "docs"
    ]
    
    todas_ok = True
    for carpeta in carpetas_requeridas:
        if os.path.exists(carpeta):
            print(f"✓ {carpeta}/")
        else:
            print(f"✗ {carpeta}/ NO EXISTE")
            todas_ok = False
    
    return todas_ok


def verificar_archivos_codigo():
    """Verifica que existan los archivos de código principales."""
    archivos_requeridos = [
        "main.py",
        "requirements.txt",
        "README.md",
        "bitacora_experimentos.csv",
        "src/__init__.py",
        "src/dog_filter.py",
        "src/analysis.py",
        "src/preprocessing.py",
        "src/visualization.py"
    ]
    
    todas_ok = True
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✓ {archivo}")
        else:
            print(f"✗ {archivo} NO EXISTE")
            todas_ok = False
    
    return todas_ok


def verificar_imagen_prueba():
    """Verifica si existe una imagen de prueba."""
    ruta_imagen = "data/raw/muestra_prueba.jpg"
    if os.path.exists(ruta_imagen):
        print(f"✓ {ruta_imagen} encontrado")
        
        # Intentar cargar con OpenCV
        try:
            import cv2
            img = cv2.imread(ruta_imagen)
            if img is not None:
                altura, ancho = img.shape[:2]
                print(f"  → Dimensiones: {ancho}×{altura} píxeles")
                return True
            else:
                print(f"⚠️  El archivo existe pero no se puede leer como imagen")
                return False
        except:
            print(f"⚠️  No se pudo verificar la imagen (OpenCV no disponible)")
            return False
    else:
        print(f"✗ {ruta_imagen} NO ENCONTRADO")
        print("  💡 Necesitas descargar una imagen de prueba:")
        print("     1. Busca en Google: 'Pap smear microscopy image'")
        print("     2. Guárdala como: data/raw/muestra_prueba.jpg")
        return False


def main():
    """Función principal de verificación."""
    print("\n" + "=" * 70)
    print("  CitoCounter Proto - Verificación del Entorno")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    resultados = {}
    
    # 1. Verificar Python
    imprimir_seccion("1. Versión de Python")
    resultados['python'] = verificar_python()
    
    # 2. Verificar librerías
    imprimir_seccion("2. Librerías Requeridas")
    librerias = [
        ('OpenCV', 'cv2'),
        ('NumPy', 'numpy'),
        ('Matplotlib', 'matplotlib'),
        ('Pillow', 'PIL')
    ]
    
    librerias_ok = []
    for nombre, import_name in librerias:
        librerias_ok.append(verificar_libreria(nombre, import_name))
    
    resultados['librerias'] = all(librerias_ok)
    
    # 3. Verificar estructura de carpetas
    imprimir_seccion("3. Estructura de Carpetas")
    resultados['carpetas'] = verificar_estructura_carpetas()
    
    # 4. Verificar archivos de código
    imprimir_seccion("4. Archivos de Código")
    resultados['archivos'] = verificar_archivos_codigo()
    
    # 5. Verificar imagen de prueba
    imprimir_seccion("5. Imagen de Prueba")
    resultados['imagen'] = verificar_imagen_prueba()
    
    # Resumen final
    imprimir_seccion("RESUMEN")
    
    todo_ok = all(resultados.values())
    
    if todo_ok:
        print("✅ ¡TODO LISTO!")
        print("\n🚀 Puedes ejecutar la primera prueba:")
        print("   python main.py")
    else:
        print("⚠️  FALTAN ALGUNOS REQUISITOS:")
        print()
        
        if not resultados['python']:
            print("❌ Actualiza Python a versión 3.8 o superior")
        
        if not resultados['librerias']:
            print("❌ Instala las librerías faltantes:")
            print("   pip install -r requirements.txt")
        
        if not resultados['carpetas']:
            print("❌ Verifica la estructura de carpetas")
        
        if not resultados['archivos']:
            print("❌ Algunos archivos de código faltan")
        
        if not resultados['imagen']:
            print("❌ Coloca una imagen de prueba en data/raw/muestra_prueba.jpg")
    
    print("\n" + "=" * 70)
    print()
    
    return 0 if todo_ok else 1


if __name__ == "__main__":
    sys.exit(main())
