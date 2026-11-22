// Genera presentacion/Ciclo_Euleriano.pptx con los videos de cada escena incrustados.
//   cd presentacion && npm install && node generar_ppt.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const RAIZ = path.resolve(__dirname, "..");
const IMG = (n) => path.join(RAIZ, "docs", "img", n);
const VID = (n) => path.join(RAIZ, "video", n);
const INTEGRANTES = fs.readFileSync(path.join(RAIZ, "integrantes.txt"), "utf8")
  .split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
const REPO = "github.com/DiegoLadrondeGuevara/Proyecto2-AED";

// Paleta tomada del video para que PPT y animacion se vean como una sola pieza
const K = {
  fondo: "0F1724", panel: "18243A", panel2: "1F3050", texto: "FFFFFF", suave: "B8C4D6",
  oro: "F7D96F", verde: "83C167", naranja: "FF862F", azul: "9CC3FF", rojo: "FC6255",
};
const FH = "Calibri", FB = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Ciclo Euleriano - Hierholzer";
pres.theme = { headFontFace: FH, bodyFontFace: FB };

pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: K.fondo },
  objects: [
    { text: { text: "CS2023 · Ciclo Euleriano", options: { x: 0.6, y: 7.0, w: 5, h: 0.3, fontSize: 10, color: K.suave, fontFace: FB } } },
  ],
  slideNumber: { x: 12.3, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: K.suave, fontFace: FB },
});

function titulo(s, txt, sub) {
  s.addText(txt, { x: 0.6, y: 0.4, w: 12.1, h: 0.8, fontSize: 36, bold: true, color: K.texto, fontFace: FH, margin: 0, isTextBox: true });
  if (sub) s.addText(sub, { x: 0.6, y: 1.15, w: 12.1, h: 0.45, fontSize: 16, color: K.suave, fontFace: FB, margin: 0, italic: true, isTextBox: true });
}

function etiquetaVideo(s, x, y, w, txt) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.38, rectRadius: 0.08, fill: { color: K.naranja } });
  s.addText("▶  " + txt, { x, y, w, h: 0.38, fontSize: 12, bold: true, color: K.fondo, align: "center", valign: "middle", margin: 0, isTextBox: true });
}

// video incrustado (o la imagen si el video no existe)
function video(s, archivo, portada, x, y, w) {
  const h = w * 9 / 16;
  s.addShape(pres.shapes.RECTANGLE, { x: x - 0.04, y: y - 0.04, w: w + 0.08, h: h + 0.08, fill: { color: K.panel2 }, line: { color: K.azul, width: 1 } });
  if (fs.existsSync(VID(archivo))) {
    s.addMedia({ type: "video", path: VID(archivo), cover: fs.existsSync(IMG(portada)) ? "data:image/png;base64," + fs.readFileSync(IMG(portada)).toString("base64") : undefined, x, y, w, h });
  } else if (fs.existsSync(IMG(portada))) {
    s.addImage({ path: IMG(portada), x, y, w, h });
  }
  return h;
}

function tarjeta(s, x, y, w, h, cabeza, cuerpo, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: K.panel } });
  s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.3, w: 0.5, h: 0.5, fill: { color } });
  s.addText(cabeza, { x: x + 0.95, y: y + 0.25, w: w - 1.15, h: 0.6, fontSize: 18, bold: true, color: K.texto, valign: "middle", margin: 0, isTextBox: true });
  s.addText(cuerpo, { x: x + 0.3, y: y + 0.95, w: w - 0.6, h: h - 1.1, fontSize: 14, color: K.suave, valign: "top", margin: 0, isTextBox: true });
}

