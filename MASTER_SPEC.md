# HLT Slide Composer para ComfyUI
## Documento maestro de producto, arquitectura e implementación para Codex

**Nombre provisional del repositorio:** `ComfyUI-HLT-SlideComposer`  
**Nombre visible del nodo:** `HLT · Slide Composer`  
**Clase Python propuesta:** `HLTSlideComposer`  
**Categoría en ComfyUI:** `HLT / Composition`  
**Versión objetivo inicial:** `0.1.0`  
**Estado:** especificación lista para implementación  
**Plataforma prioritaria:** ComfyUI en Windows  
**Compatibilidad deseada:** Windows, Linux y macOS  
**Salida principal:** `IMAGE`

---

# 1. Objetivo

Crear un nodo personalizado para ComfyUI capaz de componer entre una y cuatro imágenes dentro de una pieza editorial vertical, principalmente en formato 9:16.

El nodo debe generar un slide final listo para:

- previsualizar dentro de ComfyUI;
- guardar como imagen;
- compartir en stories o reels;
- documentar referencias, procesos y resultados;
- comparar `ref0`, `ref1` y resultado;
- presentar variaciones visuales;
- crear hojas rápidas de campaña o de producción.

La composición principal debe usar:

- fondo negro;
- textos rojos HLT;
- título superior opcional;
- hasta cuatro imágenes;
- etiqueta centrada debajo de cada imagen;
- logo inferior opcional;
- márgenes y espacios consistentes;
- proporción 9:16;
- resultado determinista.

El nodo debe permitir cambiar los colores, utilizar una imagen como fondo y seleccionar varios layouts sin quedar bloqueado exclusivamente al sistema visual de HAZ LO TUYO.

---

# 2. Problema que resuelve

Actualmente existen nodos de tipo reel, collage, contact sheet, grid o compositor, pero no hay una solución sencilla que reúna en un único nodo:

1. un lienzo social con tamaño fijo;
2. una estructura editorial ordenada;
3. entre una y cuatro imágenes opcionales;
4. un texto asociado a cada imagen;
5. un título general;
6. un logo inferior;
7. fondo sólido o fondo fotográfico;
8. varios layouts previsibles;
9. ajuste automático de imágenes y textos;
10. salida directa como `IMAGE`.

El usuario no debe construir manualmente el slide con muchos nodos de resize, crop, composite, text y mask. El nodo debe encargarse de todo el cálculo de composición.

---

# 3. Resultado esperado

Ejemplo conceptual del layout principal:

```text
┌────────────────────────────────────┐
│                                    │
│              TÍTULO                │
│                                    │
│  ┌──────────────────────────────┐  │
│  │           IMAGEN 1           │  │
│  └──────────────────────────────┘  │
│             etiqueta 1             │
│                                    │
│  ┌──────────────────────────────┐  │
│  │           IMAGEN 2           │  │
│  └──────────────────────────────┘  │
│             etiqueta 2             │
│                                    │
│  ┌──────────────────────────────┐  │
│  │           IMAGEN 3           │  │
│  └──────────────────────────────┘  │
│             etiqueta 3             │
│                                    │
│                LOGO                │
│                                    │
└────────────────────────────────────┘
```

La cantidad de bloques debe adaptarse automáticamente al número de imágenes conectadas. No deben reservarse huecos para entradas vacías.

---

# 4. Principios de diseño

## 4.1. Simplicidad

La primera versión debe funcionar solo con Python. No debe requerir una extensión JavaScript de frontend.

## 4.2. Determinismo

Con las mismas entradas y valores, el resultado debe ser siempre idéntico.

## 4.3. Modularidad

El motor de composición debe funcionar fuera de ComfyUI para poder probarlo con Pillow y `pytest`.

## 4.4. Robustez

Una entrada vacía, un texto largo, un logo sin máscara o un color incorrecto no deben cerrar ComfyUI.

## 4.5. Personalización controlada

Debe ofrecer suficientes opciones útiles sin convertirse en un compositor gráfico generalista.

## 4.6. Defaults HLT, uso universal

Los valores predeterminados deben representar el sistema visual HLT, pero todos los colores y recursos deben ser sustituibles.

---

# 5. Alcance de la versión 0.1.0

La primera versión funcional debe incluir:

- una entrada obligatoria `image_1`;
- tres entradas opcionales `image_2`, `image_3` e `image_4`;
- título general;
- cuatro etiquetas opcionales;
- entrada opcional de logo;
- entrada opcional de máscara de logo;
- entrada opcional de imagen de fondo;
- fondos mediante color HEX;
- tema HLT predeterminado;
- formatos 9:16, 4:5, 3:4, 1:1 y personalizado;
- layout `vertical_stack`;
- layout `grid_2x2`;
- layout `auto_social`;
- modos `cover`, `contain` y `stretch`;
- recorte vertical `top`, `center` y `bottom`;
- ajuste automático de textos;
- borde y radio de esquinas;
- opacidad de fondo fotográfico;
- overlay de color sobre el fondo;
- escalado proporcional del logo;
- salida `IMAGE`;
- pruebas automatizadas;
- workflow de ejemplo;
- documentación de instalación y uso.

---

# 6. Fuera de alcance en la versión inicial

No implementar todavía:

- editor visual mediante arrastre;
- controles gráficos de color en JavaScript;
- posiciones manuales independientes por imagen;
- rotaciones;
- sombras complejas;
- animación;
- vídeo;
- exportación directa a archivo desde el propio nodo;
- selección automática de fuentes mediante interfaz;
- textos enriquecidos;
- Markdown dentro de las etiquetas;
- múltiples logos;
- composición libre tipo Photoshop;
- procesamiento GPU;
- sincronización con plantillas externas;
- importación de PSD, SVG o Figma;
- generación automática de copies;
- traducción automática;
- lectura OCR;
- procesamiento avanzado de lotes en la versión 0.1.0.

---

# 7. Interfaz del nodo

## 7.1. Entradas obligatorias

