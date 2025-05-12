# ircode.py
'''
Una Máquina Intermedia "Virtual"
================================

Una CPU real generalmente consta de registros y un pequeño conjunto de
códigos de operación básicos para realizar cálculos matemáticos,
cargar/almacenar valores desde memoria y controlar el flujo básico
(ramas, saltos, etc.). Aunque puedes hacer que un compilador genere
instrucciones directamente para una CPU, a menudo es más sencillo
dirigirse a un nivel de abstracción más alto. Una de esas abstracciones
es la de una máquina de pila (stack machine).

Por ejemplo, supongamos que deseas evaluar una operación como esta:

    a = 2 + 3 * 4 - 5

Para evaluar la expresión anterior, podrías generar pseudo-instrucciones
como esta:

    CONSTI 2      ; stack = [2]
    CONSTI 3      ; stack = [2, 3]
    CONSTI 4      ; stack = [2, 3, 4]
    MULI          ; stack = [2, 12]
    ADDI          ; stack = [14]
    CONSTI 5      ; stack = [14, 5]
    SUBI          ; stack = [9]
    LOCAL_SET "a" ; stack = []

Observa que no hay detalles sobre registros de CPU ni nada por el estilo
aquí. Es mucho más simple (un módulo de nivel inferior puede encargarse
del mapeo al hardware más adelante si es necesario).

Las CPUs usualmente tienen un pequeño conjunto de tipos de datos como
enteros y flotantes. Existen instrucciones dedicadas para cada tipo. El
código IR seguirá el mismo principio, admitiendo operaciones con enteros
y flotantes. Por ejemplo:

    ADDI   ; Suma entera
    ADDF   ; Suma flotante

Aunque el lenguaje de entrada podría tener otros tipos como `bool` y
`char`, esos tipos deben ser mapeados a enteros o flotantes. Por ejemplo,
un bool puede representarse como un entero con valores {0, 1}. Un char
puede representarse como un entero cuyo valor sea el mismo que el código
del carácter (es decir, un código ASCII o código Unicode).

Con eso en mente, aquí hay un conjunto básico de instrucciones para
nuestro Código IR:

    ; Operaciones enteras
    CONSTI value             ; Apilar un literal entero
    ADDI                     ; Sumar los dos elementos superiores de la pila
    SUBI                     ; Restar los dos elementos superiores de la pila
    MULI                     ; Multiplicar los dos elementos superiores de la pila
    DIVI                     ; Dividir los dos elementos superiores de la pila
    ANDI                     ; AND bit a bit
    ORI                      ; OR bit a bit
    LTI                      : <
    LEI                      : <=
    GTI                      : >
    GEI                      : >=
    EQI                      : ==
    NEI                      : !=
    PRINTI                   ; Imprimir el elemento superior de la pila
    PEEKI                    ; Leer entero desde memoria (dirección en la pila)
    POKEI                    ; Escribir entero en memoria (valor, dirección en la pila)
    ITOF                     ; Convertir entero a flotante

    ; Operaciones en punto flotante
    CONSTF value             ; Apilar un literal flotante
    ADDF                     ; Sumar los dos elementos superiores de la pila
    SUBF                     ; Restar los dos elementos superiores de la pila
    MULF                     ; Multiplicar los dos elementos superiores de la pila
    DIVF                     ; Dividir los dos elementos superiores de la pila
    LTF                      : <
    LEF                      : <=
    GTF                      : >
    GEF                      : >=
    EQF                      : ==
    NEF                      : !=
    PRINTF                   ; Imprimir el elemento superior de la pila
    PEEKF                    ; Leer flotante desde memoria (dirección en la pila)
    POKEF                    ; Escribir flotante en memoria (valor, dirección en la pila)
    FTOI                     ; Convertir flotante a entero

    ; Operaciones orientadas a bytes (los valores se presentan como enteros)
    PRINTB                   ; Imprimir el elemento superior de la pila
    PEEKB                    ; Leer byte desde memoria (dirección en la pila)
    POKEB                    ; Escribir byte en memoria (valor, dirección en la pila)

    ; Carga/almacenamiento de variables.
    ; Estas instrucciones leen/escriben variables locales y globales. Las variables
    ; son referenciadas por algún tipo de nombre que las identifica. La gestión
    ; y declaración de estos nombres también debe ser manejada por tu generador de código.
    ; Sin embargo, las declaraciones de variables no son una instrucción normal. En cambio,
    ; es un tipo de dato que debe asociarse con un módulo o función.
    LOCAL_GET name           ; Leer una variable local a la pila
    LOCAL_SET name           ; Guardar una variable local desde la pila
    GLOBAL_GET name          ; Leer una variable global a la pila
    GLOBAL_SET name          ; Guardar una variable global desde la pila

    ; Llamadas y retorno de funciones.
    ; Las funciones se referencian por nombre. Tu generador de código deberá
    ; encontrar alguna manera de gestionar esos nombres.
    CALL name                ; Llamar función. Todos los argumentos deben estar en la pila
    RET                      ; Retornar de una función. El valor debe estar en la pila

    ; Control estructurado de flujo
    IF                       ; Comienza la parte "consecuencia" de un "if". Prueba en la pila
    ELSE                     ; Comienza la parte "alternativa" de un "if"
    ENDIF                    ; Fin de una instrucción "if"

    LOOP                     ; Inicio de un ciclo
    CBREAK                   ; Ruptura condicional. Prueba en la pila
    CONTINUE                 ; Regresa al inicio del ciclo
    ENDLOOP                  ; Fin del ciclo

    ; Memoria
    GROW                     ; Incrementar memoria (tamaño en la pila) (retorna nuevo tamaño)

Una palabra sobre el acceso a memoria... las instrucciones PEEK y POKE
se usan para acceder a direcciones de memoria cruda. Ambas instrucciones
requieren que una dirección de memoria esté en la pila *primero*. Para
la instrucción POKE, el valor a almacenar se apila después de la dirección.
El orden es importante y es fácil equivocarse. Así que presta mucha
atención a eso.

Su tarea
=========
Su tarea es la siguiente: Escribe código que recorra la estructura del
programa y la aplane a una secuencia de instrucciones representadas como
tuplas de la forma:

       (operation, operands, ...)

Por ejemplo, el código del principio podría terminar viéndose así:

    code = [
       ('CONSTI', 2),
       ('CONSTI', 3),
       ('CONSTI', 4),
       ('MULI',),
       ('ADDI',),
       ('CONSTI', 5),
       ('SUBI',),
       ('LOCAL_SET', 'a'),
    ]

Funciones
=========
Todo el código generado está asociado con algún tipo de función. Por
ejemplo, con una función definida por el usuario como esta:

    func fact(n int) int {
        var result int = 1;
        var x int = 1;
        while x <= n {
            result = result * x;
            x = x + 1;
        }
     }

Debes crear un objeto `Function` que contenga el nombre de la función,
los argumentos, el tipo de retorno, las variables locales y un cuerpo
que contenga todas las instrucciones de bajo nivel. Nota: en este nivel,
los tipos representarán tipos IR de bajo nivel como Integer (I) y Float (F).
No son los mismos tipos usados en el código GoxLang de alto nivel.

Además, todo el código que se define *fuera* de una función debe ir
igualmente en una función llamada `_init()`. Por ejemplo, si tienes
declaraciones globales como esta:

     const pi = 3.14159;
     const r = 2.0;
     print pi*r*r;

Tu generador de código debería en realidad tratarlas así:

     func _init() int {
         const pi = 3.14159;
         const r = 2.0;
         print pi*r*r;
         return 0;
     }

En resumen: todo el código debe ir dentro de una función.

Módulos
=======
La salida final de la generación de código debe ser algún tipo de
objeto `Module` que contenga todo. El módulo incluye objetos de función,
variables globales y cualquier otra cosa que puedas necesitar para
generar código posteriormente.
'''
from rich   import print
from typing import List, Union

