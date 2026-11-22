"""Animacion del ciclo euleriano (Hierholzer) con Manim.

La animacion NO calcula el ciclo: solo LEE la traza que escribe el programa
C++ (src/GrafoEuleriano.cpp) y reproduce cada evento:
    GRAFO / NODO / ARISTA            -> dibujar el grafo
    GRADO / IMPARES / CONEXO_VISITA  -> verificacion del teorema de Euler
    PUSH / AVANZA / RETROCEDE        -> ejecucion de Hierholzer
    CICLO                            -> resultado final

Generar trazas:   ./euler grafos/principal.txt -t trazas/principal.txt
Renderizar:       manim -qh animacion/escena.py Hierholzer
"""
import os

from manim import *

RAIZ_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAZAS = os.path.join(RAIZ_REPO, "trazas")
TRAZA_PRINCIPAL = os.environ.get("TRAZA", os.path.join(TRAZAS, "principal.txt"))
TRAZA_KONIGSBERG = os.path.join(TRAZAS, "konigsberg.txt")
TRAZA_DESCONECTADO = os.path.join(TRAZAS, "desconectado.txt")
TRAZA_UN_VERTICE = os.path.join(TRAZAS, "un_vertice.txt")
ARCHIVO_INTEGRANTES = os.path.join(RAIZ_REPO, "integrantes.txt")

FONDO = "#0f1724"
C_ARISTA = GREY_B
C_NODO = "#1f3b5c"
C_BORDE = "#9cc3ff"
C_CAMINO = YELLOW          # arista en el camino actual (todavia en la pila)
C_CICLO = GREEN_C          # arista ya fijada en el ciclo final
C_ACTUAL = ORANGE          # vertice en el tope de la pila
C_MALO = RED_C
C_BIEN = GREEN_C
C_DFS = BLUE_C

config.background_color = FONDO


# --------------------------------------------------------------------------
#  Lectura de la traza
# --------------------------------------------------------------------------
def leer_traza(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"No existe la traza '{ruta}'. Generala primero con el programa C++:\n"
            f"  ./euler grafos/principal.txt -t trazas/principal.txt")
    eventos = []
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            partes = linea.split()
            if not partes:
                continue
            cmd, resto = partes[0], partes[1:]
            if cmd == "VEREDICTO":
                eventos.append((cmd, resto[0]))
            elif cmd == "NODO":
                eventos.append((cmd, [int(resto[0]), float(resto[1]), float(resto[2])]))
            else:
                eventos.append((cmd, [int(x) for x in resto]))
    return eventos


def leer_integrantes():
    if os.path.exists(ARCHIVO_INTEGRANTES):
        with open(ARCHIVO_INTEGRANTES, encoding="utf-8") as f:
            nombres = [l.strip() for l in f if l.strip()]
        if nombres:
            return nombres
    return ["(completar integrantes.txt)"]


FUENTE = "Segoe UI"


def t(texto, size=26, color=WHITE, **kw):
    kw.setdefault("font", FUENTE)
    return Text(texto, font_size=size, color=color, **kw)