| Campo | Tipo | Valor predeterminado | Descripción |
|---|---:|---:|---|
| `image_1` | `IMAGE` | obligatorio | Primera imagen y única entrada visual obligatoria. |
| `canvas_preset` | lista | `9:16 Social · 1080x1920` | Tamaño del lienzo. |
| `layout` | lista | `vertical_stack` | Sistema de composición. |
| `background_color` | `STRING` | `#000000` | Fondo sólido y color de overlay. |
| `title` | `STRING multiline` | vacío | Título general. |
| `title_color` | `STRING` | `#E92124` | Color del título. |
| `label_color` | `STRING` | `#E92124` | Color de las etiquetas. |
| `image_fit` | lista | `cover` | Ajuste de imágenes dentro de sus cajas. |
| `crop_anchor` | lista | `center` | Prioridad vertical del recorte. |

## 7.2. Entradas opcionales de imagen

| Campo | Tipo | Descripción |
|---|---:|---|
| `image_2` | `IMAGE` | Segunda imagen. |
| `image_3` | `IMAGE` | Tercera imagen. |
| `image_4` | `IMAGE` | Cuarta imagen. |
| `background_image` | `IMAGE` | Fondo fotográfico o textura. |
| `logo_image` | `IMAGE` | Logo que se colocará en el pie. |
| `logo_mask` | `MASK` | Máscara opcional para recuperar la transparencia del PNG. |

## 7.3. Textos

| Campo | Tipo | Valor predeterminado |
|---|---:|---:|
| `label_1` | `STRING multiline` | vacío |
| `label_2` | `STRING multiline` | vacío |
| `label_3` | `STRING multiline` | vacío |
| `label_4` | `STRING multiline` | vacío |
| `uppercase_title` | `BOOLEAN` | `true` |
| `uppercase_labels` | `BOOLEAN` | `false` |
| `max_label_lines` | `INT` | `2` |

## 7.4. Tipografía

| Campo | Tipo | Valor predeterminado | Rango |
|---|---:|---:|---:|
| `font_path` | `STRING` | vacío | ruta opcional |
| `title_font_size` | `INT` | `64` | 12–240 |
| `label_font_size` | `INT` | `34` | 10–160 |
| `minimum_font_size` | `INT` | `18` | 8–80 |
| `line_spacing` | `INT` | `8` | 0–50 |

Cuando `font_path` esté vacío, el nodo debe buscar una fuente segura del sistema.

Orden de búsqueda propuesto:

### Windows

```text
C:\Windows\Fonts\arialbd.ttf
C:\Windows\Fonts\arial.ttf
C:\Windows\Fonts\segoeuib.ttf
C:\Windows\Fonts\segoeui.ttf
```

### Linux

```text
/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
```

### macOS

```text
/System/Library/Fonts/Supplemental/Arial Bold.ttf
/System/Library/Fonts/Supplemental/Arial.ttf
```

Si ninguna fuente TrueType está disponible, usar `ImageFont.load_default()` y generar una advertencia clara sin abortar.

## 7.5. Geometría

| Campo | Tipo | Predeterminado | Rango |
|---|---:|---:|---:|
| `outer_margin` | `INT` | `64` | 0–300 |
| `top_margin` | `INT` | `60` | 0–300 |
| `bottom_margin` | `INT` | `54` | 0–300 |
| `title_gap` | `INT` | `36` | 0–160 |
| `block_gap` | `INT` | `30` | 0–160 |
| `image_label_gap` | `INT` | `14` | 0–100 |
| `corner_radius` | `INT` | `18` | 0–160 |
| `border_width` | `INT` | `0` | 0–40 |
| `border_color` | `STRING` | `#E92124` | HEX |
| `inner_padding` | `INT` | `0` | 0–100 |

Los valores deben escalar proporcionalmente cuando el lienzo no sea 1080 × 1920.

La referencia para todos los valores absolutos será un ancho base de 1080 píxeles:

```python
scale = canvas_width / 1080.0
scaled_value = round(base_value * scale)
```

## 7.6. Fondo

| Campo | Tipo | Predeterminado |
|---|---:|---:|
| `background_mode` | lista | `solid` |
| `background_fit` | lista | `cover` |
| `background_opacity` | `FLOAT` | `1.0` |
| `overlay_opacity` | `FLOAT` | `0.0` |
| `background_blur` | `FLOAT` | `0.0` |

Valores de `background_mode`:

```text
solid
image
image_with_overlay
```

Valores de `background_fit`:

```text
cover
contain
stretch
```

Reglas:

1. Si no existe `background_image`, usar siempre `background_color`.
2. Si existe `background_image` y `background_mode=image`, dibujarla con su opacidad.
3. Si existe `background_image` y `background_mode=image_with_overlay`, dibujarla y aplicar después `background_color` con `overlay_opacity`.
4. `background_blur` puede quedar implementado desde la versión 0.1.0 si no complica el motor. Si se retrasa, debe documentarse.

## 7.7. Logo

| Campo | Tipo | Predeterminado | Rango |
|---|---:|---:|---:|
| `logo_width_percent` | `FLOAT` | `18.0` | 2–80 |
| `logo_opacity` | `FLOAT` | `1.0` | 0–1 |
| `logo_bottom_offset` | `INT` | `0` | -200–400 |
| `logo_max_height_percent` | `FLOAT` | `8.0` | 1–30 |
| `invert_logo_mask` | `BOOLEAN` | `true` | — |

Reglas:

- mantener siempre la proporción del logo;
- centrarlo horizontalmente;
- no deformarlo;
- no dibujar nada si no se conecta `logo_image`;
- aplicar la máscara si existe;
- permitir usar logos opacos sin máscara;
- no incrustar ningún logo HLT dentro del código;
- no distribuir recursos de marca dentro del repositorio salvo autorización explícita.

## 7.8. Resolución personalizada

| Campo | Tipo | Predeterminado |
|---|---:|---:|
| `custom_width` | `INT` | `1080` |
| `custom_height` | `INT` | `1920` |

Solo se usan cuando `canvas_preset=Custom`.

Rango recomendado:

```text
width: 256–8192
height: 256–8192
```

---

# 8. Presets de resolución

Implementar exactamente estos valores:

| Nombre visible | Anchura | Altura | Uso |
|---|---:|---:|---|
| `9:16 Social · 1080x1920` | 1080 | 1920 | Stories y reels. |
| `9:16 AI · 1152x2048` | 1152 | 2048 | Resolución amigable para procesos de IA. |
| `9:16 4K · 2160x3840` | 2160 | 3840 | Exportación de alta resolución. |
| `4:5 Social · 1080x1350` | 1080 | 1350 | Feed vertical. |
| `3:4 Editorial · 1536x2048` | 1536 | 2048 | Posters y piezas editoriales. |
| `1:1 Square · 1080x1080` | 1080 | 1080 | Cuadrado. |
| `Custom` | manual | manual | Tamaño definido por el usuario. |
| `Background size` | fondo | fondo | Usa la resolución de `background_image`. |

Si se selecciona `Background size` sin conectar una imagen de fondo, usar 1080 × 1920 y emitir advertencia.

---

# 9. Layouts

## 9.1. `vertical_stack`

Layout principal.

Características:

- una columna;
- entre uno y cuatro bloques;
- cada bloque contiene imagen y etiqueta;
- todas las cajas visuales tienen el mismo ancho;
- el alto se reparte automáticamente;
- no se reservan bloques vacíos;
- el título ocupa una zona superior;
- el logo ocupa una zona inferior.

Orden:

```text
title
image_1
label_1
image_2
label_2
image_3
label_3
image_4
label_4
logo
```

### Distribución vertical

El motor debe:

1. calcular el área útil del lienzo;
2. restar título y su separación si el título no está vacío;
3. restar la altura reservada para el logo si existe;
4. restar los huecos entre bloques;
5. restar el espacio previsto para etiquetas;
6. dividir el espacio restante entre las imágenes conectadas.

No usar alturas fijas para las cajas de imagen.

### Altura mínima

Si el número de imágenes o el texto hacen que cada caja sea demasiado pequeña:

1. reducir primero el tamaño de las etiquetas;
2. reducir `block_gap` hasta un mínimo razonable;
3. reducir `image_label_gap`;
4. reducir la altura de imagen;
5. no permitir valores negativos;
6. si aun así no cabe, lanzar un error descriptivo indicando qué elementos provocan el desbordamiento.

## 9.2. `grid_2x2`

Diseñado principalmente para cuatro imágenes.

Reglas:

- una imagen: una celda completa;
- dos imágenes: dos columnas;
- tres imágenes: una celda superior completa y dos inferiores;
- cuatro imágenes: cuadrícula 2 × 2;
- cada etiqueta se mantiene debajo de su imagen;
- el título sigue arriba;
- el logo sigue abajo.

Para tres imágenes:

```text
┌────────────────────────────┐
│          IMAGEN 1          │
│          etiqueta 1        │
├─────────────┬──────────────┤
│  IMAGEN 2   │   IMAGEN 3   │
│ etiqueta 2  │  etiqueta 3  │
└─────────────┴──────────────┘
```

## 9.3. `auto_social`

Selecciona automáticamente el layout:

| Número de imágenes | Layout interno |
|---:|---|
| 1 | hero vertical |
| 2 | vertical stack |
| 3 | vertical stack |
| 4 | grid 2 × 2 |

El usuario debe poder elegir manualmente otro layout.

## 9.4. `comparison`

Puede añadirse en la versión 0.2.0.

Objetivo:

- dos o tres imágenes;
- comparativa clara;
- etiquetas como `REF0`, `REF1`, `RESULTADO`;
- celdas de tamaño equivalente;
- posibilidad de disposición vertical u horizontal.

No bloquear la arquitectura de layouts para poder incorporarlo después.

## 9.5. `hero_stack`

Puede añadirse en la versión 0.2.0.

La primera imagen ocupa aproximadamente el 45–55 % del área de contenido y las restantes se distribuyen en el espacio inferior.

---

# 10. Detección de imágenes activas

La lista de imágenes activas se construirá en este orden:

```python
[
    (image_1, label_1),
    (image_2, label_2),
    (image_3, label_3),
    (image_4, label_4),
]
```

Reglas:

- `image_1` siempre debe existir;
- las entradas opcionales `None` se eliminan;
- no se altera el orden;
- una etiqueta vacía no elimina la imagen;
- una imagen desconectada elimina también su etiqueta de la composición;
- no dejar huecos por imágenes ausentes.

Ejemplo:

```text
image_1 conectada
image_2 desconectada
image_3 conectada
image_4 desconectada
```

Resultado:

```text
bloque 1 = image_1 + label_1
bloque 2 = image_3 + label_3
```

---

# 11. Tratamiento de imágenes

## 11.1. Conversión de tensor

ComfyUI entrega imágenes como tensores:

```text
[B, H, W, C]
```

Valores esperados:

```text
float32
rango 0.0–1.0
canales RGB
```

El motor debe:

1. tomar el frame correspondiente;
2. limitar valores a 0–1;
3. multiplicar por 255;
4. convertir a `uint8`;
5. crear una imagen Pillow RGB;
6. componer;
7. convertir el resultado a NumPy;
8. normalizar a 0–1;
9. convertir a tensor `float32`;
10. devolver `[B, H, W, C]`.

## 11.2. Modos de ajuste

### `cover`

- rellena toda la caja;
- mantiene proporción;
- recorta el sobrante;
- utiliza `crop_anchor`.

### `contain`

- muestra la imagen completa;
- mantiene proporción;
- puede dejar bandas;
- las bandas deben usar `cell_background_color`.

Añadir el campo:

```text
cell_background_color = #111111
```

### `stretch`

- fuerza la imagen al tamaño de la caja;
- puede deformarla;
- debe estar disponible, pero nunca como valor predeterminado.

## 11.3. Anclaje de recorte

Valores:

```text
top
center
bottom
```

Para `cover`:

- `top`: conserva la parte superior;
- `center`: recorte equilibrado;
- `bottom`: conserva la parte inferior.

Preparar el código para poder añadir en el futuro:

```text
left
right
custom_x
custom_y
```

## 11.4. Interpolación

Usar:

```python
Image.Resampling.LANCZOS
```

Evitar redimensionados de baja calidad.

## 11.5. Esquinas redondeadas

Para aplicar `corner_radius`:

1. crear máscara `L`;
2. dibujar rectángulo redondeado;
3. aplicar la máscara a la imagen;
4. pegarla sobre el lienzo;
5. dibujar después el borde si `border_width > 0`.