// ---------------------------------------------------------------- 1 portada
let s = pres.addSlide({ masterName: "CONTENIDO" });
s.background = { color: K.fondo };
s.addText("Proyecto 2 · CS2023 Algoritmos y Estructuras de Datos · UTEC 2026-2", { x: 0.7, y: 0.7, w: 8, h: 0.4, fontSize: 14, color: K.azul, margin: 0, isTextBox: true });
s.addText("Ciclo Euleriano", { x: 0.7, y: 1.9, w: 6.6, h: 1.2, fontSize: 54, bold: true, color: K.oro, margin: 0, isTextBox: true });
s.addText("Algoritmo de Hierholzer en O(|V| + |E|)", { x: 0.7, y: 3.1, w: 6.6, h: 0.6, fontSize: 22, color: K.texto, margin: 0, isTextBox: true });
s.addText(INTEGRANTES.map((n, i) => ({ text: n, options: { breakLine: i < INTEGRANTES.length - 1 } })),
  { x: 0.7, y: 4.3, w: 6.4, h: 1.2, fontSize: 18, color: K.suave, margin: 0, valign: "top", isTextBox: true });
video(s, "Portada.mp4", "portada.png", 7.6, 2.0, 5.1);
s.addNotes("Abrir con el video de portada (0:00–0:07) o solo presentar el título y al equipo.");

// ---------------------------------------------------------------- 2 problema
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "¿Qué es un ciclo euleriano?", "Recorrido cerrado que usa TODAS las aristas exactamente una vez");
tarjeta(s, 0.6, 1.9, 5.6, 1.45, "Aristas: exactamente una vez", "Cada arista del grafo aparece una sola vez en el recorrido.", K.oro);
tarjeta(s, 0.6, 3.5, 5.6, 1.45, "Empieza y termina igual", "El recorrido es cerrado: vuelve al vértice inicial.", K.verde);
tarjeta(s, 0.6, 5.1, 5.6, 1.45, "Vértices: se pueden repetir", "A diferencia del ciclo hamiltoniano, aquí lo que no se repite son las aristas.", K.azul);
video(s, "Introduccion.mp4", "intro.png", 6.7, 1.9, 6.0);
etiquetaVideo(s, 6.7, 5.45, 6.0, "Video: Introducción (0:07 – 0:34)");
s.addNotes("Reproducir la escena Introduccion: definición, usos, teorema e idea de Hierholzer.");

// ---------------------------------------------------------------- 3 usos
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "¿Para qué sirve?", "Siempre que haya que recorrer todas las conexiones sin repetir");
const usos = [
  ["Rutas de servicio", "Recolección de basura, correo, barrido o inspección de calles (problema del cartero chino).", K.oro],
  ["Genómica", "Ensamblaje de ADN: los fragmentos forman un grafo de De Bruijn y el genoma es un camino euleriano.", K.verde],
  ["Trazado sin levantar el lápiz", "Plotters, cortadoras láser y circuitos: minimizar movimientos en vacío.", K.azul],
  ["Puentes de Königsberg", "El origen (Euler, 1736): ¿se pueden cruzar los 7 puentes una sola vez? No.", K.naranja],
];
usos.forEach(([c, b, col], i) => {
  const x = 0.6 + (i % 2) * 6.15, y = 1.9 + Math.floor(i / 2) * 2.45;
  tarjeta(s, x, y, 5.95, 2.2, c, b, col);
});

// ---------------------------------------------------------------- 4 teorema
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Teorema de Euler: ¿cuándo existe?", "Se decide ANTES de buscar el ciclo, en O(V + E)");
tarjeta(s, 0.6, 1.9, 5.6, 1.9, "1 · Todos los grados son pares", "Cada vez que entras a un vértice necesitas otra arista para salir: se consumen de a pares.", K.verde);
tarjeta(s, 0.6, 4.0, 5.6, 1.9, "2 · Una sola componente", "Todos los vértices con aristas deben ser alcanzables entre sí (lo comprobamos con un DFS).", K.azul);
video(s, "Verificacion.mp4", "verificacion.png", 6.7, 1.9, 6.0);
etiquetaVideo(s, 6.7, 5.45, 6.0, "Video: Verificación (0:34 – 0:53)");
s.addNotes("Reproducir la escena Verificacion: aparecen los grados (g=2, g=4) y luego el DFS pinta de azul los vértices alcanzados.");

