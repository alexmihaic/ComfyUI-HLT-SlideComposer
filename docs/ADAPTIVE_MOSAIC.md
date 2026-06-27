# Adaptive Mosaic

`adaptive_mosaic` es un sistema experimental para `v0.2.0`. La Fase 8A
implemento el motor geometrico puro. La Fase 8B conecta ese motor con el
renderer Pillow para validar resultados visuales reales, pero todavia no lo
expone en el nodo de ComfyUI ni modifica los widgets de `v0.1.0`.

## Problema

Los layouts de `v0.1.0` funcionan bien cuando las imagenes encajan en una
estructura fija. Con mezclas de imagenes horizontales, verticales, cuadradas y
3:4, esas estructuras pueden dejar mucho fondo visible o producir cajas poco
legibles. El objetivo del nuevo motor es probar varias composiciones internas,
puntuarlas y escoger la mejor sin deformar ni recortar las fuentes.

## Arquitectura

El modulo `hlt_slide/adaptive_mosaic.py` es puro y depende solo de las
estructuras existentes:

- `Rect`
- `BlockLayout`
- `SlideLayout`

Las entradas principales son:

- `SourceImageInfo`: indice, dimensiones fuente, aspect ratio y presencia de etiqueta.
- `AdaptiveMosaicSettings`: estrategia, gaps, minimo de imagen, etiquetas y footer.
- `MosaicCandidate`: plantilla, bloques, score, penalizaciones y diagnostico.

El motor devuelve un `SlideLayout` compatible con el renderer existente.
La integracion se hace mediante funciones puras del renderer:

- `measure_adaptive_mosaic_layout(...)`
- `render_adaptive_mosaic(...)`

`render_vertical_stack(...)` conserva su contrato publico.

## Plantillas candidatas

Una imagen:

- `single`

Dos imagenes:

- `row_2`
- `column_2`
- `hero_left`
- `hero_right`
- `hero_top`
- `hero_bottom`

Tres imagenes:

- `row_3`
- `column_3`
- `hero_left_2_stack`
- `hero_right_2_stack`
- `hero_top_2_row`
- `hero_bottom_2_row`
- `justified_1_2`
- `justified_2_1`

Cuatro imagenes:

- `grid_2x2`
- `hero_left_3_stack`
- `hero_right_3_stack`
- `hero_top_3_row`
- `hero_bottom_3_row`
- `justified_1_3`
- `justified_3_1`
- `justified_2_2`

Estas plantillas son internas y no aparecen en `INPUT_TYPES`.

## Preservacion de ratio

`fit_rect_preserving_aspect()` calcula un rectangulo dentro del area disponible:

- no deforma;
- no recorta;
- no usa `stretch`;
- no sale del area disponible;
- permite que el fondo quede visible.

El motor usa ratios fuente para convertir celdas disponibles en rectangulos de
imagen. Las diferencias minimas por redondeo de pixeles se tratan como error
cero en la puntuacion.

## Integracion con renderer

El renderer experimental construye `SourceImageInfo` desde cada `SlideItem`:

- indice estable;
- anchura y altura reales de la imagen;
- aspect ratio fuente;
- presencia de etiqueta mediante `bool(label.strip())`.

No inspecciona contenido visual, no usa IA y no cambia el orden de entrada.
El maximo sigue siendo cuatro imagenes.

## Area util

El motor acepta ahora un `content_rect` explicito. Cuando no se proporciona,
mantiene el comportamiento de Fase 8A para no romper pruebas existentes.

Cuando el renderer llama al motor, calcula el area util real descontando:

- `outer_margin`;
- `top_margin`;
- titulo;
- `title_gap`;
- `bottom_margin`;
- footer;
- logo cuando obliga a reservar footer.

El titulo y el footer se guardan en `SlideLayout`, pero quedan fuera de
`content_rect`. Ninguna imagen ni etiqueta valida debe salir de esa zona.

## Fit efectivo en adaptive mosaic

