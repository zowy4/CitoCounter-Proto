"""Script para corregir herlev_patches.py y ejecutar la extracción de parches."""
import sys

# Leer el archivo
with open('src/herlev_patches.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar si hay caracteres de espacio extra
lines = content.split('\n')
print(f"Total líneas: {len(lines)}")

# Mostrar las líneas problemáticas
for i, line in enumerate(lines[235:250], start=236):
    spaces = len(line) - len(line.lstrip())
    print(f"Línea {i}: {spaces} espacios - '{line[:60]}...'")

# Verificar si PIL está disponible
try:
    from PIL import Image
    print("\nPIL/Pillow disponible")
except ImportError:
    print("\nPIL/Pillow NO disponible, se necesita instalar")
