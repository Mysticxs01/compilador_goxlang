# parse.py
#
# El analizador debe construir el modelo de
# datos o un árbol de sintaxis abstracta a
# partir de la entrada de texto. La gramática
# aquí se especifica como PEG (Parsing
# Expression Grammar).
#
# PEG Syntax:
#
#    'quoted'   : Texto literal
#    ( ... )    : Agrupacion
#      e?       : Opcional (0 o 1 coincidencia de e)
#      e*       : Repeticion (0 o mas coincidencias de e)
#      e+       : Repeticion (1 o mas coincidencias)
#     e1 e2     : Coincide e1 luego e2 (secuencia)
#    e1 / e2    : Trata e1. Si falla, trata e2.
#
# Se asume que los nombres en mayúsculas son tokens
# del archivo tokenize.py (su analizador lexico).
# EOF es "Fin del archivo".
#
# program <- statement* EOF
#
# statement <- assignment
#           /  vardecl
#           /  funcdel
#           /  if_stmt
#           /  while_stmt
#           /  break_stmt
#           /  continue_stmt
#           /  return_stmt
#           /  print_stmt
#
# assignment <- location '=' expression ';'
#
# vardecl <- ('var'/'const') ID type? ('=' expression)? ';'
#
# funcdecl <- 'import'? 'func' ID '(' parameters ')' type '{' statement* '}'
#
# if_stmt <- 'if' expression '{' statement* '}'
#         /  'if' expression '{' statement* '}' else '{' statement* '}'
#
# while_stmt <- 'while' expression '{' statement* '}'
#
# break_stmt <- 'break' ';'
#
# continue_stmt <- 'continue' ';'
#
# return_stmt <- 'return' expression ';'
#
# print_stmt <- 'print' expression ';'
#
# parameters <- ID type (',' ID type)*
#            /  empty
#
# type <- 'int' / 'float' / 'char' / 'bool'
#
# location <- ID
#          /  '`' expression
#
# expression <- orterm ('||' orterm)*
#
# orterm <- andterm ('&&' andterm)*
#
# andterm <- relterm (('<' / '>' / '<=' / '>=' / '==' / '!=') reltime)*
#
# relterm <- addterm (('+' / '-') addterm)*
#
# addterm <- factor (('*' / '/') factor)*
#
# factor <- literal
#        / ('+' / '-' / '^') expression
#        / '(' expression ')'
#        / type '(' expression ')'
#        / ID '(' arguments ')'
#        / location
#
# arguments <- expression (',' expression)*
#          / empty
#
# literal <- INTEGER / FLOAT / CHAR / bool
#
# bool <- 'true' / 'false'

from lexer.tokenizer import Token
from typing import List
from dataclasses import dataclass
from parser.modelo import (
    Integer, Float, Char, Bool, TypeCast, BinOp, 
    UnaryOp, Assignment, Variable, NamedLocation, 
    Break, Continue, Return, Print, If, While, 
    Function, Parameter, FunctionCall, Program
)

