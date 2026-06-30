# Adaptive Mosaic

`adaptive_mosaic` es el nuevo layout preparado para `v0.2.0`. El motor
geometrico puro esta integrado con el renderer Pillow y expuesto en el nodo
`HLT · Slide Composer`.

Estado de preparacion:

- integrado en `HLT · Slide Composer`;
- probado manualmente por el propietario del proyecto en su instalacion real de ComfyUI;
- validado con el Python embebido de ComfyUI;
- preparado para publicarse en `v0.2.0`.

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

## Integracion ComfyUI

En `v0.2.0`, `adaptive_mosaic` se anade como layout publico del nodo
`HLT · Slide Composer`.

Seleccion:

```text
layout = adaptive_mosaic
adaptive_strategy = balanced | editorial | compact
adaptive_hero = auto | image_1 | image_2 | image_3 | image_4
```

El valor predeterminado historico de `layout` sigue siendo `vertical_stack`.
`auto_social` no cambia: con 1-3 imagenes usa `vertical_stack` y con 4 imagenes
usa `grid_2x2`.

`adaptive_strategy` controla la ponderacion interna:

- `balanced`: legibilidad y tamanos estables;
- `editorial`: permite una imagen dominante;
- `compact`: penaliza mas el area vacia.

`adaptive_hero=auto` no fuerza protagonista. Si se elige `image_1` a `image_4`,
esa entrada intenta recibir el area dominante. Si la entrada no esta conectada,
el nodo emite una advertencia con prefijo `[HLT Slide Composer]` y vuelve a
seleccion automatica, sin reasignar el hero a otra imagen.

Los dos widgets nuevos se colocan al final del orden historico:

```text
label_vertical_align
label_clip
adaptive_strategy
adaptive_hero
```

Los workflows antiguos que no contienen estos campos usan:

```text
adaptive_strategy = balanced
adaptive_hero = auto
```

Cuando `layout != adaptive_mosaic`, el nodo mantiene el flujo anterior y llama
a `render_vertical_stack(...)`, que tambien resuelve `grid_2x2` y
`auto_social`.

Cuando `layout == adaptive_mosaic`, el nodo llama a
`render_adaptive_mosaic(...)` y construye `AdaptiveMosaicSettings` con:

- estrategia desde `adaptive_strategy`;
- hero desde `adaptive_hero`;
- `preserve_order=True`;
- `preserve_aspect=True`;
- `gap` desde `inner_padding`;
- padding y alturas de etiqueta desde los controles existentes.

No se exponen pesos, tamanos minimos, plantilla manual ni controles de
filas justificadas.

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

El renderer adaptativo construye `SourceImageInfo` desde cada `SlideItem`:

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

En `adaptive_mosaic`, `image_fit` global no controla las imagenes del layout
adaptativo. El fit efectivo es siempre:

```text
contain + transparent
```

Motivo:

- cada `image_rect` ya esta calculado con el ratio original;
- no se permite crop silencioso;
- `stretch` queda prohibido para este layout;
- el fondo debe seguir visible en los huecos.

Las esquinas redondeadas y los bordes si se aplican.

Esta excepcion tambien aplica desde el nodo ComfyUI: aunque el usuario tenga
`image_fit=cover`, `crop_anchor=top` o `contain_fill_mode=cell_color`, las
imagenes adaptativas se renderizan con proporcion conservada y bandas
transparentes para que se vea el fondo real.

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

Las estrategias estan expuestas como widget del nodo; sus pesos y plantillas
internas no se exponen.

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

El script `scripts/generate_adaptive_mosaic_node_outputs.py` produce renders
ejecutando la clase del nodo en:

```text
examples/outputs/adaptive-mosaic-node/
```

Estos directorios son salidas de QA regenerables. La release publica conserva
solo assets seleccionados bajo `docs/assets/readme/`.

El debug adaptativo muestra:

- `LAYOUT: ADAPTIVE_MOSAIC`
- `TEMPLATE`
- `STRATEGY`
- `HERO`
- `SCORE`
- `UNUSED AREA`
- penalizaciones principales
- rectangulos `TITLE`, `IMAGE N`, `LABEL N`, `FOOTER` y `LOGO`.

## Limitaciones

- Maximo de cuatro imagenes.
- Validacion principal en Windows.
- No calcula foco semantico de imagen.
- El comportamiento de `hero_index` es geometrico, no artistico.
- Puede dejar bastante fondo visible cuando conservar ratios compite con
  jerarquia editorial.
- Usa solo el primer frame de cada batch de entrada.
- El workflow publico usa nombres de imagen relativos como marcadores; el
  usuario debe sustituirlos por recursos locales en ComfyUI.
