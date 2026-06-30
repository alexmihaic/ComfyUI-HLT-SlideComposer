# HLT Text Composer

`HLT Text Composer` es la línea de trabajo prevista para añadir un segundo nodo al paquete:

```text
Internal class: HLTTextComposer
Display name: HLT · Text Composer
Category: HLT / Composition
```

El problema que resuelve es crear piezas editoriales basadas solo en texto, sin requerir imágenes de contenido. El nodo futuro debe producir un `IMAGE` de ComfyUI a partir de uno a cuatro bloques textuales, con jerarquía tipográfica, fondo y logo opcional.

## Casos de uso

- Frase editorial.
- Titular + subtitular.
- Manifiesto de tres bloques.
- Comparativa de cuatro conceptos.
- Cita + autor.
- Cartel tipográfico para stories.
- Placa técnica.
- Diseño de texto conectado desde otro nodo `STRING`.

## Relación con HLT Slide Composer

`HLT · Slide Composer` compone imágenes con textos auxiliares. `HLT · Text Composer` será un nodo complementario para piezas donde el contenido principal es texto. Ambos comparten principios: salida `IMAGE`, lienzos sociales, geometría determinista, ausencia de frontend JavaScript y separación entre core puro e integración ComfyUI.

La fase 9A no modifica el contrato público de `HLTSlideComposer`.

## Alcance de v0.3.0

La línea v0.3.0 está prevista como primera versión experimental del Text Composer. El alcance se divide en:

- Phase 9A: contrato, motor geométrico puro, diagnóstico y diagramas.
- Phase 9B: motor tipográfico para roles, ajuste de fuente y decisiones visuales.
- Phase 9C: integración como nodo ComfyUI con `INPUT_TYPES` y salida `IMAGE`.
- Phase 9D: QA visual, workflows, documentación final y validación en ComfyUI real.

## Implementado en esta rama

- Documento de visión del Text Composer.
- Borrador de contrato del futuro nodo.
- Documento de layouts textuales.
- Motor puro `hlt_slide.text_layouts`.
- Resolución de bloques activos de 1 a 4 slots.
- Roles geométricos iniciales.
- Resolución determinista de `auto_text`.
- Layouts geométricos `centered_statement`, `vertical_stack`, `split_2`, `grid_2x2` y `editorial_quote`.
- Diagnósticos legibles.
- Script de diagramas sintéticos de geometría.
- Tests unitarios y de contrato visual.
- Renderer Pillow experimental `hlt_slide.text_renderer`.
- Plan de medición `measure_text_composition`.
- Render final RGB `render_text_composition`.
- Script de renders tipográficos reales.

## Pendiente

- No existe todavía un nodo instalable `HLT · Text Composer`.
- No se registra `HLTTextComposer` en `NODE_CLASS_MAPPINGS`.
- No hay workflow de ComfyUI para Text Composer.
- No hay presets de estilo.

## Decisions made in Phase 9A

- El motor es determinista porque todos los layouts se calculan con reglas fijas, coordenadas enteras y sin aleatoriedad.
- No usa scoring porque 9A necesita un contrato predecible; la selección por puntuación queda fuera hasta que exista evidencia visual y requisitos concretos.
- No renderiza aún porque esta fase solo cierra geometría y contrato; la tipografía final requiere decisiones de 9B.
- No incorpora presets visuales porque mezclar presets con geometría dificultaría validar el contrato base.
- Los roles controlan jerarquía geométrica, pero no estilo: `headline` puede recibir más espacio que `caption`, sin decidir todavía fuente, color o tracking.
- El core se mantiene independiente de ComfyUI porque no importa `torch`, `comfy` ni `nodes`; solo usa Python y los modelos `CanvasSize` y `Rect`.

## Decisions made in Phase 9B

- Se cierran estilos base por rol para el canvas de 1080 px.
- Se usa alineación global con modo `auto`.
- Se cierran límites de líneas por rol.
- El truncado usa el comportamiento existente de `text_engine.py` y emite warning cuando corresponde.
- El clipping queda activado por defecto.
- El fondo reutiliza reglas del Slide Composer: sólido, imagen e imagen con overlay.
- El logo es opcional y puede reservar espacio antes de calcular la geometría.
- El acento se aplica al bloque completo.
- El resaltado parcial de palabras queda pospuesto.
- Los presets visuales quedan pospuestos.

## Open decisions for Phase 9C

- Orden definitivo de widgets.
- Defaults públicos exactos.
- Qué controles exponer frente a mantener internos.
- Tamaño inicial del nodo.
- Workflow público.
- Compatibilidad de widget-to-input.
- Estrategia de registro junto a `HLTSlideComposer`.
