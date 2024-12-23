class Type:
    RESERVED_WORDS = {
        "PROGRAM": "PROGRAM",
        "PROCEDURE": "PROCEDURE",
        "VAR": "VAR",
        "BEGIN": "BEGIN",
        "END": "END",
        "IF": "IF",
        "THEN": "THEN",
        "ELSE": "ELSE",
        "WHILE": "WHILE",
        "DO": "DO",
        "TRUE": "TRUE",
        "FALSE": "FALSE",
        "FOR": "FOR",
        "RETURN": "RETURN",
        "READ": "READ",
        "PROC": "PROC",
        "WRITE": "WRITE",
    }
    
    RESERVED_TYPES = {
        "INT": "INT",
        "FLOAT": "FLOAT",
        "BOOLEAN": "BOOLEAN"
    }
    
    RESERVED_TOKENS = {
        ';': "SEMICOLON",
        ':': "COLON",
        ',': "COMMA",
        '(': "OPEN_PARENTHESES",
        ')': "CLOSE_PARENTHESES",
        '{': "OPEN_BRACKETS",
        '}': "CLOSE_BRACKETS",
        '+': "PLUS",
        '-': "MINUS",
        '*': "MUL",
        '/': "DIV",
        "_": "UNDERSCORE",
        "=": "EQUAL",
        "'": "QUOT_MARKS",
        ":=": "ASSIGNMENT",
        ">": "HIGHER",
        "<": "LOWER",
        ".": "DOT",
        "!=": "NOT_EQUAL",
        "<=": "LESS_EQUAL",
        ">=": "HIGH_EQUAL",
        "==": "COMPARISON"
        
    }
 
    IDENTIFIER = "IDENTIFIER"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

class Token:
    def __init__(self, type, value, position=None):
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, line={self.position})\n"
    
class LexicalAnalyzer:
    def __init__(self, input_str):
        self.set_input(input_str)

    def set_input(self, input_str):
        self.input = input_str
        self.position = 0
        self.current = self.input[self.position] if self.input else '\0'
        self.line = 1

    def advance(self):
        if self.current == '\n':
            self.line += 1
        self.position += 1
        self.current = self.input[self.position] if self.position < len(self.input) else '\0'

    def space(self):
        while self.current != '\0' and self.current.isspace():
            self.advance()

    def reserved(self, word):
        return Type.RESERVED_WORDS.get(word.upper(), Type.IDENTIFIER)

    def identifier_or_number(self):
        result = []
        is_float = False

        if self.current.isdigit():
            while self.current != '\0' and (self.current.isdigit() or self.current == '.'):
                if self.current == '.':
                    if is_float:
                        return Token(Type.UNKNOWN, f"ERROR: Invalid number format at line {self.line}", self.line)
                    is_float = True
                result.append(self.current)
                self.advance()

            num_str = ''.join(result)
            return Token(Type.RESERVED_TYPES["FLOAT"] if is_float else Type.RESERVED_TYPES["INT"], num_str, self.line)

        elif self.current.isalpha() or self.current == '_':
            while self.current != '\0' and (self.current.isalnum() or self.current == '_'):
                result.append(self.current)
                self.advance()

            word = ''.join(result)
            token_type = self.reserved(word)

            if len(word) > 31:
                return Token(Type.UNKNOWN, f"ERROR: Identifier '{word}' too long at line {self.line}", self.line)

            return Token(token_type, word, self.line)

        else:
            unknown_char = self.current
            token_line = self.line
            self.advance()
            return Token(Type.UNKNOWN, f"ERROR: Invalid character '{unknown_char}' at line {token_line}", token_line)
    
    def reserved_token(self, char):
        return Type.RESERVED_TOKENS.get(char, Type.UNKNOWN)
    
    def peek(self):
        original_position = self.position
        original_current = self.current
        original_line = self.line
    
        self.advance()
        token = self.proxT()
    
        self.position = original_position
        self.current = original_current
        self.line = original_line
    
        return token
    
    def proxT(self):
        while self.current != '\0':
            if self.current.isspace():
                self.space()
                continue

            if self.current == ':':
                if self.peek().value == '=':
                    self.advance() 
                    self.advance()
                    return Token(Type.RESERVED_TOKENS[':='], ":=", self.line)
                    
            # Verificação para tokens de dois caracteres
            if self.current in ('!', '<', '>', '='):
                next_char = self.peek()
                compound_operator = self.current + next_char.value
                if compound_operator in Type.RESERVED_TOKENS:
                    self.advance()
                    self.advance()
                    return Token(Type.RESERVED_TOKENS[compound_operator], compound_operator, self.line)

            if self.current.isalnum() or self.current == '_':
                return self.identifier_or_number()

            if self.current in Type.RESERVED_TOKENS:
                token_type = self.reserved_token(self.current)
                value = self.current
                self.advance()
                return Token(token_type, value, self.line)

            unknown_char = self.current
            self.advance()
            return Token(Type.UNKNOWN, f"ERROR: Invalid character '{unknown_char}' at line {self.line}", self.line)

        return Token(Type.EOF, "", self.line)