# --------------------------------------------------------------------------
#  Escena base: sabe dibujar el grafo descrito en la traza
# --------------------------------------------------------------------------
class EscenaGrafo(Scene):
    def preparar(self, ruta, desplazamiento=ORIGIN):
        self.eventos = leer_traza(ruta)
        self.pos = {}
        self.aristas = {}       # id -> (u, v)
        for cmd, a in self.eventos:
            if cmd == "NODO":
                self.pos[a[0]] = np.array([a[1], a[2], 0.0]) + desplazamiento
            elif cmd == "ARISTA":
                self.aristas[a[0]] = (a[1], a[2])
        self.titulo = None
        self.leyenda = None
        self.v_nodos = {}
        self.v_aristas = {}

    # ---------- piezas visuales ----------
    def dibujo_arista(self, e, color=C_ARISTA, ancho=5):
        u, v = self.aristas[e]
        # aristas paralelas: se curvan con angulos distintos
        paralelas = [x for x, (a, b) in sorted(self.aristas.items()) if {a, b} == {u, v}]
        k = paralelas.index(e)
        total = len(paralelas)
        angulo = 0 if total == 1 else (k - (total - 1) / 2) * 0.9
        p, q = self.pos[u], self.pos[v]
        if u > v:                      # orientacion canonica para que las curvas no se crucen
            p, q = q, p
            angulo = -angulo
        if angulo == 0:
            return Line(p, q, color=color, stroke_width=ancho)
        return ArcBetweenPoints(p, q, angle=angulo, color=color, stroke_width=ancho)

    def dibujo_nodo(self, v, color=C_NODO, borde=C_BORDE):
        c = Circle(0.3, color=borde, stroke_width=3, fill_color=color, fill_opacity=1)
        return VGroup(c, t(str(v), 26, WHITE).move_to(c)).move_to(self.pos[v])

    def grafo(self):
        for e in self.aristas:
            self.v_aristas[e] = self.dibujo_arista(e)
        for v in self.pos:
            self.v_nodos[v] = self.dibujo_nodo(v)
        return VGroup(*self.v_aristas.values(), *self.v_nodos.values())

    def mostrar_grafo(self, animar=True):
        g = self.grafo()
        if animar:
            self.play(LaggedStart(*[GrowFromCenter(n) for n in self.v_nodos.values()], lag_ratio=0.08))
            if self.v_aristas:
                self.play(LaggedStart(*[Create(a) for a in self.v_aristas.values()], lag_ratio=0.08))
            self.add(*self.v_nodos.values())          # nodos por encima de las aristas
        else:
            self.add(*self.v_aristas.values(), *self.v_nodos.values())
        return g

    def poner_titulo(self, texto, color=WHITE):
        nuevo = t(texto, 32, color).to_edge(UP, buff=0.3)
        anims = [FadeIn(nuevo)]
        if self.titulo is not None:
            anims.append(FadeOut(self.titulo))
        self.titulo = nuevo
        return anims

    def poner_leyenda(self, texto, color=GREY_A):
        nuevo = t(texto, 24, color).to_edge(DOWN, buff=0.25)
        if nuevo.width > 13.5:
            nuevo.scale_to_fit_width(13.5)
        anims = [FadeIn(nuevo)]
        if self.leyenda is not None:
            anims.append(FadeOut(self.leyenda))
        self.leyenda = nuevo
        return anims

    def color_nodo(self, v, relleno, borde=C_BORDE):
        return self.v_nodos[v][0].animate.set_fill(relleno).set_stroke(borde)

    def insignia_grado(self, v, d):
        par = d % 2 == 0
        color = C_BIEN if par else C_MALO
        caja = RoundedRectangle(corner_radius=0.12, width=0.95, height=0.42,
                                color=color, fill_color=FONDO, fill_opacity=0.9, stroke_width=2)
        txt = t(f"g={d}", 20, color).move_to(caja)
        ins = VGroup(caja, txt)
        # se ubica alejandose del centro del grafo
        centro = np.mean(list(self.pos.values()), axis=0)
        dir_ = self.pos[v] - centro
        dir_ = dir_ / (np.linalg.norm(dir_) + 1e-9)
        ins.move_to(self.pos[v] + dir_ * 0.72 + UP * 0.05)
        return ins

    # ---------- verificacion del teorema ----------
    def animar_verificacion(self, pausa=1.0):
        insignias = VGroup()
        for cmd, a in self.eventos:
            if cmd == "GRADO":
                v, d = a
                ins = self.insignia_grado(v, d)
                insignias.add(ins)
                self.play(FadeIn(ins, scale=0.6), Indicate(self.v_nodos[v], color=C_BIEN if d % 2 == 0 else C_MALO),
                          run_time=0.45)
            elif cmd == "IMPARES":
                k, impares = a[0], a[1:]
                if k == 0:
                    anims = self.poner_leyenda("Condición 1: todos los grados son pares  ✓", C_BIEN)
                else:
                    lista = ", ".join(str(x) for x in impares)
                    anims = self.poner_leyenda(f"Condición 1 FALLA: {k} vértices de grado impar ({lista})", C_MALO)
                    anims += [self.color_nodo(v, "#5c1f1f", C_MALO) for v in impares]
                self.play(*anims)
                self.wait(pausa)
            elif cmd == "CONEXO_VISITA":
                if not getattr(self, "_dfs_iniciado", False):
                    self._dfs_iniciado = True
                    self.play(*self.poner_leyenda("Condición 2: DFS desde un vértice con aristas para ver si todo es conexo"),
                              run_time=0.6)
                v = a[0]
                self.play(self.color_nodo(v, "#1d4e7a", C_DFS), Flash(self.v_nodos[v], color=C_DFS, flash_radius=0.45),
                          run_time=0.4)
            elif cmd == "CONEXO":
                if a[0] == 1:
                    anims = self.poner_leyenda("Condición 2: el DFS alcanzó todos los vértices con aristas  ✓", C_BIEN)
                else:
                    faltan = [v for v in self.pos if v not in self._visitados()]
                    anims = self.poner_leyenda("Condición 2 FALLA: el DFS no alcanza todas las aristas (desconectado)", C_MALO)
                    anims += [self.color_nodo(v, "#5c1f1f", C_MALO) for v in faltan]
                self.play(*anims)
                self.wait(pausa)
            elif cmd == "VEREDICTO":
                return a, insignias
        return None, insignias

    def _visitados(self):
        return {a[0] for c, a in self.eventos if c == "CONEXO_VISITA"}


