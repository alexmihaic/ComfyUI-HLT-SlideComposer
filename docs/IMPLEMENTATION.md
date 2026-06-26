# Implementación

Este documento registra decisiones técnicas de implementación del proyecto.

## Estado

Fase 0 preparó estructura, configuración y pruebas mínimas.

Fase 1 implementó motor puro de imagen:

- `Rect`, `CanvasSize` y presets de resolución.
- Parseo de colores HEX con fallback y advertencias.
- Ajuste de imagen `cover`, `contain` y `stretch`.
- Crop anchor vertical `top`, `center` y `bottom`.
- Esquinas redondeadas y borde.
- Conversión Pillow/NumPy y adaptación diferida a Torch.

Fase 2 implementó motor puro de texto:

- Búsqueda multiplataforma de fuentes comunes.
- Cache de fuentes por ruta y tamaño.
- Fallback controlado a fuente de Pillow.
- Ajuste de texto por ancho, alto y número de líneas.
- Reducción progresiva de fuente y truncado con `…`.
- Dibujo centrado dentro de `Rect`.

Fase 3 implementó `vertical_stack` puro:

- Cálculo de geometría sin dibujo en `hlt_slide.layouts`.
- Renderer Pillow con fondo sólido en `hlt_slide.renderer`.
- Título superior opcional.
- Una a cuatro imágenes activas.
- Etiquetas opcionales debajo de cada imagen.
- Reserva geométrica de footer para futuro logo.
- Modo `debug_layout`.

Fase 4 amplió el renderer puro:

- fondo sólido, fondo de imagen y fondo con overlay;
- `cover`, `contain` y `stretch` para fondos;
- opacidad del fondo y del overlay con clamp `0.0-1.0`;
- preset `Background size` integrado en el renderer;
- logo opaco o RGBA;
- máscara externa `L`, `RGB` o `RGBA`;
- inversión de máscara para semántica compatible con ComfyUI;
- composición alpha correcta y salida final RGB;
- footer automático cuando existe logo;
- debug de footer y caja final del logo.

Fase 5 completó el motor puro de layouts:

- `grid_2x2` para una, dos, tres y cuatro imágenes;
- primera imagen a ancho completo en el caso de tres imágenes;
- filas y columnas alineadas con etiquetas por fila;
- selección determinista `auto_social`;
- integración del renderer con `vertical_stack`, `grid_2x2` y `auto_social`;
- debug con indicación del layout efectivo;
- outputs visuales sintéticos de revisión.

No existe todavía `nodes.py` ni integración con ComfyUI.

## Principio de arquitectura

El paquete `hlt_slide` debe permanecer desacoplado de ComfyUI. La integración futura vivirá en una capa fina que convertirá entradas y salidas, sin contener algoritmos de composición.

`tensor_io.py` no importa Torch al cargar el paquete. La importación de Torch queda diferida a la función que crea el tensor final, para permitir ejecutar tests fuera de ComfyUI.

La lógica de logo vive en `hlt_slide.logo_utils` porque combina escalado proporcional, máscaras e interpolación alpha. El renderer solo coordina el footer y el orden de composición.

La selección de layout vive en `hlt_slide.layouts`. `auto_social` no dibuja: decide de forma determinista entre `vertical_stack` y `grid_2x2` según el número real de imágenes activas.

## Orden de composición actual

1. color base;
2. imagen de fondo;
3. overlay;
4. título;
5. imágenes de contenido;
6. etiquetas;
7. logo;
8. guías de debug.

## Entorno real validado

Validación realizada con el Python embebido de la instalación real de ComfyUI, sin instalar ni actualizar paquetes:

- Python: `3.11.8`
- Ejecutable: `C:\IAstuff\STUDIO344\App\python_embeded\python.exe`
- Pillow: `10.4.0`
- NumPy: `1.26.4`
- Torch: `2.9.1+cu130`

Comprobaciones realizadas:

- `compileall hlt_slide`
- imports del paquete insertando la raíz del repositorio en `sys.path`
- `scripts/validate_comfy_runtime.py`
- test marcado `torch` en `tests/test_tensor_io.py`

Incidencia observada: esta distribución embebida no resolvió el paquete mediante `PYTHONPATH` en los comandos directos. La validación se hizo insertando la raíz del repositorio en `sys.path` dentro del proceso, sin instalar el paquete ni modificar ComfyUI.

## Fuera de 0.1.0

`background_blur` no se implementará en `0.1.0`. Queda como posible mejora futura si no complica el motor ni añade dependencias pesadas.
