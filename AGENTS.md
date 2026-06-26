# AGENTS.md

## 1. Identidad del proyecto

Este repositorio contiene un custom node de ComfyUI llamado:

`HLT · Slide Composer`

Nombre previsto del repositorio:

`ComfyUI-HLT-SlideComposer`

Nombre de clase propuesto:

`HLTSlideComposer`

Categoría prevista en ComfyUI:

`HLT / Composition`

Versión objetivo inicial:

`0.1.0`

El nodo debe componer entre una y cuatro imágenes dentro de un slide editorial, principalmente en formato vertical 9:16, con título, etiquetas, fondo y logo opcional.

---

## 2. Fuente de verdad

Antes de planificar, modificar o crear código, lee íntegramente:

1. `AGENTS.md`
2. `MASTER_SPEC.md`
3. `README.md`, si existe
4. el estado actual del repositorio
5. los tests existentes
6. el historial Git relevante, si es necesario

`MASTER_SPEC.md` es la fuente principal de requisitos funcionales, visuales y técnicos.

Si existe una contradicción entre archivos:

1. detén la implementación;
2. identifica la contradicción;
3. explica su impacto;
4. propone una resolución;
5. espera aprobación antes de cambiar el alcance.

No inventes requisitos para rellenar huecos.

---

## 3. Objetivo funcional

El nodo debe permitir:

- conectar entre una y cuatro imágenes;
- crear un lienzo con proporción fija;
- usar 9:16 como formato principal;
- añadir un título superior;
- añadir una etiqueta debajo de cada imagen;
- añadir un logo centrado en la parte inferior;
- usar fondo sólido o imagen de fondo;
- cambiar colores;
- ajustar imágenes mediante `cover`, `contain` o `stretch`;
- conservar proporciones salvo cuando el usuario elija `stretch`;
- producir una salida `IMAGE` válida para ComfyUI;
- funcionar de manera determinista;
- evitar huecos por entradas opcionales desconectadas.

El resultado principal debe poder utilizarse para:

- stories;
- comparativas;
- referencias;
- resultados de generación;
- presentaciones rápidas;
- documentación de workflows;
- slides de proceso visual.

---

## 4. Reglas de trabajo obligatorias

- Trabaja únicamente dentro de este repositorio.
- No modifiques otros custom nodes.
- No modifiques la instalación general de ComfyUI.
- No borres ni muevas archivos fuera del repositorio.
- No ejecutes comandos destructivos.
- No hagas `push`, publicación, release ni despliegue sin autorización explícita.
- No instales paquetes globalmente.
- No añadas JavaScript en la versión `0.1.0`.
- No añadas OpenCV.
- No añadas frameworks GUI.
- No añadas dependencias pesadas sin necesidad demostrada.
- Usa Pillow para la composición visual.
- Usa NumPy para conversiones cuando sea necesario.
- Usa el Torch proporcionado por ComfyUI.
- Mantén el renderer desacoplado de ComfyUI.
- Usa type hints en todo el código nuevo.
- Mantén funciones pequeñas, legibles y testeables.
- Añade o actualiza tests junto a cada cambio funcional.
- Ejecuta tests después de cada cambio significativo.
- Genera una salida visual de prueba al terminar cada fase relacionada con composición.
- No consideres terminada una fase solo porque el código compile.
- No incrustes logos, fotografías ni fuentes propietarias.
- No copies código de terceros sin revisar licencia y atribución.
- No cambies decisiones cerradas de `MASTER_SPEC.md` sin aprobación.
- No amplíes el alcance por iniciativa propia.
- No refactorices partes no relacionadas salvo que sea estrictamente necesario.
- No ocultes errores con excepciones genéricas o `try/except` silenciosos.
- No sustituyas una prueba real por una afirmación no verificada.

---

## 5. Restricciones técnicas

### 5.1. Motor visual

El motor de composición debe estar implementado principalmente con:

- Python;
- Pillow;
- NumPy;
- Torch ya incluido en ComfyUI.

No usar en `0.1.0`:

- OpenCV;
- PyQt;
- Tkinter;
- Electron;
- frontend JavaScript;
- motores de plantillas externos;
- librerías de composición pesadas;
- procesamiento GPU específico.

### 5.2. ComfyUI

El nodo debe respetar el contrato de imagen de ComfyUI:

```text
[B, H, W, C]
```

Condiciones:

