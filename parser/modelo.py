# model.py

# Este archivo define un modelo de datos para los programas de goxlang.
# Básicamente, el modelo de datos es una gran estructura que representa
# el contenido de un programa como objetos, en lugar de texto.
# A veces, esta estructura se conoce como un árbol de sintaxis abstracta (AST).
# Sin embargo, el modelo no está necesariamente ligado directamente a la
# sintaxis del lenguaje, por lo que es mejor pensarlo como un modelo de 
# datos más general.
#
# Para hacer esto, es necesario identificar los diferentes "elementos" que componen
# un programa y codificarlos en clases. Para esto, puede ser útil "no sobrepensar" 
# el problema. Para ilustrar, suponga que se desea codificar la idea de "asignar 
# un valor".  La asignación involucra una localización (lado izquierdo) y un valor
# como esto:
#
#       location = expression;
#
# Para representar esta idea, cree una clase con estas partes:
#
#       class Assignment:
#           def __init__(self, location, expression):
#               self.location = location
#               self.expression = expression
# 
# Ahora bien, ¿qué son "location" y "expression"? ¿importa? talvez no.
# Todo lo que sabemos es que un operador de asignación requiere ambas partes.
# NO LO PIENSE DEMASIADO. Se completarán mas detalles a medida que el proyecto
# evolucione.
#
# Este archivo se divide en secciones que describen partes de la especificación
# del lenguaje goxlang en forma de comentarios. Se debe adaptar esta 
# especificación a código real. Para ayudarte a guiarte, mira el archivo
# "program.py".
#
# Al pricipio te aconsejo que no hagas que este archivo sea demasiado
# sofisticado. Solo usa definiciones de clases de Python básico. Puedes
# agregar mejoras de usabilidad mas adelante.
#
# ------------------------------------------------------------------------------------

# DEFINICIÓN DE LA ESTRUCTURA DELL AST PARA EL LENGUAJE GLOXLANG

from dataclasses import dataclass, field
from multimethod import multimeta
from typing      import List

# ======================================================
# Definiciones de Clases Abstractas
# ======================================================
class Visitor(metaclass=multimeta):
  pass

@dataclass
class Node:
    def accept(self, v: Visitor, env):
        return v.visit(self, env)

# Clases base
@dataclass
class Statement(Node):
  pass

@dataclass
class Expression(Node):
  pass

# ------------------------------------------------------------------------------------
@dataclass
class Program(Statement):
  stmts : List[Statement] = field(default_factory=list)


# ----------------------------------------------------------------------
# Parte 1. Statements
#
# Los programas en goxlang consisten en sentencias. Estas incluyen
# operaciones como asignación, I/O (imprimir), control de flujo, entre otras.
#
# 1.1 Assignment
#
#     location = expression ;

@dataclass
class Assignment(Statement):
  loc : Expression
  expr: Expression

#
# 1.2 Printing
#     print expression ;

@dataclass
class Print(Statement):
    expression: Expression

#
# 1.3 Conditional
#     if test { consequence } else { alternative }
#

@dataclass
class If(Statement):
    test: Expression
    consequence: Statement
    alternative: Statement = None

# 1.4 While Loop
#     while test { body }
#

@dataclass
class While(Statement):
    test: Expression
    body: Statement

# 1.5 Break y Continue
#     while test {
#         ...
#         break;   // continue
#     }
#

@dataclass
class Break(Statement):
    pass

@dataclass
class Continue(Statement):
    pass

# 1.6 Return un valor
#     return expresion ;

@dataclass
class Return(Statement):
    expression: Expression

# ----------------------------------------------------------------------
# Parte 2. Definictions/Declarations
#
# goxlang requiere que todas las variables y funciones se declaren antes de 
# ser utilizadas.  Todas las definiciones tienen un nombre que las identifica.
# Estos nombres se definen dentro de un entorno que forma lo que se denomina
# un "ámbito".  Por ejemplo, ámbito global o ámbito local.

# 2.1 Variables.  Las Variables pueden ser declaradas de varias formas.
#
#     const name = value;
#     const name [type] = value;
#     var name type [= value];
#     var name [type] = value;

@dataclass
class Variable(Statement):
    name: str
    type: str = None
    value: Expression = None
    is_const: bool = False

#
# Las Constantes son inmutable. Si un valor está presente, el tipo puede ser 
# omitido e inferir desde el tipo del valor.
#
# 2.2 Function definitions.
#
#     func name(parameters) return_type { statements }
#
# Una función externa puede ser importada usando una sentencia especial:
#
#     import func name(parameters) return_type;
#   

