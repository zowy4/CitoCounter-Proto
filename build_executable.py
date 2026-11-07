"""
build_executable.py - Script para empaquetar CitoCounter-Proto con PyInstaller (J-69).
Genera ejecutables independientes offline para CLI y Qt sin requerir Python instalado.
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("Iniciando empaquetado con PyInstaller para CitoCounter-Proto (J-69)...")
    
    # Asegurar que PyInstaller esté instalado
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller no encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Directorio base
    base_dir = Path(__file__).resolve().parent

    # Archivo de pesos del modelo cito95
    model_weights = base_dir / "models" / "cito95" / "best_model_weights.pt"
    
    qt_entry = base_dir / "qt_app" / "main.py"
    cli_entry = base_dir / "main.py"

    print("Empaquetando Aplicación Qt...")
    qt_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--name", "CitoCounter-Qt",
        "--onedir",
    ]
    if model_weights.exists():
        qt_cmd.extend(["--add-data", f"{model_weights};models/cito95"])
    qt_cmd.append(str(qt_entry))
    
    subprocess.run(qt_cmd, check=True)

    print("Empaquetando Aplicación CLI...")
    cli_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--console",
        "--name", "CitoCounter-CLI",
        "--onedir",
    ]
    if model_weights.exists():
        cli_cmd.extend(["--add-data", f"{model_weights};models/cito95"])
    cli_cmd.append(str(cli_entry))
    
    subprocess.run(cli_cmd, check=True)

    print("¡Empaquetado completado con éxito! Los binarios se encuentran en la carpeta dist/.")

if __name__ == "__main__":
    main()
