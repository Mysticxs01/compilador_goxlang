# typesys.py
'''
Sistema de tipos
================
Este archivo implementa las características básicas del sistema de tipos. Existe 
mucha flexibilidad, pero la mejor estrategia podría ser no darle demasiadas 
vueltas al problema. Al menos no al principio. Estos son los requisitos 
básicos mínimos:

1. Los tipos tienen identidad (p. ej., al menos un nombre como 'int', 'float', 'char').
2. Los tipos deben ser comparables (p. ej., int != float).
3. Los tipos admiten diferentes operadores (p. ej., +, -, *, /, etc.).

Una forma de lograr todos estos objetivos es comenzar con algún tipo de 
enfoque basado en tablas. No es lo más sofisticado, pero funcionará 
como punto de partida. Puede volver a refactorizar el sistema de tipos
más adelante.
'''

typenames = { 'int', 'float', 'char', 'bool' }

# Capabilities
bin_ops = {
    # Integer operations
    ('int', 'PLUS', 'int') : 'int',
    ('int', 'MINUS', 'int') : 'int',
    ('int', 'TIMES', 'int') : 'int',
    ('int', 'DIVIDE', 'int') : 'int',

    ('int', 'LT', 'int')  : 'bool',
    ('int', 'LE', 'int') : 'bool',
    ('int', 'GT', 'int')  : 'bool',
    ('int', 'GE', 'int') : 'bool',
    ('int', 'EQ', 'int') : 'bool',
    ('int', 'NE', 'int') : 'bool',

    # Float operations
    ('float', 'PLUS', 'float') : 'float',
    ('float', 'MINUS', 'float') : 'float',
    ('float', 'TIMES', 'float') : 'float',
    ('float', 'DIVIDE', 'float') : 'float',

    ('float', 'LT', 'float')  : 'bool',
    ('float', 'LE', 'float') : 'bool',
    ('float', 'GT', 'float')  : 'bool',
    ('float', 'GE', 'float') : 'bool',
    ('float', 'EQ', 'float') : 'bool',
    ('float', 'NE', 'float') : 'bool',

    # Bools
    ('bool', 'LAND', 'bool') : 'bool',
    ('bool', 'LOR', 'bool') : 'bool',
    ('bool', 'EQ', 'bool') : 'bool',
    ('bool', 'NE', 'bool') : 'bool',

    # Char
    ('char', 'LT', 'char')  : 'bool',
    ('char', 'LE', 'char') : 'bool',
    ('char', 'GT', 'char')  : 'bool',
    ('char', 'GE', 'char') : 'bool',
    ('char', 'EQ', 'char') : 'bool',
    ('char', 'NE', 'char') : 'bool',
}

# Check if a binary operator is supported. Returns the
# result type or None (if not supported). Type checker
# uses this function.

def check_binop(op, left_type, right_type):
    result = bin_ops.get((left_type, op, right_type))
    return result

unary_ops = {
    ('PLUS', 'int') : 'int',
    ('MINUS', 'int') : 'int',
    ('GROW', 'int') : 'int',
    
    ('PLUS', 'float') : 'float',
    ('MINUS', 'float') : 'float',

    ('NOT', 'bool') : 'bool',
}

def check_unaryop(op, operand_type):
    return unary_ops.get((op, operand_type))

