# Goxlang Compiler

Un compilador para el lenguaje GoxLang que implementa un subconjunto de características de Go, incluyendo análisis léxico, sintáctico, semántico y generación de código intermedio.

---

## Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas:

```
compilador_goxlang/
├── lexer/                 # Análisis léxico
│   └── tokenizer.py      # Tokenizador
├── parser/               # Análisis sintáctico
│   ├── parser.py        # Parser
│   └── modelo.py        # Modelo AST
├── semantic/            # Análisis semántico
│   ├── check.py        # Verificador semántico
│   ├── symtab.py       # Tabla de símbolos
│   └── typesys.py      # Sistema de tipos
├── ircode.py           # Generación de código intermedio
├── test_ircode.py      # Pruebas unitarias del código IR
├── main.py             # Punto de entrada
└── samples/            # Ejemplos de código
    ├── shor.gox        # Implementación del algoritmo de Shor
    ├── factorize.gox
    └── ...
```

---

## Funcionamiento del Analizador Sintáctico

El analizador sintáctico (`parser.py`) toma como entrada una lista de tokens generada por el analizador léxico (`tokenize.py`) y construye un Árbol de Sintaxis Abstracta (AST) utilizando las clases definidas en `modelo.py`.

### Flujo del Analizador Sintáctico

1. **Tokenización**:
   - El archivo fuente se tokeniza utilizando las reglas definidas en `tokenize.py`.
   - Los tokens generados se pasan al analizador sintáctico.

2. **Construcción del AST**:
   - El analizador sintáctico utiliza una gramática basada en PEG para analizar los tokens y construir un AST.
   - Las clases del AST están definidas en `modelo.py`.

3. **Salida del AST**:
   - El AST generado se guarda en formato JSON en la carpeta `outputs/`.

---

## Método `main`

El archivo `main.py` es el punto de entrada del compilador. Realiza las siguientes tareas:

1. **Lectura del archivo fuente**:
   - Lee el archivo fuente desde la carpeta `samples/`.

2. **Tokenización**:
   - Utiliza el analizador léxico para generar una lista de tokens.

3. **Análisis sintáctico**:
   - Pasa los tokens al analizador sintáctico para construir el AST.

4. **Análisis semántico**:
   - Valida el AST utilizando el analizador semántico.

5. **Salida**:
   - Guarda el AST en formato JSON y muestra la tabla de símbolos generada o los errores semánticos.

---

## Método `ircode.py`

El archivo `ircode.py` es el punto de entrada para el generador del código intermedio. Realiza las siguientes tareas:

1. **Lectura del archivo fuente**:
   - Lee el archivo fuente desde la carpeta `samples/`.

2. **Tokenización**:
   - Utiliza el analizador léxico para generar una lista de tokens.

3. **Análisis sintáctico**:
   - Pasa los tokens al analizador sintáctico para construir el AST.

4. **Análisis semántico**:
   - Valida el AST utilizando el analizador semántico.

5. **Generación de codigo intermedio**:
   - Genera el código intermedio necesario para el interprete en las siguientes fases

## Situación Actual

1. **Modelo del AST**:
   - `modelo.py` define la estructura del lenguaje según las especificaciones del profesor.
   - Las clases están organizadas en secciones para declaraciones, expresiones, y ubicaciones.

2. **Analizador Sintáctico**:
   - `parser.py` utiliza las clases del modelo para construir el AST.
   - El parser ahora funciona correctamente y genera un AST válido.

3. **Analizador Semántico**:
   - `check.py` valida el AST utilizando reglas semánticas definidas en `typesys.py` y `symtab.py`.
   - Se corrigieron los errores que no generaban la tabla de símbolos y que no mostraban los errores del archivo .gox a procesar y ahora funciona correctamente y genera una tabla de símbolos válida.

4. **Generación de Código Intermedio (ircode.py)**:
- Generación de código IR basado en una máquina de pila virtual
- Soporte para operaciones aritméticas, lógicas y de control
- Manejo de funciones y variables locales/globales
- Instrucciones IR para:
  - Operaciones aritméticas (ADDI, SUBI, MULI, DIVI, etc.)
  - Control de flujo (IF, ELSE, ENDIF, LOOP, etc.)
  - Funciones (CALL, RET)
  - Variables (LOCAL_GET/SET, GLOBAL_GET/SET)
---

## Errores Encontrados y Soluciones

### 1. Error: `'list' object has no attribute 'accept'`
- **Causa**: Algunos nodos del AST contienen listas de nodos (por ejemplo, `If.consequence` y `While.body`), pero el analizador semántico intentaba llamar a `accept` directamente en estas listas.
- **Solución**: Se recorrieron explícitamente las listas y se llamó a `accept` en cada nodo individual.

### 2. Error: `'If' object has no attribute 'then'`
- **Causa**: El atributo correcto para el bloque de la condición verdadera es `consequence`, no `then`.
- **Solución**: Se corrigieron las referencias al atributo en el analizador semántico.

### 3. Error: `'Integer' object has no attribute 'type'`
- **Causa**: Los nodos de tipo `Literal` no tenían un atributo `type`.
- **Solución**: Se agregó una propiedad `type` a las clases de literales (`Integer`, `Float`, `Bool`, `Char`) en `modelo.py`.

### 4. Error: `'Function' object has no attribute 'parameters'`
- **Causa**: El nodo `Function` no estaba estructurado correctamente en el AST.
- **Solución**: Se verificó que el nodo `Function` tuviera los atributos `parameters` y `return_type`.

