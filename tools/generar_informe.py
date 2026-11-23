"""Genera docs/Informe_Ciclo_Euleriano.docx (luego se convierte a PDF con LibreOffice).

    python tools/generar_informe.py
    soffice --headless --convert-to pdf --outdir docs docs/Informe_Ciclo_Euleriano.docx
"""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, "docs", "img")
SALIDA = os.path.join(RAIZ, "docs", "Informe_Ciclo_Euleriano.docx")
REPO = "https://github.com/DiegoLadrondeGuevara/Proyecto2-AED"
VIDEO = REPO + "/blob/main/video/CicloEuleriano.mp4"

with open(os.path.join(RAIZ, "integrantes.txt"), encoding="utf-8") as f:
    INTEGRANTES = [l.strip() for l in f if l.strip()]

AZUL = RGBColor(0x1F, 0x3B, 0x5C)
GRIS = RGBColor(0x55, 0x5F, 0x6B)

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2.2)
    s.left_margin = s.right_margin = Cm(2.4)
estilo = doc.styles["Normal"]
estilo.font.name = "Calibri"
estilo.font.size = Pt(11)
for nivel, tam in ((1, 15), (2, 12.5)):
    h = doc.styles[f"Heading {nivel}"]
    h.font.name = "Calibri"
    h.font.size = Pt(tam)
    h.font.color.rgb = AZUL


def parrafo(texto, negrita=False, centro=False, tam=None, color=None, italica=False, espacio=6):
    p = doc.add_paragraph()
    r = p.add_run(texto)
    r.bold = negrita
    r.italic = italica
    if tam:
        r.font.size = Pt(tam)
    if color:
        r.font.color.rgb = color
    if centro:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(espacio)
    return p


