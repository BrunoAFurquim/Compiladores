# main.py
from lexicalAnalyzer import LexicalAnalyzer, Type
from interface import Interface


def process_input(input_text):
    lexer = LexicalAnalyzer(input_text)
    tokens = []

    print("Input:", input_text)
    while True:
        token = lexer.proxT()
        if token.type == Type.EOF:
            break
        tokens.append(token)

    print("Tokens:", tokens)


if __name__ == "__main__":
    interface = Interface(process_input)
    interface.run()