- dtype de salida: `float32`;
- rango de salida: `0.0–1.0`;
- canales: RGB;
- salida principal: `IMAGE`;
- batch inicial: un único frame de salida.

### 5.3. Batch

En la versión `0.1.0`:

- usa solo el primer frame de cada entrada `IMAGE`;
- registra una advertencia si el batch contiene más de un frame;
- devuelve un batch de una imagen;
- no implementes procesamiento `zip`, broadcasting ni lotes completos salvo aprobación.

### 5.4. Calidad de imagen

- Usa `Image.Resampling.LANCZOS`.
- No deformes imágenes salvo con `stretch`.
- No deformes nunca el logo.
- Mantén la proporción del logo.
- Evita redimensionados repetidos.
- Convierte cada entrada a Pillow una sola vez siempre que sea posible.
- No alteres la resolución final del preset seleccionado.

---

## 6. Decisiones cerradas del MVP

Estas decisiones no deben reinterpretarse:

- El nodo visible se llama `HLT · Slide Composer`.
- La clase propuesta es `HLTSlideComposer`.
- La categoría es `HLT / Composition`.
- El formato predeterminado es `1080 × 1920`.
- El layout predeterminado es `vertical_stack`.
- El fondo predeterminado es `#000000`.
- El rojo HLT predeterminado es `#E92124`.
- El título es rojo HLT por defecto.
- Las etiquetas son rojas HLT por defecto.
- `image_1` es obligatoria.
- `image_2`, `image_3` e `image_4` son opcionales.
- El máximo inicial es cuatro imágenes.
- Las imágenes desconectadas no dejan huecos.
- Las etiquetas se colocan debajo de cada imagen.
- El título se coloca en la zona superior.
- El logo se coloca centrado en la zona inferior.
- El logo se conecta como recurso externo.
- El logo no se incrusta en el repositorio.
- El fondo puede ser sólido o una imagen.
- La salida es `IMAGE`.
- La composición se realiza con Pillow.
- No se usa JavaScript en `0.1.0`.
- No se usa OpenCV.
- No se modifica ningún nodo externo.
- El renderer debe poder probarse sin arrancar ComfyUI.
- La geometría debe adaptarse al número real de imágenes.
- La versión inicial usa el primer frame de cada batch.

---

## 7. Estructura prevista del repositorio

Mantén una estructura equivalente a esta, salvo que haya una razón técnica documentada para ajustarla:

