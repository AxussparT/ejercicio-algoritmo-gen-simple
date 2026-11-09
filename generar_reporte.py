"""
Script generador del reporte técnico formal en formato DOCX.
Compara Algoritmo Genético (AG) vs Enjambre de Partículas (PSO con pyswarm)
sobre las dos funciones requeridas:
1. Función Esfera 2D: f(x) = x1^2 + x2^2 en [-10, 10]
2. Función Rastrigin 2D: f(x) = 10*n + sum(x_i^2 - 10*cos(2*pi*x_i)) en [-5.12, 5.12]
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Establece color de fondo de celda."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece márgenes internos de celda en dxa."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_placeholder_box(doc, title, description, instructions):
    """Agrega un recuadro formateado tipo placeholder para pegar capturas de pantalla."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F1F5F9")  # Slate muy claro
    set_cell_margins(cell, top=180, bottom=180, left=220, right=220)

    # Borde discontinuo/elegante
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="dashed" w:sz="12" w:space="0" w:color="0284C7"/>'
        f'  <w:left w:val="dashed" w:sz="12" w:space="0" w:color="0284C7"/>'
        f'  <w:bottom w:val="dashed" w:sz="12" w:space="0" w:color="0284C7"/>'
        f'  <w:right w:val="dashed" w:sz="12" w:space="0" w:color="0284C7"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    p1 = cell.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run(f"📷 [ANEXAR CAPTURA AQUÍ: {title.upper()}]\n")
    r1.font.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = RGBColor(2, 132, 199)

    p2 = cell.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r2_bold = p2.add_run("• Contenido a mostrar: ")
    r2_bold.font.bold = True
    r2_bold.font.size = Pt(9.5)
    r2_bold.font.color.rgb = RGBColor(30, 41, 59)
    r2_desc = p2.add_run(f"{description}\n")
    r2_desc.font.size = Pt(9.5)
    r2_desc.font.color.rgb = RGBColor(71, 85, 105)

    r3_bold = p2.add_run("• Instrucciones de captura: ")
    r3_bold.font.bold = True
    r3_bold.font.size = Pt(9.5)
    r3_bold.font.color.rgb = RGBColor(30, 41, 59)
    r3_inst = p2.add_run(f"{instructions}\n")
    r3_inst.font.size = Pt(9.5)
    r3_inst.font.color.rgb = RGBColor(71, 85, 105)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_after = Pt(4)

