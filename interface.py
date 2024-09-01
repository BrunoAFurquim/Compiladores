import tkinter as tk
from tkinter import filedialog


class Interface:
    def __init__(self, process_input_callback):
        self.process_input_callback = process_input_callback
        self.root = tk.Tk()
        self.root.title("Lexical Analyzer")

        self.root.attributes('-fullscreen', True)

        self.menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open File", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        self.menu_bar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=self.menu_bar)

        self.left_text = tk.Text(self.root, wrap=tk.WORD)
        self.right_text = tk.Text(self.root, wrap=tk.WORD)

        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                input_text = file.read()

            self.left_text.delete(1.0, tk.END)
            self.left_text.insert(tk.END, input_text)

            self.right_text.delete(1.0, tk.END)
            self.process_input_callback(input_text)

    def display_tokens(self, tokens):
        for token in tokens:
            self.right_text.insert(tk.END, f"{token}\n")

    def run(self):
        self.root.mainloop()