```text
ComfyUI-HLT-SlideComposer/
│
├── __init__.py
├── nodes.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── AGENTS.md
├── MASTER_SPEC.md
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

No concentres toda la lógica en `nodes.py`.

---

## 8. Responsabilidad por módulo

### `nodes.py`

Debe limitarse a:

- definir inputs;
- definir outputs;
- convertir parámetros de entrada;
- llamar al renderer;
- devolver el tensor;
- registrar el nodo.

No debe contener:

- algoritmos extensos de layout;
- lógica de texto;
- lógica de recorte;
- composición compleja;
- utilidades reutilizables.

### `config.py`

Debe contener:

- dataclasses;
- presets;
- valores predeterminados;
- enums o literales;
- validación de configuración.

### `renderer.py`

Debe:

- crear el lienzo;
- componer el fondo;
- pedir el layout;
- componer imágenes;
- componer textos;
- componer logo;
- devolver una imagen Pillow.

### `layouts.py`

Debe:

- calcular rectángulos;
- no dibujar;
- devolver geometría;
- implementar `vertical_stack`;
- implementar `grid_2x2`;
- implementar `auto_social`.

### `text_engine.py`

Debe:

- medir;
- envolver;
- reducir fuente;
- truncar;
- centrar;
- respetar saltos manuales.

### `image_utils.py`

Debe:

- implementar `cover`;
- implementar `contain`;
- implementar `stretch`;
- aplicar crop anchor;
- aplicar esquinas;
- aplicar borde;
- aplicar blur si se incluye;
- escalar proporcionalmente.

### `color_utils.py`

Debe:

- validar HEX;
- normalizar;
- aplicar fallback;
- gestionar alpha.

### `tensor_io.py`

Debe:

- convertir tensor a Pillow;
- convertir Pillow a tensor;
- convertir máscara;
- validar shapes;
- limitar valores.

### `font_utils.py`

Debe:

- resolver rutas;
- buscar fuentes comunes;
- aplicar fallback;
- cachear fuentes.

### `exceptions.py`

Debe definir excepciones específicas y comprensibles.

---

## 9. Convenciones de código

- Usa Python moderno compatible con la versión soportada por ComfyUI.
- Usa `from __future__ import annotations` cuando ayude a mantener compatibilidad.
- Añade type hints a parámetros y retornos.
- Usa dataclasses para estructuras de configuración y geometría.
- Usa nombres descriptivos.
- Evita abreviaturas ambiguas.
- Evita funciones de más de aproximadamente 50 líneas, salvo razón documentada.
- Evita clases con demasiadas responsabilidades.
- Evita estado global mutable.
- Evita números mágicos.
- Centraliza valores predeterminados.
- Mantén separada la lógica pura de la integración con ComfyUI.
- Añade docstrings donde la intención no sea evidente.
- Los comentarios deben explicar el porqué, no repetir el código.
- Mantén el idioma del código en inglés.
- Mantén la documentación de usuario en español.
- Mantén los mensajes de error claros y accionables.

---

## 10. Convenciones de Git

No hagas push sin autorización.

Cuando se autorice un commit:

- usa commits pequeños;
- no mezcles fases distintas;
- no incluyas archivos temporales;
- no incluyas outputs de pruebas salvo ejemplos aprobados;
- revisa `git status`;
- revisa el diff;
- ejecuta tests antes del commit.

Formato recomendado:

```text
feat: add vertical stack renderer
test: cover image fitting cases
fix: preserve logo aspect ratio
docs: document ComfyUI installation
refactor: isolate tensor conversion helpers
```

No:

- reescribas historial;
- hagas force push;
- borres ramas;
- cambies remotos;
- publiques releases;
- cambies visibilidad del repositorio.

---

## 11. Dependencias

Dependencias de runtime previstas:

```text
Pillow>=10.0.0
numpy>=1.24.0
```

Torch no debe declararse como instalación independiente del plugin si ComfyUI ya lo proporciona.

Dependencias de desarrollo previstas:

```text
pytest>=8.0.0
pytest-cov>=5.0.0
```

Antes de añadir cualquier otra dependencia:

1. explica el problema;
2. explica por qué no puede resolverse con la librería estándar o las dependencias existentes;
3. analiza tamaño, mantenimiento y licencia;
4. espera aprobación.

---

## 12. Comandos de validación

Usa preferentemente:

```bash
python -m pytest -q
python -m pytest --cov=hlt_slide
```

Pruebas por área:

```bash
python -m pytest tests/test_color_utils.py -q
python -m pytest tests/test_tensor_io.py -q
python -m pytest tests/test_image_fit.py -q
python -m pytest tests/test_text_engine.py -q
python -m pytest tests/test_vertical_stack.py -q
python -m pytest tests/test_grid_2x2.py -q
python -m pytest tests/test_logo_mask.py -q
python -m pytest tests/test_background.py -q
python -m pytest tests/test_node_contract.py -q
```

Si el proyecto añade un formateador o linter, documenta los comandos en `README.md` y `pyproject.toml`.

No instales herramientas globales sin permiso.

---

## 13. Estrategia de pruebas

Cada cambio funcional debe incluir pruebas.

### 13.1. Colores

Probar:

- `#RGB`;
- `#RRGGBB`;
- `#RRGGBBAA`;
- valores sin `#`;
- valor inválido;
- fallback;
- alpha.

### 13.2. Tensores

Probar:

- shape válido;
- dtype;
- rango;
- clipping;
- tensor inválido;
- roundtrip Pillow → tensor → Pillow;
- máscara válida;
- máscara inválida.

### 13.3. Ajuste de imagen

Probar:

- paisaje en caja vertical;
- retrato en caja horizontal;
- `cover`;
- `contain`;
- `stretch`;
- anchor `top`;
- anchor `center`;
- anchor `bottom`;
- esquinas;
- borde.

### 13.4. Texto

Probar:

- vacío;
- corto;
- una línea;
- dos líneas;
- muy largo;
- palabra demasiado larga;
- salto manual;
- mayúsculas;
- fuente ausente;
- truncado;
- tamaño mínimo.

### 13.5. Layout vertical

Probar:

- una imagen;
- dos imágenes;
- tres imágenes;
- cuatro imágenes;
- título vacío;
- título largo;
- etiquetas vacías;
- etiquetas largas;
- logo;
- ausencia de logo.

### 13.6. Grid

Probar:

- una imagen;
- dos imágenes;
- tres imágenes;
- cuatro imágenes;
- proporciones mixtas;
- etiquetas de alturas distintas.

