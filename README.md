# HLT Slide Composer para ComfyUI

`HLT Â· Slide Composer` serÃ¡ un custom node de ComfyUI para componer entre una y cuatro imÃ¡genes dentro de un slide editorial, principalmente vertical 9:16, con tÃ­tulo, etiquetas, fondo y logo opcional.

La fuente de verdad funcional, visual y tÃ©cnica del proyecto es `MASTER_SPEC.md`.

## Estado actual

Este repositorio tiene completadas estas fases del motor puro:

- Fase 1: geometrÃ­a, presets, colores, ajuste de imagen y conversiÃ³n Pillow/NumPy.
- Fase 2: resoluciÃ³n de fuentes, ajuste de texto y dibujo centrado.
- Fase 3: layout `vertical_stack` y renderer Pillow con fondo sÃ³lido.

TodavÃ­a no estÃ¡ listo para instalarse ni usarse dentro de ComfyUI. No existe aÃºn `nodes.py`, logo real, fondo de imagen, `grid_2x2`, `auto_social` ni workflow de ComfyUI.

## Problema que resolverÃ¡

El nodo evitarÃ¡ tener que construir manualmente un slide con varios nodos de resize, crop, composite, texto, mÃ¡scara y preview. La versiÃ³n `0.1.0` debe producir una Ãºnica salida `IMAGE` lista para previsualizar o guardar desde ComfyUI.

## Alcance previsto de 0.1.0

- Una entrada obligatoria `image_1`.
- Hasta tres imÃ¡genes opcionales adicionales.
- TÃ­tulo superior y etiquetas debajo de cada imagen.
- Fondo sÃ³lido o imagen de fondo.
- Logo externo opcional centrado abajo.
- Layouts `vertical_stack`, `grid_2x2` y `auto_social`.
- Ajustes de imagen `cover`, `contain` y `stretch`.
- Salida ComfyUI `IMAGE` en formato `[B, H, W, C]`, `float32`, rango `0.0-1.0`.
- Renderer basado en Pillow, probado fuera de ComfyUI.

`background_blur` queda fuera de la versiÃ³n `0.1.0` y se documenta como posible mejora futura.

## Arquitectura general

El proyecto separa el motor puro de composiciÃ³n de la integraciÃ³n con ComfyUI:

- `hlt_slide/`: paquete Python puro, sin imports de ComfyUI.
- `tests/`: pruebas automatizadas del paquete y, mÃ¡s adelante, del contrato del nodo.
- `docs/`: documentaciÃ³n tÃ©cnica y decisiones de implementaciÃ³n.
- `examples/`: workflows y salidas visuales generadas durante la validaciÃ³n.
- `scripts/`: scripts locales de validaciÃ³n y generaciÃ³n visual.

En fases posteriores, `nodes.py` serÃ¡ solo la capa de adaptaciÃ³n a ComfyUI: definirÃ¡ inputs, convertirÃ¡ tensores, llamarÃ¡ al renderer y devolverÃ¡ el tensor final.

## MÃ³dulos disponibles

- `hlt_slide.config`: modelos de geometrÃ­a y resoluciÃ³n.
- `hlt_slide.color_utils`: parseo tolerante de colores HEX.
- `hlt_slide.image_utils`: ajuste de imÃ¡genes con `cover`, `contain` y `stretch`.
- `hlt_slide.tensor_io`: conversiones Pillow/NumPy y adaptaciÃ³n diferida a Torch.
- `hlt_slide.font_utils`: bÃºsqueda y cache de fuentes.
- `hlt_slide.text_engine`: ajuste y dibujo centrado de texto.
- `hlt_slide.layouts`: geometrÃ­a pura de `vertical_stack`.
- `hlt_slide.renderer`: renderer Pillow puro con fondo sÃ³lido.

## Preparar entorno de desarrollo

En Windows PowerShell, desde la raÃ­z del repositorio:

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

Pruebas por Ã¡rea ya disponibles:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_color_utils.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_image_fit.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_tensor_io.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_font_utils.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_text_engine.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_vertical_stack.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_renderer.py -q
```

## ValidaciÃ³n con Python de ComfyUI

El nÃºcleo puro de Fase 1 y Fase 2 se validÃ³ con el Python embebido de ComfyUI sin instalar paquetes:

- Python 3.11.8
- Pillow 10.4.0
- NumPy 1.26.4
- Torch 2.9.1+cu130

Esta validaciÃ³n no significa que el custom node completo estÃ© integrado en ComfyUI.

## InstalaciÃ³n en ComfyUI

No instales todavÃ­a este repositorio en `custom_nodes`. La integraciÃ³n con ComfyUI se realizarÃ¡ despuÃ©s de validar el renderer independiente y crear la capa `nodes.py`.
