// Pruebas automaticas del ciclo euleriano (Hierholzer).
// 1) Grafos eulerianos aleatorios (union de ciclos aleatorios que comparten vertices):
//    el ciclo devuelto debe ser cerrado, tener |E|+1 vertices y usar cada arista una vez.
// 2) Grafos aleatorios cualesquiera: el veredicto debe coincidir con un chequeo independiente.
// 3) Casos borde: un vertice, lazos, aristas paralelas, grafo grande (camino lineal).
#include <cstdio>
#include <cstdlib>
#include <map>
#include <utility>
#include <vector>

#include "GrafoEuleriano.h"

static int fallos = 0, verificaciones = 0;

#define CHECK(cond, msg)                                     \
    do {                                                     \
        ++verificaciones;                                    \
        if (!(cond)) {                                       \
            ++fallos;                                        \
            std::printf("FALLO: %s (linea %d)\n", msg, __LINE__); \
        }                                                    \
    } while (0)

using Arista = std::pair<int, int>;

// Valida que `ciclo` sea un ciclo euleriano de las aristas dadas (multiconjunto).
static bool esCicloEuleriano(const std::vector<int>& ciclo, const std::vector<Arista>& aristas) {
    if (ciclo.size() != aristas.size() + 1) return false;
    if (ciclo.front() != ciclo.back()) return false;
    std::map<Arista, int> restantes;
    for (auto [u, v] : aristas) restantes[{std::min(u, v), std::max(u, v)}]++;
    for (size_t i = 0; i + 1 < ciclo.size(); ++i) {
        int a = ciclo[i], b = ciclo[i + 1];
        auto it = restantes.find({std::min(a, b), std::max(a, b)});
        if (it == restantes.end() || it->second == 0) return false;
        it->second--;
    }
    return true;
}

static std::vector<int> aVector(Lista<int>& l) {
    std::vector<int> r;
    for (auto* p = l.primero(); p != nullptr; p = p->siguiente) r.push_back(p->dato);
    return r;
}

// Chequeo independiente (union-find) del teorema de Euler.
static bool eulerianoFuerzaBruta(int n, const std::vector<Arista>& aristas) {
    std::vector<int> grado(n, 0), padre(n);
    for (int i = 0; i < n; ++i) padre[i] = i;
    auto raiz = [&](int x) { while (padre[x] != x) x = padre[x] = padre[padre[x]]; return x; };
    for (auto [u, v] : aristas) { grado[u]++; grado[v]++; padre[raiz(u)] = raiz(v); }
    int comp = -1;
    for (int v = 0; v < n; ++v) {
        if (grado[v] % 2) return false;
        if (grado[v] > 0) {
            if (comp == -1) comp = raiz(v);
            else if (raiz(v) != comp) return false;
        }
    }
    return true;
}

int main() {
    std::srand(2023);

    // 1) grafos eulerianos aleatorios
    for (int t = 0; t < 3000; ++t) {
        int n = 2 + std::rand() % 12;
        std::vector<Arista> aristas;
        int ciclos = 1 + std::rand() % 5;
        int ancla = std::rand() % n;                 // todos los ciclos pasan por el ancla -> conexo
        for (int c = 0; c < ciclos; ++c) {
            int largo = 2 + std::rand() % 6;
            int prev = ancla;
            for (int k = 1; k < largo; ++k) {
                int nxt = std::rand() % n;
                aristas.push_back({prev, nxt});
                prev = nxt;
            }
            aristas.push_back({prev, ancla});
        }
        GrafoEuleriano g(n);
        for (auto [u, v] : aristas) g.agregarArista(u, v);
        Lista<int> ciclo;
        bool ok = g.cicloEuleriano(ciclo, ancla);
        CHECK(ok, "debia ser euleriano");
        auto c = aVector(ciclo);
        CHECK(esCicloEuleriano(c, aristas), "ciclo invalido");
        CHECK(!c.empty() && c.front() == ancla, "no empieza en el vertice pedido");
    }

    // 2) grafos aleatorios: veredicto
    for (int t = 0; t < 3000; ++t) {
        int n = 1 + std::rand() % 9;
        int m = std::rand() % 14;
        std::vector<Arista> aristas;
        for (int i = 0; i < m; ++i) aristas.push_back({std::rand() % n, std::rand() % n});
        GrafoEuleriano g(n);
        for (auto [u, v] : aristas) g.agregarArista(u, v);
        Lista<int> ciclo;
        bool ok = g.cicloEuleriano(ciclo);
        CHECK(ok == eulerianoFuerzaBruta(n, aristas), "veredicto distinto a fuerza bruta");
        if (ok && m > 0) CHECK(esCicloEuleriano(aVector(ciclo), aristas), "ciclo invalido (aleatorio)");
    }

    // 3) casos borde
    {
        GrafoEuleriano g(1);                         // un vertice, sin aristas
        Lista<int> c;
        CHECK(g.cicloEuleriano(c) && c.tamano() == 1, "un vertice: ciclo trivial");
    }
    {
        GrafoEuleriano g(1);                         // un lazo
        g.agregarArista(0, 0);
        Lista<int> c;
        CHECK(g.cicloEuleriano(c) && c.tamano() == 2, "lazo");
    }
    {
        GrafoEuleriano g(2);                         // dos aristas paralelas
        g.agregarArista(0, 1);
        g.agregarArista(1, 0);
        Lista<int> c;
        CHECK(g.cicloEuleriano(c) && c.tamano() == 3, "paralelas");
    }
    {
        GrafoEuleriano g(2);                         // una sola arista: grados impares
        g.agregarArista(0, 1);
        Lista<int> c;
        CHECK(!g.cicloEuleriano(c), "una arista no es euleriana");
        CHECK(g.verificar() == Veredicto::GRADOS_IMPARES, "veredicto grados impares");
    }
    {
        const int N = 200000;                        // ciclo grande: no debe desbordar la pila
        GrafoEuleriano g(N);
        std::vector<Arista> aristas;
        for (int i = 0; i < N; ++i) { g.agregarArista(i, (i + 1) % N); aristas.push_back({i, (i + 1) % N}); }
        Lista<int> c;
        CHECK(g.cicloEuleriano(c) && esCicloEuleriano(aVector(c), aristas), "ciclo grande");
    }

    std::printf("%d verificaciones, %d fallos\n", verificaciones, fallos);
    return fallos == 0 ? 0 : 1;
}
