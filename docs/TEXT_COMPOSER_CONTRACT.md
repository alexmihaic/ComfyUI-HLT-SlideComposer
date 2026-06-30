# Text Composer Contract

Este documento propone el contrato futuro del nodo. Es un borrador hasta Phase 9C.

```text
Internal class: HLTTextComposer
Display name: HLT · Text Composer
Category: HLT / Composition
Output: IMAGE
```

Phase 9A no registra este nodo en ComfyUI.

## Entradas textuales futuras

```text
text_1
text_2
text_3
text_4
```

Las entradas deben plantearse como widgets estándar `STRING` multilínea. Deben seguir siendo compatibles con la conversión normal de widget a input de ComfyUI. No se implementa `forceInput`, JavaScript ni frontend personalizado en esta fase.

## Roles candidatos

```text
headline
subheadline
body
quote
caption
number
label
```

Defaults propuestos:

```text
text_1_role = headline
text_2_role = subheadline
text_3_role = body
text_4_role = caption
```

Los roles definen jerarquía y reparto geométrico inicial. No fijan todavía estilo visual final.

## Layouts iniciales

```text
auto_text
centered_statement
vertical_stack
split_2
grid_2x2
editorial_quote
```

`auto_text` se resuelve de forma determinista por número de bloques activos:

```text
1 bloque  -> centered_statement
2 bloques -> split_2
3 bloques -> vertical_stack
4 bloques -> grid_2x2
```

## Entradas visuales opcionales futuras

```text
background_image
logo_image
logo_mask
```

No se añade una salida separada para warnings en el MVP. Las advertencias futuras usarán el sistema estándar de Python con prefijo:

```text
[HLT Text Composer]
```

## Orden conceptual de widgets

Borrador hasta Phase 9C:

```text
1. text_1 .. text_4
2. canvas
3. layout
4. roles
5. background
6. text colors and accent
7. typography
8. alignment and casing
9. spacing
10. logo
11. debug
```

No se añaden presets de estilo en Phase 9A. Quedan para una fase posterior.

## Compatibilidad esperada

- La salida futura será `IMAGE`.
- El batch inicial será un único frame.
- El core geométrico debe poder probarse con Python puro.
- La integración futura debe mantener separadas las capas core, Pillow, Torch y ComfyUI.
- El contrato de `HLTSlideComposer` no debe cambiar por este nodo.
