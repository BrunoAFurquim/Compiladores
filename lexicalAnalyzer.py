class Type:
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    OPEN_PARENTHESES = "OPEN_PARENTHESES"
    CLOSE_PARENTHESES = "CLOSE_PARENTHESES"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"


class Token:
    def __init__(self, type, value, position=None):
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, position={self.position})\n"


class LexicalAnalyzer:
    def __init__(self, input_str):
        self.set_input(input_str)

    def set_input(self, input_str):
        self.input = input_str
        self.position = 0
        self.current = self.input[self.position] if self.input else '\0'

    def advance(self):
        self.position += 1
        if self.position >= len(self.input):
            self.current = '\0'
        else:
            self.current = self.input[self.position]

    def space(self):
        while self.current != '\0' and self.current.isspace():
            self.advance()

    def number(self):
        start_position = self.position
        result = []
        is_float = False
        while self.current != '\0' and (self.current.isdigit() or self.current == '.'):
            if self.current == '.':
                if is_float:
                    return Token(Type.UNKNOWN, f"ERROR: Unexpected character {self.current} at position {self.position}")
                is_float = True
            result.append(self.current)
            self.advance()
        num_str = ''.join(result)
        return Token(Type.FLOAT if is_float else Type.INTEGER, num_str, start_position)

    def proxT(self):
        while self.current != '\0':
            if self.current.isspace():
                self.space()
                continue
            if self.current.isdigit() or (self.current == '.' and self.position + 1 < len(self.input) and self.input[self.position + 1].isdigit()):
                return self.number()
            if self.current == '+':
                token_position = self.position
                self.advance()
                return Token(Type.PLUS, "+", token_position)
            if self.current == '-':
                token_position = self.position
                self.advance()
                return Token(Type.MINUS, "-", token_position)
            if self.current == '*':
                token_position = self.position
                self.advance()
                return Token(Type.MUL, "*", token_position)
            if self.current == '/':
                token_position = self.position
                self.advance()
                return Token(Type.DIV, "/", token_position)
            if self.current == '(':
                token_position = self.position
                self.advance()
                return Token(Type.OPEN_PARENTHESES, "(", token_position)
            if self.current == ')':
                token_position = self.position
                self.advance()
                return Token(Type.CLOSE_PARENTHESES, ")", token_position)

            unknown_char = self.current
            token_position = self.position
            self.advance()
            return Token(Type.UNKNOWN, f"ERROR: {unknown_char} at position {token_position}", token_position)

        return Token(Type.EOF, "", self.position)
