"""Genera docs/Informe_Ciclo_Euleriano.docx con el mismo formato del informe del Proyecto 1
(portada UTEC en Times New Roman, cuerpo en Arial, tablas con cabecera azul, bloques grises).

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
ESCENAS = REPO + "/tree/main/video"
# Enlace al video narrado (Drive / YouTube no listado). Si queda vacío se marca en rojo.
VIDEO_URL = "https://drive.google.com/file/d/103c2ffegqvUGhTvNSGfAEIh1FJ5nVPyn/view?usp=sharing"

with open(os.path.join(RAIZ, "integrantes.txt"), encoding="utf-8") as f:
    INTEGRANTES = [l.strip() for l in f if l.strip()]

NEGRO = RGBColor(0, 0, 0)
GRIS = RGBColor(0x55, 0x55, 0x55)
AZUL_TABLA = "3C78D8"
GRIS_BLOQUE = "F2F2F2"
BORDE = "BFBFBF"
CUERPO = "Arial"
PORTADA = "Times New Roman"

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2.54)
    s.left_margin = s.right_margin = Cm(2.54)


def fuente(estilo_o_run, nombre):
    estilo_o_run.font.name = nombre
    rpr = estilo_o_run.element.get_or_add_rPr() if hasattr(estilo_o_run.element, "get_or_add_rPr") \
        else estilo_o_run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), nombre)


normal = doc.styles["Normal"]
fuente(normal, CUERPO)
normal.font.size = Pt(11)
normal.paragraph_format.line_spacing = 1.15
for nivel, tam in ((1, 15), (2, 12.5)):
    h = doc.styles[f"Heading {nivel}"]
    fuente(h, CUERPO)
    h.font.size = Pt(tam)
    h.font.bold = True
    h.font.italic = False
    h.font.color.rgb = NEGRO
    h.paragraph_format.space_before = Pt(14 if nivel == 1 else 10)
    h.paragraph_format.space_after = Pt(4)


# ------------------------------------------------------------------ utilidades
def parrafo(partes, centro=False, justificar=True, espacio=6, tam=None, fnt=None, color=None):
    """partes: texto o lista de (texto, negrita)."""
    if isinstance(partes, str):
        partes = [(partes, False)]
    p = doc.add_paragraph()
    for texto, negrita in partes:
        r = p.add_run(texto)
        r.bold = negrita
        if tam:
            r.font.size = Pt(tam)
        if fnt:
            fuente(r, fnt)
        if color:
            r.font.color.rgb = color
    if centro:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif justificar:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(espacio)
    return p


def vinetas(items, numeradas=False):
    for i, it in enumerate(items, 1):
        p = doc.add_paragraph(style="List Number" if numeradas else "List Bullet")
        if isinstance(it, tuple):
            p.add_run(it[0]).bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)
        p.paragraph_format.space_after = Pt(3)


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def bordes(tabla_, color):
    tblPr = tabla_._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), color)
        b.append(e)
    tblPr.append(b)


def anchos_tabla(t, anchos):
    """Fija anchos reales (Word y LibreOffice) y centra la tabla."""
    t.autofit = False
    tblPr = t._tbl.tblPr
    w = OxmlElement("w:tblW")
    w.set(qn("w:w"), str(int(sum(anchos) / 2.54 * 1440)))
    w.set(qn("w:type"), "dxa")
    tblPr.append(w)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    tblPr.append(jc)
    mar = OxmlElement("w:tblCellMar")
    for lado, v in (("top", 50), ("bottom", 50), ("left", 100), ("right", 100)):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)
    for gc, a in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), anchos):
        gc.set(qn("w:w"), str(int(a / 2.54 * 1440)))
    for fila in t.rows:
        for c, a in zip(fila.cells, anchos):
            c.width = Cm(a)


def tabla(filas, anchos):
    t = doc.add_table(rows=len(filas), cols=len(filas[0]))
    bordes(t, BORDE)
    anchos_tabla(t, anchos)
    for i, fila in enumerate(filas):
        for j, txt in enumerate(fila):
            c = t.cell(i, j)
            c.width = Cm(anchos[j])
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(txt)
            r.font.size = Pt(10)
            if i == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                sombrear(c, AZUL_TABLA)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def bloque(texto):
    """Bloque gris con Consolas, como la salida de consola del Proyecto 1."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    anchos_tabla(t, [15.9])
    c = t.rows[0].cells[0]
    sombrear(c, GRIS_BLOQUE)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto)
    fuente(r, "Consolas")
    r.font.size = Pt(9.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def imagen(nombre, pie, ancho=14.5):
    doc.add_picture(os.path.join(IMG, nombre), width=Cm(ancho))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.space_after = Pt(2)
    p = parrafo(pie, centro=True, tam=9.5, color=GRIS, espacio=10)
    for r in p.runs:
        r.italic = True


def enlace(parr, url, texto=None):
    rid = parr.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                              is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    b = OxmlElement("w:b")
    col = OxmlElement("w:color")
    col.set(qn("w:val"), "1155CC")
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.extend([b, col, u])
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = texto or url
    run.append(t)
    h.append(run)
    parr._p.append(h)


# ------------------------------------------------------------------ portada
def linea_portada(partes, tam, espacio=6):
    return parrafo(partes, centro=True, espacio=espacio, tam=tam, fnt=PORTADA)


doc.add_paragraph()
linea_portada([("UNIVERSIDAD DE INGENIERÍA Y TECNOLOGÍA", True)], 14, 4)
linea_portada("“Año de la Esperanza y el Fortalecimiento de la Democracia”", 11, 30)
doc.add_picture(os.path.join(IMG, "logo_utec.png"), width=Cm(7.2))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.paragraphs[-1].paragraph_format.space_after = Pt(28)
linea_portada([("Proyecto 2: Ciclo Euleriano", True)], 14)
linea_portada([("Curso: ", True), ("Algoritmos y Estructuras de Datos", False)], 14)
linea_portada([("Docente: ", True), ("Wilder Nina Choquehuayta", False)], 14, 30)

t = doc.add_table(rows=1 + len(INTEGRANTES), cols=1)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
bordes(t, "000000")
anchos_tabla(t, [9.5])
for i, txt in enumerate(["Integrante" if len(INTEGRANTES) == 1 else "Integrantes"] + INTEGRANTES):
    c = t.cell(i, 0)
    c.width = Cm(9.5)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(txt)
    r.bold = True
    fuente(r, PORTADA)
    r.font.size = Pt(11)
for _ in range(3):
    doc.add_paragraph()
linea_portada([("Lima - Perú", True)], 11)
linea_portada([("2026", True)], 11, 0)
doc.add_page_break()

# ------------------------------------------------------------------ enlaces
p = doc.add_paragraph()
r = p.add_run("Enlaces del proyecto")
r.bold = True
r.font.size = Pt(23)
p.paragraph_format.space_after = Pt(6)
pv = doc.add_paragraph(style="List Bullet")
pv.add_run("Repositorio : ").bold = True
enlace(pv, REPO + ".git")
pv = doc.add_paragraph(style="List Bullet")
pv.add_run("Video: ").bold = True
if VIDEO_URL:
    enlace(pv, VIDEO_URL)
else:
    r = pv.add_run("[PEGAR ENLACE DEL VIDEO NARRADO]")
    r.bold = True
    r.font.color.rgb = RGBColor(0xC0, 0x30, 0x30)
pv = doc.add_paragraph(style="List Bullet")
pv.add_run("Escenas de Manim (MP4, 1080p): ").bold = True
enlace(pv, ESCENAS)

# ------------------------------------------------------------------ 1
doc.add_heading("1. Descripción de la estructura y TDA", 1)
parrafo([("Un ", False), ("ciclo euleriano", True), (" es un recorrido cerrado que pasa por ", False),
         ("todas las aristas de un grafo exactamente una vez", True),
         ("; los vértices sí pueden repetirse. El problema nace con los siete puentes de Königsberg, que Euler "
          "resolvió en 1736 demostrando que no existía tal recorrido.", False)])
parrafo([("No es una estructura en sí, sino un algoritmo sobre el ", False), ("TDA Grafo", True),
         (" (vértices, aristas y relación de adyacencia). La implementación trabaja sobre un multigrafo no "
          "dirigido, que admite lazos y aristas paralelas, y responde dos preguntas: ¿existe el ciclo? y, si "
          "existe, ¿cuál es?", False)])
parrafo([("Teorema de Euler: ", True),
         ("un grafo tiene ciclo euleriano si y solo si todos sus vértices tienen grado par y todas las aristas "
          "están en una misma componente conexa. Cada vez que el recorrido entra a un vértice debe salir por "
          "otra arista, así que las aristas de cada vértice se consumen de a pares.", False)])
parrafo([("Usos en la práctica: ", True),
         ("rutas que deben cubrir todas las calles (recolección de basura, correo: problema del cartero chino), "
          "ensamblaje de genomas con grafos de De Bruijn y trazado de circuitos o plotters sin levantar el "
          "cabezal.", False)])

# ------------------------------------------------------------------ 2
doc.add_heading("2. Implementación", 1)
parrafo("Todo está en C++17 y fue programado por el grupo; el algoritmo no usa std::stack, std::vector ni "
        "librerías de grafos.")
tabla([["Estructura propia", "Archivo", "Uso dentro del algoritmo"],
       ["Pila<T> (enlazada)", "estructuras/Pila.h", "Camino actual de Hierholzer y DFS de conexidad sin recursión"],
       ["Lista<T> (enlazada)", "estructuras/Lista.h", "Listas de adyacencia y ciclo resultante (inserción al inicio en O(1))"],
       ["GrafoEuleriano", "GrafoEuleriano.h/.cpp", "Multigrafo con id por arista, arreglo usada[e], verificación "
                                                    "del teorema, Hierholzer y escritura de la traza"]],
      [3.8, 4.0, 8.1])

doc.add_heading("2.1 Verificación", 2)
parrafo("verificar() calcula el grado de cada vértice (tamaño de su lista de adyacencia) y luego hace un DFS "
        "iterativo desde un vértice con aristas. El veredicto puede ser:")
vinetas([("EULERIANO: ", "grados pares y una sola componente con aristas."),
         ("GRADOS_IMPARES: ", "algún vértice tiene grado impar (por ejemplo, Königsberg)."),
         ("DESCONECTADO: ", "grados pares, pero las aristas están en dos o más componentes."),
         ("SIN_ARISTAS: ", "el ciclo es trivial: un solo vértice.")])

doc.add_heading("2.2 Algoritmo de Hierholzer", 2)
parrafo("Versión iterativa con la pila propia. En cada paso se mira el vértice v del tope:")
vinetas([("Caso A: v tiene una arista libre (v, w): ", "se marca como usada, se apila w y se continúa (evento AVANZA)."),
         ("Caso B: v no tiene aristas libres: ", "se desapila y se agrega al inicio del ciclo (evento RETROCEDE). "
                                                  "Si el nuevo tope aún tiene aristas, desde ahí nace un sub-ciclo "
                                                  "que queda empalmado automáticamente.")])
parrafo("Un puntero siguiente[v] recuerda hasta dónde se revisó la lista de v, así que nunca se vuelve a mirar "
        "una arista ya usada. Para el grafo principal (7 vértices, 9 aristas) el resultado es "
        "0 → 1 → 2 → 3 → 4 → 5 → 6 → 4 → 2 → 0.")

doc.add_heading("2.3 Animación impulsada por la implementación", 2)
parrafo([("Para que la animación sea real y no simulada, el programa escribe un ", False),
         ("archivo de traza", True),
         (" con cada paso ejecutado (GRADO, CONEXO_VISITA, PUSH, AVANZA, RETROCEDE, CICLO, etc.). El script de "
          "Manim (animacion/escena.py) no contiene lógica del algoritmo: solo lee esa traza y dibuja los eventos "
          "en el orden en que ocurrieron. Si se cambia el grafo de entrada, la animación cambia sola.", False)])

# ------------------------------------------------------------------ 3
doc.add_heading("3. Análisis de complejidad", 1)
parrafo("Sea V el número de vértices y E el número de aristas.")
tabla([["Operación", "Tiempo", "Justificación"],
       ["Leer el grafo", "O(V + E)", "Cada arista se inserta en dos listas en O(1)."],
       ["Grados", "O(V)", "El grado es el tamaño de la lista de adyacencia."],
       ["Conexidad (DFS)", "O(V + E)", "Cada vértice se apila una vez y cada lista se recorre una vez."],
       ["Hierholzer", "O(V + E)", "Cada arista se marca una vez y siguiente[v] solo avanza: se revisan 2E "
                                  "incidencias, con E+1 push y E+1 pop."],
       ["Fleury (comparación)", "O(E²)", "Antes de cada paso comprueba si la arista es puente. No implementado."],
       ["Memoria", "O(V + E)", "Listas de adyacencia, arreglo usada[], pila y ciclo."]],
      [4.0, 2.6, 9.3])
parrafo([("Peor caso: ", True),
         ("si el grafo no es euleriano, la verificación lo detecta en O(V + E) y Hierholzer no se ejecuta. El "
          "tiempo lineal es óptimo, porque la salida misma tiene E + 1 vértices.", False)])

# ------------------------------------------------------------------ 4
doc.add_page_break()
doc.add_heading("4. Herramientas, reproducción y contribuciones", 1)
tabla([["Herramienta", "Uso"],
       ["C++17 · g++ (MSYS2 UCRT64)", "Algoritmo, pruebas y generación de trazas"],
       ["Python 3.13 + Manim Community 0.21", "Escenas animadas (animacion/escena.py)"],
       ["FFmpeg", "Codificación de los MP4"],
       ["Git + GitHub", "Control de versiones y entrega"]], [6.5, 9.4])
parrafo([("Pasos para reproducir: ", True), ("(en Windows, .\\ejecutar.ps1 hace todo)", False)])
bloque("g++ -std=c++17 -O2 -o euler src/main.cpp src/GrafoEuleriano.cpp\n"
       "./euler grafos/principal.txt -t trazas/principal.txt\n"
       "manim -qh animacion/escena.py Portada Introduccion Verificacion Hierholzer CasoBorde Complejidad Creditos")
if len(INTEGRANTES) == 1:
    filas = [["Integrante", "Contribución"],
             [INTEGRANTES[0], "Trabajo individual (100 %): implementación en C++, pruebas, animación en Manim, "
                              "video, informe y presentación"]]
else:
    filas = [["Integrante", "Contribución"]] + [[n, "—"] for n in INTEGRANTES]
tabla(filas, [6.0, 9.9])

# ------------------------------------------------------------------ 5
doc.add_heading("5. Evidencia", 1)
imagen("verificacion.png", "Figura 1. Verificación de grados y DFS de conexidad sobre el grafo principal (escena Verificacion).")
imagen("hierholzer_medio.png", "Figura 2. Hierholzer a mitad de ejecución: camino actual en amarillo, pila a la "
                               "derecha y ciclo en construcción abajo (escena Hierholzer).")
imagen("konigsberg.png", "Figura 3. Caso borde: los puentes de Königsberg tienen 4 vértices de grado impar (escena CasoBorde).")
parrafo([("Salida del programa en consola:", True)], espacio=4)
bloque("Grafo: 7 vertices, 9 aristas\n"
       "Grados: 0:2 1:2 2:4 3:2 4:4 5:2 6:2\n"
       "Ciclo euleriano (10 vertices, 9 aristas):\n"
       "  0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 4 -> 2 -> 0")
parrafo([("Pruebas automáticas: ", True),
         ("se generaron 3000 multigrafos eulerianos aleatorios (el ciclo debe ser cerrado, tener E + 1 vértices y "
          "usar cada arista una sola vez) y 3000 grafos cualesquiera cuyo veredicto se comparó con un chequeo "
          "independiente basado en union-find.", False)])
bloque("12591 verificaciones, 0 fallos")
parrafo([("Casos borde considerados: ", True),
         ("un solo vértice sin aristas (ciclo trivial), un lazo, aristas paralelas, una sola arista (grados "
          "impares), grafo desconectado con grados pares y un ciclo de 200 000 vértices (la versión iterativa no "
          "desborda la pila de llamadas).", False)])

# ------------------------------------------------------------------ 6
doc.add_heading("6. Conclusiones", 1)
vinetas([("Decidir es barato. ", "La existencia del ciclo depende solo de la paridad de los grados y de la "
                                 "conexidad, ambas verificables en O(V + E) sin buscar el ciclo."),
         ("La pila hace el trabajo de empalmar. ", "Hierholzer guarda el camino actual en la pila y fija en el ciclo "
                                                  "los vértices que se atascan; así los sub-ciclos se unen solos y "
                                                  "el costo es lineal, frente a O(E²) de Fleury."),
         ("No revisar dos veces una arista es la clave. ", "Sin el arreglo usada[] y el puntero siguiente[v], el "
                                                          "peor caso subiría a O(V·E)."),
         ("La versión iterativa es más robusta. ", "Con estructuras propias evita el desbordamiento de la pila de "
                                                   "llamadas en grafos grandes."),
         ("Animar a partir de una traza separa la lógica de la visualización", ".")], numeradas=True)

# ------------------------------------------------------------------ 7
doc.add_heading("7. Referencias", 1)
vinetas([
    "Hierholzer, C. y Wiener, C. (1873). Über die Möglichkeit, einen Linienzug ohne Wiederholung und ohne "
    "Unterbrechung zu umfahren. Mathematische Annalen, 6(1), 30–32.",
    "Euler, L. (1741). Solutio problematis ad geometriam situs pertinentis. Commentarii academiae scientiarum "
    "Petropolitanae, 8, 128–140.",
    "Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022). Introduction to Algorithms (4.ª ed.). MIT Press.",
    "cp-algorithms. Finding the Eulerian path in O(M). https://cp-algorithms.com/graph/euler_path.html",
    "The Manim Community Developers. Manim – Mathematical Animation Framework. https://www.manim.community",
])

doc.save(SALIDA)
print("Informe generado:", SALIDA)
