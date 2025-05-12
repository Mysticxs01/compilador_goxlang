# Compilador GoxLang

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

## Problemas Encontrados y Soluciones

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