# --------------------------------------------------------------------------
#  1. Portada
# --------------------------------------------------------------------------
class Portada(Scene):
    def construct(self):
        titulo = t("Ciclo Euleriano", 64, YELLOW)
        sub = t("Algoritmo de Hierholzer en O(|V| + |E|)", 32, C_BORDE)
        curso = t("CS2023 · Algoritmos y Estructuras de Datos · UTEC 2026-2", 22, GREY_B)
        nombres = VGroup(*[t(n, 26) for n in leer_integrantes()]).arrange(DOWN, buff=0.15)
        bloque = VGroup(titulo, sub, curso, nombres).arrange(DOWN, buff=0.45)
        self.play(Write(titulo), run_time=1.5)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.play(FadeIn(curso), LaggedStart(*[FadeIn(n) for n in nombres], lag_ratio=0.3))
        self.wait(2.5)
        self.play(FadeOut(bloque))


# --------------------------------------------------------------------------
#  2. Introduccion conceptual
# --------------------------------------------------------------------------
class Introduccion(EscenaGrafo):
    def construct(self):
        self.preparar(TRAZA_PRINCIPAL, desplazamiento=RIGHT * 5.0 + DOWN * 0.5)
        cab = t("¿Qué es un ciclo euleriano?", 40, YELLOW).to_edge(UP, buff=0.4)
        self.play(Write(cab))
        puntos = VGroup(
            t("• Recorre TODAS las aristas", 26),
            t("  exactamente una vez", 26),
            t("• Empieza y termina en el", 26),
            t("  mismo vértice", 26),
            t("• Los vértices sí se pueden repetir", 26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(LEFT, buff=0.6).shift(UP * 0.8)
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.3) for p in puntos], lag_ratio=0.25))
        g = self.mostrar_grafo()
        self.wait(1)

        usos = VGroup(
            t("Usos en la práctica:", 26, C_BORDE),
            t("• Rutas de basura, correo o", 23, GREY_A),
            t("  inspección de calles", 23, GREY_A),
            t("• Ensamblaje de ADN (De Bruijn)", 23, GREY_A),
            t("• Dibujar una figura sin levantar el lápiz", 23, GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).next_to(puntos, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(LaggedStart(*[FadeIn(u) for u in usos], lag_ratio=0.2))
        self.wait(2.5)
        self.play(FadeOut(puntos), FadeOut(usos))

        teo = VGroup(
            t("Teorema de Euler (grafo no dirigido)", 30, YELLOW),
            t("Existe un ciclo euleriano  ⇔", 26),
            t("1) todo vértice tiene grado PAR, y", 26, C_BIEN),
            t("2) las aristas forman una sola componente conexa", 26, C_DFS),
            t("Idea: cada vez que entras a un vértice, debes poder salir", 22, GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_edge(LEFT, buff=0.6).shift(UP * 0.3)
        self.play(g.animate.scale(0.65).to_edge(RIGHT, buff=0.3).shift(DOWN * 0.6))
        self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in teo], lag_ratio=0.3))
        self.wait(3)

        idea = VGroup(
            t("Hierholzer (1873):", 28, ORANGE),
            t("1. Camina por aristas libres hasta atascarte", 24),
            t("2. Al atascarte, retrocede: ese vértice va al ciclo", 24),
            t("3. Si al retroceder hay aristas libres, ", 24),
            t("   arma un sub-ciclo y se empalma ahí", 24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(LEFT, buff=0.6).shift(DOWN * 0.2)
        self.play(FadeOut(teo))
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.2) for x in idea], lag_ratio=0.3))
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])


