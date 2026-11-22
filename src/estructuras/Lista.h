// Lista simplemente enlazada con insercion al final en O(1).
// Se usa para las listas de adyacencia y para guardar el ciclo resultante.
#ifndef LISTA_H
#define LISTA_H

template <typename T>
class Lista {
public:
    struct Nodo {
        T dato;
        Nodo* siguiente;
        explicit Nodo(const T& d) : dato(d), siguiente(nullptr) {}
    };

private:
    Nodo* cabeza;
    Nodo* cola;
    int n;

public:
    Lista() : cabeza(nullptr), cola(nullptr), n(0) {}
    ~Lista() { limpiar(); }
    Lista(const Lista&) = delete;
    Lista& operator=(const Lista&) = delete;

    void agregarFinal(const T& x) {   // O(1)
        Nodo* q = new Nodo(x);
        if (cola) cola->siguiente = q; else cabeza = q;
        cola = q;
        ++n;
    }
    void agregarInicio(const T& x) {  // O(1)
        Nodo* q = new Nodo(x);
        q->siguiente = cabeza;
        cabeza = q;
        if (!cola) cola = q;
        ++n;
    }
    void limpiar() {
        while (cabeza) {
            Nodo* q = cabeza;
            cabeza = cabeza->siguiente;
            delete q;
        }
        cola = nullptr;
        n = 0;
    }
    Nodo* primero() const { return cabeza; }
    int tamano() const { return n; }
    bool vacia() const { return n == 0; }
};

#endif
