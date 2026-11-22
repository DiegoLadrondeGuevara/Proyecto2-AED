#include "GrafoEuleriano.h"

#include <cstdlib>

GrafoEuleriano::GrafoEuleriano(int vertices)
    : n(vertices), m(0), capacidadAristas(4), traza(nullptr) {
    extremoU = new int[capacidadAristas];
    extremoV = new int[capacidadAristas];
    ady = new Lista<Incidencia>[n > 0 ? n : 1];
    posX = new double[n > 0 ? n : 1];
    posY = new double[n > 0 ? n : 1];
    for (int i = 0; i < n; ++i) posX[i] = posY[i] = 0.0;
}

GrafoEuleriano::~GrafoEuleriano() {
    delete[] extremoU;
    delete[] extremoV;
    delete[] ady;
    delete[] posX;
    delete[] posY;
}

// Formato del archivo:
//   n m
//   u v          (m lineas, vertices 0..n-1)
//   x y          (opcional: n lineas con la posicion de cada vertice)
GrafoEuleriano* GrafoEuleriano::leerArchivo(const char* ruta) {
    FILE* f = std::fopen(ruta, "r");
    if (!f) return nullptr;
    int n, m;
    if (std::fscanf(f, "%d %d", &n, &m) != 2 || n < 0 || m < 0) {
        std::fclose(f);
        return nullptr;
    }
    GrafoEuleriano* g = new GrafoEuleriano(n);
    for (int i = 0; i < m; ++i) {
        int u, v;
        if (std::fscanf(f, "%d %d", &u, &v) != 2 || u < 0 || v < 0 || u >= n || v >= n) {
            std::fclose(f);
            delete g;
            return nullptr;
        }
        g->agregarArista(u, v);
    }
    for (int i = 0; i < n; ++i) {
        double x, y;
        if (std::fscanf(f, "%lf %lf", &x, &y) != 2) break;
        g->fijarPosicion(i, x, y);
    }
    std::fclose(f);
    return g;
}

int GrafoEuleriano::agregarArista(int u, int v) {
    if (m == capacidadAristas) {                 // crecimiento geometrico
        capacidadAristas *= 2;
        int* nu = new int[capacidadAristas];
        int* nv = new int[capacidadAristas];
        for (int i = 0; i < m; ++i) { nu[i] = extremoU[i]; nv[i] = extremoV[i]; }
        delete[] extremoU;
        delete[] extremoV;
        extremoU = nu;
        extremoV = nv;
    }
    int id = m++;
    extremoU[id] = u;
    extremoV[id] = v;
    ady[u].agregarFinal({id, v});
    ady[v].agregarFinal({id, u});                // un lazo aparece dos veces en ady[u]
    return id;
}

void GrafoEuleriano::fijarPosicion(int v, double x, double y) {
    posX[v] = x;
    posY[v] = y;
}

int GrafoEuleriano::grado(int v) const { return ady[v].tamano(); }

void GrafoEuleriano::escribirEncabezado() {
    if (!traza) return;
    std::fprintf(traza, "GRAFO %d %d\n", n, m);
    for (int v = 0; v < n; ++v) std::fprintf(traza, "NODO %d %.3f %.3f\n", v, posX[v], posY[v]);
    for (int e = 0; e < m; ++e) std::fprintf(traza, "ARISTA %d %d %d\n", e, extremoU[e], extremoV[e]);
}

const char* nombreVeredicto(Veredicto v) {
    switch (v) {
        case Veredicto::EULERIANO: return "EULERIANO";
        case Veredicto::GRADOS_IMPARES: return "GRADOS_IMPARES";
        case Veredicto::DESCONECTADO: return "DESCONECTADO";
        case Veredicto::SIN_ARISTAS: return "SIN_ARISTAS";
    }
    return "?";
}

