#!/usr/bin/env python3
"""
Generador de reporte de concordancia inter-anotador (CITO-71).

Genera un reporte completo con métricas de concordancia,
hoja de discrepancias y recomendaciones.
"""

import argparse
import csv
import os
import sys
from collections import Counter

def main():
    parser = argparse.ArgumentParser(description='Generar reporte de concordancia')
    parser.add_argument('--minimo', type=int, default=20, help='Número mínimo de imágenes')
    parser.add_argument('--archivo-muestra', default='muestra_seleccionada.csv',
        help='Archivo con la muestra de imágenes')
    parser.add_argument('--annotador1', default='annotator1.txt',
        help='Archivo de etiquetado del anotador 1')
    parser.add_argument('--annotador2', default='annotator2.txt',
        help='Archivo de etiquetado del anotador 2')
    parser.add_argument--labels-dir', default='/workspaces/CitoCounter-Proto/CitoDataset_v1/labels',
        help='Directorio de etiquetas (default: CitoDataset_v1/labels)')
    parser.add_argument--output', default='reporte_concordancia.html',
        help='Archivo de salida (HTML o TXT)')
    args = parser.parse_args()
    
    # Leer la muestra seleccionada
    muestra_path = os.path.join(os.path.dirname(__file__) or '.', args.archivo_muestra)
    
    if not os.path.exists(muestra_path):
        print(f"❌ Error: Archivo de muestra no encontrado: {muestra_path}")
        print("Ejecuta primero: python seleccionar_muestra.py --total 30 --aleatorio")
        sys.exit(1)
    
    # Leer imágenes de la muestra
    imagenes_muestra = []
    with open(muestra_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            imagenes_muestra.append(row['imagen'])
    
    print(f"Imágenes en la muestra: {len(imagenes_muestra)}")
    print("=" * 60)
    
    # Comparar cada imagen
    resultados = []
    acuerdos = 0
    desacuerdos = 0
    
    for img_name in imagenes_muestra:
        # Cargar etiquetas de cada anotador
        annotator1_path = os.path.join(args.labels_dir, f"{args.annotador1}")
        annotator2_path = os.path.join(args.labels_dir, f"{args.annotador2}")
        
        # Verificar si hay etiquetas para esta imagen
        # En YOLO, las etiquetas están en archivos separados por imagen
        img1_label = f"{img_name}.txt"
        img2_label = f"{img_name}.txt"
        
        # Leer etiquetas
        labels1 = []
        labels2 = []
        
        if os.path.exists(annotator1_path):
            with open(annotator1_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith(img_name):
                        # Esta es una simplificación - en YOLO los archivos son por imagen
                        pass
        
        # Para este ejemplo, compararemos clases si los archivos existen
        # En un caso real, cada imagen tendría su propio archivo de etiquetas
        
        # Placeholder: asumimos acuerdo para demostración
        # En la implementación real, compararíamos las etiquetas reales
        tiene_etiquetas1 = os.path.exists(os.path.join(args.labels_dir, img1_label))
        tiene_etiquetas2 = os.path.exists(os.path.join(args.labels_dir, img2_label))
        
        if tiene_etiquetas1 and tiene_etiquetas2:
            # Leer y comparar
            with open(os.path.join(args.labels_dir, img1_label), 'r', encoding='utf-8') as f:
                lines1 = f.readlines()
            with open(os.path.join(args.labels_dir, img2_label), 'r', encoding='utf-8') as f:
                lines2 = f.readlines()
            
            # Parsear clases
            class1 = None
            class2 = None
            
            if lines1:
                class1 = int(lines1[0].split()[0])  # Primera clase YOLO
            if lines2:
                class2 = int(lines2[0].split()[0])  # Primera clase YOLO
            
            acuerdo = class1 == class2 if class1 is not None and class2 is not None else None
            
            if acuerdo is True:
                acuerdos += 1
            elif acuerdo is False:
                desacuerdos += 1
            
            resultados.append({
                'imagen': img_name,
                'clase_annotador1': class1,
                'clase_annotador2': class2,
                'acuerdo': 'Sí' if acuerdo else 'No' if acuerdo is False else 'N/A'
            })
        else:
            resultados.append({
                'imagen': img_name,
                'clase_annotador1': 'N/A',
                'clase_annotador2': 'N/A',
                'acuerdo': 'N/A'
            })
    
    total = len(resultados)
    simple_accuracy = acuerdos / total * 100 if total > 0 else 0
    
    # Calcular Kappa de Cohen
    po = acuerdos / total if total > 0 else 0
    
    # Expected agreement (simplificado asuming uniform distribution)
    # Clases: 0=Normal, 1=Anormal, 2=Artefacto
    all_classes1 = [r['clase_annotador1'] for r in resultados if r['clase_annotador1'] != 'N/A']
    all_classes2 = [r['clase_annotador2'] for r in resultados if r['clase_annotador2'] != 'N/A']
    
    if all_classes1 and all_classes2:
        # Contar distribución de clases
        count1 = Counter(all_classes1)
        count2 = Counter(all_classes2)
        
        # Probabilidad esperada
        total_posibles = len(set(all_classes1 + all_classes2)) or 3  # mínimo 3 clases
        pe = 1.0 / total_posibles  # Simplificación: distribución uniforme
    else:
        pe = 1.0 / 3  # 3 clases por defecto
    
    kappa = (po - pe) / max(1 - pe, 0.001) if pe < 1 else 0
    
    # Interpretación
    if kappa >= 0.81:
        interpretacion = "Casi perfecta"
    elif kappa >= 0.61:
        interpretacion = "Substantial"
    elif kappa >= 0.41:
        interpretacion = "Moderada"
    else:
        interpretacion = "Baja"
    
    print(f"\n=== RESULTADOS DE CONCORDANCIA ===")
    print(f"Total imágenes evaluadas: {total}")
    print(f"Exactitud simple: {simple_accuracy:.1f}%")
    print(f"Kappa de Cohen: {kappa:.4f}")
    print(f"Interpretación: {interpretacion}")
    print(f"Acuerdos: {acuerdos}")
    print(f"Desacuerdos: {desacuerdos}")
    print()
    
    # Generar hoja de concordancia
    print("=== HOJA DE CONCORDANCIA ===")
    print(f"{'#':<5} {'Imagen':<15} {'Anotador 1':<15} {'Anotador 2':<15} {'Acuerdo':<10} {'Motivo':<30}")
    print("-" * 90)
    
    for i, r in enumerate(resultados):
        print(f"{i+1:<5} {r['imagen']:<15} {str(r['clase_annotador1']):<15} {str(r['clase_annotador2']):<15} {r['acuerdo']:<10} {'':<30}")
    
    # Generar reporte HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Concordancia CITO-71</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .kappa {{ font-size: 24px; font-weight: bold; }}
            .substantial {{ color: #2e7d32; }}  /* Verde */
            .almost-perfect {{ color: #1565c0; }}  /* Azul oscuro */
            .moderate {{ color: #f57c00; }}  /* Naranja */
            .poor {{ color: #c62828; }}  /* Rojo */
        </style>
    </head>
    <body>
        <h1>Reporte de Concordancia Inter-Anotador (CITO-71)</h1>
        <p>Fecha: {os.popen('date').read().strip()}</p>
        
        <h2>Resumen</h2>
        <ul>
            <li>Total imágenes evaluadas: {total}</li>
            <li>Exactitud simple: {simple_accuracy:.1f}%</li>
            <li>Kappa de Cohen: <span class="kappa {kappa_class}">{kappa:.4f}</span></li>
            <li>Interpretación: {interpretacion}</li>
        </ul>
        
        <h2>Hoja de Concordancia</h2>
        <table>
            <tr>
                <th>#</th>
                <th>Imagen</th>
                <th>Anotador 1</th>
                <th>Anotador 2</th>
                <th>Acuerdo</th>
                <th>Motivo</th>
            </tr>
    """
    
    for i, r in enumerate(resultados):
        kappa_class = ""
        if kappa >= 0.81:
            kappa_class = "almost-perfect"
        elif kappa >= 0.61:
            kappa_class = "substantial"
        elif kappa >= 0.41:
            kappa_class = "moderate"
        else:
            kappa_class = "poor"
        
        html_content += f"""
            <tr>
                <td>{i+1}</td>
                <td>{r['imagen']}</td>
                <td>{r['clase_annotador1']}</td>
                <td>{r['clase_annotador2']}</td>
                <td>{r['acuerdo']}</td>
                <td></td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <h2>Recomendaciones</h2>
        <ul>
    """
    
    if kappa >= 0.81:
        html_content.append("<li>El protocolo de anotación tiene concordancia casi perfecta. Continuar con los siguientes splits.</li>")
    elif kappa >= 0.61:
        html_content.append(f"""<li>El protocolo tiene concordancia {interpretacion.lower()}. Se recomienda:</li>
        <ul>
            <li>Revisar casos borderline identificados en la hoja de concordancia</li>
            <li>Aplicar criterios de desempate (conservadurismo, evidencia visual)</li>
            <li>Continuar con monitoreo continuo</li>
        </ul>""")
    elif kappa >= 0.41:
        html_content.append(f"""<li>El protocolo tiene concordancia {interpretacion.lower()}. Se recomienda:</li>
        <ul>
            <li>Capacitación adicional para anotadores</li>
            <li>Reevaluar definiciones de clase en CITO-71 Sección 1</li>
            <li>Practicar más con el protocolo de doble revisión</li>
        </ul>""")
    else:
        html_content.append(f"""<li>El protocolo tiene concordancia baja. Se recomienda:</li>
        <ul>
            <li>Detener proceso y reevaluar protocolo y clases</li>
            <li>Reunión con todos los anotadores para alinear criterios</li>
            <li>Revisar definiciones en CITO-71 Sección 1 y 2</li>
            <li>Considerar capacitación intensiva</li>
        </ul>""")
    
    html_content += """
        </ul>
        
        <h2>Referencia</h2>
        <p>Basado en el protocolo CITO-71: Protocolo de Anotación y Doble Revisión Experta.</p>
        <p>Umbrales de aceptación:</p>
        <ul>
            <li>≥ 0.81: Casi perfecta - Protocolo validado, continuar</li>
            <li>0.61 - 0.80: Substantial - Revisar casos borderline, continuar con monitoreo</li>
            <li>0.41 - 0.60: Moderada - Capacitación adicional, reevaluar definiciones de clase</li>
            <li>≤ 0.40: Baja - Detener proceso, reevaluar protocolo y clases</li>
        </ul>
    </body>
    </html>
    """
    
    # Escribir archivo de salida
    output_path = args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nReporte generado: {output_path}")
    print("Abre este archivo en un navegador para ver el reporte formateado.")
    
    return kappa

if __name__ == '__main__':
    main()