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

- no procesa batches;
- no está integrado en ComfyUI.

## `grid_2x2`

Estado: implementado como motor puro en Fase 5.

Comportamiento:

- una imagen: una celda amplia a todo el ancho útil;
- dos imágenes: dos columnas equivalentes;
- tres imágenes: primera imagen a todo el ancho útil y segunda fila con dos columnas;
- cuatro imágenes: cuadrícula regular 2 x 2;
- etiquetas debajo de cada imagen;
- altura de etiquetas alineada por fila;
- footer manual o automático por logo;
- fondo, overlay, logo y debug coordinados desde el renderer.

`grid_2x2` calcula únicamente geometría. El ajuste de imágenes sigue reutilizando `compose_image_in_rect` con `cover`, `contain`, `stretch` y crop anchors `top`, `center` y `bottom`.

## `auto_social`

Estado: implementado como selector puro en Fase 5.

Reglas actuales:

- 1 imagen -> `vertical_stack`;
- 2 imágenes -> `vertical_stack`;
- 3 imágenes -> `vertical_stack`;
- 4 imágenes -> `grid_2x2`.

La decisión se basa en el número real de imágenes activas, por lo que las entradas opcionales desconectadas no dejan huecos ni alteran el conteo.

## Pendientes

Estos layouts siguen sin implementar:

- `comparison`;
- `hero_stack`.