# --------------------------------------------------------------------------
#  3. Verificacion de las condiciones sobre el grafo principal
# --------------------------------------------------------------------------
class Verificacion(EscenaGrafo):
    def construct(self):
        self.preparar(TRAZA_PRINCIPAL, desplazamiento=RIGHT * 2.4)
        self.play(*self.poner_titulo("Paso 0: ¿el grafo admite ciclo euleriano?"))
        self.mostrar_grafo()
        veredicto, insignias = self.animar_verificacion(pausa=1.2)
        if veredicto == "EULERIANO":
            self.play(*self.poner_leyenda("Veredicto del programa C++: EULERIANO → ejecutamos Hierholzer", C_BIEN))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])


# --------------------------------------------------------------------------
#  4. Ejecucion de Hierholzer (lo principal del video)
# --------------------------------------------------------------------------
class Hierholzer(EscenaGrafo):
    def construct(self):
        self.preparar(TRAZA_PRINCIPAL, desplazamiento=LEFT * 0.5)
        self.play(*self.poner_titulo("Algoritmo de Hierholzer"))
        self.mostrar_grafo(animar=False)

        # Panel de la pila (derecha)
        self.pila_base = np.array([3.4, -2.35, 0])
        marco = Rectangle(width=1.4, height=4.6, color=GREY_C, stroke_width=2)
        marco.move_to(self.pila_base + UP * 2.05)
        etq_pila = t("Pila", 26, C_BORDE).next_to(marco, UP, buff=0.12)
        self.pila_cajas = []

        # Fila del ciclo (abajo)
        etq_ciclo = t("Ciclo:", 24, C_CICLO).move_to([-6.25, -2.75, 0])
        self.ciclo_cajas = VGroup()

        # Leyenda de colores
        ley = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_CAMINO, stroke_width=6), t("camino actual", 18)).arrange(RIGHT, buff=0.15),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_CICLO, stroke_width=6), t("en el ciclo", 18)).arrange(RIGHT, buff=0.15),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_ARISTA, stroke_width=6), t("libre", 18)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        ley.next_to(marco, RIGHT, buff=0.35).align_to(marco, UP)
        self.play(Create(marco), FadeIn(etq_pila), FadeIn(etq_ciclo), FadeIn(ley))

        pila_aristas = []      # arista por la que se llego a cada vertice de la pila
        hubo_retroceso = False
        pasos = 0
        for cmd, a in self.eventos:
            if cmd == "PUSH":
                v = a[0]
                self.play(self.apilar(v), self.color_nodo(v, "#7a4a12", C_ACTUAL),
                          *self.poner_leyenda(f"Empezamos en el vértice {v}: lo apilamos"), run_time=0.8)
                pila_aristas.append(None)
                self.wait(0.4)
            elif cmd == "AVANZA":
                e, u, w = a
                pasos += 1
                if hubo_retroceso:
                    msg = f"{u} aún tiene aristas libres → nuevo sub-ciclo desde {u}: {u} → {w}"
                    hubo_retroceso = False
                    color_msg = ORANGE
                else:
                    msg = f"Desde {u} tomamos la arista libre {u}–{w}, la marcamos usada y apilamos {w}"
                    color_msg = GREY_A
                punto = Dot(self.pos[u], color=C_ACTUAL, radius=0.11)
                self.add(punto)
                recorrido = self.dibujo_arista(e)
                if self.aristas[e][0] != u and self.aristas[e][0] != self.aristas[e][1]:
                    recorrido = recorrido.reverse_points()
                self.play(MoveAlongPath(punto, recorrido),
                          self.v_aristas[e].animate.set_color(C_CAMINO).set_stroke(width=7),
                          self.color_nodo(u, C_NODO), self.color_nodo(w, "#7a4a12", C_ACTUAL),
                          self.apilar(w), *self.poner_leyenda(msg, color_msg), run_time=0.9)
                self.remove(punto)
                pila_aristas.append(e)
                self.wait(0.25)
            elif cmd == "RETROCEDE":
                v = a[0]
                e = pila_aristas.pop()
                hubo_retroceso = True
                anims = [self.desapilar_al_ciclo(v), self.color_nodo(v, C_NODO)]
                if e is not None:
                    anims.append(self.v_aristas[e].animate.set_color(C_CICLO).set_stroke(width=7))
                if len(self.pila_cajas) >= 1:
                    anims.append(self.color_nodo(self.pila_cajas[-1][0], "#7a4a12", C_ACTUAL))
                anims += self.poner_leyenda(f"{v} no tiene aristas libres → sale de la pila y va al INICIO del ciclo",
                                            C_CICLO)
                self.play(*anims, run_time=0.8)
                self.wait(0.25)
            elif cmd == "CICLO":
                self.mostrar_resultado(a[1:])

    # ---------- pila ----------
    def caja_pila(self, v, tope, i):
        borde, relleno = (C_ACTUAL, "#3a2a10") if tope else (GREY_B, "#222a36")
        caja = VGroup(Rectangle(width=1.1, height=0.48, color=borde, fill_color=relleno, fill_opacity=1,
                                stroke_width=2), t(str(v), 24))
        caja[1].move_to(caja[0])
        return caja.move_to(self.pila_base + UP * 0.55 * i)

    def apilar(self, v):
        i = len(self.pila_cajas)
        caja = self.caja_pila(v, True, i)
        anims = [FadeIn(caja, shift=DOWN * 0.4)]
        if self.pila_cajas:
            w, ant = self.pila_cajas[-1]
            anims.append(Transform(ant, self.caja_pila(w, False, i - 1)))
        self.pila_cajas.append((v, caja))
        return AnimationGroup(*anims)

    def desapilar_al_ciclo(self, v):
        _, caja = self.pila_cajas.pop()
        nueva = VGroup(Square(0.5, color=C_CICLO, fill_color="#123a24", fill_opacity=1, stroke_width=2), t(str(v), 24))
        nueva[1].move_to(nueva[0])
        # el vertice se agrega al INICIO del ciclo: los demas se corren a la derecha
        self.ciclo_cajas.submobjects.insert(0, nueva)
        objetivo = self.ciclo_cajas.copy().arrange(RIGHT, buff=0.06).next_to([-5.6, -2.75, 0], RIGHT, buff=0)
        anims = [ReplacementTransform(caja, nueva.move_to(objetivo[0]))]
        for i in range(1, len(self.ciclo_cajas)):
            anims.append(self.ciclo_cajas[i].animate.move_to(objetivo[i]))
        if self.pila_cajas:
            w, ant = self.pila_cajas[-1]
            anims.append(Transform(ant, self.caja_pila(w, True, len(self.pila_cajas) - 1)))
        return AnimationGroup(*anims)

    # ---------- resultado ----------
    def mostrar_resultado(self, ciclo):
        self.play(*self.poner_titulo("¡Ciclo euleriano encontrado!", C_CICLO),
                  *self.poner_leyenda("Pila vacía: el ciclo usa las " + str(len(ciclo) - 1) +
                                      " aristas una sola vez", C_CICLO))
        self.wait(1)
        # Recorrido final numerando cada arista en orden
        usadas = set()
        punto = Dot(self.pos[ciclo[0]], color=YELLOW, radius=0.13)
        self.add(punto)
        numeros = VGroup()
        for i in range(len(ciclo) - 1):
            u, w = ciclo[i], ciclo[i + 1]
            e = next(x for x, (a, b) in self.aristas.items() if x not in usadas and {a, b} == {u, w})
            usadas.add(e)
            camino = self.dibujo_arista(e)
            if self.aristas[e][0] != u and u != w:
                camino = camino.reverse_points()
            num = t(str(i + 1), 20, YELLOW).move_to(camino.point_from_proportion(0.5) + UP * 0.25)
            num.add_background_rectangle(color=FONDO, opacity=0.85, buff=0.04)
            numeros.add(num)
            self.play(MoveAlongPath(punto, camino), self.ciclo_cajas[i][0].animate.set_fill(YELLOW_E),
                      self.v_aristas[e].animate.set_color(YELLOW), FadeIn(num), run_time=0.5)
            self.play(self.v_aristas[e].animate.set_color(C_CICLO), self.ciclo_cajas[i][0].animate.set_fill("#123a24"),
                      run_time=0.15)
        self.play(self.ciclo_cajas[-1][0].animate.set_fill(YELLOW_E), Flash(punto, color=YELLOW))
        self.wait(2.5)