// ---------------------------------------------------------------- 5 idea Hierholzer
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Algoritmo de Hierholzer (1873)", "Caminar, atascarse, retroceder y empalmar sub-ciclos");
const pasos = [
  ["1", "Avanzar", "Desde el tope de la pila, tomar una arista libre, marcarla usada y apilar el vecino.", K.oro],
  ["2", "Retroceder", "Si el tope no tiene aristas libres, sacarlo de la pila y ponerlo al INICIO del ciclo.", K.verde],
  ["3", "Empalmar", "Si al retroceder el nuevo tope aún tiene aristas libres, desde ahí nace un sub-ciclo.", K.naranja],
];
pasos.forEach(([n, c, b, col], i) => {
  const y = 1.9 + i * 1.55;
  s.addShape(pres.shapes.OVAL, { x: 0.6, y, w: 0.9, h: 0.9, fill: { color: col } });
  s.addText(n, { x: 0.6, y, w: 0.9, h: 0.9, fontSize: 28, bold: true, color: K.fondo, align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText(c, { x: 1.75, y: y - 0.05, w: 4.6, h: 0.45, fontSize: 20, bold: true, color: K.texto, margin: 0, isTextBox: true });
  s.addText(b, { x: 1.75, y: y + 0.4, w: 4.6, h: 0.9, fontSize: 14, color: K.suave, margin: 0, valign: "top", isTextBox: true });
});
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.8, y: 1.9, w: 5.9, h: 4.6, rectRadius: 0.12, fill: { color: K.panel } });
s.addText([
  { text: "pila.push(inicio)", options: { breakLine: true } },
  { text: "mientras pila no vacía:", options: { breakLine: true } },
  { text: "  v = pila.tope()", options: { breakLine: true } },
  { text: "  saltar aristas usadas de v", options: { breakLine: true, color: K.suave } },
  { text: "  si hay arista libre (v,w):", options: { breakLine: true } },
  { text: "      usada[e] = true", options: { breakLine: true, color: K.oro } },
  { text: "      pila.push(w)        // AVANZA", options: { breakLine: true, color: K.oro } },
  { text: "  si no:", options: { breakLine: true } },
  { text: "      pila.pop()", options: { breakLine: true, color: K.verde } },
  { text: "      ciclo.agregarInicio(v) // RETROCEDE", options: { color: K.verde } },
], { x: 7.1, y: 2.1, w: 5.4, h: 4.2, fontFace: "Courier New", fontSize: 14, color: K.texto, valign: "top", margin: 0, isTextBox: true });

// ---------------------------------------------------------------- 6 ejecucion (video principal)
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Ejecución paso a paso", "La animación reproduce la traza real que escribe el programa C++");
video(s, "Hierholzer.mp4", "hierholzer_medio.png", 0.6, 1.8, 8.4);
const ley = [["Amarillo", "camino actual (aristas en la pila)", K.oro], ["Verde", "aristas ya fijadas en el ciclo", K.verde],
  ["Naranja", "vértice en el tope de la pila", K.naranja], ["Gris", "aristas libres", "9AA4B2"]];
ley.forEach(([c, d, col], i) => {
  const y = 1.9 + i * 0.95;
  s.addShape(pres.shapes.OVAL, { x: 9.4, y: y + 0.08, w: 0.32, h: 0.32, fill: { color: col } });
  s.addText([{ text: c, options: { bold: true, color: K.texto, breakLine: true } }, { text: d, options: { color: K.suave } }],
    { x: 9.9, y, w: 2.9, h: 0.85, fontSize: 14, margin: 0, valign: "top", isTextBox: true });
});
etiquetaVideo(s, 9.4, 5.9, 3.4, "Video: Hierholzer (0:53 – 1:29)");
s.addNotes("Escena principal. Pausar cuando 0 se atasca (primer RETROCEDE) y explicar que 2 aún tiene aristas: nace un sub-ciclo 2→3→4→2. Lo mismo en 4 con 4→5→6→4. Al final el punto recorre el ciclo numerando las 9 aristas.");

