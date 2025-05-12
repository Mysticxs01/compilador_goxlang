# check.py
'''
Este archivo contendrá la parte de verificación/validación de tipos
del compilador.  Hay varios aspectos que deben gestionarse para
que esto funcione. Primero, debe tener una noción de "tipo" en su compilador.
Segundo, debe administrar los entornos y el alcance para manejar los
nombres de las definiciones (variables, funciones, etc.).

Una clave para esta parte del proyecto es realizar pruebas adecuadas.
A medida que agregue código, piense en cómo podría probarlo.
'''
from multimethod import multimethod
from rich    import print
from rich.table import Table
from typing  import Union

from parser.modelo   import *
from semantic.symtab  import Symtab
from semantic.typesys import typenames, check_binop, check_unaryop


class Checker(Visitor):
    def __init__(self):
        self.errors = []  # <-- Aquí guardamos todos los errores

    @classmethod
    def check(cls, n: Node):
        check = cls()
        env = Symtab(name="global")

        try:
            if isinstance(n, Program):
                for stmt in n.stmts:
                    check._safe_accept(stmt, env)
            else:
                check._safe_accept(n, env)

            # 🚨 Si hay errores acumulados, los lanzamos juntos 🚨
            if check.errors:
                error_message = "\n".join(str(e) for e in check.errors)
                raise Exception(f"Se encontraron errores semánticos:\n{error_message}")

            print("debug: [INFO] Verificación semántica completada")
            env.print()
            return env

        except Exception as e:
            # Para asegurarnos de que capturamos errores en la etapa de check
            raise e

    def _safe_accept(self, node: Node, env: Symtab):
        try:
            node.accept(self, env)
        except Exception as e:
            self.errors.append(e)

    @multimethod
    def visit(self, n:Program, env:Symtab):
        '''
        1. recorrer la lista de elementos
        '''
        for stmt in n.stmts:
            stmt.accept(self, env)

    # Statements
    @multimethod
    def visit(self, n:Assignment, env:Symtab):
        '''
        1. Validar n.loc
        2. Visitar n.expr
        3. Verificar si son tipos compatibles
        '''
        loc_type = n.loc.accept(self, env)
        expr_type = n.expr.accept(self, env)
        if loc_type != expr_type:
            raise Exception(f"Error: No se puede asignar {expr_type} a {loc_type}")
        return loc_type
    
    @multimethod
    def visit(self, n:Print, env:Symtab):
        '''
        1. visitar n.expr
        '''
        n.expression.accept(self, env)

    @multimethod
    def visit(self, n:If, env:Symtab):
        '''
        1. Visitar n.test (validar tipos)
        2. Visitar Statement por n.consequence
        3. Si existe opción n.alternative, visitar
        '''
        test_type = n.test.accept(self, env)
        if test_type != 'bool':
            raise Exception(f"Línea {n.lineno}: Error: La condición del if debe ser de tipo bool, no {test_type}")
        
        # Visitar el bloque de la condición verdadera
        for stmt in n.consequence:
            stmt.accept(self, env)
        
        # Visitar el bloque de la condición alternativa (si existe)
        if n.alternative:
            for stmt in n.alternative:
                stmt.accept(self, env)

    @multimethod
    def visit(self, n:While, env:Symtab):
        '''
        1. Visitar n.test (validar tipos)
        2. visitar n.body
        '''
        test_type = n.test.accept(self, env)
        if test_type != 'bool':
            raise Exception(f"Línea {n.lineno}: Error: La condición del while debe ser de tipo bool")
        
        # Marcar que estamos dentro de un while
        env.add('in_while', True)
        # Visitar el cuerpo del while
        for stmt in n.body:
            stmt.accept(self, env)
        # Desmarcar al salir del while
        env.remove('in_while')

    @multimethod
    def visit(self, n:Union[Break, Continue], env:Symtab):
        '''
        1. Verificar que esta dentro de un ciclo while
        '''
        if not env.get('in_while'):
            raise Exception(f"Error: '{type(n).__name__.lower()}' debe estar dentro de un while")

    @multimethod
    def visit(self, n:Return, env:Symtab):
        '''
        1. Si se ha definido n.expr, validar que sea del mismo tipo de la función
        '''
        if not env.find_scope_of_type("function"):
            raise Exception("Error: 'return' fuera de función")
        if n.expression:
            expr_type = n.expression.accept(self, env)
            func_type = env.find_scope_of_type("function").get('return_type')
            if func_type != expr_type:
                raise Exception(f"Error: Tipo de retorno {expr_type} no coincide con {func_type}")

    @multimethod
    def visit(self, n: Float, env: Symtab):
        return n.type
    
    @multimethod
    def visit(self, n: Integer, env: Symtab):
        return n.type

    @multimethod
    def visit(self, n: Bool, env: Symtab):
        return n.type

    @multimethod
    def visit(self, n: Char, env: Symtab):
        return n.type
        
    # Declarations
    @multimethod
    def visit(self, n:Variable, env:Symtab):
        '''
        1. Agregar n.name a la TS actual
        '''
        if env.get(n.name):
            raise NameError(f"Error: La variable '{n.name}' ya está definida en este ámbito")
        if n.value:
            value_type = n.value.accept(self, env)
            if n.type and n.type != value_type:
                raise Exception(f"Error: El tipo de la variable '{n.name}' no coincide con el valor asignado")
        env.add(n.name, n)
        
    @multimethod
    def visit(self, n:Function, env:Symtab):
        '''
        1. Guardar la función en la TS actual
        2. Crear una nueva TS para la función
        3. Agregar todos los n.params dentro de la TS
        4. Visitar n.stmts
        '''
        if env.get(n.name):
            raise NameError(f"Error: La función '{n.name}' ya está definida")
        env.add(n.name, n)
        func_env = Symtab(name=n.name, parent=env, scope_type="function")
        func_env.add('return_type', n.return_type)
        for param in n.parameters:
            func_env.add(param.name, param)
        has_return = False
        for stmt in n.body:
            stmt.accept(self, func_env)
            if isinstance(stmt, Return):
                has_return = True

        # Verificar si hay un return_type pero no hay un return en el cuerpo
        if n.return_type and not has_return:
            raise Exception(f"Error: La función '{n.name}' tiene un tipo de retorno '{n.return_type}' pero no retorna ningún valor")

    @multimethod
    def visit(self, n:Parameter, env:Symtab):
        '''
        1. Guardar el parametro (name, type) en TS
        '''
        if env.get(n.name):
            raise NameError(f"Error: El parámetro '{n.name}' ya está definido en este ámbito")
        env.add(n.name, n)

    @multimethod
    def visit(self, n:BinOp, env:Symtab):
        '''
        1. visitar n.left y luego n.right
        2. Verificar compatibilidad de tipos
        '''

        left_type = n.left.accept(self, env)
        right_type = n.right.accept(self, env)
        result_type = check_binop(n.op, left_type, right_type)
        
        if not result_type:
            raise Exception(f"Error: Operación '{n.op}' no válida entre {left_type} y {right_type}")

        return result_type
        
    @multimethod
    def visit(self, n:UnaryOp, env:Symtab):
        '''
        1. visitar n.expr
        2. validar si es un operador unario valido
        '''
        expr_type = n.operand.accept(self, env)
        result_type = check_unaryop(n.op, expr_type)
        if not result_type:
            raise Exception(f"Error: Operador unario '{n.op}' no válido para el tipo {expr_type}")
        return result_type

    @multimethod
    def visit(self, n:TypeCast, env:Symtab):
        '''
        1. Visitar n.expr para validar
        2. retornar el tipo del cast n.type
        '''
        n.expression.accept(self, env)
        return n.target_type

    @multimethod
    def visit(self, n:FunctionCall, env:Symtab):
        '''
        1. Validar si n.name existe
        2. visitar n.args (si estan definidos)
        3. verificar que len(n.args) == len(func.params)
        4. verificar que cada arg sea compatible con cada param de la función
        '''
        func = env.get(n.name)
        if not func:
            raise NameError(f"Error: La función '{n.name}' no está definida")
        if len(n.arguments) != len(func.parameters):
            raise Exception(f"Error: La función '{n.name}' espera {len(func.parameters)} argumentos, pero se pasaron {len(n.arguments)}")
        for arg, param in zip(n.arguments, func.parameters):
            arg_type = arg.accept(self, env)
            if arg_type != param.type:
                raise Exception(f"Error: El argumento '{arg}' no es compatible con el parámetro '{param.name}' de tipo {param.type}")
        return func.return_type

    @multimethod
    def visit(self, n:NamedLocation, env:Symtab):
        '''
        1. Verificar si n.name existe en TS y obtener el tipo
        2. Retornar el tipo
        '''
        symbol = env.get(n.name)
        if not symbol:
            raise NameError(f"Error: La variable '{n.name}' no está definida")
        if n.type == None:
            n.type = symbol.type
        return symbol.type

    @multimethod
    def visit(self, n:MemoryAddress, env:Symtab):
        '''
        1. Visitar n.address (expression) para validar
        2. Retornar el tipo de datos de la expresión
        '''
        return n.address.accept(self, env)