En esta fase experimental, `image_fit` global no controla las imagenes del
layout adaptativo. El fit efectivo es siempre:

```text
contain + transparent
```

Motivo:

- cada `image_rect` ya esta calculado con el ratio original;
- no se permite crop silencioso;
- `stretch` queda prohibido para este layout;
- el fondo debe seguir visible en los huecos.

Las esquinas redondeadas y los bordes si se aplican.

## Filas justificadas

Las plantillas justificadas soportan divisiones `1+3`, `2+2` y `3+1`.
Cada fila calcula una altura compartida, descuenta gaps y reparte el error de
redondeo de forma determinista para que la ultima caja cierre contra el borde
previsto.

## Puntuacion

Cada candidato contiene penalizaciones nombradas:

- `unused_area`
- `tiny_cells`
- `aspect_error`
- `visual_imbalance`
- `extreme_size_difference`
- `label_overflow`
- `order_change`
- `edge_misalignment`

La puntuacion final parte de un valor alto y resta penalizaciones ponderadas
por estrategia. Los candidatos con imagenes por debajo del minimo, etiquetas
sin espacio o areas imposibles no se ocultan: reciben penalizaciones fuertes.

## Estrategias

- `balanced`: prioriza legibilidad y tamanos equilibrados.
- `editorial`: permite una imagen dominante y penaliza menos el desequilibrio.
- `compact`: penaliza mas el area sin usar para favorecer ocupacion.

Las estrategias son internas en esta fase.

## Geometria de etiquetas

El motor reserva `label_rect` debajo de cada imagen cuando la fuente declara
`has_label=True`. Las etiquetas usan altura minima, padding superior/inferior y
gap de separacion. Ningun `label_rect` valido debe intersectar otra imagen ni
salir del area disponible; si no cabe, el candidato queda penalizado.

## Iteracion de etiquetas

El ancho real de cada etiqueta depende de la plantilla candidata. El renderer
usa un proceso determinista:

1. genera candidatos con `label_min_height`;
2. mide cada etiqueta con el ancho real de su `label_rect`;
3. calcula altura reservada con padding superior, texto ajustado, padding
   inferior y minimo;
4. recalcula el layout con esas alturas;
5. repite hasta tres iteraciones o hasta estabilizar.

El proceso usa el motor de texto existente y conserva clipping, dos lineas y
etiquetas vacias.

## Diagnostico

`describe_candidate()` resume:

- plantilla;
- score;
- penalizaciones;
- aspect ratios fuente;
- aspect ratios de salida;
- porcentaje de area no usada.

El script `scripts/generate_adaptive_mosaic_geometry.py` produce diagramas en:

```text
examples/outputs/adaptive-mosaic/
```

El script `scripts/generate_adaptive_mosaic_rendered_outputs.py` produce
renders reales en:

```text
examples/outputs/adaptive-mosaic-rendered/
```

El debug experimental muestra:

- `LAYOUT: ADAPTIVE_MOSAIC`
- `TEMPLATE`
- `STRATEGY`
- `SCORE`
- `UNUSED`
- penalizaciones principales
- rectangulos `TITLE`, `IMAGE N`, `LABEL N`, `FOOTER` y `LOGO`.

## Limitaciones

- No esta expuesto en ComfyUI.
- No calcula foco semantico de imagen.
- Solo soporta de una a cuatro imagenes.
- El comportamiento de `hero_index` es geometrico, no artistico.
- Puede dejar bastante fondo visible cuando conservar ratios compite con
  jerarquia editorial.
- La seleccion de estrategia sigue siendo experimental y no tiene widget.

## Pendiente para Fase 8C

- decidir como se mapeara `adaptive_mosaic` a un layout visible;
- definir controles publicos sin alterar de forma brusca el nodo;
- decidir si las estrategias seran widgets o presets internos;
- revisar defaults visuales con casos reales;
- decidir si se permite una opcion de menor area vacia aunque reduzca jerarquia;
- ampliar validacion manual dentro de ComfyUI cuando se exponga el layout.
