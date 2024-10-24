# syntactic_analyzer.py
from lexicalAnalyzer import LexicalAnalyzer, Token, Type

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
            while self.current_token.type != Type.RESERVED_WORDS['END']:
                self.statement()
            self.eat(Type.RESERVED_WORDS['END'])
            self.eat(Type.RESERVED_TOKENS[';'])
        else:
            raise SyntaxError(f"Expected 'BEGIN', found {self.current_token.value}")

    def statement(self):
        print(f"Current token: {self.current_token}")

        if self.current_token.type == Type.RESERVED_WORDS['VAR']:
            self.variable_declaring()
        elif self.current_token.type == Type.IDENTIFIER:
            next_token = self.lexer.peek()
            print(f"Next token: {next_token}")

            if isinstance(next_token, Token):
                if next_token.type == Type.RESERVED_TOKENS[':=']:
                    self.variable_assignment()
                elif next_token.type == Type.IDENTIFIER:
                    self.procedure_call()
                else:
                    raise SyntaxError(f"Unexpected token after identifier: {next_token}")
            else:
                raise SyntaxError(f"Expected a Token object but got {type(next_token).__name__}")
        else:
            raise SyntaxError(f"Unexpected token in statement: {self.current_token}")

    def variable_declaring(self):
        self.eat(Type.RESERVED_WORDS['VAR'])
        var_names = []
        
        # Collect variable names
        while True:
            var_name = self.current_token.value
            self.eat(Type.IDENTIFIER)
            if var_name in self.symbol_table:
                raise SyntaxError(f"Variable '{var_name}' already declared.")
            var_names.append(var_name)
            if self.current_token.type == Type.RESERVED_TOKENS[',']:
                self.eat(Type.RESERVED_TOKENS[','])
            else:
                break
        
        # Read variable type
        self.eat(Type.RESERVED_TOKENS[':'])
        var_type = self.current_token.value
        if var_type.upper() not in Type.RESERVED_TYPES:
            raise SyntaxError(f"Invalid type '{var_type}' for variable.")
        self.eat(Type.IDENTIFIER)

        for var_name in var_names:
            self.symbol_table.add((var_name, var_type))
        
        self.eat(Type.RESERVED_TOKENS[";"])

    def variable_assignment(self):
        var_name = self.current_token.value
        if var_name not in [var[0] for var in self.symbol_table]:
            raise SyntaxError(f"Variable '{var_name}' not declared before use.")

        self.eat(Type.IDENTIFIER)  
        self.eat(Type.RESERVED_TOKENS[':=']) 

        self.expression() 

        if self.current_token.type == Type.RESERVED_TOKENS[';']: 
            self.eat(Type.RESERVED_TOKENS[';']) 
        else:
            raise SyntaxError(f"Expected ';' at the end of assignment at line {self.current_token.position}.")

    def procedure_call(self):
        print(f"Procedure call detected for '{self.current_token.value}'")
        self.eat(Type.IDENTIFIER)

    def expression(self):
        if self.current_token.type in [Type.IDENTIFIER, Type.RESERVED_TYPES['INT'], Type.RESERVED_TYPES['FLOAT'], Type.RESERVED_WORDS['TRUE'], Type.RESERVED_WORDS['FALSE']]:
            self.eat(self.current_token.type)
        else:
            raise SyntaxError(f"Unexpected token in expression: {self.current_token}")