## 11.6. Bordes

- se dibujan por fuera o centrados sobre el perímetro sin invadir excesivamente la imagen;
- respetan las esquinas redondeadas;
- el borde puede desactivarse con ancho cero;
- el color se valida como HEX.

---

# 12. Motor de texto

## 12.1. Objetivo

Evitar que los textos salgan de su caja o queden cortados.

## 12.2. Reglas generales

- medir siempre con `ImageDraw.textbbox`;
- alinear al centro;
- usar anclajes calculados, no posiciones estimadas;
- respetar salto de línea manual;
- permitir ajuste automático por palabras;
- reducir el tamaño de fuente si es necesario;
- truncar con puntos suspensivos solo como último recurso.

## 12.3. Algoritmo de ajuste

Función propuesta:

```python
fit_text(
    text: str,
    font_path: str | None,
    preferred_size: int,
    minimum_size: int,
    max_width: int,
    max_height: int,
    max_lines: int,
    line_spacing: int,
) -> FittedText
```

Proceso:

1. limpiar espacios redundantes;
2. conservar saltos de línea explícitos;
3. probar el tamaño preferido;
4. envolver por palabras;
5. comprobar ancho, alto y número de líneas;
6. reducir un punto y repetir;
7. detenerse al encontrar un tamaño válido;
8. si se alcanza el mínimo, truncar la última línea;
9. añadir `…`;
10. devolver líneas, fuente, tamaño y caja.

## 12.4. Título

- máximo recomendado: dos líneas;
- por defecto en mayúsculas;
- centrado;
- no reservar altura cuando esté vacío;
- color independiente;
- tamaño mínimo independiente si fuese necesario en el futuro.

## 12.5. Etiquetas

- máximo predeterminado: dos líneas;
- centradas;
- pueden estar vacías;
- su altura real debe participar en el cálculo del layout;
- no forzar todas las etiquetas a tener el mismo número de líneas;
- mantener alineación visual entre celdas del grid.

## 12.6. Sombra y fondo de texto

No necesarios en 0.1.0.

Preparar la arquitectura para:

- sombra;
- caja de texto;
- fondo semitransparente;
- stroke.

---

# 13. Fondo fotográfico

Cuando exista `background_image`:

1. convertir el primer frame a Pillow;
2. ajustarlo al lienzo según `background_fit`;
3. aplicar blur si procede;
4. aplicar `background_opacity`;
5. pegar sobre el color de fondo;
6. aplicar overlay si procede;
7. componer encima imágenes, textos y logo.

El fondo nunca debe alterar el tamaño final del lienzo salvo cuando se use `Background size`.

---

# 14. Tratamiento del logo y la máscara

## 14.1. Entrada sin máscara

Si solo se conecta `logo_image`:

- tratarlo como RGB opaco;
- escalar proporcionalmente;
- aplicar `logo_opacity`;
- pegarlo centrado.

## 14.2. Entrada con máscara

ComfyUI puede entregar la máscara del canal alfa invertida respecto a una máscara de opacidad convencional.

Por eso se incluye:

```text
invert_logo_mask = true
```

Algoritmo:

```python
alpha = mask
if invert_logo_mask:
    alpha = 1.0 - alpha
```

Después:

- limitar a 0–1;
- redimensionar con Lanczos;
- combinar con `logo_opacity`;
- convertir a canal alfa `L`;
- pegar el logo con esa máscara.

## 14.3. Escala del logo

El ancho máximo será:

```python
canvas_width * logo_width_percent / 100
```

El alto máximo será:

```python
canvas_height * logo_max_height_percent / 100
```

Escalar para que cumpla ambos límites sin cambiar proporción.

---

# 15. Política de batch

## 15.1. Versión 0.1.0

Usar solo el primer elemento de cada entrada `IMAGE`.

Comportamiento:

```python
image_tensor[0]
```

Si una entrada contiene más de una imagen, registrar una advertencia:

```text
HLT Slide Composer 0.1.0 usa el primer frame de cada batch.
```

La salida será un batch de una sola imagen:

```text
[1, H, W, 3]
```

## 15.2. Versión futura

Añadir:

```text
batch_mode:
- first_only
- zip
- repeat_singletons
```

No implementar en 0.1.0 salvo que todas las pruebas básicas estén terminadas.

---

# 16. Validación de colores

Aceptar:

```text
#RGB
#RRGGBB
#RRGGBBAA
RGB
RRGGBB
```

Normalizar internamente.

En caso de valor inválido:

- usar el valor predeterminado correspondiente;
- emitir advertencia;
- no abortar.

Función propuesta:

```python
parse_color(value: str, fallback: tuple[int, int, int, int]) -> tuple[int, int, int, int]
```

---

# 17. Arquitectura del repositorio

```text
ComfyUI-HLT-SlideComposer/
│
├── __init__.py
├── nodes.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── AGENTS.md
├── LICENSE
├── CHANGELOG.md
│
├── hlt_slide/
│   ├── __init__.py
│   ├── config.py
│   ├── renderer.py
│   ├── layouts.py
│   ├── text_engine.py
│   ├── image_utils.py
│   ├── color_utils.py
│   ├── tensor_io.py
│   ├── font_utils.py
│   └── exceptions.py
│
├── tests/
│   ├── conftest.py
│   ├── test_color_utils.py
│   ├── test_tensor_io.py
│   ├── test_image_fit.py
│   ├── test_text_engine.py
│   ├── test_vertical_stack.py
│   ├── test_grid_2x2.py
│   ├── test_logo_mask.py
│   ├── test_background.py
│   └── test_node_contract.py
│
├── examples/
│   ├── workflows/
│   │   └── HLT_Slide_Composer_Example.json
│   └── outputs/
│       └── .gitkeep
│
└── docs/
    ├── IMPLEMENTATION.md
    ├── LAYOUTS.md
    ├── REFERENCES.md
    └── references/
        └── README.md
```

---

# 18. Responsabilidad de cada módulo

## `nodes.py`

Debe contener únicamente:

- definición de inputs;
- definición de outputs;
- llamada al renderer;
- registro de la clase;
- conversión mínima de parámetros.

