# Changelog

Todos los cambios relevantes de este proyecto se documentarán en este archivo.

## 0.1.0 - En desarrollo

### Añadido

- Estructura inicial del repositorio.
- Configuración base de proyecto y pruebas.
- Documentación inicial de Fase 0.
- Motor puro de imagen: geometría, presets, colores, ajuste de imagen y conversiones Pillow/NumPy.
- Motor puro de texto: fuentes, ajuste, reducción, truncado y dibujo centrado.
- Tests unitarios para configuración, colores, imagen, tensores, fuentes y texto.
- Salidas visuales sintéticas de Fase 1 y Fase 2 en `examples/outputs/`.
- Validación del núcleo con Python 3.11.8 y Torch 2.9.1+cu130 del entorno real de ComfyUI.
- Layout `vertical_stack` puro y renderer Pillow con fondo sólido.
- Tests unitarios de geometría vertical y renderer.
- Script de validación `scripts/validate_comfy_runtime.py`.
- Script de generación visual `scripts/generate_phase3_outputs.py`.
- Fondo de imagen con modos `solid`, `image` e `image_with_overlay`.
- Opacidad de fondo, overlay y preset `Background size`.
- Logo inferior con alpha interno, máscara externa, inversión de máscara, opacidad y escalado proporcional.
- Tests unitarios de fondo, logo y máscara.
- Script de generación visual `scripts/generate_phase4_outputs.py`.
