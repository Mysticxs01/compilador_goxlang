import re

class Token:
    def __init__(self, type, value, lineno):
        self.type = type
        self.value = value
        self.lineno = lineno
    
    def __str__(self):
        return f"Token(type='{self.type}', value='{self.value}', lineno='{self.lineno}')"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, lineno={self.lineno})"

class Lexer:
    def __init__(self, tokens_spec):
        self.tokens_spec = tokens_spec
        
    def tokenize(self, text):
        pos = 0
        lineno = 1
        tokens = []
        
        while pos < len(text):
            match = None
            
            # Intentar hacer match con cada patrón
            for token_type, pattern in self.tokens_spec:
                regex = re.compile(pattern)
                match = regex.match(text, pos)
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE' and token_type != 'COMMENT':  # Ignorar espacios y comentarios
                        tokens.append(Token(token_type, value, lineno))
                    pos = match.end()
                    lineno += value.count('\n')
                    break
            
            if not match:
                error_char = text[pos]
                print(f"Illegal character '{error_char}' at line {lineno}")
                pos += 1  # Avanzar para continuar el análisis
        
        return tokens

# Definimos los tokens y sus patrones basados en las reglas de tokenize.py
tokens_spec = [
    # Comentarios
    ('COMMENT', r'//[^\n]*|/\*[\s\S]*?\*/'),
    
    # Palabras Reservadas
    ('CONST', r'const'),
    ('VAR', r'var'),
    ('PRINT', r'print'),
    ('STRING', r'"[^"]*"'),
    ('RETURN', r'return'),
    ('BREAK', r'break'),
    ('CONTINUE', r'continue'),
    ('IF', r'if'),
    ('ELSE', r'else'),
    ('WHILE', r'while'),
    ('FUNC', r'func'),
    ('IMPORT', r'import'),
    ('TRUE', r'true'),
    ('FALSE', r'false'),

    # Identificadores
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),

    # Literales
    ('FLOAT', r'\d+\.\d*|\.\d+'),
    ('INTEGER', r'\d+'),
    ('CHAR', r"'(\\.|[^\\'])'"),

    # Operadores
    ('LE', r'<='),
    ('GE', r'>='),
    ('EQ', r'=='),
    ('NE', r'!='),
    ('LT', r'<'),
    ('GT', r'>'),
    ('ASSIGN', r'='),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('TIMES', r'\*'),
    ('DIVIDE', r'/'),
    ('LAND', r'&&'),
    ('LOR', r'\|\|'),
    ('GROW', r'\^'),

    # Símbolos Misceláneos
    ('SEMI', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('COMMA', r','),
    ('DEREF', r'`'),

    # Espacios en blanco (para ignorar)
    ('WHITESPACE', r'\s+'),
]

def main():
    # Ejemplo de uso
    # Supongamos que el archivo factorize.gox está en el mismo directorio que este script
    file_path = 'samples/factorize.gox'

    # Lee el contenido del archivo
    with open(file_path, 'r') as file:
        gox_code = file.read()

    # Usa el analizador léxico para tokenizar el código
    lexer = Lexer(tokens_spec)
    tokens = lexer.tokenize(gox_code)
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()
