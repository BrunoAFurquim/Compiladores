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
        # Verifica se a palavra-chave 'PROGRAM' está presente
        if self.current_token.type == Type.RESERVED_WORDS['PROGRAM']:
            self.eat(Type.RESERVED_WORDS['PROGRAM'])

            # Verifica se há um identificador após 'PROGRAM'
            if self.current_token.type == Type.IDENTIFIER:
                program_name = self.current_token.value
                self.eat(Type.IDENTIFIER)

                # Verifica se há um ponto e vírgula ';' após o nome do programa
                if self.current_token.type == Type.RESERVED_TOKENS[';']:
                    self.eat(Type.RESERVED_TOKENS[';'])
                else:
                    raise SyntaxError(f"Expected ';' after program name '{program_name}', found {self.current_token.value}")
            else:
                raise SyntaxError(f"Expected program name, found {self.current_token.value}")
        else:
            raise SyntaxError(f"Expected 'PROGRAM', found {self.current_token.value}")

        # Verifica o token seguinte para identificar qual parte do programa está começando
        while self.current_token.type in (Type.RESERVED_WORDS['VAR'], Type.RESERVED_WORDS['PROCEDURE'], Type.RESERVED_WORDS['BEGIN']):
            if self.current_token.type == Type.RESERVED_WORDS['VAR']:
                self.variable_declaring()  # Chama a regra de declaração de variáveis
            elif self.current_token.type == Type.RESERVED_WORDS['PROCEDURE']:
                self.procedure_declaration()  # Chama a regra de declaração de procedimento
            elif self.current_token.type == Type.RESERVED_WORDS['BEGIN']:
                self.block()  # Chama a regra do bloco de comandos
                break  # 'BEGIN' inicia o bloco de comandos, então paramos de procurar outras declarações

        # Verifica se o programa termina com 'END.'
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

        # Verifica se os parâmetros são passados corretamente
        self.eat(Type.RESERVED_TOKENS['('])
        while self.current_token.type != Type.RESERVED_TOKENS[')']:
            self.expression()  # Avalia os parâmetros como expressões
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
        # Verifica se o token atual é 'IF'
        if self.current_token.type == Type.RESERVED_WORDS['IF']:
            self.eat(Type.RESERVED_WORDS['IF'])
            
            # Avalia a condição da expressão
            self.expression()
            
            # Verifica se o próximo token é 'THEN'
            self.eat(Type.RESERVED_WORDS['THEN'])
            
            # Executa a instrução dentro do bloco do IF
            self.statement()
            
            # Verifica a existência do ELSE opcional
            if self.current_token.type == Type.RESERVED_WORDS['ELSE']:
                self.eat(Type.RESERVED_WORDS['ELSE'])
                self.statement()

    def procedure_declaration(self):
        if self.current_token.type == Type.RESERVED_WORDS['PROCEDURE']:
            self.eat(Type.RESERVED_WORDS['PROCEDURE'])
            
            # Verifica se o próximo token é um identificador (nome do procedimento)
            procedure_name = self.current_token.value
            print(f"Procedure name: {procedure_name}")
            self.eat(Type.IDENTIFIER)
            
            # Verifica se há parâmetros entre parênteses
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
            
            # Bloco de início do procedimento
            self.block()
        else:
            raise SyntaxError(f"Expected 'PROCEDURE' keyword, found {self.current_token.value}")

    def analyze(self):
        self.program_declaration()  # Reconhece a estrutura program <identificador>;
        
        # Processa declarações de variáveis e procedimentos
        while self.current_token.type in [Type.RESERVED_WORDS['VAR'], Type.RESERVED_WORDS['PROCEDURE']]:
            if self.current_token.type == Type.RESERVED_WORDS['VAR']:
                self.variable_declaring()
            elif self.current_token.type == Type.RESERVED_WORDS['PROCEDURE']:
                self.procedure_declaration()

        # Agora processa o bloco principal do programa
        self.block()
