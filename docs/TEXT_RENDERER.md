# Text Renderer

`hlt_slide.text_renderer` convierte las geometrías puras de `text_layouts.py` en imágenes RGB renderizadas con Pillow. Sigue siendo una capa independiente de ComfyUI y Torch.

## Arquitectura

- `text_layouts.py`: resuelve bloques activos, layout efectivo y rectángulos.
- `text_engine.py`: mide, envuelve, reduce fuente, trunca y expone bounds de líneas.
- `text_renderer.py`: resuelve canvas, estilos, colores, acento, fondo, logo, fitting por bloque, clipping, debug y render final.

La API pública de Phase 9B es:

```python
measure_text_composition(...)
render_text_composition(...)
```

`measure_text_composition` devuelve un plan determinista sin dibujar la composición final. `render_text_composition` usa ese plan para generar una imagen `PIL.Image` en modo `RGB`.

## Estilos por rol

Los estilos base están definidos para un canvas de 1080 px de ancho:

| Rol | Preferred | Minimum | Max lines | Line spacing |
| --- | ---: | ---: | ---: | ---: |
| `number` | 184 | 42 | 2 | 6 |
| `headline` | 112 | 34 | 4 | 8 |
| `quote` | 88 | 30 | 7 | 10 |
| `subheadline` | 64 | 26 | 5 | 8 |
| `body` | 44 | 22 | 10 | 8 |
| `label` | 32 | 18 | 3 | 5 |
| `caption` | 28 | 16 | 4 | 5 |

Se escalan con:

```text
canvas_width / 1080 * font_scale
```

`font_scale` se valida entre `0.25` y `4.0`.

## Alineación automática

- `centered_statement`: horizontal `center`, vertical `center`.
- `vertical_stack`: horizontal `left`, vertical `center`.
- `split_2`: horizontal `left`, vertical `center`.
- `grid_2x2`: horizontal `left`, vertical `center`.
- `editorial_quote`: principal `left/center`, secundario `right/bottom`.

Los overrides globales `horizontal_align` y `vertical_align` sustituyen estas reglas para todos los bloques.

## Color y acento

Defaults:

```text
text_color = #F3F0E8
accent_color = #E92124
accent_target = none
```

`accent_target` acepta `none`, `first_active`, `text_1`, `text_2`, `text_3` y `text_4`. El acento se aplica al bloque completo. Si el slot seleccionado está vacío, se emite warning y no se reasigna a otro bloque.

No hay resaltado parcial, Markdown ni HTML.

## Truncado y clipping

Cada bloque usa `fit_text` de `text_engine.py`:

1. tamaño preferido del rol;
2. reducción hasta mínimo;
3. wrapping;
4. límite de líneas;
5. truncado como último recurso.

Si hay truncado y `warn_on_truncation=True`, se emite:

```text
[HLT Text Composer] text_N was truncated.
```

`clipping=True` recorta el dibujo final al `inner_rect`. `clipping=False` no desactiva el fitting.

## Fondos

Se soporta:

- `solid`;
- `image`;
- `image_with_overlay`.

El ajuste de imagen usa `cover`, `contain` o `stretch`. No hay blur en Phase 9B.

## Logo

El renderer acepta `logo_image` y `logo_mask`. Reutiliza el cálculo y composición de logo existentes:

- anchura porcentual;
- altura máxima;
- opacidad;
- offset inferior;
- inversión de máscara.

Con `reserve_logo_space=True`, la geometría textual reserva espacio inferior antes de seleccionar el layout. Sin reserva, el logo puede superponerse visualmente y no altera la geometría.

## Debug

`debug_layout=True` dibuja:

- `TEXT COMPOSER`;
- layout solicitado y efectivo;
- `content_rect`;
- `block rect`;
- `inner_rect`;
- slot original;
- rol;
- tamaño de fuente;
- número de líneas;
- truncado;
- alineación;
- `logo_rect` si existe.

El debug es determinista y está pensado para inspección técnica.

## Limitaciones

- No registra todavía `HLTTextComposer`.
- No hay integración ComfyUI.
- No hay controles por bloque para color o alineación.
- No hay presets visuales.
- No hay familias de fuente por rol, tracking, kerning manual ni fuentes embebidas.
- No hay resaltado parcial de palabras.
