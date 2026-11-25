"""Script para limpiar y reescribir el archivo herlev_patches.py correctamente."""
import re

with open('src/herlev_patches.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar la sección problemática
old_section = r'''                    patch_id = generar_patch_id\(image_id, y, x, augment, patch_idx\)
                    
                    img_out = output_dir / f"\{patch_id\}\.png"
                    mask_out = output_dir / f"\{patch_id\}_mask\.png"
                    
                                        # Escritura eficiente con PIL
                                        Image\.fromarray\(img_aug\)\.save\(str\(img_out\), compress_level=6\)
                                        Image\.fromarray\(mask_aug\)\.save\(str\(mask_out\), compress_level=6\)
                    
                                        patches_info\.append\(PatchInfo\('''

new_section = '''                    patch_id = generar_patch_id(image_id, y, x, augment, patch_idx)
                    
                    img_out = output_dir / f"{patch_id}.png"
                    mask_out = output_dir / f"{patch_id}_mask.png"
                    
                    # Escritura eficiente con PIL
                    Image.fromarray(img_aug).save(str(img_out), compress_level=6)
                    Image.fromarray(mask_aug).save(str(mask_out), compress_level=6)
                    
                    patches_info.append(PatchInfo('''

content = re.sub(old_section, new_section, content)

with open('src/herlev_patches.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo actualizado")
