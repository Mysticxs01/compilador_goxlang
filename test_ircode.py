import unittest
from ircode import IRCode, IRModule, IRFunction, IRGlobal
from parser.modelo import *
from semantic.symtab import Symtab
from lexer.tokenizer import Lexer, tokens_spec
from parser.parser import Parser
from semantic.check import Checker

class TestIRCode(unittest.TestCase):
    def setUp(self):
        # Create a global scope for the symbol table
        self.env = Symtab("global", scope_type="global")
        self.module = IRModule()
        self.func = IRFunction(self.module, 'test_func', [], [], 'I')
        # Create a function scope
        self.func_env = Symtab("test_func", self.env, scope_type="function")
        self.env.children.append(self.func_env)

    def test_complete_program_generation(self):
        # Test complete program generation using shor.gox as example
        source = """
        func mod(a int, b int) int {
            return a - b * (a / b);
        }
        
        func gcd(a int, b int) int {
            while b != 0 {
                var t int = b;
                b = mod(a, b);
                a = t;
            }
            return a;
        }
        """
        
        # Parse and check the program
        lexer = Lexer(tokens_spec)
        tokens = lexer.tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        env = Checker.check(ast)
        
        # Generate IR code
        module = IRCode.gencode(ast.stmts, env)
        
        # Verify module structure
        self.assertIn('mod', module.functions)
        self.assertIn('gcd', module.functions)
        
        # Verify mod function
        mod_func = module.functions['mod']
        self.assertEqual(mod_func.parmnames, ['a', 'b'])
        self.assertEqual(mod_func.parmtypes, ['I', 'I'])
        self.assertEqual(mod_func.return_type, 'I')
        
        # Verify gcd function
        gcd_func = module.functions['gcd']
        self.assertEqual(gcd_func.parmnames, ['a', 'b'])
        self.assertEqual(gcd_func.parmtypes, ['I', 'I'])
        self.assertEqual(gcd_func.return_type, 'I')



    def test_variable_declaration(self):
        # Test variable declaration based on powmod function
        node = Variable('result', 'int', Integer(1))
        node.accept(IRCode(self.env), self.func)
        
        # Verify generated code
        expected_code = [
            ('CONSTI', 1),
            ('GLOBAL_SET', 'result')
        ]
        self.assertEqual(self.func.code[-2:], expected_code)

    def test_return_statement(self):
        # Test return statement
        node = Return(Integer(42))
        node.accept(IRCode(self.env), self.func)
        
        # Verify generated code
        expected_code = [
            ('CONSTI', 42),
            ('RET',)
        ]
        self.assertEqual(self.func.code[-2:], expected_code)

    def test_print_statement(self):
        # Test print statement
        node = Print(Integer(42))
        node.accept(IRCode(self.env), self.func)
        
        # Verify generated code
        expected_code = [
            ('CONSTI', 42),
            ('PRINTI',)
        ]
        self.assertEqual(self.func.code[-2:], expected_code)

if __name__ == '__main__':
    unittest.main()