@dataclass
class Function(Statement):
    name: str
    parameters: List['Parameter']
    return_type: str
    body: List[Statement]

#
# 2.3 Function Parameters
#
#     func square(x int) int { return x*x; }
#
# Un parametro de función (p.ej., "x int") es una clase de variable especial.
# Tiene un nombre y un tipo como una variable, pero es declarada como parte
# de la definición de una función, no como una declaración "var" separada.
#

@dataclass
class Parameter:
    name: str
    type: str
    
# README

# ----------------------------------------------------------------------
# Parte 3. Expressions
#
# Las expresiones representan elementos que se evalúan y producen un valor concreto.
#
# goxlang define las siguientes expressiones y operadores
#
# 3.1 Literals
#     23           (Entero)
#     4.5          (Flotante)
#     true,false   (Booleanos)
#     'c'          (Carácter)

@dataclass
class Literal(Expression):
    pass

@dataclass
class Integer(Literal):
    value: int

    @property
    def type(self):
        return 'int'

@dataclass
class Float(Literal):
    value: float

    @property
    def type(self):
        return 'float'

@dataclass
class Bool(Literal):
    value: bool

    @property
    def type(self):
        return 'bool'

@dataclass
class Char(Literal):
    value: str

    @property
    def type(self):
        return 'char'

#
# 3.2 Binary Operators
#     left + right   (Suma)
#     left - right   (Resta)
#     left * right   (Multiplicación)
#     left / right   (División)
#     left < right   (Menor que)
#     left <= right  (Menor o igual que)
#     left > right   (Mayor que)
#     left >= right  (Mayor o igual que)
#     left == right  (Igual a)
#     left != right  (Diferente de)
#     left && right  (Y lógico)
#     left || right  (O lógico)

@dataclass
class BinOp(Expression):
    op: str
    left: Expression
    right: Expression

#
# 3.3 Unary Operators
#     +operand  (Positivo)
#     -operand  (Negación)
#     !operand  (Negación lógica)
#     ^operand  (Expandir memoria)

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

#
# 3.4 Lectura de una ubicación (vea mas adelante)
#     location
#
# 3.5 Conversiones de tipo
#     int(expr)  
#     float(expr)

@dataclass
class TypeCast(Expression):
    target_type: str
    expression: Expression

#
# 3.6 Llamadas a función
#     func(arg1, arg2, ..., argn)

@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]

#
# ----------------------------------------------------------------------
# Parte 4: Locations
#
# Una ubicación representa un lugar donde se almacena un valor. Lo complicado
# de las ubicaciones es que se usan de dos maneras diferentes.
# Primero, una ubicación podría aparecer en el lado izquierdo de una asignación
# de esta manera:
#
#     location = expression;        // Almacena un valor dentro de location
#
# Sin embargo, una ubicación podria aparecer como parte de una expresión:
#
#     print location + 10;          // Lee un valor desde location
#
# Una ubicación no es necesariamente simple nombre de variable. Por ejemplo,
# considere el siguiente ejemplo en Python:
#
#     >>> a = [1,2,3,4] 
#     >>> a[2] = 10                 // Almacena en ubicación "a[2]"
#     >>> print(a[2])               // Lee desde ubicación "a[2]" 
#
# goxlang tiene dos tipos de locations (ubicaciones):
#
# 4.1 Ubicaciones primitivas
#
#     abc = 123;
#     print abc;
#
#     Cualquier nombre usado debe referirse a una definición de variable existente.
#     Por ejemplo, "abc" en este ejmeplo debe tener una declaración correspondiente
#     tal como
#
#     var abc int;

@dataclass
class Location(Expression):
    name: str

#
# 4.2 Direcciones de memoria. Un número entero precedido por una comilla invertida (``)
#
#     `address = 123;
#     print `address + 10;
#

@dataclass
class MemoryAddress(Expression):
    address: int

# 4.3 Ubicaciones nombradas
#
#     Una ubicación nombrada se refiere a una variable con un nombre específico.
#     Por ejemplo:
#
#     var x int;
#     x = 42;
#     print x;

@dataclass
class NamedLocation(Location):
    type: str = None

# Nota: Históricamente, comprender la naturaleza de las ubicaciones ha sido
# una de las partes pas dificiles del proyecto del compilador.  Se espera
# mucho mas debate sobre este tema. Sugiero enfáticamente posponer el trabajo de las
# direcciones hasta mucho mas adelantes del proyecto.
