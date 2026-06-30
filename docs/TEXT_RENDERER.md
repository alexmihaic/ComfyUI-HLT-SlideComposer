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

| Rol | Maximum | Preferred | Minimum | Max lines | Line spacing |
| --- | ---: | ---: | ---: | ---: | ---: |
| `number` | 300 | 220 | 48 | 2 | 6 |
| `headline` | 220 | 168 | 40 | 4 | 8 |
| `quote` | 170 | 120 | 36 | 7 | 10 |
| `subheadline` | 150 | 104 | 30 | 5 | 8 |
| `body` | 100 | 68 | 24 | 10 | 8 |
| `label` | 82 | 56 | 20 | 3 | 5 |
| `caption` | 68 | 44 | 18 | 4 | 5 |

Se escalan con:

```text
canvas_width / 1080 * font_scale
```

`font_scale` se valida entre `0.25` y `4.0`.

Phase 9B.1 usa una estrategia largest-fit: intenta el tamaño máximo del rol y baja de forma determinista hasta encontrar el tamaño mayor que cabe completo en el `inner_rect`. El tamaño preferido queda documentado como referencia de intención, pero no limita el crecimiento cuando el bloque tiene espacio suficiente.

## Defaults de roles

Los cuatro roles internos por defecto del futuro Text Composer son:

```text
headline
headline
headline
headline
```

La jerarquía editorial mediante `body`, `caption`, `quote` u otros roles debe ser una elección explícita.

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

1. tamaño máximo del rol;
2. reducción hasta mínimo buscando el mayor tamaño que cabe;
3. wrapping;
4. límite de líneas;
5. truncado como último recurso.

Text Composer conserva palabras completas durante el wrapping automático. Los saltos manuales siguen siendo obligatorios. Si un token aislado no cabe en el tamaño mínimo, se trunca con ellipsis; no se insertan guiones ni separación silábica.

`text_engine.fit_text` conserva compatibilidad hacia atrás porque `break_long_words=True` sigue siendo el valor predeterminado. Text Composer llama al motor con `break_long_words=False`.

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
- tamaño preferido y máximo;
- número de líneas;
- truncado;
- porcentaje de uso de ancho y alto;
- conservación de palabras;
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
