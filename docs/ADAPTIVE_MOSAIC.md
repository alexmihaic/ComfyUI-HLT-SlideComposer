# Adaptive Mosaic

`adaptive_mosaic` es un motor geometrico experimental para `v0.2.0`.
En esta fase solo calcula rectangulos: no dibuja imagenes reales, no se
integra en ComfyUI y no modifica el orden de widgets de `v0.1.0`.

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

El motor devuelve un `SlideLayout` compatible con el renderer futuro, pero no
lo conecta todavia al nodo.

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

## Limitaciones

- No renderiza imagenes fotograficas.
- No esta expuesto en ComfyUI.
- No decide todavia textos reales ni wrapping visual.
- No calcula foco semantico de imagen.
- Solo soporta de una a cuatro imagenes.
- El comportamiento de `hero_index` es geometrico, no artistico.

## Pendiente para renderizado

- decidir como se mapeara `adaptive_mosaic` a un layout visible;
- conectar las cajas al renderer Pillow existente;
- validar con imagenes reales;
- definir controles publicos sin alterar de forma brusca el nodo;
- decidir si las estrategias seran widgets o presets internos.