# --------------------------------------------------------------------------
#  5. Casos borde
# --------------------------------------------------------------------------
class CasoBorde(EscenaGrafo):
    def construct(self):
        # (a) Puentes de Konigsberg: grados impares
        aviso = VGroup(t("Casos borde", 48, C_MALO),
                       t("¿Qué pasa si el grafo NO admite ciclo euleriano?", 28)).arrange(DOWN, buff=0.4)
        self.play(FadeIn(aviso))
        self.wait(1.5)
        self.play(FadeOut(aviso))

        self.preparar(TRAZA_KONIGSBERG)
        self.play(*self.poner_titulo("Caso 1: los 7 puentes de Königsberg (multigrafo)"))
        self.mostrar_grafo()
        veredicto, _ = self.animar_verificacion(pausa=1.0)
        self.play(*self.poner_leyenda(f"Veredicto: {veredicto} → Hierholzer ni se ejecuta (Euler, 1736)", C_MALO))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.titulo = self.leyenda = None
        self._dfs_iniciado = False

        # (b) grados pares pero desconectado
        self.preparar(TRAZA_DESCONECTADO)
        self.play(*self.poner_titulo("Caso 2: todos los grados pares, pero desconectado"))
        self.mostrar_grafo()
        veredicto, _ = self.animar_verificacion(pausa=1.0)
        self.play(*self.poner_leyenda(f"Veredicto: {veredicto} → no hay un solo ciclo que cubra ambas partes", C_MALO))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])
        self.titulo = self.leyenda = None
        self._dfs_iniciado = False

        # (c) un solo vertice, sin aristas
        self.preparar(TRAZA_UN_VERTICE)
        self.play(*self.poner_titulo("Caso 3: un solo vértice y ninguna arista"))
        self.mostrar_grafo()
        ciclo = next(a[1:] for c, a in self.eventos if c == "CICLO")
        veredicto = next(a for c, a in self.eventos if c == "VEREDICTO")
        res = t(f"Veredicto: {veredicto} → ciclo trivial [{', '.join(map(str, ciclo))}] (0 aristas)", 26, C_BIEN)
        res.next_to(self.v_nodos[0], DOWN, buff=0.8)
        self.play(Write(res), Indicate(self.v_nodos[0], color=C_BIEN))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])


