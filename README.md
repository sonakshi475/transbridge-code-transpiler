# Python-to-Java Code Translator (GUI)

This project is a graphical tool that translates user-written Python code into equivalent Java code and also simulates the Python code execution. It supports a subset of Python constructs such as:

- Variable assignment
- `input()` with `int()` and `str()` casting
- `print()` statements
- `if` / `else` conditionals
- `while` loops

The project is implemented using Python's `tkinter` for GUI, `ast` for Python code parsing, and a custom intermediate representation (IR) for translation and simulation.

---

## 🔧 Features

-  **Write Python code** in the GUI
-  **AST-based parser** converts Python to IR
-  **Java code generator** outputs readable Java code
-  **Simulation mode** mimics Python execution with real user input
-  **User input fields** dynamically generated for each `input()` call

---

## 🖼️ GUI Preview

The GUI has 4 main sections:

1. **Python Code Input**
2. **Java Code Output**
3. **Dynamic Input Fields**
4. **Simulated Output Window**

