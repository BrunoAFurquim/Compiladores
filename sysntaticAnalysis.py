from lexicalAnalyzer import LexicalAnalyzer, Type

class SyntacticAnalyzer:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.proxT()
        self.symbol_table = set()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.proxT()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}, expected {token_type}")

    def block(self):
        if self.current_token.type == Type.RESERVED_WORDS['BEGIN']:
            self.eat(Type.RESERVED_WORDS['BEGIN'])
            self.statement()
            self.eat(Type.RESERVED_WORDS['END'])
            self.eat(Type.RESERVED_TOKENS[';'])
        else:
            raise SyntaxError(f"Expected 'BEGIN', found {self.current_token.value}")

    def statement(self):
        self.variable_declaring()
        self.variable_assignment()

    def variable_declaring(self): 
        self.eat(Type.RESERVED_WORDS['VAR'])
        var_name = self.current_token.value
        self.eat(Type.IDENTIFIER)

        if var_name in self.symbol_table:
            raise SyntaxError(f"Variable '{var_name}' already declared.")
        
        self.symbol_table.add(var_name)
        self.eat(Type.RESERVED_TOKENS[";"])

    def variable_assignment(self):
        var_name = self.current_token.value

        if var_name not in self.symbol_table:
            raise SyntaxError(f"Variable '{var_name}' not declared before use.")
        
        self.eat(Type.IDENTIFIER)
        self.eat(Type.RESERVED_TOKENS[':=']) 
        
        if self.current_token.type in [Type.RESERVED_WORDS['INT'], Type.RESERVED_WORDS['FLOAT'], Type.IDENTIFIER]:
            self.eat(self.current_token.type)
        else:
            raise SyntaxError(f"Unexpected token in expression: {self.current_token}")
        self.eat(Type.RESERVED_TOKENS[";"])

# Example usage
input_text = """
    BEGIN
        var x;
        y := 10;
    END;
"""
lexer = LexicalAnalyzer(input_text)
parser = SyntacticAnalyzer(lexer)
try:
    parser.block()
    print("Bloco e atribuição de variável reconhecidos com sucesso.")
except SyntaxError as e:
    print(f"Erro de sintaxe: {e}")
