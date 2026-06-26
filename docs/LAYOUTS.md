# Layouts

Este documento describe los layouts soportados por `HLT · Slide Composer`.

## `vertical_stack`

Estado: implementado como motor puro y ampliado en Fase 4.

Características actuales:

- una columna;
- de una a cuatro imágenes;
- título superior opcional;
- etiquetas opcionales debajo de cada imagen;
- las etiquetas vacías no reservan caja;
- footer reservado opcional;
- footer automático cuando existe logo;
- logo centrado dentro del footer;
- cálculo determinista;
- rectángulos dentro del lienzo;
- modo visual de depuración.

El layout sigue sin dibujar contenido: solo calcula geometría. El renderer coordina fondo, imágenes, textos y logo.

Limitaciones actuales:

- no usa `grid_2x2`;
- no usa `auto_social`;
- no procesa batches;
- no está integrado en ComfyUI.

## Pendientes

Estos layouts siguen sin implementar:

- `grid_2x2`;
- `auto_social`;
- `comparison`;
- `hero_stack`.
