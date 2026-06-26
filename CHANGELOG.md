# Changelog

Todos los cambios relevantes de este proyecto se documentarÃ¡n en este archivo.

## 0.1.0 - En desarrollo

### AÃ±adido

- Estructura inicial del repositorio.
- ConfiguraciÃ³n base de proyecto y pruebas.
- DocumentaciÃ³n inicial de Fase 0.
- Motor puro de imagen: geometrÃ­a, presets, colores, ajuste de imagen y conversiones Pillow/NumPy.
- Motor puro de texto: fuentes, ajuste, reducciÃ³n, truncado y dibujo centrado.
- Tests unitarios para configuraciÃ³n, colores, imagen, tensores, fuentes y texto.
- Salidas visuales sintÃ©ticas de Fase 1 y Fase 2 en `examples/outputs/`.
- ValidaciÃ³n del nÃºcleo con Python 3.11.8 y Torch 2.9.1+cu130 del entorno real de ComfyUI.
- Layout `vertical_stack` puro y renderer Pillow con fondo sÃ³lido.
- Tests unitarios de geometrÃ­a vertical y renderer.
- Script de validaciÃ³n `scripts/validate_comfy_runtime.py`.
- Script de generaciÃ³n visual `scripts/generate_phase3_outputs.py`.
