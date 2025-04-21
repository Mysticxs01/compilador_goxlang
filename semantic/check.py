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
from rich    import print
from rich.table import Table
from typing  import Union

from parser.modelo   import *
from semantic.symtab  import Symtab
from semantic.typesys import typenames, check_binop, check_unaryop


class Checker(Visitor):
    @classmethod
    def check(cls, n: Node):
        '''
        1. Crear una nueva tabla de simbolos
        2. Visitar todas las declaraciones
        '''
        print("debug: [INFO] Iniciando verificación semántica")
        print("debug: [INFO] Creando tabla de símbolos")
        check = cls()
        env = Symtab(name="global")  # Agregar un nombre para la tabla de símbolos raíz

        # Verificar si el nodo raíz es un Program
        if isinstance(n, Program):
            print("debug: [INFO] Procesando nodo raíz Program")
            for stmt in n.stmts:  # Recorrer cada declaración en el programa
                stmt.accept(check, env)
        else:
            print("debug: [INFO] Procesando nodo raíz no Program")
            # Si no es un Program, procesar directamente
            n.accept(check, env)

        print("debug: [INFO] Verificación semántica completada")
        return check

    def visit(self, n:Program, env:Symtab):
        '''
        1. recorrer la lista de elementos
        '''
        print("debug: [INFO] Procesando nodo Program")
        for stmt in n.stmts:
            stmt.accept(self, env)

    # Statements

    def visit(self, n:Assignment, env:Symtab):
        '''
        1. Validar n.loc
        2. Visitar n.expr
        3. Verificar si son tipos compatibles
        '''
        loc_type = n.loc.accept(self, env)
        expr_type = n.expr.accept(self, env)
        if loc_type != expr_type:
            raise TypeError(f"Error: No se puede asignar {expr_type} a {loc_type}")
        return loc_type

    def visit(self, n:Print, env:Symtab):
        '''
        1. visitar n.expr
        '''
        n.expression.accept(self, env)

    def visit(self, n:If, env:Symtab):
        '''
        1. Visitar n.test (validar tipos)
        2. Visitar Statement por n.consequence
        3. Si existe opción n.alternative, visitar
        '''
        test_type = n.test.accept(self, env)
        if test_type != 'bool':
            raise TypeError(f"Línea {n.lineno}: Error: La condición del if debe ser de tipo bool, no {test_type}")
        
        # Visitar el bloque de la condición verdadera
        for stmt in n.consequence:
            stmt.accept(self, env)
        
        # Visitar el bloque de la condición alternativa (si existe)
        if n.alternative:
            for stmt in n.alternative:
                stmt.accept(self, env)
            
    def visit(self, n:While, env:Symtab):
        '''
        1. Visitar n.test (validar tipos)
        2. visitar n.body
        '''
        test_type = n.test.accept(self, env)
        if test_type != 'bool':
            raise TypeError(f"Línea {n.lineno}: Error: La condición del while debe ser de tipo bool, no {test_type}")
        
        # Visitar el cuerpo del while
        for stmt in n.body:
            stmt.accept(self, env)
            
    def visit(self, n:Union[Break, Continue], env:Symtab):
        '''
        1. Verificar que esta dentro de un ciclo while
        '''
        # Aquí se necesitaría un mecanismo para verificar si estamos dentro de un ciclo
        pass
            
    def visit(self, n:Return, env:Symtab):
        '''
        1. Si se ha definido n.expr, validar que sea del mismo tipo de la función
        '''
        if n.expression:
            expr_type = n.expression.accept(self, env)
            func_type = env.get('return_type')
            if func_type != expr_type:
                raise TypeError(f"Error: El tipo de retorno {expr_type} no coincide con el tipo de la función {func_type}")
    
    # Declarations

    def visit(self, n:Variable, env:Symtab):
        '''
        1. Agregar n.name a la TS actual
        '''
        if env.get(n.name):
            raise NameError(f"Error: La variable '{n.name}' ya está definida en este ámbito")
        if n.value:
            value_type = n.value.accept(self, env)
            if n.type and n.type != value_type:
                raise TypeError(f"Error: El tipo de la variable '{n.name}' no coincide con el valor asignado")
        env.add(n.name, n)
        

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

        # Crear un nuevo entorno para la función
        func_env = Symtab(n.name, env)

        # Agregar el tipo de retorno al entorno
        func_env.add('return_type', n.return_type)

        # Agregar parámetros al entorno de la función
        for param in n.parameters:
            func_env.add(param.name, param)

        # Visitar cada sentencia en el cuerpo de la función
        for stmt in n.body:
            stmt.accept(self, func_env)

    def visit(self, n:Parameter, env:Symtab):
        '''
        1. Guardar el parametro (name, type) en TS
        '''
        if env.get(n.name):
            raise NameError(f"Error: El parámetro '{n.name}' ya está definido en este ámbito")
        env.add(n.name, n)
        
    # Expressions

    def visit(self, n:Literal, env:Symtab):
        '''
        1. Retornar el tipo de la literal
        '''
        return n.type

    def visit(self, n:BinOp, env:Symtab):
        '''
        1. visitar n.left y luego n.right
        2. Verificar compatibilidad de tipos
        '''

        left_type = n.left.accept(self, env)
        right_type = n.right.accept(self, env)
        result_type = check_binop(n.op, left_type, right_type)
        
        if not result_type:
            raise TypeError(f"Error: Operación '{n.op}' no válida entre {left_type} y {right_type}")

        return result_type
        
    def visit(self, n:UnaryOp, env:Symtab):
        '''
        1. visitar n.expr
        2. validar si es un operador unario valido
        '''
        expr_type = n.operand.accept(self, env)
        result_type = check_unaryop(n.op, expr_type)
        if not result_type:
            raise TypeError(f"Error: Operador unario '{n.op}' no válido para el tipo {expr_type}")
        return result_type

    def visit(self, n:TypeCast, env:Symtab):
        '''
        1. Visitar n.expr para validar
        2. retornar el tipo del cast n.type
        '''
        n.expression.accept(self, env)
        return n.target_type

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
            raise TypeError(f"Error: La función '{n.name}' espera {len(func.parameters)} argumentos, pero se pasaron {len(n.arguments)}")
        for arg, param in zip(n.arguments, func.parameters):
            arg_type = arg.accept(self, env)
            if arg_type != param.type:
                raise TypeError(f"Error: El argumento '{arg}' no es compatible con el parámetro '{param.name}' de tipo {param.type}")
        return func.return_type

    def visit(self, n:NamedLocation, env:Symtab):
        '''
        1. Verificar si n.name existe en TS y obtener el tipo
        2. Retornar el tipo
        '''
        symbol = env.get(n.name)
        if not symbol:
            raise NameError(f"Error: La variable '{n.name}' no está definida")
        
        return symbol.type

    def visit(self, n:MemoryAddress, env:Symtab):
        '''
        1. Visitar n.address (expression) para validar
        2. Retornar el tipo de datos
        '''
        return n.address.accept(self, env)
    
    def print_symbol_table(self, env: Symtab):
        '''
        Imprime la tabla de símbolos usando rich.Table
        '''
        table = Table(title="Tabla de Símbolos")
        table.add_column("Nombre", style="cyan")
        table.add_column("Tipo", style="green")
        table.add_column("Valor", style="magenta")

        for name, symbol in env.entries.items():
            table.add_row(name, symbol.__class__.__name__, str(symbol))
        print(table)