No debe incluir algoritmos largos de composición.

## `config.py`

- dataclasses de configuración;
- presets de resolución;
- valores predeterminados;
- enumeraciones internas;
- validación básica.

## `renderer.py`

- coordina todo el proceso;
- crea lienzo;
- llama al layout;
- compone fondo;
- compone imágenes;
- compone textos;
- compone logo;
- devuelve Pillow.

## `layouts.py`

- calcula cajas;
- no dibuja;
- devuelve coordenadas;
- contiene `vertical_stack`, `grid_2x2` y `auto_social`.

Estructuras propuestas:

```python
@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

@dataclass(frozen=True)
class BlockLayout:
    image_rect: Rect
    label_rect: Rect

@dataclass(frozen=True)
class SlideLayout:
    title_rect: Rect | None
    blocks: list[BlockLayout]
    logo_rect: Rect | None
```

## `text_engine.py`

- ajuste de línea;
- medición;
- reducción de fuente;
- truncado;
- dibujo centrado.

## `image_utils.py`

- cover;
- contain;
- stretch;
- crop;
- rounded mask;
- bordes;
- blur;
- escalado proporcional.

## `color_utils.py`

- parseo HEX;
- normalización;
- alpha;
- fallbacks.

## `tensor_io.py`

- tensor a Pillow;
- Pillow a tensor;
- máscara a Pillow;
- validación de shape.

## `font_utils.py`

- resolver ruta;
- cargar fuente;
- fallback multiplataforma;
- cachear fuentes.

## `exceptions.py`

Excepciones claras:

```python
class HLTSlideError(Exception):
    pass

class LayoutOverflowError(HLTSlideError):
    pass

class InvalidTensorError(HLTSlideError):
    pass
```

---

# 19. Contrato del nodo ComfyUI

Estructura orientativa:

```python
class HLTSlideComposer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_1": ("IMAGE",),
                "canvas_preset": (...,),
                "layout": (...,),
                "background_color": ("STRING", {"default": "#000000"}),
                "title": ("STRING", {"multiline": True, "default": ""}),
                "title_color": ("STRING", {"default": "#E92124"}),
                "label_color": ("STRING", {"default": "#E92124"}),
                "image_fit": (["cover", "contain", "stretch"],),
                "crop_anchor": (["top", "center", "bottom"],),
            },
            "optional": {
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "background_image": ("IMAGE",),
                "logo_image": ("IMAGE",),
                "logo_mask": ("MASK",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("slide",)
    FUNCTION = "compose"
    CATEGORY = "HLT / Composition"
```

Registro:

```python
NODE_CLASS_MAPPINGS = {
    "HLTSlideComposer": HLTSlideComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HLTSlideComposer": "HLT · Slide Composer",
}
```

`__init__.py` debe exportar ambos mappings.

---

# 20. Rendimiento

## Objetivo

La composición 1080 × 1920 con cuatro imágenes debe tardar habitualmente menos de un segundo en una CPU moderna, excluyendo carga desde disco.

## Reglas

- no copiar tensores innecesariamente;
- convertir cada imagen una sola vez;
- no redimensionar varias veces;
- cachear fuentes por ruta y tamaño;
- usar Pillow para composición;
- usar NumPy únicamente en conversiones;
- no introducir OpenCV salvo necesidad demostrada;
- no introducir dependencias pesadas;
- no usar GPU en 0.1.0.

---

# 21. Dependencias

`requirements.txt`:

```text
Pillow>=10.0.0
numpy>=1.24.0
```

No declarar `torch` como dependencia instalable del plugin porque ComfyUI ya lo proporciona.

Para desarrollo:

```text
pytest>=8.0.0
pytest-cov>=5.0.0
```

Pueden ir en un extra de desarrollo de `pyproject.toml`.

---

# 22. Gestión de errores y advertencias

## Errores que deben detener el nodo

- `image_1` con shape inválida;
- resolución menor que 1;
- imposibilidad matemática de crear el layout;
- error interno de tensor que impida producir una imagen.

## Advertencias recuperables

- color inválido;
- fuente no encontrada;
- batch con más de un frame;
- fondo ausente en preset `Background size`;
- máscara de logo con shape no coincidente;
- texto truncado;
- logo demasiado grande y reducido;
- blur no disponible.

Las advertencias deben comenzar por:

```text
[HLT Slide Composer]
```

---

# 23. Modo de depuración

Añadir:

```text
debug_layout: BOOLEAN = false
```

Cuando esté activo:

- dibujar el límite del título;
- dibujar cajas de imagen;
- dibujar cajas de etiquetas;
- dibujar zona del logo;
- escribir coordenadas pequeñas;
- usar colores de depuración claramente visibles.

El modo debug debe alterar solo el render visual, no la geometría.

No debe activarse por defecto.

---

# 24. Pruebas automatizadas

## 24.1. Utilidades

- colores válidos;
- colores inválidos;
- alpha;
- tensor RGB;
- tensor con valores fuera de rango;
- resolución personalizada;
- selección de preset.

## 24.2. Ajuste de imagen

Probar:

- paisaje dentro de retrato con `cover`;
- retrato dentro de caja horizontal;
- `contain`;
- `stretch`;
- anchor top;
- anchor center;
- anchor bottom;
- esquinas;
- borde.

## 24.3. Texto

Probar:

- texto corto;
- texto vacío;
- una línea;
- dos líneas;
- texto muy largo;
- palabra más larga que la caja;
- salto manual;
- mayúsculas;
- fuente no encontrada;
- truncado con `…`.

## 24.4. Layout vertical

Generar pruebas con:

- una imagen;
- dos imágenes;
- tres imágenes;
- cuatro imágenes;
- título vacío;
- título de dos líneas;
- todas las etiquetas vacías;
- etiquetas de dos líneas;
- logo;
- sin logo.

## 24.5. Grid

Generar pruebas con:

- una imagen;
- dos imágenes;
- tres imágenes;
- cuatro imágenes;
- etiquetas de alturas diferentes;
- proporciones diferentes.

## 24.6. Fondo

Probar:

- sólido;
- imagen cover;
- imagen contain;
- opacidad;
- overlay;
- `Background size`.

## 24.7. Logo

Probar:

