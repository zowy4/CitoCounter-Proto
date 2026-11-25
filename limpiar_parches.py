"""Script para limpiar el directorio de parches parciales."""
import shutil
from pathlib import Path

output_dir = Path("data/processed/herlev_patches")
if output_dir.exists():
    shutil.rmtree(output_dir.resolve())
    print(f"Directorio eliminado: {output_dir}")
else:
    print("Directorio no existe")