// ---------------------------------------------------------------- 7 resultado
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Resultado: un ciclo que usa las 9 aristas", "Salida del programa C++ para grafos/principal.txt");
if (fs.existsSync(IMG("hierholzer_final.png"))) s.addImage({ path: IMG("hierholzer_final.png"), x: 0.6, y: 1.8, w: 7.6, h: 7.6 * 9 / 16 });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.6, y: 1.8, w: 4.1, h: 4.3, rectRadius: 0.12, fill: { color: K.panel } });
s.addText([
  { text: "0 → 1 → 2 → 3 → 4 →", options: { breakLine: true } },
  { text: "5 → 6 → 4 → 2 → 0", options: { breakLine: true } },
], { x: 8.85, y: 2.0, w: 3.7, h: 1.2, fontSize: 20, bold: true, color: K.oro, margin: 0, isTextBox: true });
s.addText([
  { text: "10 vértices = |E| + 1", options: { breakLine: true, bullet: true } },
  { text: "Los vértices 2 y 4 (grado 4) se visitan dos veces", options: { breakLine: true, bullet: true } },
  { text: "Los sub-ciclos 2→3→4→2 y 4→5→6→4 quedaron empalmados solos", options: { bullet: true } },
], { x: 8.85, y: 3.3, w: 3.7, h: 2.7, fontSize: 14, color: K.suave, margin: 0, valign: "top", paraSpaceAfter: 6, isTextBox: true });

// ---------------------------------------------------------------- 8 implementacion
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Implementación: la animación es real", "C++ ejecuta el algoritmo; Manim solo reproduce sus eventos");
const flujo = [
  ["grafos/*.txt", "n m, aristas u v y posiciones", K.azul],
  ["euler.exe (C++)", "Pila y Lista propias, Hierholzer, verificación", K.oro],
  ["trazas/*.txt", "GRADO, AVANZA e u w, RETROCEDE v, CICLO…", K.naranja],
  ["escena.py (Manim)", "lee la traza y anima cada evento → MP4", K.verde],
];
flujo.forEach(([c, d, col], i) => {
  const x = 0.6 + i * 3.15;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.1, w: 2.75, h: 2.0, rectRadius: 0.12, fill: { color: K.panel }, line: { color: col, width: 2 } });
  s.addText(c, { x: x + 0.15, y: 2.25, w: 2.45, h: 0.5, fontSize: 17, bold: true, color: col, align: "center", margin: 0, isTextBox: true });
  s.addText(d, { x: x + 0.15, y: 2.8, w: 2.45, h: 1.2, fontSize: 13, color: K.suave, align: "center", margin: 0, valign: "top", isTextBox: true });
  if (i < 3) s.addText("→", { x: x + 2.75, y: 2.75, w: 0.4, h: 0.6, fontSize: 28, color: K.texto, align: "center", margin: 0, isTextBox: true });
});
s.addText([
  { text: "Sin std::stack ni std::vector en el algoritmo: Pila<T> y Lista<T> enlazadas propias", options: { bullet: true, breakLine: true } },
  { text: "Multigrafo: aristas con id, admite lazos y aristas paralelas (Königsberg)", options: { bullet: true, breakLine: true } },
  { text: "Arreglo usada[e] + puntero siguiente[v] por vértice → nunca se revisa dos veces una arista", options: { bullet: true, breakLine: true } },
  { text: "Pruebas: 12 591 verificaciones, 0 fallos (incluye un ciclo de 200 000 aristas)", options: { bullet: true } },
], { x: 0.6, y: 4.5, w: 12.1, h: 2.2, fontSize: 16, color: K.texto, margin: 0, valign: "top", paraSpaceAfter: 6, isTextBox: true });