# --------------------------------------------------------------------------
#  6. Complejidad
# --------------------------------------------------------------------------
class Complejidad(Scene):
    def construct(self):
        cab = t("Complejidad  (V = vértices, E = aristas)", 36, YELLOW).to_edge(UP, buff=0.4)
        filas = [
            ["Paso", "Tiempo", "Por qué"],
            ["Calcular grados", "O(V)", "tamaño de cada lista de adyacencia"],
            ["Verificar conexidad", "O(V + E)", "un DFS iterativo con pila propia"],
            ["Hierholzer", "O(V + E)", "cada arista se marca usada 1 vez"],
            ["", "", "el puntero de cada lista solo avanza"],
            ["", "", "E+1 push y E+1 pop en la pila"],
            ["Memoria", "O(V + E)", "listas de adyacencia + pila + ciclo"],
            ["Fleury (comparación)", "O(E²)", "revisa si cada arista es puente"],
        ]
        anchos = [3.6, 2.2, 6.6]
        tabla = VGroup()
        for i, fila in enumerate(filas):
            col = [YELLOW if i == 0 else WHITE, YELLOW if i == 0 else C_BIEN, YELLOW if i == 0 else GREY_A]
            if i == len(filas) - 1:
                col = [GREY_B, C_MALO, GREY_B]
            celdas = VGroup(*[t(txt, 24 if j < 2 else 22, col[j]) for j, txt in enumerate(fila)])
            x = -6.3
            for j, c in enumerate(celdas):
                c.move_to([x + anchos[j] / 2, 2.2 - i * 0.62, 0])
                x += anchos[j]
            tabla.add(celdas)
        linea = Line([-6.3, 1.9, 0], [6.1, 1.9, 0], color=GREY_C)
        self.play(Write(cab))
        self.play(FadeIn(tabla[0]), Create(linea))
        for f in tabla[1:]:
            self.play(FadeIn(f, shift=UP * 0.15), run_time=0.5)
            self.wait(0.5)
        nota = t("Total: O(V + E) → lineal en el tamaño del grafo", 30, C_BIEN).to_edge(DOWN, buff=0.6)
        caja = SurroundingRectangle(nota, color=C_BIEN, buff=0.15)
        self.play(Write(nota), Create(caja))
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])


# --------------------------------------------------------------------------
#  7. Creditos
# --------------------------------------------------------------------------
class Creditos(Scene):
    def construct(self):
        cab = t("Ciclo Euleriano · Hierholzer", 44, YELLOW)
        nombres = VGroup(*[t(n, 28) for n in leer_integrantes()]).arrange(DOWN, buff=0.15)
        info = VGroup(
            t("Implementación: C++17 (pila y listas propias)", 22, GREY_A),
            t("Animación: Manim Community, impulsada por la traza del programa C++", 22, GREY_A),
            t("CS2023 · Algoritmos y Estructuras de Datos · UTEC 2026-2", 22, GREY_B),
        ).arrange(DOWN, buff=0.15)
        bloque = VGroup(cab, nombres, info).arrange(DOWN, buff=0.6)
        self.play(FadeIn(cab, shift=UP * 0.3))
        self.play(LaggedStart(*[FadeIn(n) for n in nombres], lag_ratio=0.3))
        self.play(FadeIn(info))
        self.wait(3)
        self.play(FadeOut(bloque))