- logo RGB opaco;
- logo con máscara;
- máscara invertida;
- máscara directa;
- opacidad;
- límites máximos de tamaño;
- ausencia de logo.

## 24.8. Contrato ComfyUI

Comprobar:

- `INPUT_TYPES`;
- `RETURN_TYPES`;
- `FUNCTION`;
- `CATEGORY`;
- `NODE_CLASS_MAPPINGS`;
- shape final `[1, H, W, 3]`;
- dtype `float32`;
- rango 0–1.

---

# 25. Golden tests visuales

Además de las pruebas unitarias, generar imágenes de referencia estables.

Casos mínimos:

```text
golden_01_vertical_one.png
golden_02_vertical_three.png
golden_03_vertical_four.png
golden_04_grid_four.png
golden_05_background_image.png
golden_06_logo_alpha.png
golden_07_long_text.png
golden_08_debug_layout.png
```

Los tests no deben comparar cada píxel si ello provoca falsos fallos entre versiones de Pillow.

Comparar:

- tamaño;
- regiones clave;
- presencia de colores;
- ausencia de píxeles transparentes inesperados;
- posición aproximada de cajas;
- hash perceptual opcional con tolerancia.

---

# 26. Criterios de aceptación de la versión 0.1.0

La versión se considera terminada cuando:

1. ComfyUI detecta el nodo sin errores.
2. Aparece como `HLT · Slide Composer`.
3. Acepta entre una y cuatro imágenes.
4. No deja huecos por entradas desconectadas.
5. Genera exactamente 1080 × 1920 en el preset principal.
6. El fondo predeterminado es negro.
7. Título y etiquetas son rojos HLT por defecto.
8. Cada etiqueta aparece debajo de su imagen.
9. El logo aparece centrado en la zona inferior.
10. El logo conserva su proporción.
11. El logo puede utilizar transparencia mediante máscara.
12. Un fondo conectado puede cubrir el lienzo.
13. `cover`, `contain` y `stretch` funcionan.
14. El título y las etiquetas no salen del lienzo.
15. El texto largo se reduce o trunca de manera controlada.
16. `vertical_stack` funciona con 1, 2, 3 y 4 imágenes.
17. `grid_2x2` funciona con 1, 2, 3 y 4 imágenes.
18. `auto_social` escoge el layout correcto.
19. Los colores HEX inválidos no bloquean el nodo.
20. La ausencia de fuente personalizada no bloquea el nodo.
21. Todos los tests pasan.
22. Existe un workflow de ejemplo.
23. Existe documentación de instalación.
24. Existe una imagen de demostración creada por el propio nodo.
25. El repositorio no modifica otros custom nodes.

---

# 27. Fases de implementación para Codex

## Fase 0 · Preparación

Objetivo:

- crear repositorio;
- añadir estructura;
- añadir `AGENTS.md`;
- añadir entorno de pruebas;
- crear datos artificiales.

Entregables:

```text
estructura creada
pytest funcionando
README inicial
sin integración ComfyUI todavía
```

## Fase 1 · Motor de imagen

Implementar:

- `Rect`;
- presets;
- colores;
- tensor a Pillow;
- Pillow a tensor;
- cover;
- contain;
- stretch;
- crop anchor;
- esquinas;
- bordes.

Criterio:

```text
pytest tests/test_color_utils.py
pytest tests/test_tensor_io.py
pytest tests/test_image_fit.py
```

## Fase 2 · Texto

Implementar:

- búsqueda de fuente;
- medición;
- wrap;
- reducción;
- truncado;
- dibujo centrado.

Criterio:

```text
pytest tests/test_text_engine.py
```

## Fase 3 · Layout vertical

Implementar:

- título;
- 1–4 bloques;
- etiquetas;
- reserva de logo;
- cálculo dinámico.

Criterio:

```text
pytest tests/test_vertical_stack.py
```

Generar una imagen real en `examples/outputs/`.

## Fase 4 · Logo y fondo

Implementar:

- máscara;
- opacidad;
- escalado;
- background image;
- overlay;
- background size.

Criterio:

```text
pytest tests/test_logo_mask.py
pytest tests/test_background.py
```

## Fase 5 · Grid y auto layout

Implementar:

- casos 1–4;
- alineación de etiquetas;
- auto social.

Criterio:

```text
pytest tests/test_grid_2x2.py
```

## Fase 6 · Integración ComfyUI

Implementar:

- clase del nodo;
- inputs;
- optional inputs;
- mappings;
- salida IMAGE;
- advertencias;
- debug.

Criterio:

```text
pytest tests/test_node_contract.py
```

Después:

1. instalar en `custom_nodes`;
2. reiniciar ComfyUI;
3. comprobar consola;
4. localizar nodo;
5. ejecutar workflow.

## Fase 7 · QA final

Probar manualmente:

- una foto horizontal;
- una foto vertical;
- cuatro fotos mezcladas;
- logo PNG;
- fondo fotográfico;
- texto largo;
- 1080 × 1920;
- 1536 × 2048;
- 2160 × 3840.

Crear:

- capturas del nodo;
- output de ejemplo;
- README final;
- changelog;
- versión `0.1.0`.

---

# 28. Contenido recomendado para `AGENTS.md`

