# Layouts

Este documento describe los layouts soportados por `HLT Â· Slide Composer`.

## `vertical_stack`

Estado: implementado como motor puro en Fase 3.

CaracterÃ­sticas actuales:

- una columna;
- de una a cuatro imÃ¡genes;
- tÃ­tulo superior opcional;
- etiquetas opcionales debajo de cada imagen;
- las etiquetas vacÃ­as no reservan caja;
- footer reservado opcional para futuro logo;
- cÃ¡lculo determinista;
- rectÃ¡ngulos dentro del lienzo;
- modo visual de depuraciÃ³n.

Limitaciones actuales:

- no dibuja logo;
- no usa imagen de fondo;
- no aplica overlay;
- no procesa batches;
- no estÃ¡ integrado en ComfyUI.

## Pendientes

Estos layouts siguen sin implementar:

- `grid_2x2`;
- `auto_social`;
- `comparison`;
- `hero_stack`.
