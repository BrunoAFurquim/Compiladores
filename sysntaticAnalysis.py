# syntactic_analyzer.py
from lexicalAnalyzer import LexicalAnalyzer, Token, Type

class SyntacticAnalyzer:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.proxT()
        self.symbol_table = []  # Escopos de variáveis
        self.declared_variables = []  # Variáveis declaradas globalmente
        self.declared_procedures = []  # Procedimentos declarados
        self.push_scope()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.proxT()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token}, expected {token_type}")
    
    def push_scope(self):
        self.symbol_table.append({})

    def pop_scope(self):
        if self.symbol_table:
            self.symbol_table.pop()
        else:
            raise SyntaxError("Scope underflow: Tried to pop from an empty scope stack.")

    def declare_variable(self, var_name, var_type):
        if var_name in self.symbol_table[-1]:
            raise SyntaxError(f"Variable '{var_name}' already declared in the current scope.")
        self.symbol_table[-1][var_name] = var_type
        self.declared_variables.append((var_name, var_type))

    def lookup_variable(self, var_name):
        for scope in reversed(self.symbol_table):
            if var_name in scope:
                return scope[var_name]
        raise SyntaxError(f"Variable '{var_name}' not declared.")

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
            elif self.current_token.type == Type.RESERVED_TOKENS[';']:
                self.eat(Type.RESERVED_TOKENS[';'])
            else:
                raise SyntaxError(f"Expected '.' or ';' after 'END', found {self.current_token.value}")
        else:
            raise SyntaxError(f"Expected 'END' to close the program, found {self.current_token.value}")

    def block(self):
        self.push_scope()
        if self.current_token.type == Type.RESERVED_WORDS['BEGIN']:
            self.eat(Type.RESERVED_WORDS['BEGIN'])
            while self.current_token.type != Type.RESERVED_WORDS['END']:
                self.statement()
            self.eat(Type.RESERVED_WORDS['END'])
            self.eat(Type.RESERVED_TOKENS[';'])
        else:
            raise SyntaxError(f"Expected 'BEGIN', found {self.current_token.value}")
        self.pop_scope()


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
            self.expression() 
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
            if self.current_token.type == Type.IDENTIFIER:
                var_names.append(self.current_token.value)
                self.eat(Type.IDENTIFIER)
            else:
                raise SyntaxError(f"Expected identifier, found {self.current_token}")

            if self.current_token.type == Type.RESERVED_TOKENS[',']:
                self.eat(Type.RESERVED_TOKENS[','])
            else:
                break
            
        if self.current_token.type == Type.RESERVED_TOKENS[':']:
            self.eat(Type.RESERVED_TOKENS[':'])
        else:
            raise SyntaxError(f"Expected ':', found {self.current_token}")

        if self.current_token.type == Type.IDENTIFIER and self.current_token.value.upper() in Type.RESERVED_TYPES:
            var_type = self.current_token.value.upper()
            self.eat(Type.IDENTIFIER)
        else:
            raise SyntaxError(f"Invalid or missing type for variable declaration, found {self.current_token}")

        for var_name in var_names:
            self.declare_variable(var_name, var_type)
            
        if self.current_token.type == Type.RESERVED_TOKENS[";"]:
            self.eat(Type.RESERVED_TOKENS[";"])
        else:
            raise SyntaxError(f"Expected ';' after variable declaration, found {self.current_token}")

    def variable_assignment(self):
        var_name = self.current_token.value
        var_type = self.lookup_variable(var_name)

        self.eat(Type.IDENTIFIER)  
        self.eat(Type.RESERVED_TOKENS[':=']) 

        assigned_type = self.evaluate_expression()

        if var_type != assigned_type:
            raise SyntaxError(f"Type mismatch: Cannot assign '{assigned_type}' to '{var_type}'.")

        if self.current_token.type == Type.RESERVED_TOKENS[';']:
            self.eat(Type.RESERVED_TOKENS[';'])
        else:
            raise SyntaxError(f"Expected ';' at the end of assignment, found {self.current_token}")

    def evaluate_expression(self):
        result_type = self.evaluate_term()

        while self.current_token.type in [Type.RESERVED_TOKENS['+'], Type.RESERVED_TOKENS['-']]:
            operator = self.current_token.type
            self.eat(operator)
            term_type = self.evaluate_term()

            if result_type != term_type:
                raise SyntaxError(f"Type mismatch in operation: '{result_type}' and '{term_type}' are incompatible.")

            if result_type == Type.RESERVED_TYPES["FLOAT"] or term_type == Type.RESERVED_TYPES["FLOAT"]:
                result_type = Type.RESERVED_TYPES["FLOAT"]

        return result_type

    
    def evaluate_term(self):
        result_type = self.evaluate_factor()

        while self.current_token.type in [Type.RESERVED_TOKENS['*'], Type.RESERVED_TOKENS['/']]:
            operator = self.current_token.type
            self.eat(operator)
            factor_type = self.evaluate_factor()

            if result_type != factor_type:
                raise SyntaxError(f"Type mismatch in operation: '{result_type}' and '{factor_type}' are incompatible.")

            if result_type == Type.RESERVED_TYPES["FLOAT"] or factor_type == Type.RESERVED_TYPES["FLOAT"]:
                result_type = Type.RESERVED_TYPES["FLOAT"]

        return result_type

    
    def evaluate_factor(self):
        if self.current_token.type == Type.IDENTIFIER:
            var_type = self.lookup_variable(self.current_token.value)
            self.eat(Type.IDENTIFIER)
            return var_type

        elif self.current_token.type == Type.RESERVED_TYPES["INT"]:
            self.eat(Type.RESERVED_TYPES["INT"])
            return Type.RESERVED_TYPES["INT"]

        elif self.current_token.type == Type.RESERVED_TYPES["FLOAT"]:
            self.eat(Type.RESERVED_TYPES["FLOAT"])
            return Type.RESERVED_TYPES["FLOAT"]

        elif self.current_token.type == Type.RESERVED_TOKENS['(']:
            self.eat(Type.RESERVED_TOKENS['('])
            result_type = self.evaluate_expression()
            self.eat(Type.RESERVED_TOKENS[')'])
            return result_type

        else:
            raise SyntaxError(f"Unexpected token in factor: {self.current_token}")


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
            self.eat(Type.IDENTIFIER)
            self.declared_procedures.append(procedure_name)

            self.eat(Type.RESERVED_TOKENS['('])
            param_list = []
    
            while self.current_token.type != Type.RESERVED_TOKENS[')']:
                param_name = self.current_token.value
                self.eat(Type.IDENTIFIER)
                self.eat(Type.RESERVED_TOKENS[':'])
                param_type = self.current_token.value.upper()

                if param_type not in Type.RESERVED_TYPES:
                    raise SyntaxError(f"Invalid parameter type '{param_type}' for procedure '{procedure_name}' at line {self.current_token.position}.")

                self.eat(Type.IDENTIFIER)
                param_list.append((param_name, param_type))

                if self.current_token.type == Type.RESERVED_TOKENS[',']:
                    self.eat(Type.RESERVED_TOKENS[','])

            self.eat(Type.RESERVED_TOKENS[')'])
            self.eat(Type.RESERVED_TOKENS[';'])
            
            self.push_scope()

            for param_name, param_type in param_list:
                self.declare_variable(param_name, param_type)

            self.block()

            self.pop_scope()
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

