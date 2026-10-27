"""
Generador del Manual de Usuario y Arquitectura Técnica en formato DOCX.
Incluye descripción completa del sistema y un banco de 10 ejemplos prácticos de ejecución.
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    """Establece el color de fondo de una celda."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Configura márgenes internos de una celda."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_manual():
    doc = docx.Document()

    # Configuración de márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Colores temáticos
    COLOR_PRIMARY = RGBColor(30, 58, 138)     # Azul marino corporativo (#1E3A8A)
    COLOR_SECONDARY = RGBColor(14, 116, 144) # Cian oscuro (#0E7490)
    COLOR_DARK = RGBColor(30, 41, 59)         # Pizarra oscura (#1E293B)
    COLOR_MUTED = RGBColor(100, 116, 139)    # Gris (#64748B)

    # Estilos de fuente base
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_DARK

    # =========================================================================
    # PORTADA / ENCABEZADO
    # =========================================================================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(40)
    title_p.paragraph_format.space_after = Pt(10)
    title_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("MANUAL DE USUARIO Y ARQUITECTURA TÉCNICA")
    run_title.font.name = 'Segoe UI'
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(25)
    sub_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("Sistema de Optimización Genética de Funciones Univariadas f(x)\nImplementación Rigurosa de Métodos de '05_hiperparametros'\nIncluye Banco de 10 Pruebas Prácticas de Validación")
    run_sub.font.name = 'Segoe UI'
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_SECONDARY

    # Caja decorativa de metadatos
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    metadata = [
        ("Proyecto:", "Algoritmo Genético Simple Modular"),
        ("Ubicación:", r"C:\Users\Admin\Desktop\alogoritmo genetico simple"),
        ("Versión del Software:", "1.0.0 (Release Modular Completo)"),
        ("Entorno de Ejecución:", "Python 3.13+ / Tkinter & Matplotlib")
    ]

    for i, (k, v) in enumerate(metadata):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "F8FAFC")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)

        p0 = c0.paragraphs[0]
        p0.add_run(k).bold = True
        p0.runs[0].font.size = Pt(10)
        p0.runs[0].font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        p1.add_run(v)
        p1.runs[0].font.size = Pt(10)

    doc.add_page_break()

    # =========================================================================
    # HELPERS DE CONTENIDO
    # =========================================================================
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = COLOR_DARK
        return p

    def add_p(text, bold_prefix="", space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = COLOR_DARK
        p.add_run(text)
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
        p.add_run(text)
        return p

    def add_note_box(text, title="NOTA IMPORTANTE"):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "EFF6FF")
        set_cell_margins(cell, 120, 120, 150, 150)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r_t = p.add_run(f"📌 {title}: ")
        r_t.bold = True
        r_t.font.color.rgb = COLOR_PRIMARY
        r_body = p.add_run(text)
        r_body.font.size = Pt(10)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # =========================================================================
    # SECCIÓN 1: INTRODUCCIÓN Y PROPÓSITO DEL SISTEMA
    # =========================================================================
    add_h1("1. Introducción y Propósito del Sistema")
    add_p(
        "Esta aplicación es una plataforma interactiva y educativa diseñada para explorar, comparar y validar "
        "el comportamiento de algoritmos genéticos en problemas de optimización matemática univariada. "
        "El sistema resuelve problemas de la forma:"
    )
    add_p("optimizar f(x),   con x perteneciente a [a, b]", bold_prefix="Objetivo Matemático: ")
    add_p(
        "donde f(x) puede ser minimizada o maximizada según el criterio seleccionado. "
        "A diferencia de herramientas de optimización convencionales basadas en cajas negras, este sistema "
        "desglosa con total transparencia cada fase del ciclo evolutivo y permite intercambiar de forma modular "
        "todos los operadores documentados en la unidad de estudio '05_hiperparametros'."
    )
    add_note_box(
        "El sistema implementa una restricción de diseño rigurosa para enfocarse en funciones univariadas f(x). "
        "Todos los operadores evolutivos (tanto de representación continua como de permutación) han sido "
        "adaptados funcionalmente para operar de manera transparente y verificable sobre este dominio.",
        "ENFOQUE UNIVARIADO"
    )

    # =========================================================================
    # SECCIÓN 2: ARQUITECTURA MODULAR DEL SOFTWARE
    # =========================================================================
    add_h1("2. Arquitectura Modular del Software")
    add_p(
        "El código ha sido estructurado en módulos altamente desacoplados siguiendo las mejores prácticas "
        "de ingeniería de software. Cada responsabilidad reside en una carpeta independiente, garantizando "
        "que ningún archivo concentre la totalidad del programa y facilitando el mantenimiento y la extensión."
    )

    arch_table = doc.add_table(rows=6, cols=3)
    arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    arch_table.autofit = False

    headers = ["Módulo / Directorio", "Responsabilidad Principal", "Archivos Clave"]
    col_widths = [Inches(1.8), Inches(3.2), Inches(1.5)]

    for j, h in enumerate(headers):
        cell = arch_table.rows[0].cells[j]
        cell.width = col_widths[j]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(10)

    modules_data = [
        ("logica/", "Implementación del ciclo evolutivo, operadores matemáticos y cálculo de aptitud.", "individual.py, ga_engine.py, selection.py, crossover.py, mutation.py, replacement.py"),
        ("ui/", "Interfaz visual moderna (Tkinter + Matplotlib). Paneles desacoplados y estilos.", "main_window.py, styles.py, components/*.py"),
        ("benchmarks/", "Catálogo de funciones matemáticas univariadas clásicas con óptimos conocidos.", "test_functions.py"),
        ("almacenamiento/", "Gestión de persistencia histórica en archivos JSON y generación de reportes TXT/CSV.", "experiment_logger.py, registros/"),
        ("tests/", "Batería de pruebas unitarias y de integración para validar operadores y convergencia.", "test_operators.py, test_ga.py")
    ]

    for i, (m, r, f) in enumerate(modules_data, start=1):
        row = arch_table.rows[i]
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, text in enumerate([m, r, f]):
            cell = row.cells[j]
            cell.width = col_widths[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.add_run(text).font.size = Pt(9.5)
            if j == 0:
                p.runs[0].bold = True

    add_h2("Flujo de Concurrencia (Multithreading)")
    add_p(
        "Para evitar que la interfaz de usuario se bloquee o deje de responder durante simulaciones largas o "
        "con miles de evaluaciones, el motor genético (GAEngine) opera en un hilo secundario (threading.Thread). "
        "La comunicación hacia la interfaz gráfica de usuario se realiza a través de una cola sincronizada (queue.Queue), "
        "permitiendo pausar, reanudar o detener el algoritmo de manera limpia en cualquier momento sin afectar la estabilidad."
    )

    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 3: FUNDAMENTOS MATEMÁTICOS DE LOS OPERADORES
    # =========================================================================
    add_h1("3. Métodos Evolutivos e Hiperparámetros (05_hiperparametros)")
    add_p(
        "A continuación se detallan las fórmulas, funcionamiento e hiperparámetros de todos los métodos incluidos "
        "en la aplicación según lo expuesto en el archivo de referencia."
    )

    add_h2("3.1. Operadores de Selección")
    add_bullet(
        "Asigna a cada individuo una probabilidad de reproducción pi = fi / sum(fj), proporcional a su aptitud escalada. "
        "Se calcula la distribución acumulada y se realizan sorteos con números aleatorios r en [0, 1]. "
        "Permite repetir individuos con alta aptitud.",
        "Ruleta Proporcional: "
    )
    add_bullet(
        "Ordena la población de mejor a peor (rango 1 a m) y asigna probabilidades que disminuyen linealmente con la posición: "
        "p(r) = [amax - (amax - amin)*(rank - 1)/(m - 1)] / m, donde 1 <= amax <= 2 y amin = 2 - amax. "
        "Evita que un individuo superdominante monopolice la población.",
        "Ranking Lineal: "
    )
    add_bullet(
        "Asigna probabilidades que decrecen geométricamente según el factor q en (0, 1): "
        "w(r) = q * (1 - q)^(rank - 1), normalizando luego como p'(r) = w(r) / sum(w). "
        "Un valor alto de q incrementa drásticamente la presión selectiva sobre los primeros lugares.",
        "Ranking No Lineal: "
    )
    add_bullet(
        "Elige k candidatos al azar de la población y el individuo con mayor aptitud gana el derecho a reproducirse. "
        "Incrementar k eleva la presión selectiva; k = 2 representa el clásico torneo binario.",
        "Selección por Torneo: "
    )
    add_bullet(
        "Muestreo Estocástico Universal (SUS). Utiliza un único sorteo u en [0, 1/m) y genera m punteros equidistantes "
        "u + i/m sobre la distribución acumulada. Selecciona toda la camada en una sola pasada con mínima varianza estocástica.",
        "Muestreo Estocástico Universal: "
    )

    add_h2("3.2. Operadores de Cruce (Combinación)")
    add_bullet(
        "Genera una máscara binaria (aleatoria o fija con probabilidad Pmask = 0.5). "
        "Si la posición en la máscara es 1, el primer hijo hereda el gen del Padre 1; si es 0, del Padre 2. "
        "El segundo hijo toma las decisiones complementarias.",
        "Cruce Uniforme: "
    )
    add_bullet(
        "Realiza una media ponderada convexa entre ambos progenitores: "
        "H1 = a*P1 + (1 - a)*P2  y  H2 = (1 - a)*P1 + a*P2, con 0 <= a <= 1. "
        "Garantiza que los descendientes queden ubicados dentro del segmento que une a los padres.",
        "Cruce Aritmético: "
    )
    add_bullet(
        "Para cada gen, sortea un valor uniforme independiente entre el menor y el mayor valor de los padres: "
        "hj ~ U(min(P1j, P2j), max(P1j, P2j)).",
        "Cruce Plano: "
    )
    add_bullet(
        "Cruce BLX-α. Amplía el intervalo parental en una proporción α de su longitud I = |P1 - P2|: "
        "h ~ U(min - α*I, max + α*I). Permite tanto interpolación (explotación) como extrapolación controlada (exploración). "
        "Con α = 0 equivale al cruce plano.",
        "Cruce BLX-α: "
    )
    add_bullet(
        "Cruce por Correspondencia Parcial (PMX), Cruce de Orden (OX) y Cruce de Ciclos (CX). "
        "Diseñados para problemas de orden y permutación, asegurando que cada alelo aparezca exactamente una vez. "
        "El sistema incluye soporte tanto para cromosomas discretos como adaptadores continuos.",
        "PMX, OX y CX: "
    )

    add_h2("3.3. Operadores de Mutación")
    add_bullet(
        "Sustituye el gen elegido por un valor sorteado uniformemente en todo el dominio permitido [LB, UB]. "
        "x'j ~ U(LBj, UBj). Genera saltos grandes para escapar de óptimos locales.",
        "Mutación Uniforme: "
    )
    add_bullet(
        "Ajusta el tamaño de la perturbación conforme transcurren las generaciones. "
        "Δ(t, y) = y * [1 - r^((1 - t/T)^b)], donde t es la generación actual, T es el número máximo de generaciones, "
        "r en [0, 1] y b controla la velocidad de enfriamiento. Al inicio (t=0) realiza grandes saltos; al final (t->T) realiza afinamiento fino.",
        "Mutación No Uniforme: "
    )
    add_bullet(
        "Intercambia dos posiciones al azar en el cromosoma o realiza una reflexión simétrica con perturbación gaussiana.",
        "Mutación por Intercambio (Swap): "
    )

    add_h2("3.4. Estrategias de Sustitución y Reemplazo")
    add_bullet(
        "Reemplazo generacional completo donde los mejores n_elite individuos de la población anterior sobreviven automáticamente "
        "a la siguiente generación, protegiendo las mejores soluciones halladas contra degradación estocástica.",
        "Generacional con Elitismo: "
    )
    add_bullet(
        "Sustituye solo una fracción n de la población en cada iteración. Típicamente, los n peores individuos de la población "
        "actual son expulsados y reemplazados por los nuevos descendientes.",
        "Sustitución Steady-State: "
    )
    add_bullet(
        "Para insertar cada nuevo descendiente, extrae una muestra aleatoria de tamaño CF de la población actual y reemplaza "
        "al individuo más parecido (menor distancia fenotípica). Preserva activamente la diversidad genética.",
        "Factor de Crowding: "
    )

    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 4: GUÍA PASO A PASO DE USUARIO
    # =========================================================================
    add_h1("4. Guía de Operación Paso a Paso")
    add_p("A continuación se presenta el procedimiento para operar la aplicación de manera óptima.")

    add_h2("Paso 1: Ejecución Inicial del Programa")
    add_p("Abra una consola de comandos (PowerShell o CMD), diríjase a la carpeta del proyecto y ejecute:")
    add_p("cd \"C:\\Users\\Admin\\Desktop\\alogoritmo genetico simple\"\npython main.py", bold_prefix="Comando: ")

    add_h2("Paso 2: Configuración de la Función Objetivo")
    add_bullet(
        "En el panel izquierdo ('1. Función Objetivo f(x)'), seleccione una de las funciones de prueba del menú desplegable "
        "(ej. Esfera 1D, Rastrigin 1D, Ackley 1D) o elija 'Personalizada...'.",
        "Opción A - Función de Prueba: "
    )
    add_bullet(
        "Si desea probar su propia ecuación, escríbala en el campo de texto usando la variable 'x'. "
        "Puede utilizar funciones como sin(x), cos(x), exp(x), sqrt(x), potencias (x**2 o x^2), etc.",
        "Opción B - Fórmula Personalizada: "
    )
    add_bullet(
        "Establezca los límites inferior 'a' y superior 'b' de la variable x (por ejemplo a = -5.0, b = 5.0).",
        "Intervalo [a, b]: "
    )
    add_bullet(
        "Elija si desea Minimizar (buscar el punto más bajo) o Maximizar (buscar el punto más alto).",
        "Criterio de Optimización: "
    )
    add_bullet(
        "Haga clic en '🔍 Previsualizar Curva' para trazar la función en la pantalla antes de iniciar la optimización.",
        "Previsualización: "
    )

    add_h2("Paso 3: Selección de Métodos Evolutivos e Hiperparámetros")
    add_p(
        "El panel '2. Operadores Evolutivos e Hiperparámetros' cuenta con menús limpios y adaptativos. "
        "Al cambiar cualquier método de selección, cruce, mutación o sustitución, los parámetros exclusivos de ese "
        "método se mostrarán de forma automática, ocultando los que no aplican para no saturar la interfaz:"
    )
    add_bullet("Selección: Elija entre Torneo (configure k), Ranking Lineal (amax), Ranking No Lineal (q), Ruleta o SUS.")
    add_bullet("Cruce: Elija el método (BLX-α, Aritmético, Plano, Uniforme, etc.) y defina la probabilidad Pc (típicamente 0.8 a 0.9).")
    add_bullet("Mutación: Elija entre No Uniforme, Uniforme o Intercambio, y defina la probabilidad Pm (típicamente 0.05 a 0.15).")
    add_bullet("Sustitución: Seleccione Generacional con Elitismo, Steady-State o Factor de Crowding.")
    add_bullet("Población y Generaciones: Ajuste el tamaño N (ej. 30 a 60) y las generaciones T (ej. 50 a 100).")
    add_bullet("Semilla Opcional: Presione '⚙ Ajustes Opcionales...' si desea fijar una semilla entera para replicar exactamente un experimento.")

    add_h2("Paso 4: Iniciar la Optimización y Observar Resultados")
    add_bullet("Haga clic en el botón superior '▶ Iniciar Optimización'.", "Iniciar: ")
    add_bullet(
        "En la gráfica superior observará la función f(x) con puntos de colores que representan a todos los miembros de la población "
        "moviéndose hacia la solución, y una estrella destacada sobre el mejor individuo.",
        "Visualización del Paisaje: "
    )
    add_bullet(
        "En la gráfica inferior observará en tiempo real la curva de convergencia generacional: la línea verde representa el mejor valor "
        "encontrado y la línea violeta el promedio poblacional.",
        "Visualización de Convergencia: "
    )
    add_bullet(
        "En la tarjeta inferior de métricas se actualizan de forma continua: Mejor x, Mejor f(x), Aptitud, Generación actual, "
        "Evaluaciones acumuladas y Tiempo de cálculo.",
        "Métricas Numéricas: "
    )
    add_bullet("Puede presionar en cualquier instante el botón '⏹ Detener' para pausar la simulación inmediatamente.", "Detener: ")

    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 5: HISTORIAL, REPORTES TXT Y CSV
    # =========================================================================
    add_h1("5. Historial, Reportes en TXT y Exportación a CSV")
    add_p(
        "Cada vez que una optimización finaliza (o se detiene), el sistema almacena de forma autónoma dos archivos "
        "dentro del directorio 'almacenamiento/registros/':"
    )
    add_bullet("Archivo JSON estructurado: Contiene la configuración completa, metadatos y la serie temporal de todas las generaciones.", ".json: ")
    add_bullet("Reporte TXT formateado: Resumen legible listo para imprimir o anexar a reportes técnicos o tareas académicas.", ".txt: ")

    add_h2("5.1. Visualizador de Historial Integrado")
    add_p(
        "Al presionar el botón '📋 Historial y Registros' en la barra superior se despliega una ventana modal interactiva con tres funciones:"
    )
    add_bullet("Exploración de ejecuciones: Lista todas las pruebas ordenadas cronológicamente de la más reciente a la más antigua con vista previa instantánea del reporte.")
    add_bullet("📥 Cargar Parámetros en UI: Restaura con un solo clic todos los hiperparámetros y la función de un experimento pasado en la pantalla principal para reejecutarlo o afinarlo.")
    add_bullet("📊 Exportar a CSV: Genera un archivo tabular (.csv) con las columnas [generación, evaluaciones, mejor x, mejor f(x), aptitud, media f(x), desviación estándar] compatible con Excel y MATLAB.")
    add_bullet("📄 Abrir TXT: Abre directamente el reporte en el Bloc de Notas de Windows.")

    # =========================================================================
    # SECCIÓN 6: CATÁLOGO DE FUNCIONES DE PRUEBA
    # =========================================================================
    add_h1("6. Catálogo de Funciones de Prueba (Benchmarks)")
    add_p("La aplicación incluye funciones univariadas analíticas para evaluar diferentes retos algorítmicos:")

    bench_table = doc.add_table(rows=8, cols=4)
    bench_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    bench_table.autofit = False

    b_headers = ["Función", "Expresión f(x)", "Intervalo", "Óptimo Teórico"]
    b_widths = [Inches(1.8), Inches(2.2), Inches(1.1), Inches(1.4)]

    for j, h in enumerate(b_headers):
        cell = bench_table.rows[0].cells[j]
        cell.width = b_widths[j]
        set_cell_background(cell, "0E7490")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

    benchmarks_rows = [
        ("Esfera 1D", "x**2", "[-10, 10]", "x = 0.0, f(x) = 0.0"),
        ("Rastrigin 1D", "10 + x**2 - 10*cos(2*pi*x)", "[-5.12, 5.12]", "x = 0.0, f(x) = 0.0"),
        ("Ackley 1D", "-20*exp(-0.2*abs(x)) - exp(cos(2*pi*x)) + 20 + e", "[-5.0, 5.0]", "x = 0.0, f(x) = 0.0"),
        ("Rosenbrock 1D", "(1 - x)**2 + 100*(x - x**2)**2", "[-2.0, 2.0]", "x = 1.0, f(x) = 0.0"),
        ("Picos Michalewicz", "-sin(x) * (sin(x**2 / pi))**20", "[0.0, 3.1416]", "x ≈ 2.203, f(x) ≈ -1.801"),
        ("Seno Amortiguado", "sin(10*x)*x + cos(5*x)", "[0.0, 10.0]", "Maximización global"),
        ("Griewank 1D", "(x**2 / 4000) - cos(x) + 1", "[-10, 10]", "x = 0.0, f(x) = 0.0")
    ]

    for i, (fn, expr, bnds, opt) in enumerate(benchmarks_rows, start=1):
        row = bench_table.rows[i]
        bg = "F0FDF4" if i % 2 == 1 else "FFFFFF"
        for j, text in enumerate([fn, expr, bnds, opt]):
            cell = row.cells[j]
            cell.width = b_widths[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 70, 70)
            p = cell.paragraphs[0]
            p.add_run(text).font.size = Pt(9)
            if j == 0:
                p.runs[0].bold = True

    # =========================================================================
    # SECCIÓN 7: CONSEJOS DE CALIBRACIÓN
    # =========================================================================
    add_h1("7. Consejos de Calibración de Hiperparámetros")
    add_h2("¿Cómo evitar la convergencia prematura en funciones multimodales como Rastrigin?")
    add_p(
        "En funciones con múltiples óptimos locales, si la población converge demasiado rápido a un pozo subóptimo, "
        "se recomienda: 1) Utilizar selección por Torneo con k pequeño (k=2) o Ranking Lineal moderado (amax=1.2); "
        "2) Emplear cruce BLX-α con α = 0.5 o 0.7 para mayor dispersión; 3) Activar la sustitución por Factor de Crowding (CF=3 a 5), "
        "la cual penaliza la aglomeración de individuos en una misma coordenada."
    )

    add_h2("¿Por qué la mutación no uniforme es más eficiente al final de la ejecución?")
    add_p(
        "La mutación no uniforme reduce el radio de perturbación Δ en función de (1 - t/T)^b. "
        "Esto simula el recocido simulado: permite explorar todo el intervalo al inicio y afinarse milimétricamente en el punto óptimo "
        "en las generaciones finales, eliminando las oscilaciones erráticas."
    )

    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 8: BANCO DE 10 EJEMPLOS PRÁCTICOS DE VALIDACIÓN
    # =========================================================================
    add_h1("8. Banco de 10 Ejemplos Prácticos de Ejecución")
    add_p(
        "A continuación se presenta una guía práctica con 10 configuraciones experimentales completas diseñadas "
        "para poner a prueba la versatilidad del sistema, explorando combinaciones contrastantes de operadores evolutivos "
        "y diversos perfiles de paisajes matemáticos."
    )

    examples = [
        {
            "num": 1,
            "title": "Convergencia Rápida en Función Convexa Clásica (Esfera 1D)",
            "problem": "Minimizar f(x) = x² en el intervalo [-10.0, 10.0].",
            "config": [
                ("Función:", "Esfera 1D (Convexa simple) [x**2]"),
                ("Intervalo / Objetivo:", "[-10.0, 10.0] | Minimizar"),
                ("Selección:", "Torneo determinista (k = 2)"),
                ("Cruce:", "BLX-α (α = 0.5, Pc = 0.85)"),
                ("Mutación:", "No uniforme (b = 1.5, Pm = 0.10)"),
                ("Sustitución:", "Generacional con Elitismo (élites = 1)"),
                ("Población / Generaciones:", "N = 30, T = 40, Semilla = 42")
            ],
            "expected": "x* ≈ 0.0000, f(x*) ≈ 0.0000 (error < 1e-4).",
            "phenomenon": "Valida la capacidad del algoritmo para contraer rápidamente la población hacia el mínimo global en un paisaje cuadrático suave."
        },
        {
            "num": 2,
            "title": "Evasión de Múltiples Trampas Locales (Rastrigin 1D)",
            "problem": "Minimizar f(x) = 10 + x² - 10·cos(2πx) en [-5.12, 5.12]. Paisaje con ondulaciones periódicas intensas.",
            "config": [
                ("Función:", "Rastrigin 1D (Altamente multimodal)"),
                ("Intervalo / Objetivo:", "[-5.12, 5.12] | Minimizar"),
                ("Selección:", "Ranking Lineal (amax = 1.3, presión suave)"),
                ("Cruce:", "BLX-α (α = 0.7, Pc = 0.90)"),
                ("Mutación:", "No uniforme (b = 2.0, Pm = 0.15)"),
                ("Sustitución:", "Factor de Crowding (CF = 4)"),
                ("Población / Generaciones:", "N = 50, T = 80, Semilla = 100")
            ],
            "expected": "x* ≈ 0.0000, f(x*) ≈ 0.0000.",
            "phenomenon": "El Factor de Crowding y la alta tasa de recombinación BLX evitan que todos los individuos caigan en pozos locales periféricos (x = ±1, ±2), encontrando el valle central."
        },
        {
            "num": 3,
            "title": "Exploración en Valle Central Escarpado (Ackley 1D)",
            "problem": "Minimizar Ackley 1D en [-5.0, 5.0], caracterizada por una meseta externa casi plana y un pozo central profundo.",
            "config": [
                ("Función:", "Ackley 1D (Multimodal con valle central)"),
                ("Intervalo / Objetivo:", "[-5.0, 5.0] | Minimizar"),
                ("Selección:", "Torneo (k = 3)"),
                ("Cruce:", "Cruce Plano (Pc = 0.85)"),
                ("Mutación:", "Uniforme (Pm = 0.12)"),
                ("Sustitución:", "Generacional con Elitismo (élites = 2)"),
                ("Población / Generaciones:", "N = 40, T = 70, Semilla = 77")
            ],
            "expected": "x* ≈ 0.0000, f(x*) ≈ 0.0000.",
            "phenomenon": "La mutación uniforme genera saltos suficientes para atravesar la meseta externa hasta que algún individuo cae en el valle central de atracción."
        },
        {
            "num": 4,
            "title": "Maximización de Picos Crecientes (Seno Amortiguado)",
            "problem": "Maximizar f(x) = sin(10x)·x + cos(5x) en [0.0, 10.0]. La función posee múltiples crestas cuya amplitud crece con x.",
            "config": [
                ("Función:", "Maximización de Seno Amortiguado"),
                ("Intervalo / Objetivo:", "[0.0, 10.0] | Maximizar"),
                ("Selección:", "Ruleta Proporcional (fitness escalado dinámico)"),
                ("Cruce:", "Cruce Aritmético (a = 0.35, Pc = 0.80)"),
                ("Mutación:", "No uniforme (b = 1.0, Pm = 0.10)"),
                ("Sustitución:", "Generacional con Elitismo (élites = 1)"),
                ("Población / Generaciones:", "N = 40, T = 60, Semilla = 2026")
            ],
            "expected": "x* ≈ 7.95 - 8.05, f(x*) ≈ 8.6 - 8.9.",
            "phenomenon": "Demuestra la transformación y escalamiento automático de aptitud positiva para problemas de maximización, guiando la población hacia la cresta de mayor energía en el extremo derecho."
        },
        {
            "num": 5,
            "title": "Optimización Incremental Continua (Rosenbrock 1D / Banana Valley)",
            "problem": "Minimizar f(x) = (1 - x)² + 100·(x - x²)² en [-2.0, 2.0]. Gradiente extremadamente empinado en los bordes.",
            "config": [
                ("Función:", "Rosenbrock 1D / Valle"),
                ("Intervalo / Objetivo:", "[-2.0, 2.0] | Minimizar"),
                ("Selección:", "Muestreo Estocástico Universal (SUS)"),
                ("Cruce:", "Cruce Aritmético (a = 0.50, Pc = 0.85)"),
                ("Mutación:", "Uniforme (Pm = 0.08)"),
                ("Sustitución:", "Steady-State (reemplazos n = 4)"),
                ("Población / Generaciones:", "N = 35, T = 60, Semilla = 33")
            ],
            "expected": "x* ≈ 1.0000, f(x*) ≈ 0.0000.",
            "phenomenon": "Combina la baja varianza estocástica del operador SUS con la sustitución Steady-State, reemplazando a los peores individuos paso a paso sin renovación masiva."
        },
        {
            "num": 6,
            "title": "Preservación en Mesetas Planas (Picos de Michalewicz 1D)",
            "problem": "Minimizar f(x) = -sin(x)·(sin(x²/π))^20 en [0.0, 3.1416]. Cañón abrupto rodeado de zonas donde el gradiente es cero.",
            "config": [
                ("Función:", "Picos de Michalewicz 1D"),
                ("Intervalo / Objetivo:", "[0.0, 3.1416] | Minimizar"),
                ("Selección:", "Ranking No Lineal (factor geométrico q = 0.3)"),
                ("Cruce:", "BLX-α (α = 0.5, Pc = 0.85)"),
                ("Mutación:", "No uniforme (b = 3.0, enfriamiento pronunciado)"),
                ("Sustitución:", "Factor de Crowding (CF = 3)"),
                ("Población / Generaciones:", "N = 45, T = 70, Semilla = 55")
            ],
            "expected": "x* ≈ 2.2029, f(x*) ≈ -1.8013.",
            "phenomenon": "El Ranking No lineal asigna una probabilidad diferenciada a los pocos individuos que caen dentro del valle empinado, acelerando el hallazgo del fondo del cañón."
        },
        {
            "num": 7,
            "title": "Evaluación con Cruce Uniforme en Ondulaciones Finas (Griewank 1D)",
            "problem": "Minimizar Griewank 1D en [-10.0, 10.0]. Múltiples oscilaciones superpuestas sobre una parábola general.",
            "config": [
                ("Función:", "Griewank 1D"),
                ("Intervalo / Objetivo:", "[-10.0, 10.0] | Minimizar"),
                ("Selección:", "Ranking Lineal (amax = 1.6)"),
                ("Cruce:", "Cruce Uniforme (P_máscara = 0.5, Pc = 0.90)"),
                ("Mutación:", "No uniforme (b = 1.5, Pm = 0.12)"),
                ("Sustitución:", "Generacional con Elitismo (élites = 2)"),
                ("Población / Generaciones:", "N = 40, T = 60, Semilla = 12")
            ],
            "expected": "x* ≈ 0.0000, f(x*) ≈ 0.0000.",
            "phenomenon": "Prueba el comportamiento del cruce uniforme con máscara binaria y su convergencia hacia el centro de coordenadas."
        },
        {
            "num": 8,
            "title": "Función Personalizada: Parábola Perturbada con Ruido Senoidal",
            "problem": "Minimizar una función definida por el usuario: f(x) = 0.5*(x - 3)**2 + sin(8*x) en el intervalo [-2.0, 8.0].",
            "config": [
                ("Función:", "Personalizada... [0.5*(x - 3)**2 + sin(8*x)]"),
                ("Intervalo / Objetivo:", "[-2.0, 8.0] | Minimizar"),
                ("Selección:", "Torneo (k = 4, alta presión selectiva)"),
                ("Cruce:", "BLX-α (α = 0.4, Pc = 0.85)"),
                ("Mutación:", "Por intercambio (Swap / reflexión simétrica, Pm = 0.10)"),
                ("Sustitución:", "Steady-State (reemplazos n = 6)"),
                ("Población / Generaciones:", "N = 40, T = 50, Semilla = 888")
            ],
            "expected": "x* ≈ 3.01 (en el valle del seno más cercano al vértice), f(x*) ≈ -0.95 a -1.0.",
            "phenomenon": "Valida el analizador seguro AST con funciones personalizadas y comprueba la efectividad del operador de mutación por intercambio en individuos continuos."
        },
        {
            "num": 9,
            "title": "Función Personalizada: Potencial de Doble Pozo Asimétrico (Double-Well)",
            "problem": "Minimizar f(x) = (x**2 - 4)**2 + 0.8*x en [-3.0, 3.0]. Dos pozos: uno local cerca de x = 1.9 y uno global más profundo cerca de x = -2.05.",
            "config": [
                ("Función:", "Personalizada... [(x**2 - 4)**2 + 0.8*x]"),
                ("Intervalo / Objetivo:", "[-3.0, 3.0] | Minimizar"),
                ("Selección:", "Muestreo Estocástico Universal (SUS)"),
                ("Cruce:", "Cruce Plano (Pc = 0.85)"),
                ("Mutación:", "No uniforme (b = 1.0, Pm = 0.12)"),
                ("Sustitución:", "Factor de Crowding (CF = 5)"),
                ("Población / Generaciones:", "N = 50, T = 60, Semilla = 404")
            ],
            "expected": "x* ≈ -2.05, f(x*) ≈ -1.60.",
            "phenomenon": "Demuestra cómo el Factor de Crowding mantiene colonias en ambos pozos simultáneamente antes de que el pozo global predomine numéricamente sin estancarse en el pozo falso."
        },
        {
            "num": 10,
            "title": "Validación de Operadores de Permutación y Orden (PMX / OX / CX)",
            "problem": "Minimizar una función objetivo evaluando la recombinación de subestructuras con operadores de orden (PMX, OX, CX).",
            "config": [
                ("Función:", "Esfera 1D o Personalizada [abs(x - 2.5) + (x - 2.5)**2]"),
                ("Intervalo / Objetivo:", "[0.0, 5.0] | Minimizar"),
                ("Selección:", "Torneo (k = 2)"),
                ("Cruce:", "PMX (Partially Mapped Crossover, Pc = 0.80)"),
                ("Mutación:", "Por intercambio (Swap, Pm = 0.15)"),
                ("Sustitución:", "Generacional con Elitismo (élites = 1)"),
                ("Población / Generaciones:", "N = 30, T = 40, Semilla = 7")
            ],
            "expected": "x* ≈ 2.5000, f(x*) ≈ 0.0000.",
            "phenomenon": "Comprueba que los operadores de correspondencia parcial y permutación preservan la consistencia de los alelos y convergen sin divergencias numéricas."
        }
    ]

    for ex in examples:
        add_h2(f"Ejemplo {ex['num']}: {ex['title']}")
        add_p(ex['problem'], bold_prefix="Problema a Resolver: ")

        # Tabla de configuración
        tbl = doc.add_table(rows=len(ex['config']), cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False

        for row_i, (k, val) in enumerate(ex['config']):
            c0, c1 = tbl.rows[row_i].cells[0], tbl.rows[row_i].cells[1]
            c0.width = Inches(2.2)
            c1.width = Inches(4.3)
            set_cell_background(c0, "F1F5F9")
            set_cell_background(c1, "FFFFFF")
            set_cell_margins(c0, 40, 40, 70, 70)
            set_cell_margins(c1, 40, 40, 70, 70)

            p0 = c0.paragraphs[0]
            p0.add_run(k).bold = True
            p0.runs[0].font.size = Pt(9)
            p0.runs[0].font.color.rgb = COLOR_PRIMARY

            p1 = c1.paragraphs[0]
            p1.add_run(val).font.size = Pt(9)

        add_p(ex['expected'], bold_prefix="Resultado Esperado: ", space_after=3)
        add_p(ex['phenomenon'], bold_prefix="Fenómeno Observado: ", space_after=12)

    # Guardar documento en la carpeta del proyecto
    dest_path = r"C:\Users\Admin\Desktop\alogoritmo genetico simple\MANUAL_DE_USUARIO_Y_ARQUITECTURA.docx"
    alt_path = r"C:\Users\Admin\Desktop\alogoritmo genetico simple\MANUAL_DE_USUARIO_CON_EJEMPLOS.docx"
    try:
        doc.save(dest_path)
        print(f"Documento actualizado y guardado exitosamente en: {dest_path}")
    except PermissionError:
        doc.save(alt_path)
        print(f"Nota: El archivo original estaba abierto en Word. Documento guardado como: {alt_path}")

if __name__ == "__main__":
    create_manual()