```md
# AGENTS.md

## Proyecto

Este repositorio contiene un custom node de ComfyUI llamado
`HLT · Slide Composer`.

## Objetivo

Componer entre una y cuatro imágenes dentro de un slide editorial,
principalmente vertical 9:16, con título, etiquetas, fondo y logo.

## Reglas obligatorias

- Responder y documentar en español salvo código y nombres técnicos.
- No modificar archivos externos al repositorio.
- No modificar otros custom nodes de ComfyUI.
- No añadir JavaScript en la versión 0.1.0.
- No añadir OpenCV, GUI frameworks ni dependencias pesadas.
- Mantener el renderer independiente de ComfyUI.
- Usar Pillow para la composición.
- Conservar el formato IMAGE `[B,H,W,C]`.
- Devolver tensores float32 en rango 0–1.
- No deformar imágenes salvo en modo `stretch`.
- No deformar nunca el logo.
- No dejar huecos por imágenes opcionales desconectadas.
- No incrustar logos ni fuentes propietarias.
- No copiar código de terceros sin revisar licencia y atribución.
- Ejecutar tests después de cada cambio significativo.
- Generar una imagen de prueba al terminar cada fase visual.
- No considerar terminada una fase si solo compila.
- Mantener funciones pequeñas, tipadas y testeables.
- Añadir type hints a todo el código nuevo.
- Documentar decisiones no evidentes.
- Mostrar errores recuperables como advertencias claras.
- Evitar cambios de alcance no solicitados.

## Comandos

```bash
python -m pytest -q
python -m pytest --cov=hlt_slide
```

## Definición de terminado

Una tarea se considera terminada cuando:

1. el código funciona;
2. los tests pasan;
3. la salida visual se ha generado;
4. no hay regresiones;
5. la documentación correspondiente está actualizada.

## Flujo de trabajo

1. Leer esta especificación completa.
2. Inspeccionar el repositorio.
3. Proponer un plan breve.
4. Implementar una fase.
5. Ejecutar tests.
6. Generar output visual.
7. Revisar errores.
8. Resumir cambios y archivos modificados.

## Restricciones de seguridad

- No borrar archivos fuera del repositorio.
- No ejecutar comandos destructivos.
- No instalar paquetes globales.
- No publicar ni hacer push sin autorización explícita.
```

---

# 29. Prompt inicial para Codex

Usar este prompt después de guardar el documento maestro en el repositorio como `MASTER_SPEC.md`:

```text
Trabaja sobre este repositorio para crear el custom node de ComfyUI
`HLT · Slide Composer`.

Lee primero, en este orden:

1. AGENTS.md
2. MASTER_SPEC.md
3. README.md
4. el estado actual del repositorio

No programes todavía después de leerlos.

Primero:

- resume el objetivo del nodo;
- identifica decisiones cerradas;
- señala contradicciones o puntos ambiguos;
- propone un plan de implementación por fases;
- enumera los archivos que crearás o modificarás;
- indica los comandos de prueba que utilizarás;
- señala cualquier dependencia innecesaria que debamos evitar.

Restricciones:

- no modifiques otros custom nodes;
- no añadas JavaScript;
- no añadas OpenCV;
- no incrustes logos ni fuentes propietarias;
- usa Pillow, NumPy y el Torch que ya proporciona ComfyUI;
- mantén el renderer desacoplado de ComfyUI;
- usa type hints;
- implementa pruebas antes de integrar el nodo;
- no hagas push ni publiques nada.

Espera mi aprobación del plan antes de implementar.
```

---

# 30. Prompt para comenzar la Fase 1

```text
Plan aprobado.

Ejecuta únicamente la Fase 1 de MASTER_SPEC.md.

Objetivo:

- modelos de geometría;
- presets de resolución;
- parseo de colores;
- conversiones tensor/Pillow;
- cover, contain y stretch;
- crop anchor;
- esquinas redondeadas;
- bordes;
- pruebas unitarias correspondientes.

No implementes todavía:

- textos;
- layouts completos;
- logo;
- fondo fotográfico;
- clase final de ComfyUI.

Antes de terminar:

1. ejecuta los tests;
2. genera al menos tres imágenes de prueba;
3. revisa shapes, dtype y rango;
4. resume los cambios;
5. enumera cualquier decisión tomada que no estuviese cerrada en la especificación.

No hagas push.
```

---

# 31. Prompt para revisión final de Codex

```text
Realiza una auditoría final del proyecto contra MASTER_SPEC.md.

No añadas funciones nuevas durante la primera pasada.

Comprueba:

- contrato de inputs y outputs;
- layouts;
- comportamiento con 1–4 imágenes;
- ausencia de huecos;
- tamaños exactos;
- fondos;
- logo y máscara;
- textos largos;
- fallbacks de fuente;
- validación de colores;
- batch;
- shape y rango del tensor;
- tests;
- documentación;
- workflow de ejemplo;
- dependencias;
- compatibilidad con Windows;
- ausencia de cambios en otros custom nodes.

Entrega:

1. matriz de cumplimiento;
2. fallos encontrados;
3. riesgos;
4. cambios mínimos necesarios;
5. comandos exactos para validar;
6. lista de archivos modificados.

Después corrige únicamente los incumplimientos confirmados, ejecuta toda la suite
y genera los outputs finales de validación.

No hagas push ni publiques.
```

---

# 32. Instalación prevista

Ruta genérica:

```text
<COMFYUI_ROOT>/custom_nodes/ComfyUI-HLT-SlideComposer
```

Pasos:

```bash
cd <COMFYUI_ROOT>/custom_nodes
git clone <URL_DEL_REPOSITORIO>
cd ComfyUI-HLT-SlideComposer
python -m pip install -r requirements.txt
```

Después:

1. reiniciar ComfyUI;
2. revisar la consola;
3. buscar `HLT Slide Composer`;
4. cargar workflow de ejemplo.

Para instalaciones portables, documentar el uso del Python incluido por ComfyUI.

Ejemplo genérico:

```bash
<COMFYUI_ROOT>/python_embeded/python.exe -m pip install -r requirements.txt
```

No asumir una ruta única en el código.

---

# 33. Workflow mínimo de ejemplo

El workflow de ejemplo debe contener:

```text
Load Image · foto 1 ─────────────┐
Load Image · foto 2 ─────────────┤
Load Image · foto 3 ─────────────┤
Load Image · logo ─ IMAGE ───────┤
                  └ MASK ────────┤
                                 ▼
                      HLT · Slide Composer
                                 │
                                 ▼
                          Preview Image
                                 │
                                 ▼
                            Save Image
```

Debe incluir valores HLT:

```text
canvas_preset = 9:16 Social · 1080x1920
layout = vertical_stack
background_color = #000000
title_color = #E92124
label_color = #E92124
title = REFERENCIAS Y RESULTADO
label_1 = REF0 · PRODUCTO
label_2 = REF1 · PERSONA
label_3 = RESULTADO
image_fit = cover
crop_anchor = center
logo_width_percent = 18
```

---

# 34. Referencias técnicas externas

Estas referencias sirven para estudiar patrones, no para copiar repositorios completos.

## ComfyUI LayerStyle

Repositorio:

