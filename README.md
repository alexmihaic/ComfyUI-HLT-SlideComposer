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
- Fase 6A: capa backend de integración ComfyUI dentro del repositorio.

Todavía no se ha instalado físicamente en ComfyUI ni se ha validado durante el arranque real de ComfyUI. No existe aún un workflow JSON exportado desde ComfyUI.

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
- Modo `contain_fill_mode`: `transparent` deja visible el fondo del slide en las bandas de `contain`; `cell_color` conserva el relleno sólido con `cell_background_color`.
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
En el estado actual, `nodes.py` ya existe como capa fina de backend y mantiene la lógica visual dentro de `hlt_slide/`.

## Módulos disponibles

- `hlt_slide.config`: modelos de geometría y resolución.
- `hlt_slide.color_utils`: parseo tolerante de colores HEX.
- `hlt_slide.image_utils`: ajuste de imágenes con `cover`, `contain`, `stretch` y relleno transparente opcional para `contain`.
- `hlt_slide.tensor_io`: conversiones Pillow/NumPy y adaptación diferida a Torch.
- `hlt_slide.font_utils`: búsqueda y cache de fuentes.
- `hlt_slide.text_engine`: ajuste y dibujo centrado de texto.
- `hlt_slide.layouts`: geometría pura de `vertical_stack`, `grid_2x2` y `auto_social`.
- `hlt_slide.logo_utils`: escalado, máscara y composición del logo.
- `hlt_slide.renderer`: renderer Pillow puro con fondo, contenido, logo y selección de layout.
- `nodes.py`: integración ComfyUI, conversión de `IMAGE`/`MASK`, mappings y contrato del nodo.

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
.\.venv\Scripts\python.exe -m pytest tests/test_node_contract.py -q
```

## Validación con Python de ComfyUI

El núcleo puro se validó con el Python embebido de ComfyUI sin instalar paquetes:

- Python 3.11.8
- Pillow 10.4.0
- NumPy 1.26.4
- Torch 2.9.1+cu130

La capa backend del nodo también se valida sin instalar el plugin mediante:

```powershell
$ComfyPython = "C:\IAstuff\STUDIO344\App\python_embeded\python.exe"
& $ComfyPython scripts\validate_node_integration.py
```

Esta validación no sustituye la prueba de arranque real de ComfyUI con el nodo instalado.

## Instalación en ComfyUI

No se ha ejecutado todavía ninguna instalación en `custom_nodes`.

Método recomendado actual, para ejecutar manualmente en la siguiente fase:

```powershell
cd C:\IAstuff\STUDIO344\App\ComfyUI\custom_nodes
git clone https://github.com/alexmihaic/ComfyUI-HLT-SlideComposer.git
```

Si Pillow y NumPy ya están presentes en el Python de ComfyUI con versiones compatibles, no ejecutes `pip install`.

Después:

1. reiniciar ComfyUI;
2. revisar la consola;
3. buscar `HLT · Slide Composer`;
4. ejecutar el plan de primera prueba en `docs/FIRST_TEST_PLAN.md`.

## Desinstalación o rollback

1. cerrar ComfyUI;
2. borrar la carpeta `ComfyUI-HLT-SlideComposer`, o renombrarla con sufijo `.disabled`;
3. reiniciar ComfyUI.