from parser.modelo  import *
from semantic.symtab import Symtab

# Todo el código IR se empaquetará en un módulo. Un 
# módulo es un conjunto de funciones.

class IRModule:
	def __init__(self):
		self.functions = { }       # Dict de funciones IR 
		self.globals = { }         # Dict de variables global
		
	def dump(self):
		print("MODULE:::")
		for glob in self.globals.values():
			glob.dump()
			
		for func in self.functions.values():
			func.dump()
			
# Variables Globales
class IRGlobal:
	def __init__(self, name, type):
		self.name = name
		self.type = type
		
	def dump(self):
		print(f"GLOBAL::: {self.name}: {self.type}")

# Las funciones sirven como contenedor de las 
# instrucciones IR de bajo nivel específicas de cada
# función. También incluyen metadatos como el nombre 
# de la función, los parámetros y el tipo de retorno.

class IRFunction:
	def __init__(self, module, name, parmnames, parmtypes, return_type, imported=False):
		# Agreguemos la lista de funciones del módulo adjunto
		self.module = module
		module.functions[name] = self
		
		self.name = name
		self.parmnames = parmnames
		self.parmtypes = parmtypes
		self.return_type = return_type
		self.imported = imported
		self.locals = { }    # Variables Locales
		self.code = [ ]      # Lista de Instrucciones IR 
		
	def new_local(self, name, type):
		self.locals[name] = type
		
	def append(self, instr):
		self.code.append(instr)
		
	def extend(self, instructions):
		self.code.extend(instructions)
		
	def dump(self):
		print(f"FUNCTION::: {self.name}, {self.parmnames}, {self.parmtypes} {self.return_type}")
		print(f"locals: {self.locals}")
		for instr in self.code:
			print(instr)
			
