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
        if self.position >= len(self.input):
            self.current = '\0'
        else:
            self.current = self.input[self.position]

    def space(self):
        while self.current != '\0' and self.current.isspace():
            self.advance()

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

    def proxT(self):
        while self.current != '\0':
            if self.current.isspace():
                self.space()
                continue
            if self.current.isdigit() or (self.current == '.' and self.position + 1 < len(self.input) and self.input[self.position + 1].isdigit()):
                return self.number()
            if self.current == '+':
                token_line = self.line
                self.advance()
                return Token(Type.PLUS, "+", token_line)
            if self.current == '-':
                token_line = self.line
                self.advance()
                return Token(Type.MINUS, "-", token_line)
            if self.current == '*':
                token_line = self.line
                self.advance()
                return Token(Type.MUL, "*", token_line)
            
            if self.current == '/':
                token_line = self.line
                self.advance()
                return Token(Type.DIV, "/", token_line)
            if self.current == '(':
                token_line = self.line
                self.advance()
                return Token(Type.OPEN_PARENTHESES, "(", token_line)
            if self.current == ')':
                token_line = self.line
                self.advance()
                return Token(Type.CLOSE_PARENTHESES, ")", token_line)

            unknown_char = self.current
            token_line = self.line
            self.advance()
            return Token(Type.UNKNOWN, f"ERROR: {unknown_char} at line {token_line}", token_line)

        return Token(Type.EOF, "", self.line)
