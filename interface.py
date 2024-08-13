import tkinter as tk
from tkinter import filedialog


class Interface:
    def __init__(self, process_input_callback):
        self.process_input_callback = process_input_callback
        self.root = tk.Tk()
        self.root.title("Lexical Analyzer")

        open_button = tk.Button(
            self.root, text="Open File", command=self.open_file)
        open_button.pack(pady=20)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                input_text = file.read()
            self.process_input_callback(input_text)

    def run(self):
        self.root.mainloop()