# Mapeo de tipos de GoxLang a tipos de IR
_typemap = {
	'int'  : 'I',
	'float': 'F',
	'bool' : 'I',
	'char' : 'I',
}

# Generar un nombre de variable temporal único
def new_temp(n=[0]):
	n[0] += 1
	return f'$temp{n[0]}'

# Una función de nivel superior que comenzará a generar IRCode

class IRCode(Visitor):
	_binop_code = {
		('int', 'PLUS', 'int')  : 'ADDI',
		('int', 'MINUS', 'int')  : 'SUBI',
		('int', 'TIMES', 'int')  : 'MULI',
		('int', 'DIVIDE', 'int')  : 'DIVI',
		('int', 'LT', 'int')  : 'LTI',
		('int', 'LE', 'int') : 'LEI',
		('int', 'GT', 'int')  : 'GTI',
		('int', 'GE', 'int') : 'GEI',
		('int', 'EQ', 'int') : 'EQI',
		('int', 'NE', 'int') : 'NEI',

		('float', 'PLUS',  'float') : 'ADDF',
		('float', 'MINUS',  'float') : 'SUBF',
		('float', 'TIMES',  'float') : 'MULF',
		('float', 'DIVIDE',  'float') : 'DIVF',
		('float', 'LT',  'float') : 'LTF',
		('float', 'LE', 'float') : 'LEF',
		('float', 'GT',  'float') : 'GTF',
		('float', 'GE', 'float') : 'GEF',
		('float', 'EQ', 'float') : 'EQF',
		('float', 'NE', 'float') : 'NEF',
		
		('char', 'LT', 'char')  : 'LTI',
		('char', 'LE', 'char') : 'LEI',
		('char', 'GT', 'char')  : 'GTI',
		('char', 'GE', 'char') : 'GEI',
		('char', 'EQ', 'char') : 'EQI',
		('char', 'NE', 'char') : 'NEI',
	}
	_unaryop_code = {
		('PLUS', 'int')   : [],
		('PLUS', 'float') : [],
		('MINUS', 'int')   : [('CONSTI', -1), ('MULI',)],
		('MINUS', 'float') : [('CONSTF', -1.0), ('MULF',)],
		('NOT', 'bool')  : [('CONSTI', -1), ('MULI',)],
		('^', 'int')   : [ ('GROW',) ]
	}
	_typecast_code = {
		# (from, to) : [ ops ]
		('int', 'float') : [ ('ITOF',) ],
		('float', 'int') : [ ('FTOI',) ],
	}

	def __init__(self, env):
		self.env = env  # Tabla de símbolos

	@classmethod
	def gencode(cls, node:List[Statement], env):
		'''
		El nodo es el nodo superior del árbol de 
		modelo/análisis.
		La función inicial se llama "_init". No acepta 
		argumentos. Devuelve un entero.
		'''
		ircode = cls(env)
		
		module = IRModule()
		func = IRFunction(module, 'main', [], [], 'I')
		for item in node:
			item.accept(ircode, func)
		if '_actual_main' in module.functions:
			func.append(('CALL', '_actual_main'))
		else:
			func.append(('CONSTI', 0))
		func.append(('RET',))
		return module

	# --- Statements
	
	def visit(self, n:Assignment, func:IRFunction):
		#Acepta para Assignment
		n.expr.accept(self, func)
		if isinstance(n.loc, NamedLocation):
			# Determinar si es local o global basado en el scope
			scope = self.env.find_scope_of_type_name_child("function", n.loc.name)
			if scope:
				func.append(('LOCAL_SET', n.loc.name))
			else:
				func.append(('GLOBAL_SET', n.loc.name))
		else:
			func.append(('POKEI',))

	def visit(self, n:Print, func:IRFunction):
		#Acepta para Print, diferencia entre int y float
		n.expression.accept(self, func)
		# Determinar el tipo de la expresión
		expr_type = self._get_expression_type(n.expression)
		if expr_type == 'int':
			func.append(('PRINTI',))
		elif expr_type == 'float':
			func.append(('PRINTF',))
		else:
			func.append(('PRINTB',))

	def _get_expression_type(self, expr):
		if hasattr(expr, 'type'):
			return expr.type
		elif isinstance(expr, BinOp):
			left_type = self._get_expression_type(expr.left)
			right_type = self._get_expression_type(expr.right)
			# Si ambos operandos son del mismo tipo, ese es el tipo resultante
			if left_type == right_type:
				return left_type
			# Si uno es float, el resultado es float
			if left_type == 'float' or right_type == 'float':
				return 'float'
			# Por defecto, si son enteros, el resultado es entero
			return 'int'
		elif isinstance(expr, UnaryOp):
			return self._get_expression_type(expr.operand)
		elif isinstance(expr, FunctionCall):
			return self.env.get(expr.name).return_type
		else:
			raise TypeError(f"No se puede determinar el tipo de la expresión {expr}")

	def visit(self, n:If, func:IRFunction):
		#Acepta para If
		n.test.accept(self, func)
		func.append(('IF',))
		for stmt in n.consequence:
			stmt.accept(self, func)
		func.append(('ELSE',))
		if n.alternative:
			for stmt in n.alternative:
				stmt.accept(self, func)
		func.append(('ENDIF',))

	def visit(self, n:While, func:IRFunction):
		#Acepta para While
		func.append(('LOOP',))
		func.append(('CONSTI', 1))
		n.test.accept(self, func)
		func.append(('SUBI',))
		func.append(('CBREAK',))
		for stmt in n.body:
			stmt.accept(self, func)
		func.append(('ENDLOOP',))

	def visit(self, n:Break, func:IRFunction):
		#Acepta para Break
		func.append(('CBREAK',))

	def visit(self, n:Continue, func:IRFunction):
		#Acepta para Continue
		func.append(('CONTINUE',))

	def visit(self, n:Return, func:IRFunction):
		#Acepta para Return
		if n.expression:
			n.expression.accept(self, func)
		func.append(('RET',))

	# --- Declaration
		
	def visit(self, n:Variable, func:IRFunction):
		#Acepta para Variable
		if n.value:
			n.value.accept(self, func)
			# Solo crear variable local si estamos dentro de una función
			scope = self.env.find_scope_of_type_name_child("function", n.name)
			if scope:
				if n.value != None:
					func.append(('LOCAL_SET', n.name))
				func.new_local(n.name, _typemap[n.type])
			else:
				# Si es global, agregar al módulo
				if n.value != None:
					func.append(('GLOBAL_SET', n.name))
				func.module.globals[n.name] = IRGlobal(n.name, _typemap[n.type])

	def visit(self, n:Function, func:IRFunction):
		#Acepta para Function
		module = func.module
		new_func = IRFunction(module, n.name, 
							[p.name for p in n.parameters],
							[_typemap[p.type] for p in n.parameters],
							_typemap[n.return_type])
		
		# Procesar el cuerpo de la función
		for stmt in n.body:
			stmt.accept(self, new_func)

	# --- Expressions
	
	def visit(self, n:Integer, func:IRFunction):
		#Acepta para Integer
		func.append(('CONSTI', n.value))

	def visit(self, n:Float, func:IRFunction):
		#Acepta para Float
		func.append(('CONSTF', n.value))
	def visit(self, n:Char, func:IRFunction):
		#Acepta para Char
		func.append(('CONSTB', n.value))

	def visit(self, n:Bool, func:IRFunction):
		#Acepta para Bool
		func.append(('CONSTI', 1 if n.value else 0))

	def visit(self, n:BinOp, func:IRFunction):
		#Acepta para BinOp
		n.left.accept(self, func)
		n.right.accept(self, func)
		left_type = self._get_expression_type(n.left)
		right_type = self._get_expression_type(n.right)
		func.append((self._binop_code[(left_type, n.op, right_type)],))

	def visit(self, n:UnaryOp, func:IRFunction):
		#Acepta para UnaryOp
		n.operand.accept(self, func)
		for instr in self._unaryop_code[(n.op, n.operand.type)]:
			func.append(instr)

	def visit(self, n:TypeCast, func:IRFunction):
		#Acepta para TypeCast
		n.expression.accept(self, func)
		if n.target_type == 'float' and n.expression.type == 'int':
			func.append(('ITOF',))
		elif n.target_type == 'int' and n.expression.type == 'float':
			func.append(('FTOI',))

	def visit(self, n:FunctionCall, func:IRFunction):
		#Acepta para FunctionCall
		for arg in n.arguments:
			arg.accept(self, func)
		func.append(('CALL', n.name))

	def visit(self, n:NamedLocation, func:IRFunction):
		#Acepta para NamedLocation
		# Determinar si es local o global basado en el scope
		scope = self.env.find_scope_of_type_name_child("function", n.name)
		if scope and scope.get(n.name):
			func.append(('LOCAL_GET', n.name))
		else:
			func.append(('GLOBAL_GET', n.name))

	def visit(self, n:MemoryAddress, func:IRFunction):
		if n.usage == 'load':
			# Visitar n.address
			n.address.accept(self, func)
			if n.type in {'int', 'bool'}:
				func.append('PEEKI',)
			elif n.type == 'float':
				func.append('PEEKF',)
			elif n.type == 'char':
				func.append('PEEKB',)
		elif n.usage == 'store':
			# Visitar n.address
			n.address.accept(self, func)
			# Visitar n.store_value (agregado en nodo Assignment)
			n.store_value.accept(self, func)
			if n.type in {'int', 'bool'}:
				func.append('POKEI',)
			elif n.type == 'float':
				func.append('POKEF',)
			elif n.type == 'char':
				func.append('POKEB',)


if __name__ == '__main__':
	import sys
	
	from parser.parser import Parser
	from lexer.tokenizer import Lexer, tokens_spec
	from semantic.check import Checker

	#if len(sys.argv) != 2:
	#	raise SystemExit("Usage: python ircode.py <filename>")
	
	source_path = "samples/shor.gox"
	txt = open(source_path, encoding='utf-8').read()
	
	lexer = Lexer(tokens_spec)
	tokens = lexer.tokenize(txt)
	
	top = Parser(tokens)
	ast = top.parse()

	env = Checker.check(ast)
		
	module = IRCode.gencode(ast.stmts, env)
	module.dump()
		
