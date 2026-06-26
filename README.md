# HLT Slide Composer para ComfyUI

`HLT · Slide Composer` será un custom node de ComfyUI para componer entre una y cuatro imágenes dentro de un slide editorial, principalmente vertical 9:16, con título, etiquetas, fondo y logo opcional.

La fuente de verdad funcional, visual y técnica del proyecto es `MASTER_SPEC.md`.

## Estado actual

Este repositorio tiene completadas estas fases del motor puro:

- Fase 1: geometría, presets, colores, ajuste de imagen y conversión Pillow/NumPy.
- Fase 2: resolución de fuentes, ajuste de texto y dibujo centrado.
- Fase 3: layout `vertical_stack` y renderer Pillow con fondo sólido.
- Fase 4: fondo de imagen, overlay, logo, máscara y composición alpha.
- Fase 5: layout `grid_2x2`, selector `auto_social` y renderer puro multi-layout.

Todavía no está listo para instalarse ni usarse dentro de ComfyUI. No existe aún `nodes.py` ni workflow de ComfyUI.

## Problema que resolverá

El nodo evitará tener que construir manualmente un slide con varios nodos de resize, crop, composite, texto, máscara y preview. La versión `0.1.0` debe producir una única salida `IMAGE` lista para previsualizar o guardar desde ComfyUI.

## Alcance previsto de 0.1.0

- Una entrada obligatoria `image_1`.
- Hasta tres imágenes opcionales adicionales.
- Título superior y etiquetas debajo de cada imagen.
- Fondo sólido o imagen de fondo.
- Logo externo opcional centrado abajo.
- Layouts `vertical_stack`, `grid_2x2` y `auto_social`.
- Ajustes de imagen `cover`, `contain` y `stretch`.
- Salida ComfyUI `IMAGE` en formato `[B, H, W, C]`, `float32`, rango `0.0-1.0`.
- Renderer basado en Pillow, probado fuera de ComfyUI.

`background_blur` queda fuera de la versión `0.1.0` y se documenta como posible mejora futura.

## Arquitectura general

El proyecto separa el motor puro de composición de la integración con ComfyUI:

- `hlt_slide/`: paquete Python puro, sin imports de ComfyUI.
- `tests/`: pruebas automatizadas del paquete y, más adelante, del contrato del nodo.
- `docs/`: documentación técnica y decisiones de implementación.
- `examples/`: workflows y salidas visuales generadas durante la validación.
- `scripts/`: scripts locales de validación y generación visual.

En fases posteriores, `nodes.py` será solo la capa de adaptación a ComfyUI: definirá inputs, convertirá tensores, llamará al renderer y devolverá el tensor final.

## Módulos disponibles

- `hlt_slide.config`: modelos de geometría y resolución.
- `hlt_slide.color_utils`: parseo tolerante de colores HEX.
- `hlt_slide.image_utils`: ajuste de imágenes con `cover`, `contain` y `stretch`.
- `hlt_slide.tensor_io`: conversiones Pillow/NumPy y adaptación diferida a Torch.
- `hlt_slide.font_utils`: búsqueda y cache de fuentes.
- `hlt_slide.text_engine`: ajuste y dibujo centrado de texto.
- `hlt_slide.layouts`: geometría pura de `vertical_stack`, `grid_2x2` y `auto_social`.
- `hlt_slide.logo_utils`: escalado, máscara y composición del logo.
- `hlt_slide.renderer`: renderer Pillow puro con fondo, contenido, logo y selección de layout.

## Preparar entorno de desarrollo

En Windows PowerShell, desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

No instales dependencias globalmente.

## Ejecutar tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest --cov=hlt_slide
```

Pruebas por área ya disponibles:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_color_utils.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_image_fit.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_tensor_io.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_font_utils.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_text_engine.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_vertical_stack.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_renderer.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_background.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_logo_mask.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_grid_2x2.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_auto_social.py -q
```

## Validación con Python de ComfyUI

El núcleo puro se validó con el Python embebido de ComfyUI sin instalar paquetes:

- Python 3.11.8
- Pillow 10.4.0
- NumPy 1.26.4
- Torch 2.9.1+cu130

Esta validación no significa que el custom node completo esté integrado en ComfyUI.

## Instalación en ComfyUI

No instales todavía este repositorio en `custom_nodes`. La integración con ComfyUI se realizará después de validar el renderer independiente y crear la capa `nodes.py`.