// Teorema de Euler (grafo no dirigido): existe un ciclo euleriano si y solo si
//  (1) todo vertice tiene grado par, y
//  (2) todos los vertices con grado > 0 estan en una misma componente conexa.
Veredicto GrafoEuleriano::verificar() {
    // (1) grados: O(|V|)
    int impares = 0;
    for (int v = 0; v < n; ++v) {
        if (traza) std::fprintf(traza, "GRADO %d %d\n", v, grado(v));
        if (grado(v) % 2 != 0) ++impares;
    }
    if (traza) {
        std::fprintf(traza, "IMPARES %d", impares);
        for (int v = 0; v < n; ++v)
            if (grado(v) % 2 != 0) std::fprintf(traza, " %d", v);
        std::fprintf(traza, "\n");
    }

    if (m == 0) {
        if (traza) std::fprintf(traza, "VEREDICTO %s\n", nombreVeredicto(Veredicto::SIN_ARISTAS));
        return Veredicto::SIN_ARISTAS;
    }

    // (2) conexidad con un DFS iterativo (pila propia): O(|V| + |E|)
    int inicio = 0;
    while (grado(inicio) == 0) ++inicio;
    bool* visto = new bool[n];
    for (int v = 0; v < n; ++v) visto[v] = false;
    Pila<int> pila;
    pila.push(inicio);
    visto[inicio] = true;
    if (traza) std::fprintf(traza, "CONEXO_VISITA %d\n", inicio);
    while (!pila.vacia()) {
        int u = pila.pop();
        for (auto* p = ady[u].primero(); p != nullptr; p = p->siguiente) {
            int w = p->dato.vecino;
            if (!visto[w]) {
                visto[w] = true;
                if (traza) std::fprintf(traza, "CONEXO_VISITA %d\n", w);
                pila.push(w);
            }
        }
    }
    bool conexo = true;
    for (int v = 0; v < n; ++v)
        if (grado(v) > 0 && !visto[v]) conexo = false;
    delete[] visto;
    if (traza) std::fprintf(traza, "CONEXO %d\n", conexo ? 1 : 0);

    Veredicto r = Veredicto::EULERIANO;
    if (impares > 0) r = Veredicto::GRADOS_IMPARES;
    else if (!conexo) r = Veredicto::DESCONECTADO;
    if (traza) std::fprintf(traza, "VEREDICTO %s\n", nombreVeredicto(r));
    return r;
}

// Algoritmo de Hierholzer, version iterativa:
//   - pila con el camino actual; empezamos en `inicio`.
//   - mientras la pila no este vacia, miramos el tope v:
//       * si v aun tiene una arista sin usar (v,w): la marcamos usada y apilamos w.
//       * si no: v queda "atascado", lo sacamos y lo agregamos al ciclo.
//   Al terminar, el ciclo tiene |E|+1 vertices.
// Cada arista se marca una sola vez y el puntero `siguiente[v]` de cada lista
// de adyacencia solo avanza, asi que el trabajo total es O(|V| + |E|).
bool GrafoEuleriano::cicloEuleriano(Lista<int>& ciclo, int inicio) {
    ciclo.limpiar();
    Veredicto ver = verificar();
    if (ver == Veredicto::SIN_ARISTAS) {          // caso borde: ciclo trivial
        if (n == 0) return false;
        int s = (inicio >= 0 && inicio < n) ? inicio : 0;
        ciclo.agregarFinal(s);
        if (traza) std::fprintf(traza, "CICLO 1 %d\nFIN\n", s);
        return true;
    }
    if (ver != Veredicto::EULERIANO) {
        if (traza) std::fprintf(traza, "FIN\n");
        return false;
    }

    if (inicio < 0 || inicio >= n || grado(inicio) == 0) {
        inicio = 0;
        while (grado(inicio) == 0) ++inicio;
    }

    bool* usada = new bool[m];
    for (int e = 0; e < m; ++e) usada[e] = false;
    // puntero a la siguiente incidencia por revisar de cada vertice
    Lista<Incidencia>::Nodo** siguiente = new Lista<Incidencia>::Nodo*[n];
    for (int v = 0; v < n; ++v) siguiente[v] = ady[v].primero();

    Pila<int> pila;
    pila.push(inicio);
    if (traza) std::fprintf(traza, "HIERHOLZER %d\nPUSH %d\n", inicio, inicio);

    while (!pila.vacia()) {
        int v = pila.tope();
        while (siguiente[v] != nullptr && usada[siguiente[v]->dato.arista])
            siguiente[v] = siguiente[v]->siguiente;      // saltar aristas ya usadas
        if (siguiente[v] != nullptr) {
            Incidencia inc = siguiente[v]->dato;
            siguiente[v] = siguiente[v]->siguiente;
            usada[inc.arista] = true;
            pila.push(inc.vecino);
            if (traza) std::fprintf(traza, "AVANZA %d %d %d\n", inc.arista, v, inc.vecino);
        } else {
            pila.pop();
            ciclo.agregarInicio(v);
            if (traza) std::fprintf(traza, "RETROCEDE %d\n", v);
        }
    }
    delete[] usada;
    delete[] siguiente;

    if (traza) {
        std::fprintf(traza, "CICLO %d", ciclo.tamano());
        for (auto* p = ciclo.primero(); p != nullptr; p = p->siguiente) std::fprintf(traza, " %d", p->dato);
        std::fprintf(traza, "\nFIN\n");
    }
    return true;
}
