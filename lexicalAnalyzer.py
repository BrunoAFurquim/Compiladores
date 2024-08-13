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


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})\n"


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
        result = []
        is_float = False
        while self.current != '\0' and (self.current.isdigit() or self.current == '.'):
            if self.current == '.':
                if is_float:  # If there's already a dot, it's a malformed number
                    raise RuntimeError(f"Unexpected character: {self.current}")
                is_float = True
            result.append(self.current)
            self.advance()
        num_str = ''.join(result)
        return Token(Type.FLOAT if is_float else Type.INTEGER, num_str)

    def proxT(self):
        while self.current != '\0':
            if self.current.isspace():
                self.space()
                continue
            if self.current.isdigit() or (self.current == '.' and self.input[self.position + 1].isdigit()):
                return self.number()
            if self.current == '+':
                self.advance()
                return Token(Type.PLUS, "+")
            if self.current == '-':
                self.advance()
                return Token(Type.MINUS, "-")
            if self.current == '*':
                self.advance()
                return Token(Type.MUL, "*")
            if self.current == '/':
                self.advance()
                return Token(Type.DIV, "/")
            if self.current == '(':
                self.advance()
                return Token(Type.OPEN_PARENTHESES, "(")
            if self.current == ')':
                self.advance()
                return Token(Type.CLOSE_PARENTHESES, ")")
            raise RuntimeError(f"Unexpected character: {self.current}")
        return Token(Type.EOF, "")