def build_report():
    doc = docx.Document()

    # Configuración de márgenes estándar de 2.5 cm (1 pulgada)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Colores institucionales
    COLOR_PRIMARY = RGBColor(15, 23, 42)     # Slate 900
    COLOR_ACCENT = RGBColor(2, 132, 199)     # Sky 600
    COLOR_SUBTEXT = RGBColor(100, 116, 139)  # Slate 500

    # ==========================
    # 1. ENCABEZADO Y TÍTULO
    # ==========================
    p_head = doc.add_paragraph()
    r_inst = p_head.add_run("REPORTE TÉCNICO DE BENCHMARK EVOLUTIVO\n")
    r_inst.font.size = Pt(9.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_ACCENT

    r_title = p_head.add_run("Comparativa de Rendimiento y Convergencia:\nAlgoritmo Genético (AG) vs. Enjambre de Partículas (PSO)")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY
    p_head.paragraph_format.space_after = Pt(6)

    # Metadatos del reporte
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(16)
    r_meta = p_meta.add_run(
        "Herramienta implementada: Sistema Modular AG con extensión pyswarm (PSO)\n"
        "Métricas evaluadas: Precisión de f(x*), Tiempo de Cómputo (s), Total de Evaluaciones y Convergencia"
    )
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = COLOR_SUBTEXT

    # Línea divisoria
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(14)
    run_div = p_div.add_run("―" * 58)
    run_div.font.color.rgb = RGBColor(203, 213, 225)

    # ==========================
    # 2. RESUMEN EJECUTIVO
    # ==========================
    h1 = doc.add_heading("1. Resumen Ejecutivo", level=1)
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(6)

    p_resumen = doc.add_paragraph()
    p_resumen.paragraph_format.line_spacing = 1.15
    p_resumen.paragraph_format.space_after = Pt(10)
    p_resumen.add_run(
        "El presente informe analiza de manera comparativa la eficacia, velocidad y precisión de convergencia entre "
        "dos de las metaheurísticas bioinspiradas más influyentes en optimización continua: los "
    )
    r_b1 = p_resumen.add_run("Algoritmos Genéticos (AG)")
    r_b1.font.bold = True
    p_resumen.add_run(" y el ")
    r_b2 = p_resumen.add_run("Enjambre de Partículas (PSO)")
    r_b2.font.bold = True
    p_resumen.add_run(
        ", implementado mediante la biblioteca científica estándar pyswarm. "
        "La evaluación se llevó a cabo bajo dos paisajes de optimización representativos: "
        "(1) la función convexa e unimodal de la Esfera 2D y (2) la función altamente multimodal y compleja de Rastrigin 2D. "
        "Ambos algoritmos fueron ejecutados con parámetros equivalentes de población/enjambre (N=40), iteraciones (T=50) "
        "y bajo las mismas condiciones de frontera."
    )

    # ==========================
    # 3. MARCO TEÓRICO Y FUNCIONES
    # ==========================
    h2 = doc.add_heading("2. Descripción de las Funciones de Prueba", level=1)
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(6)

    # Función 1
    p_f1 = doc.add_paragraph()
    p_f1.paragraph_format.space_after = Pt(4)
    r_f1_t = p_f1.add_run("2.1. Función Esfera 2D (Unimodal Cuadrática)\n")
    r_f1_t.font.bold = True
    r_f1_t.font.size = Pt(11)
    p_f1.add_run(
        "• Formulación matemática:  f(x) = x₁² + x₂²\n"
        "• Espacio de búsqueda:  -10.0 ≤ x₁, x₂ ≤ 10.0\n"
        "• Mínimo global teórico:  f(0, 0) = 0.0\n"
        "• Característica del paisaje: Convexa, suave y continua, sin mínimos locales secundarios. "
        "Mide la velocidad de aceleración y capacidad de afinamiento de los algoritmos hacia el gradiente central."
    )

    # Función 2
    p_f2 = doc.add_paragraph()
    p_f2.paragraph_format.space_after = Pt(12)
    r_f2_t = p_f2.add_run("2.2. Función Rastrigin 2D (Altamente Multimodal)\n")
    r_f2_t.font.bold = True
    r_f2_t.font.size = Pt(11)
    p_f2.add_run(
        "• Formulación matemática:  f(x) = 10·n + ∑ [xᵢ² - 10·cos(2πxᵢ)]    (con n = 2, f(x) = 20 + [x₁² - 10cos(2πx₁)] + [x₂² - 10cos(2πx₂)])\n"
        "• Espacio de búsqueda:  -5.12 ≤ x₁, x₂ ≤ 5.12\n"
        "• Mínimo global teórico:  f(0, 0) = 0.0\n"
        "• Característica del paisaje: Altamente no lineal y rugosa, poblada por una gran cantidad de mínimos locales periódicos. "
        "Pone a prueba la capacidad de escape de trampas locales y el balance entre exploración global y explotación local."
    )

    # ==========================
    # 4. TABLA COMPARATIVA DE RESULTADOS
    # ==========================
    h3 = doc.add_heading("3. Resultados Experimentales y Métricas Comparativas", level=1)
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(6)

    # Tabla Esfera
    doc.add_paragraph().add_run("Tabla 1. Comparativa de Rendimiento en Función Esfera 2D (Convexa)").font.bold = True
    
    t_esfera = doc.add_table(rows=5, cols=4)
    t_esfera.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Métrica de Desempeño", "Algoritmo Genético (AG)", "Enjambre Partículas (PSO)", "Algoritmo Ganador"]
    
    for i, h in enumerate(headers):
        cell = t_esfera.cell(0, i)
        cell.text = h
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

    data_esfera = [
        ("Mejor f(x*) alcanzado", "0.000000 (1.40e-10)", "0.000000 (3.75e-10)", "AG (Ligera ventaja en precisión)"),
        ("Tiempo de ejecución", "0.4731 s", "0.0619 s", "PSO (7.6x más rápido)"),
        ("Total de evaluaciones", "2,040 evals", "1,360 evals", "PSO (Menor costo computacional)"),
        ("Vector solución óptimo x*", "[0.0000, 0.0000]", "[0.0000, 0.0000]", "Empate (Ambos convergen a x*=0)")
    ]

    for row_idx, row_data in enumerate(data_esfera, start=1):
        for col_idx, text in enumerate(row_data):
            cell = t_esfera.cell(row_idx, col_idx)
            cell.text = text
            bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.size = Pt(9)
                if col_idx == 3:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(2, 132, 199)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Tabla Rastrigin
    doc.add_paragraph().add_run("Tabla 2. Comparativa de Rendimiento en Función Rastrigin 2D (Multimodal)").font.bold = True
    t_ras = doc.add_table(rows=5, cols=4)
    t_ras.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, h in enumerate(headers):
        cell = t_ras.cell(0, i)
        cell.text = h
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

    data_ras = [
        ("Mejor f(x*) alcanzado", "0.000001 (1.10e-06)", "0.994959 (Mínimo local)", "AG (Encontró el óptimo global)"),
        ("Tiempo de ejecución", "0.4793 s", "0.0817 s", "PSO (5.8x más veloz)"),
        ("Total de evaluaciones", "2,040 evals", "1,600 evals", "PSO"),
        ("Vector solución óptimo x*", "[0.0000, 0.0001]", "[0.0000, -0.9950]", "AG (PSO quedó atrapado en pozo x2≈-1)")
    ]

    for row_idx, row_data in enumerate(data_ras, start=1):
        for col_idx, text in enumerate(row_data):
            cell = t_ras.cell(row_idx, col_idx)
            cell.text = text
            bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.size = Pt(9)
                if col_idx == 3:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(16, 185, 129) if "AG" in text else RGBColor(2, 132, 199)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # ==========================
    # 5. RECUADROS PARA CAPTURAS
    # ==========================
    h4 = doc.add_heading("4. Evidencia Visual y Capturas del Sistema", level=1)
    h4.paragraph_format.space_before = Pt(10)
    h4.paragraph_format.space_after = Pt(8)

    # Recuadro 1: Pestaña comparativa Esfera
    add_placeholder_box(
        doc,
        title="1. Pestaña Comparativa AG vs PSO - Función Esfera 2D",
        description="Captura de la pestaña '⚡ Comparativa AG vs Enjambre (PSO)' configurada con la función Esfera 2D.",
        instructions="En la aplicación, selecciona 'Esfera 2D (x1² + x2² en [-10, 10])', presiona '⚡ Ejecutar Comparativa' y toma captura cuando finalice. "
                     "Debe observarse la gráfica de convergencia comparativa (curva azul AG vs curva verde PSO) y la tabla de resumen inferior con los valores en decimal o notación científica."
    )

    # Recuadro 2: Superficie 3D Esfera
    add_placeholder_box(
        doc,
        title="2. Superficie Interactiva 3D con Óptimos - Función Esfera 2D",
        description="Ventana emergente 3D interactiva que muestra el tazón paraboloide de la Esfera con los marcadores de AG (estrella azul) y PSO (cruz verde).",
        instructions="Haz clic en el botón '🌐 Abrir Paisaje 3D Comparativo' en la parte superior derecha de la gráfica. "
                     "Gira ligeramente la superficie tridimensional con el mouse para apreciar la cavidad central y toma la captura."
    )

    # Recuadro 3: Pestaña comparativa Rastrigin
    add_placeholder_box(
        doc,
        title="3. Pestaña Comparativa AG vs PSO - Función Rastrigin 2D",
        description="Captura de la comparativa ejecutada para Rastrigin 2D donde se evidencia la convergencia del AG hacia 0.0000 y el estancamiento de PSO en f≈0.995.",
        instructions="Selecciona en el menú desplegable 'Rastrigin 2D (A=10 en [-5.12, 5.12])', presiona '⚡ Ejecutar Comparativa' y captura la pantalla al finalizar. "
                     "Verifica que la tabla muestre el contraste de métricas y la curva de convergencia."
    )

    # Recuadro 4: Superficie 3D Rastrigin
    add_placeholder_box(
        doc,
        title="4. Superficie Interactiva 3D de Rastrigin 2D (Picos y Valles)",
        description="Ventana emergente 3D del paisaje rugoso de Rastrigin mostrando los múltiples mínimos locales y la ubicación de las soluciones de AG y PSO.",
        instructions="Con Rastrigin seleccionado, presiona '🌐 Abrir Paisaje 3D Comparativo'. "
                     "Rota la vista para evidenciar la multitud de picos y cómo el punto de AG llegó al valle central (0,0) mientras PSO quedó en uno de los valles laterales adyacentes."
    )

    # ==========================
    # 6. ANÁLISIS CRÍTICO Y CONCLUSIONES
    # ==========================
    h5 = doc.add_heading("5. Análisis Crítico y Discusión de Resultados", level=1)
    h5.paragraph_format.space_before = Pt(10)
    h5.paragraph_format.space_after = Pt(6)

    p_disc = doc.add_paragraph()
    p_disc.paragraph_format.line_spacing = 1.15
    p_disc.paragraph_format.space_after = Pt(8)
    p_disc.add_run(
        "A partir de las pruebas cuantitativas se identifican dos comportamientos algorítmicos bien definidos:\n\n"
        "1. Rapidez y Eficiencia Vectorial de PSO:\n"
        "El Enjambre de Partículas (PSO) destacó ampliamente en tiempo de cómputo, siendo entre 5 y 8 veces más rápido que el AG. "
        "Esto se debe a su naturaleza puramente vectorial basada en actualización matricial de velocidades y posiciones "
        "(sin el costo operativo de selección por torneo, cruce probabilístico y reemplazos generacionales). "
        "En funciones unimodales continuas como la Esfera, PSO converge hacia el mínimo con extrema velocidad.\n\n"
        "2. Robustez de AG frente a Multimodalidad (Trampas Locales):\n"
        "En la función de Rastrigin, la alta presencia de ondas locales provocó que el enjambre de partículas sufriera convergencia prematura: "
        "las partículas fueron atraídas rápidamente por el mejor personal/global hacia un valle secundario en x₂ ≈ -0.9950, finalizando en f(x) ≈ 0.9949. "
        "Por el contrario, el Algoritmo Genético, gracias a la diversidad genética aportada por el cruce BLX-α y la mutación no uniforme, "
        "logró escapar de los atractores locales y alcanzó el mínimo global con precisión f(x*) ≈ 1.10e-06."
    )

    h6 = doc.add_heading("6. Conclusiones Finales", level=1)
    h6.paragraph_format.space_before = Pt(8)
    h6.paragraph_format.space_after = Pt(6)

    p_conc = doc.add_paragraph()
    p_conc.paragraph_format.line_spacing = 1.15
    p_conc.add_run(
        "• Para problemas convexos o continuos suaves (tipo Esfera), PSO representa la opción superior gracias a su bajo costo computacional y altísima velocidad de convergencia.\n"
        "• Para paisajes de optimización altamente accidentados y multimodales (tipo Rastrigin), el Algoritmo Genético configurado con operadores de dispersión continua ofrece mayor resiliencia contra estancamientos prematuros.\n"
        "• La integración del módulo comparativo dentro del entorno gráfico permite verificar empíricamente estas diferencias teóricas mediante curvas iterativas y superficies interactivas 3D en tiempo real."
    )

    output_dir = r"C:\Users\axush\Desktop\ejercicio genetico\ejercicio-algoritmo-gen-simple"
    output_path = os.path.join(output_dir, "Reporte_Comparativo_AG_vs_PSO.docx")
    doc.save(output_path)
    print(f"Reporte generado con exito en: {output_path}")
    return output_path

if __name__ == "__main__":
    build_report()
