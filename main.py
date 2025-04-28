# main.py
import json
from lexer.tokenizer import Lexer, tokens_spec
from parser.parser import Parser
from semantic.check import Checker
from rich import print as pprint

def main():
    source_path = "samples/factorize.gox"  # Cambia si tienes otro archivo

    # Leer código fuente
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {source_path}")
        return

    print(f"[INFO] Analizando archivo: {source_path}\n")

    # Tokenizar
    lexer = Lexer(tokens_spec)
    tokens = lexer.tokenize(code)

    print("[INFO] Tokens generados:")
    for t in tokens:
        print(f"  {t}")

    # Parsear
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except SyntaxError as e:
        print(f"[ERROR] Error de sintaxis: {e}")
        return

    # AST a JSON
    def ast_to_dict(node):
        if isinstance(node, list):
            return [ast_to_dict(item) for item in node]
        elif hasattr(node, "__dict__"):
            return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
        else:
            return node

    print("\n[INFO] AST generado:")
    pprint(ast)
    ast_json = json.dumps(ast_to_dict(ast), indent=4)

    # Guardar AST
    output_path = "outputs/ast_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ast_json)

    # Analizar semánticamente
    print("\n[INFO] Iniciando análisis semántico...")
    try:
        print("\n[INFO] Tabla de símbolos generada:")
        Checker.check(ast)
        print("\n[INFO] Análisis semántico completado con éxito.")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
