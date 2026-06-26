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

Fase 6A añadió la capa backend de integración ComfyUI dentro del repositorio:

- `nodes.py` define `HLTSlideComposer`;
- `__init__.py` raíz exporta únicamente los mappings de ComfyUI;
- `INPUT_TYPES` declara imágenes, máscara, formato, layout, textos, fondo, tipografía, geometría, borde, logo y debug;
- el nodo convierte `IMAGE` de ComfyUI a Pillow usando el primer frame;
- el nodo convierte `MASK` a Pillow `L` y conserva la opción `invert_logo_mask`;
- la salida vuelve como tensor `IMAGE` `[1,H,W,3]`, `float32`, rango `0.0-1.0`;
- `scripts/validate_node_integration.py` valida el contrato sin copiar el repositorio a `custom_nodes`.

El nodo todavía no se ha instalado físicamente en ComfyUI, no se ha validado durante el arranque real y no existe workflow JSON exportado desde ComfyUI.

## Principio de arquitectura

El paquete `hlt_slide` debe permanecer desacoplado de ComfyUI. La integración futura vivirá en una capa fina que convertirá entradas y salidas, sin contener algoritmos de composición.

`tensor_io.py` no importa Torch al cargar el paquete. La importación de Torch queda diferida a la función que crea el tensor final, para permitir ejecutar tests fuera de ComfyUI.

La lógica de logo vive en `hlt_slide.logo_utils` porque combina escalado proporcional, máscaras e interpolación alpha. El renderer solo coordina el footer y el orden de composición.

La selección de layout vive en `hlt_slide.layouts`. `auto_social` no dibuja: decide de forma determinista entre `vertical_stack` y `grid_2x2` según el número real de imágenes activas.

La capa `nodes.py` debe seguir siendo fina: no contiene layout, crop, texto ni composición alpha. Solo ordena inputs, convierte tensores, construye `RenderSettings`, llama al renderer y devuelve el tensor final.

## Relleno de `contain`

`image_fit="contain"` soporta dos modos mediante `contain_fill_mode`:

- `transparent`: modo predeterminado. La imagen conserva su proporcion y las bandas sobrantes se mantienen transparentes para que se vea el fondo real ya compuesto del slide, sea solido, imagen u overlay.
- `cell_color`: modo de compatibilidad. Las bandas sobrantes se rellenan con `cell_background_color`.

`cell_background_color` solo afecta a imagenes de contenido cuando `image_fit="contain"` y `contain_fill_mode="cell_color"`. No participa en `cover` ni `stretch`.

La composicion usa capas RGBA para evitar multiplicar dos veces el alpha interno de PNGs y la salida final del renderer sigue siendo RGB.

## Descubrimiento en ComfyUI

ComfyUI carga cada custom node como paquete a partir del `__init__.py` de la carpeta instalada. Por eso el entrypoint raíz debe resolver el `nodes.py` interno del paquete y no debe caer en un módulo top-level llamado `nodes`, que puede pertenecer al propio ComfyUI.

La carga realista se valida con `scripts/validate_package_discovery.py`. Ese script importa el repositorio mediante `spec_from_file_location(..., submodule_search_locations=[...])`, bloquea el paquete top-level `hlt_slide` y simula un módulo global `nodes` vacío para comprobar que `NODE_CLASS_MAPPINGS["HLTSlideComposer"]` procede de `<paquete_temporal>.nodes`.

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
