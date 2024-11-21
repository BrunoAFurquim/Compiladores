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

    def program_declaration(self):
        if self.current_token.type == Type.RESERVED_WORDS['PROGRAM']:
            self.eat(Type.RESERVED_WORDS['PROGRAM'])

            if self.current_token.type == Type.IDENTIFIER:
                program_name = self.current_token.value
                self.eat(Type.IDENTIFIER)

                if self.current_token.type == Type.RESERVED_TOKENS[';']:
                    self.eat(Type.RESERVED_TOKENS[';'])
                else:
                    raise SyntaxError(f"Expected ';' after program name '{program_name}', found {self.current_token.value}")
            else:
                raise SyntaxError(f"Expected program name, found {self.current_token.value}")
        else:
            raise SyntaxError(f"Expected 'PROGRAM', found {self.current_token.value}")

        while self.current_token.type in (Type.RESERVED_WORDS['VAR'], Type.RESERVED_WORDS['PROCEDURE'], Type.RESERVED_WORDS['BEGIN']):
            if self.current_token.type == Type.RESERVED_WORDS['VAR']:
                self.variable_declaring() 
            elif self.current_token.type == Type.RESERVED_WORDS['PROCEDURE']:
                self.procedure_declaration() 
            elif self.current_token.type == Type.RESERVED_WORDS['BEGIN']:
                self.block()  
                break  

        if self.current_token.type == Type.RESERVED_WORDS['END']:
            self.eat(Type.RESERVED_WORDS['END'])

            if self.current_token.type == Type.RESERVED_TOKENS['.']:
                self.eat(Type.RESERVED_TOKENS['.'])
            else:
                raise SyntaxError(f"Expected '.' after 'END', found {self.current_token.value}")
        else:
            raise SyntaxError(f"Expected 'END' to close the program, found {self.current_token.value}")


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
        elif self.current_token.type == Type.RESERVED_WORDS['IF']:
            self.conditional_statement()
        elif self.current_token.type == Type.IDENTIFIER:
            next_token = self.lexer.peek()
            print(f"Next token: {next_token}")

            if isinstance(next_token, Token):
                if next_token.type == Type.RESERVED_TOKENS[':=']:
                    self.variable_assignment()
                elif next_token.type == Type.RESERVED_TOKENS['(']:
                    self.procedure_call()
                else:
                    raise SyntaxError(f"Unexpected token after identifier: {next_token}")
            else:
                raise SyntaxError(f"Expected a Token object but got {type(next_token).__name__}")
        elif self.current_token.type == Type.RESERVED_WORDS['READ']:
            self.read_expression()
        elif self.current_token.type == Type.RESERVED_WORDS['WRITE']:
            self.write_expression()
        elif self.current_token.type == Type.RESERVED_WORDS['PROC']:
            self.proc_expression()
        else:
            raise SyntaxError(f"Unexpected token in statement: {self.current_token}")

    def read_expression(self):
        self.eat(Type.RESERVED_WORDS['READ'])
        self.eat(Type.RESERVED_TOKENS['('])
        
        while self.current_token.type != Type.RESERVED_TOKENS[')']:
            if self.current_token.type == Type.IDENTIFIER:
                var_name = self.current_token.value
                if var_name not in [var[0] for var in self.symbol_table]:
                    raise SyntaxError(f"Variable '{var_name}' not declared before use.")
                self.eat(Type.IDENTIFIER)
                
                if self.current_token.type == Type.RESERVED_TOKENS[',']:
                    self.eat(Type.RESERVED_TOKENS[','])
            else:
                raise SyntaxError(f"Expected identifier in READ statement, found {self.current_token.value}")
        
        self.eat(Type.RESERVED_TOKENS[')'])
        self.eat(Type.RESERVED_TOKENS[';'])

    def write_expression(self):
        self.eat(Type.RESERVED_WORDS['WRITE'])
        self.eat(Type.RESERVED_TOKENS['('])

        while self.current_token.type != Type.RESERVED_TOKENS[')']:
            self.expression()  # Escreve a expressão ou variável que queremos exibir
            if self.current_token.type == Type.RESERVED_TOKENS[',']:
                self.eat(Type.RESERVED_TOKENS[','])

        self.eat(Type.RESERVED_TOKENS[')'])
        self.eat(Type.RESERVED_TOKENS[';'])

    def proc_expression(self):
        self.eat(Type.RESERVED_WORDS['PROC'])
        
        procedure_name = self.current_token.value
        if procedure_name not in [proc[0] for proc in self.symbol_table if proc[1] == 'PROC']:
            raise SyntaxError(f"Procedure '{procedure_name}' not declared before use.")
        
        self.eat(Type.IDENTIFIER)
        self.eat(Type.RESERVED_TOKENS['('])

        while self.current_token.type != Type.RESERVED_TOKENS[')']:
            self.expression()
            if self.current_token.type == Type.RESERVED_TOKENS[',']:
                self.eat(Type.RESERVED_TOKENS[','])

        self.eat(Type.RESERVED_TOKENS[')'])
        self.eat(Type.RESERVED_TOKENS[';'])


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

        self.eat(Type.RESERVED_TOKENS['('])
        while self.current_token.type != Type.RESERVED_TOKENS[')']:
            self.expression()
            if self.current_token.type == Type.RESERVED_TOKENS[',']:
                self.eat(Type.RESERVED_TOKENS[','])
        self.eat(Type.RESERVED_TOKENS[')'])
        self.eat(Type.RESERVED_TOKENS[';'])

    def expression(self):
        if self.current_token.type in [Type.IDENTIFIER, Type.RESERVED_TYPES['INT'], Type.RESERVED_TYPES['FLOAT'], Type.RESERVED_WORDS['TRUE'], Type.RESERVED_WORDS['FALSE']]:
            self.eat(self.current_token.type)
        else:
            raise SyntaxError(f"Unexpected token in expression: {self.current_token}")

    def conditional_statement(self):
        if self.current_token.type == Type.RESERVED_WORDS['IF']:
            self.eat(Type.RESERVED_WORDS['IF'])
            self.boolean_expression()
            self.eat(Type.RESERVED_WORDS['THEN'])
            self.statement()
            if self.current_token.type == Type.RESERVED_WORDS['ELSE']:
                self.eat(Type.RESERVED_WORDS['ELSE'])
                self.statement()

    def boolean_expression(self):
        self.term() 
        while self.current_token.type in [Type.RESERVED_TOKENS['<'], Type.RESERVED_TOKENS['>'], Type.RESERVED_TOKENS['<='], Type.RESERVED_TOKENS['>='], Type.RESERVED_TOKENS['=='], Type.RESERVED_TOKENS['!=']]:
            op = self.current_token.type
            self.eat(op)
            self.term() 

    #def read_expression(self):
    #def proc_expression(self):
    #def write_expression(self):
     

    def term(self):
        self.factor()
        while self.current_token.type in [Type.RESERVED_TOKENS['+'], Type.RESERVED_TOKENS['-']]:
            op = self.current_token.type
            self.eat(op)
            self.factor()

    def factor(self):
        if self.current_token.type in [Type.IDENTIFIER, Type.RESERVED_TYPES['INT'], Type.RESERVED_TYPES['FLOAT']]:
            self.eat(self.current_token.type)
        elif self.current_token.type == Type.RESERVED_TOKENS['(']:
            self.eat(Type.RESERVED_TOKENS['('])
            self.boolean_expression()
            self.eat(Type.RESERVED_TOKENS[')'])
        else:
            raise SyntaxError(f"Unexpected token in factor: {self.current_token}")

    def procedure_declaration(self):
        if self.current_token.type == Type.RESERVED_WORDS['PROCEDURE']:
            self.eat(Type.RESERVED_WORDS['PROCEDURE'])
            
            procedure_name = self.current_token.value
            print(f"Procedure name: {procedure_name}")
            self.eat(Type.IDENTIFIER)
            
            self.eat(Type.RESERVED_TOKENS['('])
            while self.current_token.type != Type.RESERVED_TOKENS[')']:
                param_name = self.current_token.value
                self.eat(Type.IDENTIFIER)
                self.eat(Type.RESERVED_TOKENS[':'])
                param_type = self.current_token.value
                self.eat(Type.IDENTIFIER)
                if self.current_token.type == Type.RESERVED_TOKENS[',']:
                    self.eat(Type.RESERVED_TOKENS[','])
            self.eat(Type.RESERVED_TOKENS[')'])
            self.eat(Type.RESERVED_TOKENS[';'])
            
            self.block()
        else:
            raise SyntaxError(f"Expected 'PROCEDURE' keyword, found {self.current_token.value}")

    def analyze(self):
        self.program_declaration() 
        
        while self.current_token.type in [Type.RESERVED_WORDS['VAR'], Type.RESERVED_WORDS['PROCEDURE']]:
            if self.current_token.type == Type.RESERVED_WORDS['VAR']:
                self.variable_declaring()
            elif self.current_token.type == Type.RESERVED_WORDS['PROCEDURE']:
                self.procedure_declaration()

        self.block()