### 5. Error: `'list' object has no attribute 'accept'` en `FunctionCall`
- **Causa**: El analizador semántico intentaba procesar argumentos de funciones sin recorrerlos correctamente.
- **Solución**: Se recorrieron los argumentos y se llamó a `accept` en cada uno.

### 6. Error: Modelo sin el patrón `Visitor`
- **Causa**: El modelo del AST no implementaba el patrón `Visitor`, lo que impedía que el analizador semántico procesara correctamente los nodos.
- **Solución**: Se implementó el patrón `Visitor` en las clases del modelo (`modelo.py`).

---

### Nuevos Errores Encontrados y Soluciones

### 7. Error: Análisis Semántico no detectaba errores correctamente
- **Causa**: El analizador semántico no estaba lanzando excepciones correctamente ni generando la tabla de símbolos.
- **Solución**: Se modificó el flujo del visitor para acumular los errores encontrados y lanzar las excepciones al finalizar la validación. Además, ahora se genera e imprime correctamente la tabla de símbolos (`Symtab`).

### 8. Error: Dispatch incorrecto de excepciones
- **Causa**: Las excepciones capturadas por el analizador semántico no contenían la información del error, entregaban un dispatch en lugar de un `raise` correcto.
- **Solución**: Se ajustó la gestión de errores para realizar un `raise` explícito de las excepciones con el mensaje adecuado, permitiendo una mejor trazabilidad de fallos.

### 9. Error: Tokenización y parseo incorrecto de tipos de datos
- **Causa**: Existían problemas al tokenizar y parsear correctamente los tipos de datos básicos (`int`, `float`, `char`, `bool`).
- **Solución**: Se corrigieron las reglas de tokenización (`tokenize.py`) y el parseo en el analizador sintáctico (`parser.py`) para interpretar correctamente los literales y tipos de datos.

### 10. Validación final de errores semánticos
- **Causa**: No se había verificado que el analizador semántico detectara todos los errores esperados en distintos casos de prueba.
- **Solución**: Se realizaron pruebas adicionales para confirmar la correcta detección de errores semánticos, asegurando que tanto la acumulación de errores como la tabla de símbolos funcionen de forma estable.

### Nuevos Errores Encontrados y Soluciones código intermedio

### 1. Manejo de Ámbitos
- **Problema**: Confusión entre variables locales y globales
- **Solución**: Implementación de una jerarquía de tablas de símbolos con ámbitos anidados

### 2. Generación de Código IR
- **Problema**: Dificultad en la generación de código para expresiones complejas
- **Solución**: Corrección de un sistema de visitantes para recorrer el AST

### 3. Manejo de Tipos
- **Problema**: Mal manejo de tipos en expresiones y localizaciones debido a tipos no definidos
- **Solución**: Asignación de tipos durante la verificación en el analizador semántico

### 4. Construcción de Expresiones Binarias
- **Problema**: Errores en la construcción de nodos BinOp y asignación de tipos
- **Solución**: Corrección en la creación de nodos AST y asignación de tipos a las expresiones

### 5. Pruebas Unitarias
- **Problema**: Complejidad en la construcción de casos de prueba
- **Solución**: Creación de un framework de pruebas que simula el entorno de ejecución

### 6. Inicialización de Tabla de Símbolos
- **Problema**: Falta de parámetros requeridos en la construcción de Symtab
- **Solución**: Implementación correcta de la inicialización con nombre y tipo de ámbito

### 7. Manejo de Variables en Pruebas
- **Problema**: Variables no registradas en la tabla de símbolos antes de su uso
- **Solución**: Registro de variables en el ámbito correcto antes de su utilización en las pruebas 

### 8. Ámbitos en Ciclos
- **Problema**: Definición incorrecta de variables locales dentro de ciclos
- **Solución**: Simplificación del modelo de ámbitos a solo dos niveles: global y función 

---

## Pruebas Unitarias

Las pruebas unitarias (`test_ircode.py`) cubren:

1. **Generación de Código Completo**
   - Prueba de generación de código para el algoritmo de Shor
   - Verificación de la estructura del módulo y sus funciones
   - Validación de parámetros y tipos de retorno de funciones

2. **Declaración de Variables**
   - Prueba de declaración de variables con inicialización
   - Verificación de asignación de valores iniciales
   - Validación de tipos de variables

3. **Instrucciones de Retorno**
   - Prueba de instrucciones return con valores
   - Verificación de la generación correcta de código RET
   - Validación de valores de retorno

4. **Instrucciones de Impresión**
   - Prueba de instrucciones print con diferentes tipos
   - Verificación de la generación correcta de código PRINTI
   - Validación de la impresión de valores enteros

---

## Pendiente por Implementar

### MemoryAddress
- Implementación de operaciones de memoria directa
- Soporte para:
  - PEEKI/PEEKF: Lectura de memoria
  - POKEI/POKEF: Escritura en memoria
  - GROW: Incremento de memoria
- Manejo de direcciones de memoria para:
  - Arrays
  - Punteros
  - Estructuras de datos dinámicas

---

## Conclusión

El compilador GoxLang ha alcanzado un hito significativo con la implementación de la generación de código intermedio. Las pruebas unitarias actuales demuestran la funcionalidad básica del generador de código IR, cubriendo:

- Generación de código para programas completos
- Manejo de variables y sus tipos
- Instrucciones de control básicas
- Funciones y sus parámetros

### Estado Actual
- ✅ Análisis léxico y sintáctico
- ✅ Verificación semántica
- ✅ Generación de código IR básica
- ✅ Pruebas unitarias para funcionalidad core

Angie Carolina Vargas Villegas  
David Santiago Lugo Cabrera