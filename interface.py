# interface.py
import tkinter as tk
from tkinter import filedialog, messagebox
from lexicalAnalyzer import LexicalAnalyzer, Type  
from sysntaticAnalysis import SyntacticAnalyzer 
from code_generator import StackCodeGenerator  
class Interface:
    def __init__(self, process_input_callback):
        self.process_input_callback = process_input_callback
        self.root = tk.Tk()
        self.root.title("Lexical Analyzer")
        self.root.attributes('-fullscreen', True)

        # Menu com as opções
        self.menu_bar = tk.Menu(self.root)
        self.menu_bar.add_cascade(label="Open File", command=self.open_file)
        self.menu_bar.add_cascade(label="Run", command=self.run_lexical_analysis)
        self.menu_bar.add_cascade(label="Export", command=self.export)
        self.menu_bar.add_cascade(label="Generate Code", command=self.generate_code)  # Novo botão para gerar código
        self.menu_bar.add_cascade(label="Exit", command=self.root.quit)
        self.root.config(menu=self.menu_bar)

        self.line_numbers = tk.Text(self.root, width=5, padx=5, state='disabled')
        self.left_text = tk.Text(self.root, wrap=tk.WORD)
        self.right_text = tk.Text(self.root, wrap=tk.WORD)

        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.right_text.tag_configure("error", foreground="red")
        self.right_text.tag_configure("warning", foreground="yellow")

        self.left_text.bind("<KeyRelease>", self.update_line_numbers)
        self.original_expression = ""

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                input_text = file.read()

            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(tk.END, input_text)
            self.right_text.delete(1.0, tk.END)
            self.update_line_numbers()

    def run_lexical_analysis(self):
        self.original_expression = self.left_text.get(1.0, tk.END).strip()
        if self.original_expression:
            tokens = self.process_input_callback(self.original_expression)
            self.right_text.delete(1.0, tk.END)
            self.display_tokens(tokens)
            self.run_syntactic_analysis()

    def run_syntactic_analysis(self):
        lexer = LexicalAnalyzer(self.original_expression)
        parser = SyntacticAnalyzer(lexer)
        try:
            parser.program_declaration()
            self.right_text.insert(tk.END, "\nSyntactic analysis: Success", "success")
        except SyntaxError as e:
            self.right_text.insert(tk.END, f"\nSyntactic analysis ERROR: {e}", "error")

    # Novo método para gerar o código a partir da análise sintática
    def generate_code(self):
        lexer = LexicalAnalyzer(self.original_expression)
        parser = SyntacticAnalyzer(lexer)
        code_generator = StackCodeGenerator()

        try:
            parser.program_declaration()  # Análise sintática do programa
            self.right_text.insert(tk.END, "\nSyntactic analysis: Success", "success")

            # Gera o código para variáveis
            for var_name, var_type in parser.declared_variables:
                code_generator.generate_variable_declaration(var_name, var_type)

            # Gera o código para procedimentos
            for proc in parser.declared_procedures:
                code_generator.generate_procedure_declaration(proc)

            self.generated_code = code_generator.get_code()
            self.display_generated_code(self.generated_code)

        except SyntaxError as e:
            self.right_text.insert(tk.END, f"\nSyntactic analysis ERROR: {e}", "error")


    def display_tokens(self, tokens):
        for token in tokens:
            if "UNKNOWN" in token:
                tag = "error"
            elif "WARNING" in token:
                tag = "warning"
            else:
                tag = None
            self.right_text.insert(tk.END, f"{token}\n", tag)

    def display_generated_code(self, generated_code):
        self.right_text.insert(tk.END, "\nGenerated Code:\n", "success")
        self.right_text.insert(tk.END, generated_code)

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        line_count = int(self.left_text.index('end-1c').split('.')[0])
        line_number_string = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert(1.0, line_number_string)
        self.line_numbers.config(state='disabled')

    def export(self):
        tokens_text = self.right_text.get(1.0, tk.END).strip()
        
        if tokens_text:  
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                title="Save tokens as"
            )
            if file_path:  
                with open(file_path, 'w') as file:
                    file.write("Original Expression:\n")
                    file.write(self.original_expression + "\n\n")
                    file.write("Tokens:\n")
                    file.write(tokens_text)
                messagebox.showinfo("Export", "Tokens exported successfully!")
        else:
            messagebox.showwarning("Export", "No tokens to export!")

    def run(self):
        self.root.mainloop()
