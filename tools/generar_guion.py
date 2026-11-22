"""Genera docs/Guion_Exposicion.docx (y luego PDF con LibreOffice).

Guion para grabar la exposicion con presentacion/Ciclo_Euleriano.pdf y los mini videos de video/.
Cada diapositiva tiene:  ACCIONES (lo que haces)  y  DECIR (lo que lees en voz alta).
"""
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "docs", "Guion_Exposicion.docx")

AZUL = RGBColor(0x1F, 0x3B, 0x5C)
GRIS = RGBColor(0x5A, 0x63, 0x70)
NARANJA = RGBColor(0xB4, 0x52, 0x00)

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(1.8)
    s.left_margin = s.right_margin = Cm(2.2)
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(12)


def fondo(parr, color):
    pPr = parr._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    pPr.append(shd)


def texto(t, tam=12, negrita=False, color=None, italica=False, centro=False, despues=6):
    p = doc.add_paragraph()
    r = p.add_run(t)
    r.font.size = Pt(tam)
    r.bold = negrita
    r.italic = italica
    if color:
        r.font.color.rgb = color
    if centro:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(despues)
    return p


def accion(t):
    """Caja naranja: algo que HACES (no se lee en voz alta)."""
    p = doc.add_paragraph()
    r = p.add_run("▶ ACCIÓN:  ")
    r.bold = True
    r.font.color.rgb = NARANJA
    r2 = p.add_run(t)
    r2.bold = True
    fondo(p, "FFE9D2")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(0.2)


def gesto(t):
    """Indicacion de actuacion: tono, pausa, señalar."""
    p = doc.add_paragraph()
    r = p.add_run("(" + t + ")")
    r.italic = True
    r.font.size = Pt(11)
    r.font.color.rgb = GRIS
    p.paragraph_format.space_after = Pt(4)


def decir(t):
    """Texto que lees en voz alta."""
    p = doc.add_paragraph()
    r = p.add_run("🎤 DECIR:  ")
    r.bold = True
    r.font.color.rgb = AZUL
    p.add_run(t)
    fondo(p, "EAF1FB")
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.left_indent = Cm(0.2)


def diapositiva(n, titulo, tiempo):
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    p = texto(f"DIAPOSITIVA {n} · {titulo}", 15, True, AZUL, despues=2)
    r = p.add_run(f"     ⏱ {tiempo}")
    r.font.size = Pt(11)
    r.font.color.rgb = GRIS
    r.bold = False


# --------------------------------------------------------------------- portada
texto("Guion de exposición", 26, True, AZUL, centro=True, despues=2)
texto("Ciclo Euleriano · Algoritmo de Hierholzer", 16, False, GRIS, centro=True, despues=2)
texto("Diego Abraham Ladrón de Guevara · CS2023 AED · UTEC 2026-2", 12, False, GRIS, centro=True, despues=14)

texto("Cómo leer este guion", 14, True, AZUL, despues=4)
accion("Las cajas naranjas son cosas que HACES: pasar diapositiva, abrir o pausar un video.")
decir("Las cajas azules son lo que DICES en voz alta. Puedes leerlas tal cual o con tus palabras.")
gesto("El texto gris en cursiva entre paréntesis es cómo decirlo: tono, pausas, qué señalar.")

texto("Antes de grabar (checklist)", 14, True, AZUL, despues=4)
for item in [
    "Abre presentacion/Ciclo_Euleriano.pdf en pantalla completa (F5 en Acrobat / Ctrl+L, o modo presentación de tu visor).",
    "Abre la carpeta video/ en el Explorador. Los mini videos NO se reproducen dentro del PDF: "
    "cuando el guion diga REPRODUCIR, abre el .mp4 con doble clic, ponlo en pantalla completa (tecla F en el "
    "reproductor de Windows) y al terminar ciérralo (Esc + Alt+F4) para volver al PDF.",
    "Los videos no tienen audio: tú narras encima mientras se ven. El texto de cada video está medido "
    "para su duración; si te quedas corto, pausa el video con la barra espaciadora.",
    "Graba la pantalla con audio de micrófono (OBS, Xbox Game Bar con Win+G, o la grabación de PowerPoint).",
    "Duración objetivo: ~4 min 40 s. El MÁXIMO de la rúbrica es 5 min: respeta los tiempos ⏱ de cada diapositiva y no agregues explicaciones largas.",
    "Alternativa: si presentas con el .pptx en PowerPoint, los videos ya están incrustados en su diapositiva; "
    "solo haz clic sobre el video para reproducirlo y no necesitas abrir los archivos.",
]:
    p = doc.add_paragraph(item, style="List Bullet")
    p.paragraph_format.space_after = Pt(2)

texto("Mapa rápido", 14, True, AZUL, despues=4)
t = doc.add_table(rows=1, cols=3)
t.style = "Light Grid Accent 1"
for c, h in zip(t.rows[0].cells, ["Diapositiva", "Video a reproducir (carpeta video/)", "Duración"]):
    c.text = h