### 13.7. Fondo

Probar:

- sólido;
- imagen;
- cover;
- contain;
- stretch;
- overlay;
- opacidad;
- `Background size`.

### 13.8. Logo

Probar:

- RGB opaco;
- máscara;
- máscara invertida;
- máscara directa;
- opacidad;
- tamaño máximo;
- proporción;
- ausencia.

### 13.9. Contrato del nodo

Comprobar:

- `INPUT_TYPES`;
- `RETURN_TYPES`;
- `RETURN_NAMES`;
- `FUNCTION`;
- `CATEGORY`;
- mappings;
- shape final;
- dtype;
- rango.

---

## 14. Golden outputs y validación visual

Al terminar cada fase visual:

1. genera imágenes sintéticas de prueba;
2. guarda outputs en una carpeta temporal o de ejemplo;
3. comprueba resolución;
4. comprueba alineación;
5. comprueba ausencia de deformación;
6. comprueba textos;
7. comprueba logo;
8. comprueba márgenes;
9. comprueba esquinas y bordes;
10. resume cualquier desviación.

Outputs mínimos previstos:

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

No uses comparación exacta de cada píxel si puede variar entre versiones de Pillow.

---

## 15. Gestión de errores

Errores que deben detener el nodo:

- `image_1` inválida;
- resolución inválida;
- tensor con shape incompatible;
- imposibilidad matemática de crear el layout;
- error que impida producir una imagen válida.

Advertencias recuperables:

- color inválido;
- fuente no encontrada;
- batch con más de un frame;
- fondo ausente con preset `Background size`;
- máscara no coincidente;
- texto truncado;
- logo reducido;
- blur no disponible.

Todos los mensajes propios deben empezar por:

```text
[HLT Slide Composer]
```

No uses `except Exception: pass`.

No ocultes errores importantes.

---

## 16. Licencias y código de terceros

Antes de adaptar código de otro repositorio:

1. revisa su licencia;
2. identifica el archivo exacto;
3. limita la adaptación;
4. conserva atribuciones;
5. documenta el origen;
6. añade `NOTICE.md` si procede;
7. evita copiar grandes bloques;
8. prefiere implementación propia para lógica sencilla.

Repositorios de referencia permitidos para estudio:

- `chflame163/ComfyUI_LayerStyle`
- `rjgoif/ComfyUI-Img-Label-Tools`
- `erosDiffusion/ComfyUI-enricos-nodes`
- `APZmedia/comfyui-textools`
- `chflame163/ComfyUI_LayerStyle_Advance`

No clones su arquitectura completa dentro de este proyecto.

---

## 17. Fases de implementación

### Fase 0 · Preparación

Crear:

- estructura;
- entorno de tests;
- configuración;
- README inicial;
- datos sintéticos.

No integrar todavía con ComfyUI.

### Fase 1 · Motor de imagen

Implementar:

- geometría;
- presets;
- colores;
- tensor/Pillow;
- cover;
- contain;
- stretch;
- crop anchor;
- esquinas;
- bordes.

### Fase 2 · Texto

Implementar:

- fuentes;
- medición;
- wrap;
- reducción;
- truncado;
- centrado.

### Fase 3 · Vertical stack

Implementar:

- título;
- bloques dinámicos;
- etiquetas;
- reserva de logo;
- cálculo con 1–4 imágenes.

### Fase 4 · Fondo y logo

Implementar:

- imagen de fondo;
- overlay;
- opacidad;
- máscara;
- escala;
- posición.

### Fase 5 · Grid y auto layout

Implementar:

- `grid_2x2`;
- casos 1–4;
- `auto_social`.

### Fase 6 · Integración ComfyUI

Implementar:

- clase;
- inputs;
- outputs;
- mappings;
- warnings;
- debug.

### Fase 7 · QA final

Validar:

- Windows;
- ComfyUI real;
- workflow;
- ejemplos;
- documentación;
- versión `0.1.0`.

No avances a una fase nueva sin cerrar la anterior o explicar el bloqueo.

---

## 18. Protocolo al comenzar una tarea

Antes de modificar código:

1. lee la petición;
2. revisa `MASTER_SPEC.md`;
3. inspecciona los archivos relevantes;
4. revisa tests existentes;
5. revisa `git status`;
6. presenta un plan breve;
7. indica archivos afectados;
8. indica tests que ejecutarás;
9. espera aprobación cuando la petición lo exija.

