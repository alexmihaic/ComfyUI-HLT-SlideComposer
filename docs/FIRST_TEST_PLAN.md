# Plan de primera prueba en ComfyUI

Este flujo se ejecutará después de instalar manualmente el repositorio en `custom_nodes`.

No es un workflow JSON exportado ni validado todavía dentro de ComfyUI.

## Flujo previsto

```text
Load Image -> image_1
Load Image -> image_2
Load Image -> image_3
Load Image logo -> logo_image
Load Image logo -> logo_mask
HLT · Slide Composer
Preview Image
Save Image
```

## Valores iniciales recomendados

- `canvas_preset`: `9:16 Social · 1080x1920`
- `layout`: `vertical_stack`
- `background_mode`: `solid`
- `background_color`: `#000000`
- `title`: `REFERENCIAS Y RESULTADO`
- `label_1`: `REF0 · PRODUCTO`
- `label_2`: `REF1 · PERSONA`
- `label_3`: `RESULTADO`
- `image_fit`: `cover`
- `crop_anchor`: `center`
- `logo_width_percent`: `18`
- `invert_logo_mask`: `true`

## Comprobaciones

- El nodo aparece como `HLT · Slide Composer`.
- La salida llega a `Preview Image`.
- La resolución es `1080 x 1920`.
- No quedan huecos por imágenes opcionales desconectadas.
- El logo conserva proporción y queda centrado abajo.
- La máscara del logo responde a `invert_logo_mask`.
- La consola no muestra errores del custom node.
