// Uso:
//   ./euler <grafo.txt> [-s inicio] [-t traza.txt]
// Lee el grafo, verifica si es euleriano y, si lo es, imprime un ciclo euleriano.
// Con -t escribe la traza de eventos que lee la animacion de Manim.
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "GrafoEuleriano.h"

int main(int argc, char** argv) {
    if (argc < 2) {
        std::printf("Uso: %s <grafo.txt> [-s inicio] [-t traza.txt]\n", argv[0]);
        return 1;
    }
    const char* rutaTraza = nullptr;
    int inicio = -1;
    for (int i = 2; i < argc; ++i) {
        if (std::strcmp(argv[i], "-t") == 0 && i + 1 < argc) rutaTraza = argv[++i];
        else if (std::strcmp(argv[i], "-s") == 0 && i + 1 < argc) inicio = std::atoi(argv[++i]);
    }

    GrafoEuleriano* g = GrafoEuleriano::leerArchivo(argv[1]);
    if (!g) {
        std::printf("No se pudo leer el grafo '%s'\n", argv[1]);
        return 1;
    }
    FILE* traza = nullptr;
    if (rutaTraza) {
        traza = std::fopen(rutaTraza, "w");
        if (!traza) {
            std::printf("No se pudo crear la traza '%s'\n", rutaTraza);
            delete g;
            return 1;
        }
        g->activarTraza(traza);
        g->escribirEncabezado();
    }

    std::printf("Grafo: %d vertices, %d aristas\n", g->vertices(), g->aristas());
    std::printf("Grados:");
    for (int v = 0; v < g->vertices(); ++v) std::printf(" %d:%d", v, g->grado(v));
    std::printf("\n");

    Lista<int> ciclo;
    bool ok = g->cicloEuleriano(ciclo, inicio);
    if (ok) {
        std::printf("Ciclo euleriano (%d vertices, %d aristas):\n  ", ciclo.tamano(), g->aristas());
        bool primero = true;
        for (auto* p = ciclo.primero(); p != nullptr; p = p->siguiente) {
            std::printf(primero ? "%d" : " -> %d", p->dato);
            primero = false;
        }
        std::printf("\n");
    } else {
        g->activarTraza(nullptr);          // no ensuciar la traza al re-verificar
        Veredicto v = g->verificar();
        if (v == Veredicto::GRADOS_IMPARES)
            std::printf("NO tiene ciclo euleriano: hay vertices de grado impar.\n");
        else if (v == Veredicto::DESCONECTADO)
            std::printf("NO tiene ciclo euleriano: las aristas no estan en una sola componente.\n");
        else
            std::printf("Grafo vacio.\n");
    }

    if (traza) std::fclose(traza);
    delete g;
    return 0;
}
