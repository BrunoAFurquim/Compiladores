class Type:
    RESERVED_WORDS = {
        "INT": "INT",
        "FLOAT": "FLOAT",
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
        '_': "UNDERSCORE",
        '=': "EQUAL",
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
        # Check if the word is in reserved words dictionary
        return Type.RESERVED_WORDS.get(word.upper(), Type.IDENTIFIER)

    def identifier(self):
        result = []
        while self.current != '\0' and (self.current.isalnum() or self.current == '_'):
            result.append(self.current)
            self.advance()
        word = ''.join(result)
        token_type = self.reserved(word)  # Check if it's a reserved word
        return Token(token_type, word, self.line)

    def number(self):
        result = []
        is_float = False
        while self.current != '\0' and (self.current.isdigit() or self.current == '.'):
            if self.current == '.':
                if is_float:
                    return Token(Type.UNKNOWN, f"ERROR: Unexpected character {self.current} at line {self.line}")
                is_float = True
            result.append(self.current)
            self.advance()
        num_str = ''.join(result)
        return Token(Type.FLOAT if is_float else Type.INTEGER, num_str, self.line)

    def reserved_token(self, char):
        # Check if the character is in reserved tokens dictionary
        return Type.RESERVED_TOKENS.get(char, Type.UNKNOWN)

    def proxT(self):
        while self.current != '\0':
            if self.current.isspace():
                self.space()
                continue

            # Handle numbers
            if self.current.isdigit() or (self.current == '.' and self.position + 1 < len(self.input) and self.input[self.position + 1].isdigit()):
                return self.number()

            # Handle identifiers and reserved words
            if self.current.isalpha() or self.current == '_':
                return self.identifier()

            # Handle reserved tokens
            if self.current in Type.RESERVED_TOKENS:
                token_type = self.reserved_token(self.current)
                token_line = self.line
                value = self.current
                self.advance()
                return Token(token_type, value, token_line)

            # Handle unknown characters
            unknown_char = self.current
            token_line = self.line
            self.advance()
            return Token(Type.UNKNOWN, f"ERROR: {unknown_char} at line {token_line}", token_line)

        return Token(Type.EOF, "", self.line)
