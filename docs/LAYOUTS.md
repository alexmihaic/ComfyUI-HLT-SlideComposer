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
- la integración backend existe, pero todavía no se ha probado durante el arranque real de ComfyUI.

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

La capa ComfyUI expone `vertical_stack`, `grid_2x2` y `auto_social` mediante el input `layout`. El renderer puro resuelve el layout efectivo antes de dibujar.

## Relleno de imagen en `contain`

Todos los layouts usan el mismo comportamiento de `contain_fill_mode`:

- `transparent`: valor predeterminado. Las bandas sobrantes de `contain` dejan ver el fondo del slide, incluyendo fondo solido, imagen de fondo y overlay.
- `cell_color`: conserva el relleno solido con `cell_background_color`.

Este ajuste no cambia la geometria de `vertical_stack`, `grid_2x2` ni `auto_social`; solo afecta a la composicion visual dentro del rectangulo de imagen.

## Pendientes

Estos layouts siguen sin implementar:

- `comparison`;
- `hero_stack`.