# -------------------------------
# Implementación del Parser
# -------------------------------

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements = []
        while self.peek() and self.peek().type != "EOF":
            statements.append(self.statement())
        return Program(statements)  # Encapsular las declaraciones en un nodo Program

    # -------------------------------
    # Análisis de declaraciones
    # -------------------------------
    def statement(self):
        if self.match("ID"):
            return self.assignment()
        elif self.match("VAR") or self.match("CONST"):
            return self.vardecl()
        elif self.match("FUNC"):
            return self.funcdecl()
        elif self.match("IF"):
            return self.if_stmt()
        elif self.match("WHILE"):
            return self.while_stmt()
        elif self.match("BREAK"):
            return Break()
        elif self.match("CONTINUE"):
            return Continue()
        elif self.match("RETURN"):
            return self.return_stmt()
        elif self.match("PRINT"):
            return self.print_stmt()
        else:
            raise SyntaxError(f"Línea {self.peek().lineno}: Declaración inesperada")

    def assignment(self):
        location = self.tokens[self.current - 1]
        if self.match("LPAREN"):
            arguments = self.arguments()
            self.consume("RPAREN", "Se esperaba ')'")
            self.consume("SEMI", "Se esperaba ';'")
            return FunctionCall(location.value, arguments)
        self.consume("ASSIGN", "Se esperaba '='")
        expression = self.expression()
        self.consume("SEMI", "Se esperaba ';'")
        return Assignment(NamedLocation(location.value), expression)

    def vardecl(self):
        is_const = self.tokens[self.current - 1].value == "CONST"
        name = self.consume("ID", "Se esperaba un identificador")
        type_ = None
        if self.match("TYPE"):
            type_ = self.tokens[self.current - 1].value
        value = None
        if self.match("ASSIGN"):
            value = self.expression()
        self.consume("SEMI", "Se esperaba ';'")
        return Variable(name.value, type_, value, is_const)

    def funcdecl(self):
        is_imported = self.match("IMPORT")
        name = self.consume("ID", "Se esperaba un identificador")
        self.consume("LPAREN", "Se esperaba '('")
        parameters = self.parameters()
        self.consume("RPAREN", "Se esperaba ')'")
        return_type = None
        if self.match("TYPE"):
            return_type = self.tokens[self.current - 1].value
        body = []
        if not is_imported:
            self.consume("LBRACE", "Se esperaba '{'")
            while not self.match("RBRACE"):
                body.append(self.statement())
        return Function(name.value, parameters, return_type, body)

    def if_stmt(self):
        test = self.expression()
        self.consume("LBRACE", "Se esperaba '{'")
        consequence = []
        while not self.match("RBRACE"):
            consequence.append(self.statement())
        alternative = None
        if self.match("ELSE"):
            self.consume("LBRACE", "Se esperaba '{'")
            alternative = []
            while not self.match("RBRACE"):
                alternative.append(self.statement())
        return If(test, consequence, alternative)

    def while_stmt(self):
        test = self.expression()
        self.consume("LBRACE", "Se esperaba '{'")
        body = []
        while not self.match("RBRACE"):
            body.append(self.statement())
        return While(test, body)

    def return_stmt(self):
        expression = self.expression()
        self.consume("SEMI", "Se esperaba ';'")
        return Return(expression)

    def print_stmt(self):
        expression = self.expression()
        self.consume("SEMI", "Se esperaba ';'")
        return Print(expression)

    # -------------------------------
    # Análisis de expresiones
    # -------------------------------
    def expression(self):
        return self.orterm()

    def orterm(self):
        left = self.andterm()
        while self.match("LOR"):
            op = "||"
            right = self.andterm()
            left = BinOp(op, left, right)
        return left

    def andterm(self):
        left = self.relterm()
        while self.match("LAND"):
            op = "&&"
            right = self.relterm()
            left = BinOp(op, left, right)
        return left

    def relterm(self):
        left = self.addterm()
        while self.match("LT") or self.match("GT") or self.match("LE") or self.match("GE") or self.match("EQ") or self.match("NE"):
            op = self.tokens[self.current - 1].type
            right = self.addterm()
            left = BinOp(op, left, right)
        return left

    def addterm(self):
        left = self.factor()
        while self.match("PLUS") or self.match("MINUS") or self.match("TIMES") or self.match("DIVIDE"):
            op = self.tokens[self.current - 1].type  # Obtener el operador actual
            right = self.factor()
            left = BinOp(op, left, right)  # Crear un nodo BinOp para el AST
        return left

    def factor(self):
        if self.match("INTEGER"):
            return Integer(int(self.tokens[self.current - 1].value))
        elif self.match("FLOAT"):
            return Float(float(self.tokens[self.current - 1].value))
        elif self.match("CHAR"):
            return Char(self.tokens[self.current - 1].value)
        elif self.match("TRUE") or self.match("FALSE"):
            return Bool(self.tokens[self.current - 1].value == "true")
        elif self.match("PLUS") or self.match("MINUS") or self.match("GROW"):  # Manejo de operadores unarios
            op = self.tokens[self.current - 1].type
            operand = self.factor()
            return UnaryOp(op, operand)
        elif self.match("LPAREN"):
            expr = self.expression()
            self.consume("RPAREN", "Se esperaba ')'")
            return expr
        elif self.match("TYPE"):
            type_ = self.tokens[self.current - 1].value
            self.consume("LPAREN", "Se esperaba '('")
            expression = self.expression()
            self.consume("RPAREN", "Se esperaba ')'")
            return TypeCast(type_, expression)
        elif self.match("ID"):
            name = self.tokens[self.current - 1].value
            if self.match("LPAREN"):
                arguments = self.arguments()
                self.consume("RPAREN", "Se esperaba ')'")
                return FunctionCall(name, arguments)
            return NamedLocation(name)
        else:
            raise SyntaxError(f"Línea {self.peek().lineno}: Expresión inesperada")

    def parameters(self):
        params = []
        if not self.match("RPAREN"):
            while True:
                name = self.consume("ID", "Se esperaba un identificador")
                type_ = self.consume("TYPE", "Se esperaba un tipo")
                params.append(Parameter(name.value, type_.value))
                if not self.match("COMMA"):
                    break
        return params

    def arguments(self):
        args = []
        if self.peek() and self.peek().type != "RPAREN":
            while True:
                args.append(self.expression())
                if not self.match("COMMA"):
                    break
        return args
    
	# -------------------------------
	# Trate de conservar este codigo
	# -------------------------------

    def peek(self) -> Token:
        return self.tokens[self.current] if self.current < len(self.tokens) else None
		
    def advance(self) -> Token:
        token = self.peek()
        self.current += 1
        return token
    
    def match(self, token_type: str) -> bool:
        if self.peek() and self.peek().type == token_type:
            self.advance()
            return True
        return False
    	
    def consume(self, token_type: str, message: str):
        if self.match(token_type):
            return self.tokens[self.current - 1]
        raise SyntaxError(f"Línea {self.peek().lineno}: {message}")
