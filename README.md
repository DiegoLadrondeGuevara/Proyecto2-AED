# Ciclo Euleriano (Algoritmo de Hierholzer) : Proyecto 2, CS2023 AED

Implementación **en C++** del algoritmo de Hierholzer para encontrar un ciclo euleriano en
O(|V| + |E|), y una animación en **Manim** que reproduce los pasos **reales** que ejecuta el
programa (la animación lee una traza de eventos generada por el C++; no calcula nada por su cuenta).

> **Curso:** CS2023 – Algoritmos y Estructuras de Datos · UTEC · 2026-2
>
> **Integrante:** Diego Abraham Ladrón de Guevara

**Video narrado:** https://drive.google.com/file/d/103c2ffegqvUGhTvNSGfAEIh1FJ5nVPyn/view?usp=sharing

**Escenas animadas (1080p):** carpeta [`video/`](video/), una por escena (`Portada`, `Introduccion`, `Verificacion`, `Hierholzer`, `CasoBorde`, `Complejidad`, `Creditos`).

**Informe:** [`docs/Informe_Ciclo_Euleriano.pdf`](docs/Informe_Ciclo_Euleriano.pdf)

## ¿Qué hay en el repo?

```
src/
  estructuras/
    Pila.h              pila enlazada propia (Hierholzer + DFS de conexidad)
    Lista.h             lista enlazada propia (listas de adyacencia y el ciclo)
  GrafoEuleriano.h/.cpp multigrafo no dirigido, verificación del teorema de Euler,
                        Hierholzer iterativo y escritura de la traza
  main.cpp              programa de línea de comandos
tests/pruebas.cpp       12 591 verificaciones contra un chequeo independiente
grafos/                 instancias: principal, konigsberg, desconectado, un_vertice
trazas/                 trazas generadas por el C++ (las lee la animación)
animacion/escena.py     escenas de Manim
integrantes.txt         nombres que aparecen en la portada y créditos del video
ejecutar.ps1            compila, prueba, genera trazas y renderiza las escenas
video/                  escenas renderizadas (.mp4)
docs/                   informe (PDF/DOCX) e imágenes
tools/generar_informe.py genera el informe
```

## 1. Compilar y ejecutar el C++

Necesitas `g++` con C++17 (en Windows: MSYS2 UCRT64).

```bash
g++ -std=c++17 -Wall -O2 -o euler src/main.cpp src/GrafoEuleriano.cpp
./euler grafos/principal.txt -t trazas/principal.txt
```

Salida:

```
Grafo: 7 vertices, 9 aristas
Grados: 0:2 1:2 2:4 3:2 4:4 5:2 6:2
Ciclo euleriano (10 vertices, 9 aristas):
  0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 4 -> 2 -> 0
```

Opciones: `-t archivo` escribe la traza, `-s v` elige el vértice inicial.

Formato del grafo: primera línea `n m`, luego `m` líneas `u v` (vértices 0..n-1) y,
opcionalmente, `n` líneas `x y` con la posición de cada vértice (solo para dibujar).

### Formato de la traza

| Evento | Significado |
|---|---|
| `GRAFO n m`, `NODO v x y`, `ARISTA e u v` | el grafo leído |
| `GRADO v d`, `IMPARES k ...` | condición 1 del teorema (grados pares) |
| `CONEXO_VISITA v`, `CONEXO 0/1` | condición 2 (DFS de conexidad) |
| `VEREDICTO X` | `EULERIANO`, `GRADOS_IMPARES`, `DESCONECTADO` o `SIN_ARISTAS` |
| `PUSH v` | vértice inicial apilado |
| `AVANZA e u w` | se usa la arista `e` de `u` a `w` y se apila `w` |
| `RETROCEDE v` | `v` no tiene aristas libres: sale de la pila y va al inicio del ciclo |
| `CICLO k v0 ... vk-1` | resultado final |

## 2. Pruebas

```bash
g++ -std=c++17 -O2 -Isrc -o pruebas tests/pruebas.cpp src/GrafoEuleriano.cpp
./pruebas        # -> 12591 verificaciones, 0 fallos
```

Genera 3000 grafos eulerianos aleatorios (multigrafos con lazos y aristas paralelas) y comprueba que el
ciclo sea cerrado, tenga |E|+1 vértices y use cada arista una sola vez; 3000 grafos cualesquiera
donde el veredicto se compara con un chequeo independiente (union-find); y casos borde
(un vértice, un lazo, aristas paralelas, una sola arista, un ciclo de 200 000 vértices).

## 3. Generar el video

Requisitos: Python 3.10+, [Manim Community](https://docs.manim.community) 0.18+ y `ffmpeg`.

```bash
pip install manim
manim -qh animacion/escena.py Portada Introduccion Verificacion Hierholzer CasoBorde Complejidad Creditos
```

O todo de una vez en Windows (compila, prueba, genera trazas y deja cada escena a 1080p en `video/`):

```powershell
.\ejecutar.ps1            # calidad final (1080p60)
.\ejecutar.ps1 -Calidad l # rápido para probar (480p)
```

| Escena | Contenido |
|---|---|
| `Portada` | título, curso e integrantes |
| `Introduccion` | qué es un ciclo euleriano, usos, teorema de Euler e idea de Hierholzer |
| `Verificacion` | grados y DFS de conexidad sobre el grafo principal |
| `Hierholzer` | ejecución paso a paso: pila, aristas usadas, sub-ciclos y recorrido final |
| `CasoBorde` | Königsberg (grados impares), grafo desconectado, un solo vértice |
| `Complejidad` | análisis O(V + E) y comparación con Fleury |
| `Creditos` | integrantes y herramientas |

## Complejidad

| Paso | Tiempo |
|---|---|
| Grados | O(V) |
| Conexidad (DFS iterativo) | O(V + E) |
| Hierholzer | O(V + E) — cada arista se marca una vez y el puntero de cada lista solo avanza |
| Memoria | O(V + E) |

## Referencias

- Hierholzer, C. & Wiener, C. (1873). Über die Möglichkeit, einen Linienzug ohne Wiederholung und ohne Unterbrechung zu umfahren. *Mathematische Annalen*, 6(1), 30–32.
- Cormen, T. et al. (2022). *Introduction to Algorithms* (4th ed.), problema 20-3 (Euler tour). MIT Press.
- cp-algorithms: *Finding the Eulerian path in O(M)* — https://cp-algorithms.com/graph/euler_path.html
- Manim Community — https://www.manim.community · Estilo inspirado en 3Blue1Brown.
