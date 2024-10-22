# syntactic_analyzer.py
from lexicalAnalyzer import LexicalAnalyzer, Type

class SyntacticAnalyzer:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.proxT()
        self.symbol_table = set()

    # le o caractere caso ele bata com o token_type passado
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
        if self.current_token.type == Type.RESERVED_WORDS['VAR']:
            self.variable_declaring()
        elif self.current_token.type == Type.IDENTIFIER:
            self.variable_assignment()
        elif self.current_token.type == Type.RESERVED_WORDS['FUNCTION']:
            self.function_declaring()
        else:
            raise SyntaxError(f"Unexpected token in statement: {self.current_token}")
        
    def variable_declaring(self): 
        self.eat(Type.RESERVED_WORDS['VAR'])
        var_names = []
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
        if var_name not in self.symbol_table:
            raise SyntaxError(f"Variable '{var_name}' not declared before use.")
        self.eat(Type.IDENTIFIER)
        self.eat(Type.RESERVED_TOKENS[':'])
        if self.current_token.type in [Type.RESERVED_WORDS['INT'], Type.RESERVED_WORDS['FLOAT'], Type.IDENTIFIER]:
            self.eat(self.current_token.type)
        else:
            raise SyntaxError(f"Unexpected token in expression: {self.current_token}")
        self.eat(Type.RESERVED_TOKENS[';'])

    def function_declaring(self):
        self.eat(Type.RESERVED_WORDS['FUNCTION'])
        func_name = self.current_token.value
        self.eat(Type.IDENTIFIER)

        if func_name in self.symbol_table:
            raise SyntaxError(f"Function '{func_name}' already declared.")
        self.symbol_table.add(func_name)
        self.eat(Type.RESERVED_TOKENS['('])

        params = []
        if self.current_token.type != Type.RESERVED_TOKENS[')']:
            while True:
                param_type = self.current_token.type
                if param_type not in [Type.RESERVED_WORDS['INT'], Type.RESERVED_WORDS['CHAR']]:
                    raise SyntaxError(f"Invalid parameter type: {self.current_token.value}")
                self.eat(param_type) 

                param_name = self.current_token.value
                self.eat(Type.IDENTIFIER)  

                if param_name in self.symbol_table:
                    raise SyntaxError(f"Parameter '{param_name}' already declared.")

                params.append((param_type, param_name))
                self.symbol_table.add(param_name)

                if self.current_token.type == Type.RESERVED_TOKENS[',']:
                    self.eat(Type.RESERVED_TOKENS[','])  
                else:
                    break
        self.eat(Type.RESERVED_TOKENS[')'])
        self.eat(Type.RESERVED_TOKENS['{'])
        self.block()
        self.eat(Type.RESERVED_TOKENS['}'])
