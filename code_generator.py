class StackCodeGenerator:
    def __init__(self):
        self.code = []  
        self.label_counter = 0  

    def generate_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def generate_program(self, memory_slots):
        self.code.append("INPP")  
        self.code.append(f"AMEM {memory_slots}")  

    def generate_input(self, var_index):
        self.code.append("LEIT")  
        self.code.append(f"ARMZ {var_index}")  

    def generate_output(self, var_index):
        self.code.append(f"CRVL {var_index}")  
        self.code.append("IMPE")  

    def generate_constant(self, value):
        self.code.append(f"CRCT {value}")  

    def generate_store(self, var_index):
        self.code.append(f"ARMZ {var_index}")

    def generate_load(self, var_index):
        self.code.append(f"CRVL {var_index}")

    def generate_addition(self):
        self.code.append("SOMA")

    def generate_subtraction(self):
        self.code.append("SUBT")

    def generate_multiplication(self):
        self.code.append("MULT")

    def generate_division(self):
        self.code.append("DIVI")

    def generate_jump(self, label):
        self.code.append(f"DSVS {label}")

    def generate_conditional_jump(self, label):
        self.code.append(f"DSVF {label}")

    def generate_label_declaration(self, label):
        self.code.append(f"{label} NADA")

    def generate_end(self):
        self.code.append("PARA")  

    def get_code(self):
        return "\n".join(self.code)
