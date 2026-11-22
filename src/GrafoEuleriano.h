// Grafo no dirigido (multigrafo, admite aristas paralelas y lazos)
// con el algoritmo de Hierholzer para hallar un ciclo euleriano en O(|V| + |E|).
#ifndef GRAFO_EULERIANO_H
#define GRAFO_EULERIANO_H

#include <cstdio>
#include "estructuras/Lista.h"
#include "estructuras/Pila.h"

// Una entrada de la lista de adyacencia: "por la arista id llego a vecino".
struct Incidencia {
    int arista;
    int vecino;
};

enum class Veredicto { EULERIANO, GRADOS_IMPARES, DESCONECTADO, SIN_ARISTAS };

class GrafoEuleriano {
    int n;                       // cantidad de vertices
    int m;                       // cantidad de aristas
    int capacidadAristas;
    int* extremoU;               // extremos de cada arista
    int* extremoV;
    Lista<Incidencia>* ady;      // listas de adyacencia
    double* posX;                // coordenadas (solo para dibujar)
    double* posY;
    FILE* traza;                 // si no es nullptr, se escriben los eventos

public:
    explicit GrafoEuleriano(int vertices);
    ~GrafoEuleriano();
    GrafoEuleriano(const GrafoEuleriano&) = delete;
    GrafoEuleriano& operator=(const GrafoEuleriano&) = delete;

    static GrafoEuleriano* leerArchivo(const char* ruta);   // nullptr si falla

    int agregarArista(int u, int v);                         // O(1) amortizado
    void fijarPosicion(int v, double x, double y);
    void activarTraza(FILE* f) { traza = f; }

    int vertices() const { return n; }
    int aristas() const { return m; }
    int grado(int v) const;                                  // O(1)

    // Verifica las condiciones del teorema de Euler: O(|V| + |E|)
    Veredicto verificar();

    // Hierholzer iterativo. Devuelve true y llena `ciclo` (|E|+1 vertices)
    // si el grafo es euleriano. O(|V| + |E|).
    bool cicloEuleriano(Lista<int>& ciclo, int inicio = -1);

    void escribirEncabezado();   // GRAFO / NODO / ARISTA en la traza
};

const char* nombreVeredicto(Veredicto v);

#endif
