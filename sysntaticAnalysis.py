# syntactic_analyzer.py
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
        self.if_function()

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

    def if_function(self):
        # Verifica e consome o token IF
        if self.current_token.type == Type.RESERVED_WORDS['IF']:
            self.eat(Type.RESERVED_WORDS['IF'])
        else:
            raise SyntaxError(f"Expected 'IF', found {self.current_token.value}")

        # Avalia a expressão condicional
        self.expression

        # Verifica e consome o token THEN
        if self.current_token.type == Type.RESERVED_WORDS['THEN']:
            self.eat(Type.RESERVED_WORDS['THEN'])
        else:
            raise SyntaxError(f"Expected 'THEN', found {self.current_token.value}")

        # Executa as instruções dentro do bloco THEN
        self.block()

        # Verifica se existe uma cláusula ELSE
        if self.current_token.type == Type.RESERVED_WORDS['ELSE']:
            self.eat(Type.RESERVED_WORDS['ELSE'])
            # Executa as instruções dentro do bloco ELSE
            self.block()

    def expression(self):
        # Expressão simples inicial
        self.simple_expression()

        # Avalia uma relação opcional
        if self.current_token.type in [Type.RESERVED_TOKENS['='], Type.RESERVED_TOKENS['<>'], 
                                    Type.RESERVED_TOKENS['<'], Type.RESERVED_TOKENS['<='],
                                    Type.RESERVED_TOKENS['>'], Type.RESERVED_TOKENS['>=']]:
            operator = self.current_token.type
            self.eat(operator)  # Consome o operador relacional
            self.simple_expression()  # Avalia a segunda expressão simples

    def simple_expression(self):
        # Consome um operador opcional + ou -
        if self.current_token.type == Type.RESERVED_WORDS['(']:
            self.eat(Type.RESERVED_WORDS['('])
        else:
            raise SyntaxError(f"Expected 'IF', found {self.current_token.value}")

        if self.current_token.type in [Type.RESERVED_TOKENS['+'], Type.RESERVED_TOKENS['-']]:
            self.eat(self.current_token.type)
        
        # Avalia o termo inicial
        self.term()

        # Consome operadores de baixa prioridade como +, -, or
        while self.current_token.type in [Type.RESERVED_TOKENS['+'], Type.RESERVED_TOKENS['-'], Type.RESERVED_WORDS['or']]:
            operator = self.current_token.type
            self.eat(operator)  # Consome o operador
            self.term()  # Avalia o próximo termo

    def term(self):
        # Avalia o fator inicial
        self.factor()

        # Consome operadores de média prioridade como *, div, and
        while self.current_token.type in [Type.RESERVED_TOKENS['*'], Type.RESERVED_WORDS['div'], Type.RESERVED_WORDS['and']]:
            operator = self.current_token.type
            self.eat(operator)  # Consome o operador
            self.factor()  # Avalia o próximo fator

    def factor(self):
        # Avalia um número, uma variável, uma expressão entre parênteses ou o operador not
        if self.current_token.type == Type.INT or self.current_token.type == Type.FLOAT:
            self.eat(self.current_token.type)  # Consome o número
        elif self.current_token.type == Type.IDENTIFIER:
            self.eat(Type.IDENTIFIER)  # Consome a variável
        elif self.current_token.type == Type.RESERVED_TOKENS['(']:
            self.eat(Type.RESERVED_TOKENS['('])  # Consome o '('
            self.expression()  # Avalia a sub-expressão
            self.eat(Type.RESERVED_TOKENS[')'])  # Consome o ')'
        elif self.current_token.type == Type.RESERVED_WORDS['not']:
            self.eat(Type.RESERVED_WORDS['not'])  # Consome o 'not'
            self.factor()  # Avalia o fator após 'not'
        else:
            raise SyntaxError(f"Unexpected token in factor: {self.current_token}")

    def expression_list(self):
        # Avalia a primeira expressão
        self.expression()

        # Avalia a lista de expressões separadas por vírgula
        while self.current_token.type == Type.RESERVED_TOKENS[',']:
            self.eat(Type.RESERVED_TOKENS[','])  # Consome a vírgula
            self.expression()  # Avalia a próxima expressão
