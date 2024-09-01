import tkinter as tk
from tkinter import filedialog


class Interface:
    def __init__(self, process_input_callback):
        self.process_input_callback = process_input_callback
        self.root = tk.Tk()
        self.root.title("Lexical Analyzer")

        self.root.attributes('-fullscreen', True)

        self.menu_bar = tk.Menu(self.root)

        self.menu_bar.add_cascade(label="Open File", command=self.open_file)
        self.menu_bar.add_cascade(
            label="Run", command=self.run_lexical_analysis)
        self.menu_bar.add_cascade(label="Exit", command=self.root.quit)

        self.root.config(menu=self.menu_bar)

        self.left_text = tk.Text(self.root, wrap=tk.WORD)
        self.right_text = tk.Text(self.root, wrap=tk.WORD)

        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Define tags for token types
        self.right_text.tag_configure("error", foreground="red")
        self.right_text.tag_configure("warning", foreground="yellow")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                input_text = file.read()

            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(tk.END, input_text)

            self.right_text.delete(1.0, tk.END)

    def run_lexical_analysis(self):
        input_text = self.left_text.get(1.0, tk.END).strip()
        if input_text:
            tokens = self.process_input_callback(input_text)
            self.right_text.delete(1.0, tk.END)
            self.display_tokens(tokens)

    def display_tokens(self, tokens):
        for token in tokens:
            if token.type == "UNKNOWN":
                tag = "error"
            elif token.type == "WARNING":
                tag = "warning"
            else:
                tag = None

            self.right_text.insert(tk.END, f"{token}\n", tag)

    def run(self):
        self.root.mainloop()