Para tareas pequeñas y explícitamente aprobadas, puedes implementar directamente, pero debes mantener el alcance estricto.

---

## 19. Protocolo al terminar una tarea

Entrega siempre:

1. resumen de cambios;
2. archivos creados;
3. archivos modificados;
4. tests ejecutados;
5. resultado de los tests;
6. outputs visuales generados;
7. limitaciones conocidas;
8. decisiones tomadas;
9. siguiente paso recomendado;
10. confirmación de que no se hizo push, salvo autorización.

No digas que algo funciona si no lo has ejecutado o validado.

---

## 20. Formato esperado de respuesta de Codex

Usa este formato:

```text
Resumen
- ...

Archivos modificados
- ...

Validación
- Comando:
- Resultado:

Salida visual
- ...

Decisiones
- ...

Riesgos o pendientes
- ...

Siguiente paso
- ...
```

Sé directo y concreto.

No generes explicaciones innecesariamente largas cuando el trabajo ya esté claro.

---

## 21. Criterios de aceptación de `0.1.0`

La versión inicial estará terminada cuando:

1. ComfyUI detecte el nodo.
2. Aparezca como `HLT · Slide Composer`.
3. Acepte 1–4 imágenes.
4. No deje huecos por entradas desconectadas.
5. Produzca 1080 × 1920 en el preset principal.
6. Use fondo negro por defecto.
7. Use rojo `#E92124` por defecto.
8. Coloque las etiquetas debajo de cada imagen.
9. Coloque el logo centrado abajo.
10. Mantenga la proporción del logo.
11. Admita máscara.
12. Admita fondo de imagen.
13. Funcionen `cover`, `contain` y `stretch`.
14. Los textos no salgan del lienzo.
15. Los textos largos se reduzcan o trunquen.
16. Funcione `vertical_stack`.
17. Funcione `grid_2x2`.
18. Funcione `auto_social`.
19. Los colores inválidos no bloqueen.
20. La ausencia de fuente no bloquee.
21. Todos los tests pasen.
22. Exista workflow de ejemplo.
23. Exista documentación.
24. Exista un output demostrativo.
25. No se hayan modificado otros nodos.

---

## 22. Definición de terminado

Una tarea o fase solo se considera terminada cuando:

1. el código está implementado;
2. los tests relevantes pasan;
3. la salida visual ha sido generada cuando procede;
4. no existen errores conocidos sin documentar;
5. la documentación está actualizada;
6. el diff ha sido revisado;
7. el alcance coincide con la petición;
8. no se han añadido dependencias innecesarias;
9. no se han modificado archivos externos;
10. el resultado se ha resumido con honestidad.

---

## 23. Restricciones de seguridad

No:

- borres archivos fuera del repositorio;
- ejecutes `git clean -fdx`;
- ejecutes `rm -rf` sobre rutas no verificadas;
- ejecutes `Remove-Item -Recurse -Force` fuera del repositorio;
- modifiques variables globales del sistema;
- cambies Python global;
- actualices Torch;
- actualices ComfyUI;
- cambies drivers;
- modifiques CUDA;
- instales paquetes globales;
- publiques tokens;
- muestres secretos;
- hagas push sin permiso;
- alteres remotos;
- crees releases;
- publiques en ComfyUI Registry.

Si una tarea requiere una acción de riesgo, detente y pide autorización.

---

## 24. Entorno Windows

El proyecto se desarrolla inicialmente en Windows.

Ruta local prevista:

```text
C:\Users\<USUARIO>\Documents\CODEXperimentos\ComfyUI-HLT-SlideComposer
```

No codifiques rutas absolutas.

Usa:

- `pathlib.Path`;
- rutas relativas al repositorio;
- detección multiplataforma de fuentes;
- comandos compatibles con PowerShell cuando documentes Windows.

La integración con ComfyUI se realizará después de validar el motor independiente.

No copies el repositorio a `custom_nodes` hasta que la fase correspondiente esté aprobada.

---

## 25. Primer encargo de Codex

Cuando se inicie el proyecto por primera vez:

1. lee `AGENTS.md`;
2. lee `MASTER_SPEC.md`;
3. inspecciona el repositorio;
4. no programes todavía;
5. resume el objetivo;
6. identifica decisiones cerradas;
7. detecta contradicciones;
8. propone plan por fases;
9. enumera archivos;
10. enumera tests;
11. identifica riesgos;
12. espera aprobación.

No empieces a crear código en la primera respuesta salvo instrucción explícita.
