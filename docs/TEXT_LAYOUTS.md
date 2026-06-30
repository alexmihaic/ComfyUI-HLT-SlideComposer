# Text Layouts

Los layouts de Phase 9A son geométricos. Calculan rectángulos de bloques de texto, pero no renderizan tipografía final.

Todos los layouts:

- usan coordenadas enteras;
- respetan `content_rect`;
- producen rectángulos positivos;
- evitan solapes;
- conservan el orden de las fuentes;
- escalan con el canvas real;
- son deterministas.

## Bloques activos

Un bloque está activo cuando su texto no queda vacío tras `strip()`. El texto original se conserva sin reescribir, incluidos Unicode, acentos y saltos de línea.

`source_index` conserva el slot original `0..3`, incluso cuando hay slots intermedios vacíos.

## Roles y pesos geométricos

Los pesos iniciales solo reparten espacio geométrico:

```text
number       = 1.50
headline     = 1.35
quote        = 1.25
subheadline  = 1.00
body         = 0.90
label        = 0.70
caption      = 0.60
```

No representan tamaño final de fuente. Un `headline` recibe más altura que un `caption` en `vertical_stack`, pero la tipografía queda pendiente de Phase 9B.

## auto_text

Selecciona el layout por número de bloques activos:

```text
1 bloque  -> centered_statement
2 bloques -> split_2
3 bloques -> vertical_stack
4 bloques -> grid_2x2
```

No hay scoring ni aleatoriedad en Phase 9A.

## centered_statement

Permitido: exactamente 1 bloque.

Geometría:

- rectángulo amplio y centrado;
- respeta márgenes;
- reserva padding interno;
- no ocupa obligatoriamente el 100 % del `content_rect`.

Fallback:

- si hay más de un bloque, lanza error.

## vertical_stack

Permitido: de 1 a 4 bloques.

Geometría:

- una columna;
- mantiene el orden original;
- reparte altura según pesos de rol;
- respeta `block_gap`;
- ningún bloque sale del `content_rect`.

Fallback:

- si el canvas no permite las alturas mínimas, lanza error descriptivo.

## split_2

Permitido: exactamente 2 bloques.

Geometría:

- `split_axis=auto` usa división superior/inferior en canvas vertical;
- `split_axis=auto` usa división izquierda/derecha en canvas horizontal;
- canvas cuadrado usa división superior/inferior como regla fija;
- `horizontal` fuerza izquierda/derecha;
- `vertical` fuerza superior/inferior.

Fallback:

- si no hay exactamente dos bloques, lanza error.

## grid_2x2

Permitido: de 2 a 4 bloques.

Geometría:

- dos columnas y dos filas;
- lectura estable: izquierda a derecha, arriba a abajo;
- con dos bloques ocupa la primera fila;
- con tres bloques ocupa dos celdas superiores y la celda inferior izquierda;
- con cuatro bloques usa las cuatro celdas.

Fallback:

- no reordena silenciosamente;
- si hay un solo bloque, debe usarse `centered_statement` o `auto_text`.

## editorial_quote

Permitido: 1 o 2 bloques.

Geometría:

- con un bloque, usa todo el `content_rect`;
- con dos bloques, el principal domina la composición;
- la proporción inicial es aproximadamente 78 % para el bloque principal y 22 % para el secundario incluyendo gap;
- funciona en vertical y horizontal.

Fallback:

- si hay más de dos bloques, lanza error.

## Alineación en el renderer

Phase 9B mantiene la geometría de este documento y añade reglas de renderizado:

- `centered_statement`: horizontal `center`, vertical `center`.
- `vertical_stack`: horizontal `left`, vertical `center`.
- `split_2`: horizontal `left`, vertical `center`.
- `grid_2x2`: horizontal `left`, vertical `center`.
- `editorial_quote`: bloque principal `left/center`, segundo bloque `right/bottom`.

Los overrides globales del renderer pueden sustituir estas reglas sin modificar la geometría.
