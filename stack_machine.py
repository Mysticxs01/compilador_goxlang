class StackMachine:
    def __init__(self):
        self.stack = []                       # Pila principal
        self.memory = [0] * 1024              # Memoria lineal
        self.globals = {}                     # Variables globales
        self.locals_stack = []                # Stack de variables locales por función
        self.call_stack = []                  # Stack de retorno
        self.functions = {}                   # Diccionario de funciones
        self.function_params = {}             # Parámetros de las funciones
        self.pc = 0                           # Contador de programa
        self.program = []                     # Programa IR cargado
        self.running = False
        self.current_function = None          # Función actual en ejecución
        self.debug = False                     # Modo debug

    def debug_print(self, *args):
        if self.debug:
            print("DEBUG:", *args)

    def load_program(self, program):
        self.program = program
        if self.debug:
            print("\nPrograma cargado:")
            for i, instr in enumerate(program):
                print(f"{i}: {instr}")

    def load_functions(self, functions_dict, params_dict=None):
        """
        Carga las funciones en el diccionario de funciones.
        functions_dict debe ser un diccionario donde:
        - Las claves son los nombres de las funciones
        - Los valores son listas de instrucciones IR
        params_dict es un diccionario opcional que especifica los parámetros de cada función
        """
        self.functions = functions_dict
        self.function_params = params_dict or {}
        if self.debug:
            print("\nFunciones cargadas:")
            for name, code in functions_dict.items():
                print(f"\nFUNCIÓN: {name}")
                for i, instr in enumerate(code):
                    print(f"{i}: {instr}")

    def run(self):
        self.pc = 0
        self.running = True
        self.current_function = None
        while self.running and self.pc < len(self.program):
            instr = self.program[self.pc]
            opname = instr[0]
            args = instr[1:] if len(instr) > 1 else []
            if self.debug:
                print(f"\nEjecutando: {opname} {args}")
                print(f"Stack: {self.stack}")
                if self.locals_stack:
                    print(f"Locals: {self.locals_stack[-1]}")
            method = getattr(self, f"op_{opname}", None)
            if method:
                method(*args)
            else:
                raise RuntimeError(f"Instrucción desconocida: {opname}")
            self.pc += 1

    # Operaciones con enteros
    def op_CONSTI(self, value):
        self.stack.append(('int', value))

    def op_ADDI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', a + b))
        else:
            raise TypeError("ADDI requiere dos enteros")

    def op_SUBI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', a - b))
        else:
            raise TypeError("SUBI requiere dos enteros")

    def op_MULI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', a * b))
        else:
            raise TypeError("MULI requiere dos enteros")

    def op_DIVI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            if b == 0:
                raise ZeroDivisionError("División por cero")
            self.stack.append(('int', a // b))
        else:
            raise TypeError("DIVI requiere dos enteros")

    def op_MODI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            if b == 0:
                raise ZeroDivisionError("Módulo por cero")
            self.stack.append(('int', a % b))
        else:
            raise TypeError("MODI requiere dos enteros")

    # Operaciones de comparación
    def op_LTI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', 1 if a < b else 0))
        else:
            raise TypeError("LTI requiere dos enteros")

    def op_LEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', 1 if a <= b else 0))
        else:
            raise TypeError("LEI requiere dos enteros")

    def op_GTI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', 1 if a > b else 0))
        else:
            raise TypeError("GTI requiere dos enteros")

    def op_GEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', 1 if a >= b else 0))
        else:
            raise TypeError("GEI requiere dos enteros")

    def op_EQI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', 1 if a == b else 0))
        else:
            raise TypeError("EQI requiere dos enteros")

    def op_NEI(self):
        b_type, b = self.stack.pop()
        a_type, a = self.stack.pop()
        if a_type == b_type == 'int':
            self.stack.append(('int', 1 if a != b else 0))
        else:
            raise TypeError("NEI requiere dos enteros")

    # Operaciones de impresión
    def op_PRINTI(self):
        val_type, value = self.stack.pop()
        if val_type == 'int':
            print(value, end='', flush=True)  # Forzar flush para ver la salida inmediatamente
        else:
            raise TypeError("PRINTI requiere un entero")

    def op_PRINTB(self):
        val_type, value = self.stack.pop()
        if val_type == 'int':
            print(chr(value), end='', flush=True)  # Forzar flush para ver la salida inmediatamente
        else:
            raise TypeError("PRINTB requiere un entero")

    # Operaciones de control de flujo
    def op_IF(self):
        val_type, value = self.stack.pop()
        if val_type == 'int':
            if value == 0:
                # Buscar el ELSE o ENDIF correspondiente
                depth = 1
                while depth > 0:
                    self.pc += 1
                    if self.pc >= len(self.program):
                        raise RuntimeError("IF sin ENDIF correspondiente")
                    opname = self.program[self.pc][0]
                    if opname == 'IF':
                        depth += 1
                    elif opname == 'ELSE' and depth == 1:
                        depth = 0
                    elif opname == 'ENDIF':
                        depth -= 1
        else:
            raise TypeError("IF requiere un entero")

    def op_ELSE(self):
        # Buscar el ENDIF correspondiente
        depth = 1
        while depth > 0:
            self.pc += 1
            if self.pc >= len(self.program):
                raise RuntimeError("ELSE sin ENDIF correspondiente")
            opname = self.program[self.pc][0]
            if opname == 'IF':
                depth += 1
            elif opname == 'ENDIF':
                depth -= 1

    def op_ENDIF(self):
        pass  # No necesita hacer nada

    def op_LOOP(self):
        pass  # No necesita hacer nada, el CBREAK maneja la lógica

    def op_CBREAK(self):
        val_type, value = self.stack.pop()
        if val_type == 'int':
            if value == 0:
                # Buscar el ENDLOOP correspondiente
                depth = 1
                while depth > 0:
                    self.pc += 1
                    if self.pc >= len(self.program):
                        raise RuntimeError("CBREAK sin ENDLOOP correspondiente")
                    opname = self.program[self.pc][0]
                    if opname == 'LOOP':
                        depth += 1
                    elif opname == 'ENDLOOP':
                        depth -= 1
        else:
            raise TypeError("CBREAK requiere un entero")

    def op_CONTINUE(self):
        # Buscar el LOOP correspondiente
        depth = 1
        while depth > 0:
            self.pc -= 1
            if self.pc < 0:
                raise RuntimeError("CONTINUE sin LOOP correspondiente")
            opname = self.program[self.pc][0]
            if opname == 'LOOP':
                depth -= 1
            elif opname == 'ENDLOOP':
                depth += 1

    def op_ENDLOOP(self):
        pass  # No necesita hacer nada

    # Operaciones de variables locales
    def op_LOCAL_GET(self, name):
        if not self.locals_stack:
            raise RuntimeError("No hay variables locales disponibles")
        locals_dict = self.locals_stack[-1]
        if name not in locals_dict:
            raise RuntimeError(f"Variable local '{name}' no definida")
        self.stack.append(locals_dict[name])

    def op_LOCAL_SET(self, name):
        if not self.locals_stack:
            raise RuntimeError("No hay variables locales disponibles")
        value = self.stack.pop()
        self.locals_stack[-1][name] = value

    # Operaciones de funciones
    def op_CALL(self, name):
        if name not in self.functions:
            raise RuntimeError(f"Función '{name}' no definida")
        # Guardar el punto de retorno y el programa actual
        self.call_stack.append((self.pc, self.program))
        # Crear nuevo scope de variables locales
        new_locals = {}
        # Inicializar parámetros de la función
        if name in self.function_params:
            param_names = self.function_params[name]
            # Los parámetros están en la pila en orden inverso
            for param_name in reversed(param_names):
                if not self.stack:
                    raise RuntimeError(f"Falta argumento para {param_name} en llamada a {name}")
                new_locals[param_name] = self.stack.pop()
        self.locals_stack.append(new_locals)
        # Cambiar al programa de la función
        self.program = self.functions[name]
        self.pc = -1  # Se incrementará a 0 en el siguiente ciclo
        self.current_function = name

    def op_RET(self):
        if not self.call_stack:
            self.running = False
            return
        # Restaurar el punto de retorno y el programa
        self.pc, self.program = self.call_stack.pop()
        # Eliminar el scope de variables locales
        if self.locals_stack:
            self.locals_stack.pop()
        self.current_function = None

    # Operaciones de variables globales
    def op_GLOBAL_GET(self, name):
        if name not in self.globals:
            raise RuntimeError(f"Variable global '{name}' no definida")
        self.stack.append(self.globals[name])

    def op_GLOBAL_SET(self, name):
        if not self.stack:
            raise RuntimeError(f"No hay valor en la pila para asignar a '{name}'")
        self.globals[name] = self.stack.pop()

# Ejemplo de uso
if __name__ == '__main__':
    import sys
    from ircode import IRCode
    from parser.parser import Parser
    from lexer.tokenizer import Lexer, tokens_spec
    from semantic.check import Checker

    #if len(sys.argv) != 2:
    #    raise SystemExit("Usage: python stack_machine.py <filename>")
    
    # Leer y parsear el archivo fuente
    #source_path = sys.argv[1]
    source_path = "samples/print.gox"
    txt = open(source_path, encoding='utf-8').read()
    
    lexer = Lexer(tokens_spec)
    tokens = lexer.tokenize(txt)
    
    top = Parser(tokens)
    ast = top.parse()

    # Verificar semánticamente
    env = Checker.check(ast)
    
    # Generar código IR
    module = IRCode.gencode(ast.stmts, env)
    module.dump()
    # Convertir el módulo IR a formato para la máquina virtual
    functions = {}
    function_params = {}
    
    # Procesar cada función del módulo
    for func_name, func in module.functions.items():
        functions[func_name] = func.code
        function_params[func_name] = func.parmnames

    # Crear y configurar la máquina virtual
    vm = StackMachine()
    vm.load_functions(functions, function_params)
    
    # Cargar el programa principal (función main)
    if 'main' in functions:
        vm.load_program(functions['main'])
        print("Ejecutando programa...")
        vm.run()
        print("\nPrograma terminado.")
    else:
        print("Error: No se encontró la función main")