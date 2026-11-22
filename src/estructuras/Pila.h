// Pila enlazada (LIFO) implementada por el grupo.
// Se usa en Hierholzer (pila de vertices del recorrido) y en el DFS
// iterativo que verifica la conexidad. No se usa std::stack.
#ifndef PILA_H
#define PILA_H

#include <stdexcept>

template <typename T>
class Pila {
    struct Nodo {
        T dato;
        Nodo* abajo;
        Nodo(const T& d, Nodo* a) : dato(d), abajo(a) {}
    };
    Nodo* cima;
    int n;

public:
    Pila() : cima(nullptr), n(0) {}
    ~Pila() { while (!vacia()) pop(); }
    Pila(const Pila&) = delete;
    Pila& operator=(const Pila&) = delete;

    void push(const T& x) {          // O(1)
        cima = new Nodo(x, cima);
        ++n;
    }
    T pop() {                        // O(1)
        if (vacia()) throw std::runtime_error("pop en pila vacia");
        Nodo* q = cima;
        T x = q->dato;
        cima = q->abajo;
        delete q;
        --n;
        return x;
    }
    T& tope() {                      // O(1)
        if (vacia()) throw std::runtime_error("tope en pila vacia");
        return cima->dato;
    }
    bool vacia() const { return cima == nullptr; }
    int tamano() const { return n; }
};

#endif
