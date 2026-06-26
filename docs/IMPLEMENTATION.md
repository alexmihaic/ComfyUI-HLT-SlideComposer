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

Fase 3 implementÃ³ `vertical_stack` puro:

- CÃ¡lculo de geometrÃ­a sin dibujo en `hlt_slide.layouts`.
- Renderer Pillow con fondo sÃ³lido en `hlt_slide.renderer`.
- TÃ­tulo superior opcional.
- Una a cuatro imÃ¡genes activas.
- Etiquetas opcionales debajo de cada imagen.
- Reserva geomÃ©trica de footer para futuro logo.
- Modo `debug_layout`.

No existe todavÃ­a logo real, mÃ¡scara, fondo fotogrÃ¡fico, overlay, `grid_2x2`, `auto_social` ni integraciÃ³n con ComfyUI.

## Principio de arquitectura

El paquete `hlt_slide` debe permanecer desacoplado de ComfyUI. La integraciÃ³n futura vivirÃ¡ en una capa fina que convertirÃ¡ entradas y salidas, sin contener algoritmos de composiciÃ³n.

`tensor_io.py` no importa Torch al cargar el paquete. La importaciÃ³n de Torch queda diferida a la funciÃ³n que crea el tensor final, para permitir ejecutar tests fuera de ComfyUI.

## Entorno real validado

ValidaciÃ³n realizada con el Python embebido de la instalaciÃ³n real de ComfyUI, sin instalar ni actualizar paquetes:

- Python: `3.11.8`
- Ejecutable: `C:\IAstuff\STUDIO344\App\python_embeded\python.exe`
- Pillow: `10.4.0`
- NumPy: `1.26.4`
- Torch: `2.9.1+cu130`

Comprobaciones realizadas:

- `compileall hlt_slide`
- imports del paquete insertando la raÃ­z del repositorio en `sys.path`
- `scripts/validate_comfy_runtime.py`
- test marcado `torch` en `tests/test_tensor_io.py`

Incidencia observada: esta distribuciÃ³n embebida no resolviÃ³ el paquete mediante `PYTHONPATH` en los comandos directos. La validaciÃ³n se hizo insertando la raÃ­z del repositorio en `sys.path` dentro del proceso, sin instalar el paquete ni modificar ComfyUI.

## Fuera de 0.1.0

`background_blur` no se implementarÃ¡ en `0.1.0`. Queda como posible mejora futura si no complica el motor ni aÃ±ade dependencias pesadas.