def vinetas(items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        if isinstance(it, tuple):
            p.add_run(it[0]).bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)
        p.paragraph_format.space_after = Pt(2)


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def tabla(filas, anchos):
    t = doc.add_table(rows=len(filas), cols=len(filas[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, fila in enumerate(filas):
        for j, txt in enumerate(fila):
            c = t.cell(i, j)
            c.width = Cm(anchos[j])
            c.text = ""
            r = c.paragraphs[0].add_run(txt)
            r.font.size = Pt(10)
            if i == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                sombrear(c, "1F3B5C")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def codigo(texto):
    p = doc.add_paragraph()
    r = p.add_run(texto)
    r.font.name = "Consolas"
    r.font.size = Pt(9)
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(6)


def imagen(nombre, pie, ancho=15.5):
    ruta = os.path.join(IMG, nombre)
    if not os.path.exists(ruta):
        parrafo(f"[falta imagen {nombre}]", color=GRIS)
        return
    doc.add_picture(ruta, width=Cm(ancho))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo(pie, centro=True, tam=9, color=GRIS, italica=True)


def enlace(parr, url, texto=None):
    rid = parr.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                              is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    col = OxmlElement("w:color")
    col.set(qn("w:val"), "1F5FBF")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(col)
    rpr.append(u)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = texto or url
    run.append(t)
    h.append(run)
    parr._p.append(h)


# ------------------------------------------------------------------ caratula
for _ in range(3):
    doc.add_paragraph()
parrafo("UNIVERSIDAD DE INGENIERÍA Y TECNOLOGÍA — UTEC", True, True, 13, AZUL)
parrafo("CS2023 · Algoritmos y Estructuras de Datos · 2026-2", False, True, 12)
parrafo("Prof. Wilder Nina Choquehuayta", False, True, 11, GRIS, espacio=40)
parrafo("Proyecto Final 2 — Anima tu Algoritmo", True, True, 16)
parrafo("Ciclo Euleriano", True, True, 28, AZUL, espacio=2)
parrafo("Algoritmo de Hierholzer en O(|V| + |E|)", False, True, 14, GRIS, espacio=40)
parrafo("Integrante" if len(INTEGRANTES) == 1 else "Integrantes", True, True, 12)
for n in INTEGRANTES:
    parrafo(n, False, True, 12, espacio=2)
doc.add_paragraph()
parrafo("Estructura asignada: 2. Ciclo euleriano", False, True, 11, GRIS)
parrafo("Lima, noviembre de 2026", False, True, 11, GRIS)
doc.add_page_break()

# ------------------------------------------------------------------ 1
doc.add_heading("1. Descripción del algoritmo", 1)
parrafo("Un ciclo euleriano es un recorrido cerrado que pasa por todas las aristas de un grafo exactamente "
        "una vez (los vértices sí pueden repetirse). El problema nace con los siete puentes de Königsberg, "
        "que Euler resolvió en 1736 demostrando que no existía tal recorrido.")
parrafo("No se trata de una estructura de datos sino de un algoritmo sobre la estructura grafo "
        "(TDA Grafo: vértices, aristas y relación de adyacencia). Su objetivo es responder: ¿existe un "
        "recorrido cerrado que use cada arista una sola vez? y, si existe, construirlo.")
doc.add_heading("Teorema de Euler (grafo no dirigido)", 2)
parrafo("Un grafo tiene un ciclo euleriano si y solo si (1) todos sus vértices tienen grado par y (2) "
        "todos los vértices con al menos una arista pertenecen a una misma componente conexa. La intuición: "
        "cada vez que el recorrido entra a un vértice por una arista debe salir por otra, así que las "
        "aristas de cada vértice se consumen de a pares.")
doc.add_heading("Algoritmo de Hierholzer (1873)", 2)
vinetas([
    ("Paso 1. ", "Se parte de un vértice con aristas y se camina por aristas no usadas, marcándolas, hasta "
                 "atascarse (por el teorema, esto solo ocurre al volver al inicio del sub-ciclo)."),
    ("Paso 2. ", "Al atascarse en v, v se saca de la pila y se agrega al ciclo final."),
    ("Paso 3. ", "Si el nuevo tope de la pila aún tiene aristas libres, desde ahí se recorre un sub-ciclo "
                 "que queda empalmado en ese punto del ciclo. Se repite hasta vaciar la pila."),
])
parrafo("Versión iterativa implementada:")
codigo("pila.push(inicio)\n"
       "mientras pila no vacía:\n"
       "    v = pila.tope()\n"
       "    saltar en ady[v] las aristas ya usadas (puntero siguiente[v])\n"
       "    si queda una arista (v, w):  marcarla usada;  pila.push(w)      -> AVANZA\n"
       "    si no:                       pila.pop();  ciclo.agregarInicio(v) -> RETROCEDE")
parrafo("Usos en la práctica: planificación de rutas que deben cubrir todas las calles (recolección de basura, "
        "correo, inspección de redes: problema del cartero chino), ensamblaje de genomas con grafos de De "
        "Bruijn, trazado de circuitos/plotters sin levantar el cabezal y generación de secuencias de De Bruijn.")

# ------------------------------------------------------------------ 2
doc.add_heading("2. Implementación", 1)
parrafo("Toda la lógica está en C++17 y fue programada por el grupo; no se usan std::stack, std::vector ni "
        "librerías de grafos en el algoritmo:")
vinetas([
    ("Pila<T> ", "(src/estructuras/Pila.h): pila enlazada, push/pop/tope en O(1). La usan Hierholzer y el DFS de conexidad."),
    ("Lista<T> ", "(src/estructuras/Lista.h): lista enlazada con inserción al inicio y al final en O(1). "
                  "Se usa para las listas de adyacencia y para construir el ciclo."),
    ("GrafoEuleriano ", "(src/GrafoEuleriano.h/.cpp): multigrafo no dirigido (admite lazos y aristas paralelas). "
                        "Cada arista tiene un id; la lista de adyacencia guarda pares (arista, vecino) y un arreglo "
                        "usada[e] evita recorrer dos veces la misma arista desde sus dos extremos."),
    ("verificar() ", "comprueba el teorema: grados pares y conexidad con un DFS iterativo."),
    ("cicloEuleriano() ", "ejecuta Hierholzer y, si se activa la traza, escribe un evento por cada paso."),
])
doc.add_heading("Animación impulsada por la implementación real", 2)
parrafo("Igual que en el Proyecto 1, el programa C++ escribe una traza de eventos (GRADO, CONEXO_VISITA, "
        "PUSH, AVANZA, RETROCEDE, CICLO, …) y la escena de Manim solo la lee y la reproduce: el dibujo de la "
        "pila, el color de cada arista y el orden del ciclo salen de la traza. Si se cambia el grafo de "
        "entrada y se vuelve a ejecutar, la animación cambia sola.")
codigo("./euler grafos/principal.txt -t trazas/principal.txt\n"
       "Grados: 0:2 1:2 2:4 3:2 4:4 5:2 6:2\n"
       "Ciclo euleriano (10 vertices, 9 aristas):\n"
       "  0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 4 -> 2 -> 0")
doc.add_heading("Pruebas", 2)
parrafo("tests/pruebas.cpp realiza 12 591 verificaciones (0 fallos): 3000 multigrafos eulerianos aleatorios "
        "(el ciclo debe ser cerrado, tener |E|+1 vértices y usar cada arista exactamente una vez), 3000 grafos "
        "cualesquiera cuyo veredicto se compara con un chequeo independiente basado en union-find, y casos "
        "borde: un vértice sin aristas, un lazo, aristas paralelas, una sola arista y un ciclo de 200 000 "
        "vértices (la versión iterativa no desborda la pila de llamadas).")

# ------------------------------------------------------------------ 3
doc.add_heading("3. Herramientas y pasos para reproducir el video", 1)
tabla([["Herramienta", "Uso"],
       ["C++17 · g++ 15 (MSYS2 UCRT64)", "algoritmo, pruebas y generación de trazas"],
       ["Python 3.13 + Manim Community 0.21", "animación (escena.py)"],
       ["FFmpeg", "unir las escenas en un solo MP4"],
       ["Git + GitHub", "control de versiones y entrega"]], [6.5, 9])
codigo("g++ -std=c++17 -O2 -o euler src/main.cpp src/GrafoEuleriano.cpp\n"
       "./euler grafos/principal.txt   -t trazas/principal.txt\n"
       "./euler grafos/konigsberg.txt  -t trazas/konigsberg.txt\n"
       "./euler grafos/desconectado.txt -t trazas/desconectado.txt\n"
       "./euler grafos/un_vertice.txt  -t trazas/un_vertice.txt\n"
       "manim -qh animacion/escena.py Portada Introduccion Verificacion Hierholzer CasoBorde Complejidad Creditos\n"
       "# En Windows, todo lo anterior + unir el video:  .\\ejecutar.ps1")
doc.add_heading("Contenido del video (≈ 2 min 36 s, 1080p)", 2)
tabla([["Escena", "Contenido", "Requisito de la rúbrica"],
       ["Portada", "título, curso e integrantes", "título y nombres"],
       ["Introducción", "definición, usos, teorema de Euler, idea de Hierholzer", "introducción conceptual"],
       ["Verificación", "grados y DFS de conexidad sobre el grafo principal", "demostración animada"],
       ["Hierholzer", "pila, aristas usadas, sub-ciclos empalmados y recorrido final", "demostración animada"],
       ["Casos borde", "Königsberg (grados impares), grafo desconectado, un solo vértice", "caso borde"],
       ["Complejidad", "tabla de costos y comparación con Fleury", "análisis de complejidad"],
       ["Créditos", "integrantes y herramientas", "nombres"]], [3, 8, 4.5])

# ------------------------------------------------------------------ 4
doc.add_heading("4. Análisis de complejidad", 1)
tabla([["Paso", "Tiempo", "Justificación"],
       ["Leer el grafo", "O(V + E)", "cada arista se inserta en dos listas en O(1)"],
       ["Grados", "O(V)", "el grado es el tamaño de la lista de adyacencia"],
       ["Conexidad", "O(V + E)", "DFS iterativo: cada vértice se apila una vez y cada lista se recorre una vez"],
       ["Hierholzer", "O(V + E)", "cada arista se marca usada una vez; el puntero siguiente[v] solo avanza, "
                                  "así que en total se revisan 2E incidencias; hay E+1 push y E+1 pop"],
       ["Memoria", "O(V + E)", "listas de adyacencia, arreglo usada[], pila y ciclo"],
       ["Fleury (comparación)", "O(E²)", "antes de cada paso verifica si la arista es puente"]], [3.3, 2.4, 10])
parrafo("El punto clave es no volver a examinar aristas ya usadas: sin el puntero siguiente[v], cada consulta "
        "recorrería la lista desde el principio y el peor caso sería O(V·E). Con él, el algoritmo es lineal "
        "en el tamaño del grafo, que es óptimo porque la salida misma tiene E+1 vértices.")
parrafo("Caso borde / peor caso: si el grafo no es euleriano (Königsberg o un grafo desconectado), la "
        "verificación lo detecta en O(V + E) y Hierholzer no se ejecuta. Si no hay aristas, la respuesta es el "
        "ciclo trivial de un vértice.")

# ------------------------------------------------------------------ 5
doc.add_heading("5. Evidencia", 1)
p = parrafo("Repositorio: ")
enlace(p, REPO)
p = parrafo("Escenas animadas con Manim (MP4, 1080p): ")
enlace(p, REPO + "/tree/main/video")
parrafo("Video final narrado (PPT + escenas): [AGREGAR ENLACE DE DRIVE / YOUTUBE NO LISTADO]",
        negrita=True, color=RGBColor(0xC0, 0x30, 0x30))
imagen("verificacion.png", "Figura 1. Verificación de grados (g) y DFS de conexidad sobre el grafo principal.")
imagen("hierholzer_medio.png", "Figura 2. Hierholzer a mitad de ejecución: camino actual en amarillo, aristas ya "
                               "fijadas en el ciclo en verde, pila a la derecha y ciclo en construcción abajo.")
imagen("hierholzer_final.png", "Figura 3. Ciclo final 0→1→2→3→4→5→6→4→2→0 con el orden de cada arista.")
imagen("konigsberg.png", "Figura 4. Caso borde: los puentes de Königsberg tienen 4 vértices de grado impar.")
imagen("desconectado.png", "Figura 5. Caso borde: grados pares pero aristas en dos componentes.")

# ------------------------------------------------------------------ 6
doc.add_heading("6. Contribuciones", 1)
filas = [["Integrante", "Contribución"]]
if len(INTEGRANTES) == 1:
    filas.append([INTEGRANTES[0], "Trabajo individual: implementación en C++ (Pila, Lista, GrafoEuleriano, "
                                  "Hierholzer), pruebas, animación en Manim, video narrado, informe, "
                                  "presentación y README (100 %)"])
else:
    roles = ["Implementación en C++ (Pila, Lista, GrafoEuleriano, Hierholzer) y pruebas",
             "Animación en Manim, guion y edición del video",
             "Informe, presentación y README"]
    for i, n in enumerate(INTEGRANTES):
        filas.append([n, roles[i] if i < len(roles) else "Revisión general"])
tabla(filas, [6, 9.5])

# ------------------------------------------------------------------ 7
doc.add_heading("7. Conclusiones", 1)
vinetas([
    "La existencia de un ciclo euleriano se decide solo con dos propiedades locales/globales baratas "
    "(paridad de grados y conexidad), ambas verificables en O(V + E), sin necesidad de buscar el ciclo.",
    "Hierholzer construye el ciclo en tiempo lineal porque nunca revisa dos veces una arista: la pila guarda "
    "el camino actual y los vértices que se atascan se van fijando en el ciclo, lo que empalma los sub-ciclos "
    "automáticamente. Fleury, en cambio, cuesta O(E²).",
    "Separar la lógica (C++) de la visualización (Manim) mediante una traza de eventos garantiza que la "
    "animación muestre la ejecución real y permite reutilizar el mismo visualizador con cualquier grafo.",
    "La versión iterativa con estructuras propias evita el desbordamiento de la pila de llamadas en grafos "
    "grandes (probado con 200 000 aristas) y soporta multigrafos con lazos y aristas paralelas.",
])

# ------------------------------------------------------------------ 8
doc.add_heading("Referencias", 1)
vinetas([
    "Hierholzer, C. & Wiener, C. (1873). Über die Möglichkeit, einen Linienzug ohne Wiederholung und ohne "
    "Unterbrechung zu umfahren. Mathematische Annalen, 6(1), 30–32.",
    "Euler, L. (1741). Solutio problematis ad geometriam situs pertinentis. Commentarii academiae scientiarum Petropolitanae, 8, 128–140.",
    "Cormen, T., Leiserson, C., Rivest, R. & Stein, C. (2022). Introduction to Algorithms (4.ª ed.). MIT Press.",
    "cp-algorithms. Finding the Eulerian path in O(M). https://cp-algorithms.com/graph/euler_path.html",
    "Manim Community Developers. Manim Community v0.21. https://www.manim.community — estilo inspirado en 3Blue1Brown.",
])

# ------------------------------------------------------------------ Anexo
ARCHIVOS_CODIGO = [
    ("src/estructuras/Pila.h", "Pila enlazada propia (usada por Hierholzer y por el DFS de conexidad)."),
    ("src/estructuras/Lista.h", "Lista enlazada propia (listas de adyacencia y ciclo resultante)."),
    ("src/GrafoEuleriano.h", "Interfaz del TDA GrafoEuleriano."),
    ("src/GrafoEuleriano.cpp", "Verificación del teorema de Euler, Hierholzer iterativo y escritura de la traza."),
    ("src/main.cpp", "Programa de línea de comandos."),
    ("tests/pruebas.cpp", "Pruebas aleatorias y de casos borde."),
    ("animacion/escena.py", "Escenas de Manim que leen la traza generada por el C++."),
    ("ejecutar.ps1", "Script que compila, prueba, genera las trazas y renderiza las escenas."),
]


def bloque_codigo(texto):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    celda = t.rows[0].cells[0]
    celda.width = Cm(16.2)
    sombrear(celda, "F4F6F8")
    p = celda.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto.expandtabs(4).rstrip())
    r.font.name = "Consolas"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    r.font.size = Pt(7.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


doc.add_page_break()
doc.add_heading("Anexo A. Código fuente", 1)
parrafo("Código completo del proyecto, idéntico al del archivo .zip entregado en Gradescope. Ninguna "
        "estructura proviene de bibliotecas: la pila y la lista son implementaciones propias.")
p = parrafo("Repositorio: ")
enlace(p, REPO)
for ruta, desc in ARCHIVOS_CODIGO:
    doc.add_heading(ruta, 2)
    parrafo(desc, italica=True, color=GRIS, espacio=3)
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        bloque_codigo(f.read())

doc.save(SALIDA)
print("Informe generado:", SALIDA)