for fila in [
    ("1 · Portada", "Portada.mp4 (opcional)", "0:07"),
    ("2 · ¿Qué es un ciclo euleriano?", "Introduccion.mp4", "0:27"),
    ("3 · ¿Para qué sirve?", "—", ""),
    ("4 · Teorema de Euler", "Verificacion.mp4", "0:19"),
    ("5 · Algoritmo de Hierholzer", "—", ""),
    ("6 · Ejecución paso a paso", "Hierholzer.mp4  (el más importante)", "0:35"),
    ("7 · Resultado", "—", ""),
    ("8 · Implementación", "—", ""),
    ("9 · Casos borde", "CasoBorde.mp4", "0:44"),
    ("10 · Complejidad", "— (no hace falta)", ""),
    ("11 · Conclusiones", "—", ""),
]:
    cells = t.add_row().cells
    for c, v in zip(cells, fila):
        c.text = v
doc.add_page_break()

# --------------------------------------------------------------------- 1
diapositiva(1, "Portada", "~15 s")
accion("Empieza con el PDF en pantalla completa en la diapositiva 1. Respira, empieza a grabar.")
gesto("Tono tranquilo y amable, mirando a la cámara si te grabas.")
decir("Buenos días, profesor. ¿Qué tal? Soy Diego Ladrón de Guevara y voy a presentar el Proyecto 2: "
      "el ciclo euleriano y el algoritmo de Hierholzer, implementado en C++ y animado con Manim a partir "
      "de la ejecución real de mi programa.")
gesto("Opcional: puedes reproducir Portada.mp4 (7 s) mientras dices esto. No es necesario.")
accion("PASAR a la diapositiva 2.")

# --------------------------------------------------------------------- 2
diapositiva(2, "¿Qué es un ciclo euleriano?", "~40 s")
gesto("Señala las tres tarjetas de la izquierda mientras las nombras.")
decir("Un ciclo euleriano es un recorrido cerrado que pasa por todas las aristas de un grafo "
      "exactamente una vez; los vértices sí se pueden repetir. Es un algoritmo sobre el TDA Grafo: "
      "vértices, aristas y su relación de adyacencia.")
accion("REPRODUCIR  video/Introduccion.mp4  (27 s) en pantalla completa.")
gesto("Narra encima del video, siguiendo lo que aparece:")
decir("Este es el grafo de ejemplo: siete vértices y nueve aristas.")
gesto("Cuando aparezca el bloque 'Teorema de Euler':")
decir("El teorema de Euler dice que el ciclo existe si todos los grados son pares y las aristas están "
      "en una sola componente conexa.")
gesto("Cuando aparezca 'Hierholzer (1873)':")
decir("Y Hierholzer lo construye caminando hasta atascarse, retrocediendo y empalmando sub-ciclos.")
accion("Cierra el video (Esc y Alt+F4) y vuelve al PDF.  PASAR a la diapositiva 3.")

# --------------------------------------------------------------------- 3
diapositiva(3, "¿Para qué sirve?", "~15 s")
gesto("Recorre las cuatro tarjetas de izquierda a derecha, de arriba hacia abajo.")
decir("¿Para qué sirve? Para rutas que deben cubrir todas las calles, como la basura o el correo; para "
      "ensamblar ADN; y para trazar figuras sin levantar el lápiz. Y su origen son los puentes de "
      "Königsberg, que veremos como caso borde.")
accion("PASAR a la diapositiva 4.")

# --------------------------------------------------------------------- 4
diapositiva(4, "Teorema de Euler: ¿cuándo existe?", "~25 s")
decir("Antes de buscar el ciclo, el programa verifica estas dos condiciones.")
accion("REPRODUCIR  video/Verificacion.mp4  (19 s).")
gesto("Cuando aparezcan las etiquetas verdes 'g=2', 'g=4':")
decir("Calcula los grados: todos son pares, porque cada vez que entras a un vértice necesitas otra arista para salir.")
gesto("Cuando los vértices se pinten de azul uno por uno:")
decir("Luego un DFS alcanza a todos los vértices: es conexo. Veredicto: euleriano.")
accion("Cierra el video y vuelve al PDF.  PASAR a la diapositiva 5.")

# --------------------------------------------------------------------- 5
diapositiva(5, "Algoritmo de Hierholzer", "~20 s")
gesto("Señala los círculos 1, 2 y 3 y luego el pseudocódigo de la derecha.")
decir("Hierholzer usa una pila. Si el tope tiene una arista libre, la marco y apilo el vecino: avanzar. "
      "Si no, lo saco y lo pongo al inicio del ciclo: retroceder. Y si el nuevo tope aún tiene aristas, "
      "nace un sub-ciclo que queda empalmado ahí.")
accion("PASAR a la diapositiva 6.")

