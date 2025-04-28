# Goxlang Compiler

Este proyecto implementa un compilador para el lenguaje Goxlang. El compilador incluye un analizador léxico, un analizador sintáctico, y un analizador semántico. A continuación, se describe la estructura del proyecto, el funcionamiento de cada componente, y los problemas encontrados durante el desarrollo.

---

## Estructura del Proyecto

El proyecto está organizado en las siguientes carpetas:

- `lexer/`: Contiene el analizador léxico (`tokenize.py`).
- `parser/`: Contiene el analizador sintáctico (`parser.py`) y el modelo del AST (`modelo.py`).
- `semantic/`: Contiene el analizador semántico (`check.py`, `symtab.py`, `typesys.py`).
- `samples/`: Contiene ejemplos de código fuente en Goxlang.
- `outputs/`: Contiene los resultados generados, como el AST en formato JSON.

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

---

## Pruebas Unitarias

Se implementaron pruebas unitarias para el analizador semántico (`check.py`) utilizando mocks para simular nodos del AST. Estas pruebas verifican el comportamiento del visitor y la validación de tipos.

---

## Problemas Pendientes

1. **Validación Semántica, Sintáctica y Léxica de algunos casos**:
   - Ahora el analizador funciona correctamente. Pueden existir casos aislados que les falte detección de errores.

2. **Ejecución del Código**:
   - Actualmente, no hay un intérprete o generador de código para ejecutar programas en Goxlang.

---

## Conclusión

El analizador sintáctico ahora funciona correctamente y genera un AST válido. Además, se han corregido múltiples errores en el analizador semántico, incluyendo problemas en el modelo del AST, la implementación del patrón Visitor, y la gestión de excepciones. Actualmente, el analizador semántico genera una tabla de símbolos válida y detecta errores semánticos de manera estable. Sin embargo, se recomienda realizar pruebas adicionales para cubrir casos límite y garantizar la robustez del sistema. También se sugiere implementar un intérprete o generador de código para completar el flujo del compilador.

Angie Carolina Vargas Villegas  
David Santiago Lugo Cabrera