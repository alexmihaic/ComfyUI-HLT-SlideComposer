# Layouts

Este documento describe los layouts soportados por `HLT · Slide Composer`.

## `vertical_stack`

Estado: implementado como motor puro y ampliado en Fase 4.

Caracteristicas actuales:

- una columna;
- de una a cuatro imagenes;
- titulo superior opcional;
- etiquetas opcionales debajo de cada imagen;
- las etiquetas vacias no reservan caja;
- footer reservado opcional;
- footer automatico cuando existe logo;
- logo centrado dentro del footer;
- calculo determinista;
- rectangulos dentro del lienzo;
- modo visual de depuracion.

El layout sigue sin dibujar contenido: solo calcula geometria. El renderer coordina fondo, imagenes, textos y logo.

### Espaciado de etiquetas

La secuencia de cada bloque con etiqueta es:

```text
imagen
image_label_gap
label_padding_top
texto
label_padding_bottom
label_after_gap
siguiente imagen
```

`image_label_gap` separa la imagen de su etiqueta. `label_after_gap` separa la zona completa de etiqueta del siguiente bloque. `block_gap` solo se usa entre bloques consecutivos cuando el bloque anterior no tiene etiqueta, para evitar sumar dos separaciones equivalentes.

Limitaciones actuales:

- no procesa batches completos; en `0.1.0` usa el primer frame de cada entrada;
- los workflows JSON de ejemplo deben exportarse desde ComfyUI durante QA manual.

## `grid_2x2`

Estado: implementado como motor puro en Fase 5.

Comportamiento:

- una imagen: una celda amplia a todo el ancho util;
- dos imagenes: dos columnas equivalentes;
- tres imagenes: primera imagen a todo el ancho util y segunda fila con dos columnas;
- cuatro imagenes: cuadricula regular 2 x 2;
- etiquetas debajo de cada imagen;
- altura de etiquetas alineada por fila;
- footer manual o automatico por logo;
- fondo, overlay, logo y debug coordinados desde el renderer.

`grid_2x2` calcula unicamente geometria. El ajuste de imagenes sigue reutilizando `compose_image_in_rect` con `cover`, `contain`, `stretch` y crop anchors `top`, `center` y `bottom`.

En cada fila, todas las etiquetas comparten la misma altura de zona, calculada a partir de la etiqueta mas alta de esa fila. Si una fila tiene etiquetas, la siguiente fila empieza despues de `label_after_gap`; si la fila no tiene ninguna etiqueta, no se reserva caja de etiqueta ni ese gap posterior.

## `auto_social`

Estado: implementado como selector puro en Fase 5.

Reglas actuales:

- 1 imagen -> `vertical_stack`;
- 2 imagenes -> `vertical_stack`;
- 3 imagenes -> `vertical_stack`;
- 4 imagenes -> `grid_2x2`.

La decision se basa en el numero real de imagenes activas, por lo que las entradas opcionales desconectadas no dejan huecos ni alteran el conteo.

La capa ComfyUI expone `vertical_stack`, `grid_2x2`, `auto_social` y
`adaptive_mosaic` mediante el input `layout`. El renderer puro resuelve el
layout efectivo antes de dibujar.

## Relleno de imagen en `contain`

Todos los layouts usan el mismo comportamiento de `contain_fill_mode`:

- `transparent`: valor predeterminado. Las bandas sobrantes de `contain` dejan ver el fondo del slide, incluyendo fondo solido, imagen de fondo y overlay.
- `cell_color`: conserva el relleno solido con `cell_background_color`.

Este ajuste no cambia la geometria de `vertical_stack`, `grid_2x2` ni `auto_social`; solo afecta a la composicion visual dentro del rectangulo de imagen.

## `adaptive_mosaic`

Estado: implementado para `v0.2.0`.

`adaptive_mosaic` selecciona una composicion de mosaico segun cantidad de
imagenes, proporciones fuente, espacio disponible, estrategia y hero opcional.

Caracteristicas:

- genera candidatos automaticamente;
- preserva aspect ratio;
- no aplica crop;
- no aplica stretch;
- usa containment transparente;
- soporta estrategias `balanced`, `editorial` y `compact`;
- permite `adaptive_hero=auto` o `image_1` a `image_4`;
- incluye filas justificadas internas;
- mantiene el maximo de cuatro imagenes;
- usa solo el primer frame de cada batch, como el resto del nodo.

`auto_social` no selecciona `adaptive_mosaic` automaticamente. El usuario debe
elegirlo explicitamente.

## Pendientes

Estos layouts siguen sin implementar:

- `comparison`;
- `hero_stack`.
