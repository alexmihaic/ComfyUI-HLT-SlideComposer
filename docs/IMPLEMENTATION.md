# ImplementaciÃ³n

Este documento registra decisiones tÃ©cnicas de implementaciÃ³n del proyecto.

## Estado

Fase 0 preparÃ³ estructura, configuraciÃ³n y pruebas mÃ­nimas.

Fase 1 implementÃ³ motor puro de imagen:

- `Rect`, `CanvasSize` y presets de resoluciÃ³n.
- Parseo de colores HEX con fallback y advertencias.
- Ajuste de imagen `cover`, `contain` y `stretch`.
- Crop anchor vertical `top`, `center` y `bottom`.
- Esquinas redondeadas y borde.
- ConversiÃ³n Pillow/NumPy y adaptaciÃ³n diferida a Torch.

Fase 2 implementÃ³ motor puro de texto:

- BÃºsqueda multiplataforma de fuentes comunes.
- Cache de fuentes por ruta y tamaÃ±o.
- Fallback controlado a fuente de Pillow.
- Ajuste de texto por ancho, alto y nÃºmero de lÃ­neas.
- ReducciÃ³n progresiva de fuente y truncado con `â€¦`.
- Dibujo centrado dentro de `Rect`.

No existe todavÃ­a renderer de slide, layouts generales ni integraciÃ³n con ComfyUI.

## Principio de arquitectura

El paquete `hlt_slide` debe permanecer desacoplado de ComfyUI. La integraciÃ³n futura vivirÃ¡ en una capa fina que convertirÃ¡ entradas y salidas, sin contener algoritmos de composiciÃ³n.

`tensor_io.py` no importa Torch al cargar el paquete. La importaciÃ³n de Torch queda diferida a la funciÃ³n que crea el tensor final, para permitir ejecutar tests fuera de ComfyUI.

## Fuera de 0.1.0

`background_blur` no se implementarÃ¡ en `0.1.0`. Queda como posible mejora futura si no complica el motor ni aÃ±ade dependencias pesadas.
