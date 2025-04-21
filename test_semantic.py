import unittest
from unittest.mock import MagicMock
from semantic.check import Checker
from semantic.symtab import Symtab
from parser.modelo import Float, Integer, Program, Assignment, Print, Literal, NamedLocation

class TestChecker(unittest.TestCase):
    def setUp(self):
        # Create a mock symbol table
        self.symtab = Symtab("global")

    def test_check_program(self):
        # Mock a Program node with statements
        stmt1 = MagicMock()
        stmt2 = MagicMock()
        program = Program(stmts=[stmt1, stmt2])

        # Mock the visit method for statements
        stmt1.accept = MagicMock()
        stmt2.accept = MagicMock()

        # Run the checker
        Checker.check(program)

        # Verify that the statements were visited
        stmt1.accept.assert_called_once()
        stmt2.accept.assert_called_once()

    def test_assignment_type_check(self):
        # Mock an Assignment node
        location = NamedLocation(name="x")
        expression = Integer(value=42)  # Updated constructor
        assignment = Assignment(loc=location, expr=expression)

        # Mock the symbol table and add a variable
        self.symtab.add("x", MagicMock(dtype="int"))

        # Mock the behavior of location.accept to return "int"
        location.accept = MagicMock(return_value="int")

        # Run the checker
        result_type = Checker().visit(assignment, self.symtab)

        # Verify the types match
        self.assertEqual(result_type, "int")

    def test_type_mismatch_in_assignment(self):
        # Mock an Assignment node with a type mismatch
        location = NamedLocation(name="x")
        expression = Float(value=3.14)  # Updated constructor
        assignment = Assignment(loc=location, expr=expression)

        # Mock the symbol table and add a variable with a different type
        self.symtab.add("x", MagicMock(dtype="int"))

        # Mock the behavior of location.accept to return "int"
        location.accept = MagicMock(return_value="int")

        # Run the checker and expect a type mismatch error
        with self.assertRaises(TypeError):
            Checker().visit(assignment, self.symtab)

if __name__ == "__main__":
    unittest.main()