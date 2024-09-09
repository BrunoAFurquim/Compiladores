from lexicalAnalyzer import LexicalAnalyzer, Type

class Syntactic_Analysis:
    def __init__ (self, tokens):
        self.tokens = tokens
        self.pos = 0

    #See how long is the tokens and if there is <0, there is nothing to do    
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    #To ensure that the quee is not wrong
    def expected(self, token_type):
        token = self.current()
        if token and token[0] == token_type:
            self.pos +=1
            return token
        else:
            raise SystaxError(f"Expected an operation not a number")
    
    # This def define the rules about the Parentheses and the systeshis about the number that are in
    def factor(self):
        token = self.current()
        if token[0] == NUMBER():
            self.expected(NUMBER)
            return float(token[1])
        elif token[0] == LPAREN:
            self.consume(OPEN_PARENTHESES):
            result = self.expr()
            self.expected(CLOSE_PARENTHESES)
            return result
        else:
            raise SystaxError("Invalid")

    
     #Purpose: work with '*' and '/'

    

    