// ---------------------------------------------------------------- 9 casos borde
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Casos borde", "Qué pasa cuando el grafo NO admite ciclo euleriano");
tarjeta(s, 0.6, 1.9, 5.6, 1.5, "Königsberg: grados impares", "4 vértices impares (5, 3, 3, 3) → GRADOS_IMPARES. Hierholzer no se ejecuta.", K.rojo);
tarjeta(s, 0.6, 3.55, 5.6, 1.5, "Dos triángulos separados", "Grados pares, pero el DFS no alcanza la 2.ª parte → DESCONECTADO.", K.naranja);
tarjeta(s, 0.6, 5.2, 5.6, 1.5, "Un vértice, cero aristas", "SIN_ARISTAS → ciclo trivial [0].", K.verde);
video(s, "CasoBorde.mp4", "konigsberg.png", 6.7, 1.9, 6.0);
etiquetaVideo(s, 6.7, 5.45, 6.0, "Video: Casos borde (1:29 – 2:13)");
s.addNotes("Reproducir la escena CasoBorde: Königsberg (multigrafo con aristas paralelas), grafo desconectado y un solo vértice.");

// ---------------------------------------------------------------- 10 complejidad
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Complejidad", "V = vértices, E = aristas");
s.addText("O(V + E)", { x: 0.6, y: 2.0, w: 4.6, h: 1.3, fontSize: 60, bold: true, color: K.verde, margin: 0, isTextBox: true });
s.addText("tiempo y memoria: lineal en el tamaño del grafo (óptimo: la salida tiene E+1 vértices)", { x: 0.6, y: 3.3, w: 4.4, h: 1.2, fontSize: 16, color: K.suave, margin: 0, valign: "top", isTextBox: true });
s.addText("vs.  O(E²)  con Fleury", { x: 0.6, y: 4.8, w: 4.6, h: 0.6, fontSize: 22, bold: true, color: K.rojo, margin: 0, isTextBox: true });
const cab = { bold: true, color: K.fondo, fill: { color: K.oro } };
const fila = (a, b, c) => [{ text: a, options: { color: K.texto } }, { text: b, options: { color: K.verde, bold: true } }, { text: c, options: { color: K.suave } }];
s.addTable([
  [{ text: "Paso", options: cab }, { text: "Tiempo", options: cab }, { text: "Por qué", options: cab }],
  fila("Grados", "O(V)", "tamaño de cada lista"),
  fila("Conexidad", "O(V + E)", "DFS iterativo con pila propia"),
  fila("Hierholzer", "O(V + E)", "cada arista se usa 1 vez; el puntero solo avanza; E+1 push/pop"),
  fila("Memoria", "O(V + E)", "listas + usada[] + pila + ciclo"),
], { x: 5.6, y: 2.0, w: 7.1, colW: [1.7, 1.4, 4.0], fontSize: 14, fontFace: FB, fill: { color: K.panel }, border: { type: "solid", color: K.panel2, pt: 1 }, rowH: 0.55 });
etiquetaVideo(s, 5.6, 5.3, 7.1, "Video: Complejidad (2:13 – 2:29)");
s.addNotes("Opcional: reproducir la escena Complejidad (video/Complejidad.mp4) si hay tiempo.");

// ---------------------------------------------------------------- 11 conclusiones
s = pres.addSlide({ masterName: "CONTENIDO" });
titulo(s, "Conclusiones");
const concl = [
  ["Decidir es barato", "Paridad de grados + conexidad deciden la existencia en O(V + E), sin buscar el ciclo.", K.azul],
  ["Construir también", "Hierholzer nunca revisa dos veces una arista: la pila empalma los sub-ciclos sola.", K.verde],
  ["Animación honesta", "La traza separa lógica y dibujo: cualquier grafo nuevo genera su propio video.", K.oro],
];
concl.forEach(([c, b, col], i) => tarjeta(s, 0.6 + i * 4.1, 1.8, 3.9, 3.1, c, b, col));
s.addText("Repositorio: " + REPO, { x: 0.6, y: 5.4, w: 12.1, h: 0.5, fontSize: 16, color: K.azul, margin: 0, isTextBox: true,
  hyperlink: { url: "https://" + REPO } });
s.addText("¡Gracias! ¿Preguntas?", { x: 0.6, y: 6.0, w: 12.1, h: 0.6, fontSize: 24, bold: true, color: K.oro, margin: 0, isTextBox: true });

pres.writeFile({ fileName: path.join(__dirname, "Ciclo_Euleriano.pptx") }).then((f) => console.log("PPT generada:", f));
