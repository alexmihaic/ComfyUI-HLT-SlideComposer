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
- Layout `grid_2x2` para una, dos, tres y cuatro imágenes.
- Selector puro `auto_social` basado en imágenes activas.
- Integración del renderer con `vertical_stack`, `grid_2x2` y `auto_social`.
- Tests unitarios de grid y auto social.
- Script de generación visual `scripts/generate_phase5_outputs.py`.
- Capa backend de ComfyUI con `HLTSlideComposer`, `nodes.py`, mappings y salida `IMAGE`.
- Conversión de entradas `IMAGE` y `MASK` para ejecutar el renderer puro desde el nodo.
- Tests de contrato del nodo y tests de ejecución marcados para Torch.
- Script `scripts/validate_node_integration.py` para validar la integración sin instalar en `custom_nodes`.
- Plan de primera prueba manual en `docs/FIRST_TEST_PLAN.md`.
- Input `contain_fill_mode` con modos `transparent` y `cell_color`.
- Relleno transparente por defecto para `image_fit="contain"`, dejando visible el fondo real del slide.
- Script de generación visual `scripts/generate_contain_transparent_outputs.py`.

### Corregido

- Corrección de imports relativos para el descubrimiento real en ComfyUI.
- Eliminación del fallback ambiguo al módulo global `nodes`.
- Nueva validación de carga como paquete mediante `scripts/validate_package_discovery.py`.
- Corrección de mojibake en los nombres canónicos de presets de resolución.
- Compatibilidad temporal con aliases antiguos de presets guardados con codificación corrupta.
- Nueva validación para comprobar que el preset predeterminado expuesto por la interfaz se puede resolver y ejecutar.