# --------------------------------------------------------------------- 6
diapositiva(6, "Ejecución paso a paso  (DIAPOSITIVA CLAVE)", "~50 s")
gesto("Antes del video, explica la leyenda de colores de la derecha.")
decir("Veamos la ejecución real: amarillo es el camino en la pila, verde lo que ya está en el ciclo.")
accion("REPRODUCIR  video/Hierholzer.mp4  (35 s). Ten el dedo en la barra espaciadora por si necesitas pausar.")
gesto("Al inicio, cuando el punto recorre 0 → 1 → 2 → 0:")
decir("Cero, uno, dos y de vuelta al cero. El cero se atasca: sale de la pila y entra al ciclo.")
gesto("Cuando aparezca el mensaje naranja 'aún tiene aristas libres → nuevo sub-ciclo':")
decir("Pero el dos aún tiene aristas: nace el sub-ciclo dos, tres, cuatro, dos. Y en el cuatro, el de cuatro, cinco, seis.")
gesto("Señala la pila a la derecha (sin pausar):")
decir("Cada vértice que se atasca baja de la pila a la fila del ciclo; así los sub-ciclos se empalman solos.")
gesto("Al final, cuando el punto amarillo recorre todo y numera las aristas:")
decir("Pila vacía: ciclo completo, las nueve aristas usadas una sola vez.")
accion("Cierra el video y vuelve al PDF.  PASAR a la diapositiva 7.")

# --------------------------------------------------------------------- 7
diapositiva(7, "Resultado", "~8 s")
gesto("Señala la secuencia amarilla de la derecha.")
decir("Este es el ciclo que imprime el programa: diez vértices, es decir, aristas más uno.")
accion("PASAR a la diapositiva 8.")

# --------------------------------------------------------------------- 8
diapositiva(8, "Implementación: la animación es real", "~20 s")
gesto("Sigue con el dedo el flujo de las cuatro cajas, de izquierda a derecha.")
decir("La animación es real: mi programa en C++ ejecuta Hierholzer y escribe una traza con cada evento, "
      "y Manim solo la dibuja. Usé mi propia pila y lista enlazada, y lo validé con más de doce mil "
      "pruebas automáticas sin fallos.")
accion("PASAR a la diapositiva 9.")

# --------------------------------------------------------------------- 9
diapositiva(9, "Casos borde", "~50 s")
decir("Ahora, tres casos borde.")
accion("REPRODUCIR  video/CasoBorde.mp4  (44 s).")
gesto("Cuando aparezca Königsberg con las etiquetas rojas:")
decir("Königsberg: un multigrafo con aristas repetidas, que mi implementación soporta. Sus cuatro "
      "vértices tienen grado impar, así que no hay ciclo y Hierholzer ni se ejecuta.")
gesto("Cuando aparezcan los dos triángulos separados:")
decir("Aquí todos los grados son pares, pero son dos triángulos separados: el DFS no alcanza la segunda "
      "parte. Veredicto: desconectado.")
gesto("Cuando aparezca un solo vértice verde:")
decir("Y con un solo vértice sin aristas, la respuesta es el ciclo trivial.")
accion("Cierra el video y vuelve al PDF.  PASAR a la diapositiva 10.")

# --------------------------------------------------------------------- 10
diapositiva(10, "Complejidad", "~25 s")
gesto("Señala el O(V + E) grande y luego la tabla fila por fila.")
decir("Todo es O de V más E, en tiempo y en memoria. La clave: cada arista se marca usada una sola vez y "
      "el puntero de cada lista de adyacencia solo avanza. Fleury, en cambio, es O de E al cuadrado.")
gesto("No reproduzcas Complejidad.mp4: la tabla ya está en la diapositiva y te ahorras tiempo.")
accion("PASAR a la diapositiva 11.")

# --------------------------------------------------------------------- 11
diapositiva(11, "Conclusiones y cierre", "~25 s")
gesto("Una conclusión por tarjeta, con tono de cierre.")
decir("En conclusión: decidir si existe el ciclo es lineal; construirlo con Hierholzer también, porque "
      "nunca revisa dos veces una arista; y la traza garantiza que la animación muestra la ejecución real. "
      "El código está en el repositorio de GitHub en pantalla. Muchas gracias.")
gesto("Sonríe y haz una pausa de 2 segundos antes de cortar la grabación.")
accion("DETENER la grabación. (No pongas Creditos.mp4: tu nombre ya está en la portada.)")

doc.add_paragraph()
texto("Después de grabar", 14, True, AZUL, despues=4)
for item in [
    "Sube el video a Drive (con acceso para cualquiera con el enlace) o a YouTube como no listado.",
    "Pega el enlace en la sección '5. Evidencia' del informe (docs/Informe_Ciclo_Euleriano.docx, "
    "línea en rojo) y vuelve a exportarlo a PDF.",
    "Prueba que el enlace abra desde una ventana de incógnito antes de entregar en Gradescope.",
]:
    p = doc.add_paragraph(item, style="List Bullet")
    p.paragraph_format.space_after = Pt(2)

doc.save(SALIDA)
print("Guion generado:", SALIDA)