```text
https://github.com/chflame163/ComfyUI_LayerStyle
```

Revisar:

- entradas opcionales de imágenes;
- reel;
- composición;
- fuentes;
- convenciones de nodos.

## ComfyUI Img Label Tools

Repositorio:

```text
https://github.com/rjgoif/ComfyUI-Img-Label-Tools
```

Revisar:

- resize;
- pad;
- crop;
- etiquetas;
- galerías;
- manejo de distintas proporciones.

## Enrico’s Compositor

Repositorio:

```text
https://github.com/erosDiffusion/ComfyUI-enricos-nodes
```

Revisar:

- capas;
- fondo;
- escalado;
- composición.

No replicar su complejidad de frontend.

## APZmedia Textools

Repositorio:

```text
https://github.com/APZmedia/comfyui-textools
```

Revisar:

- ajuste de texto;
- reducción de fuente;
- truncado;
- medición.

## LayerStyle Advance

Repositorio:

```text
https://github.com/chflame163/ComfyUI_LayerStyle_Advance
```

Revisar:

- canvas;
- collage;
- fondo;
- bordes;
- esquinas.

## Documentación de ComfyUI

```text
https://docs.comfy.org/custom-nodes/backend/server_overview
https://docs.comfy.org/custom-nodes/backend/images_and_masks
```

---

# 35. Licencias y atribución

Antes de adaptar código de terceros:

1. comprobar la licencia exacta del repositorio;
2. identificar el archivo concreto;
3. evitar copiar más de lo necesario;
4. conservar avisos de copyright;
5. añadir atribución en `NOTICE.md` si procede;
6. documentar qué patrón o función se ha adaptado;
7. preferir implementación propia cuando la lógica sea sencilla.

El repositorio debe incluir una licencia definida antes de publicarse.

Recomendación inicial:

```text
MIT
```

No publicar con licencia hasta confirmar que todo el código incluido es compatible.

---

# 36. Decisiones cerradas

Estas decisiones no deben reinterpretarse durante el MVP:

- el nodo principal se llama `HLT · Slide Composer`;
- el formato predeterminado es 1080 × 1920;
- el fondo predeterminado es negro;
- el rojo HLT predeterminado es `#E92124`;
- el título y las etiquetas son rojos por defecto;
- el logo es una entrada externa;
- no se incrusta ningún logo;
- hay un máximo de cuatro imágenes;
- `image_1` es obligatoria;
- las demás imágenes son opcionales;
- no se dejan huecos;
- las etiquetas se colocan debajo de cada imagen;
- el título se coloca arriba;
- el logo se coloca abajo;
- la salida es `IMAGE`;
- se usa Pillow;
- no se usa JavaScript en 0.1.0;
- no se modifica ningún custom node existente;
- no se usa OpenCV;
- el motor se prueba sin arrancar ComfyUI;
- se usa el primer frame de cada batch en 0.1.0;
- la geometría se adapta al número real de imágenes.

---

# 37. Decisiones que pueden ajustarse tras una primera prueba

Codex puede proponer ajustes, pero no aplicarlos sin revisión:

- altura exacta de la zona del título;
- altura exacta reservada al logo;
- tamaño inicial de las etiquetas;
- separación entre bloques;
- porcentaje predeterminado del logo;
- criterio de tres imágenes en grid;
- cantidad máxima de líneas del título;
- presencia de blur en 0.1.0;
- estilo del borde en esquinas redondeadas;
- formato del mensaje de advertencia.

---

# 38. Riesgos conocidos

## Demasiados controles

Un nodo con muchos inputs puede resultar incómodo en ComfyUI.

Mitigación:

- agrupar controles por orden lógico;
- usar defaults correctos;
- considerar dos nodos en el futuro:
  - `HLT Slide Composer`;
  - `HLT Slide Style`.

No dividirlo en la versión inicial salvo que la interfaz sea realmente inmanejable.

## Fuentes multiplataforma

Las rutas cambian.

Mitigación:

- campo `font_path`;
- resolver fuentes comunes;
- fallback;
- documentación.

## Máscara invertida

La semántica puede confundir.

Mitigación:

- `invert_logo_mask=true`;
- ejemplo de workflow;
- test específico.

## Cuatro imágenes en vertical

Pueden quedar demasiado bajas.

Mitigación:

- ofrecer `grid_2x2`;
- `auto_social` usa grid para cuatro;
- advertencia si el alto calculado es muy pequeño.

## Textos largos

Pueden reducir demasiado las imágenes.

Mitigación:

- máximo de líneas;
- tamaño mínimo;
- truncado;
- warnings.

## Resoluciones 4K

Aumentan memoria y tiempo.

Mitigación:

- Pillow;
- conversión única;
- aviso en documentación;
- tests de smoke, no tests exhaustivos en cada ejecución.

---

# 39. Roadmap posterior

## 0.2.0

- layout comparison;
- hero stack;
- batch zip;
- sombras;
- fondo de etiqueta;
- posición horizontal de logo;
- color diferente por etiqueta;
- exportación de JSON de estilo;
- presets guardados.

## 0.3.0

- nodo separado de estilo;
- selector de color visual;
- selector de fuente;
- preview de layout en el nodo;
- crop X/Y personalizado;
- posición manual de foco por imagen;
- footer de texto;
- numeración automática.

## 1.0.0

- API estable;
- compatibilidad verificada;
- publicación en ComfyUI Registry;
- documentación completa;
- ejemplos;
- soporte de batches;
- migración al esquema de nodos recomendado por ComfyUI si procede.

---

# 40. Definición final de éxito

El proyecto habrá cumplido su objetivo cuando un usuario pueda:

1. cargar una referencia de producto;
2. cargar una fotografía de persona;
3. cargar un resultado generado;
4. conectar un logo PNG;
5. escribir un título y tres etiquetas;
6. seleccionar 9:16;
7. pulsar Queue;
8. obtener una sola imagen 1080 × 1920;
9. verla sobre fondo negro;
10. leer textos rojos centrados;
11. ver cada etiqueta debajo de su imagen;
12. ver el logo abajo sin deformación;
13. guardar el resultado sin construir manualmente la composición.

Ese flujo debe ser estable, rápido y repetible.
