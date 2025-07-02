import tkinter as tk
from tkinter import messagebox, scrolledtext
import ast

# --- IR Node Definitions ---
class IRNode: pass

class IRAssignment(IRNode):
    def __init__(self, target, value):
        self.target = target
        self.value = value

class IRPrint(IRNode):
    def __init__(self, value):
        self.value = value

class IRInput(IRNode):
    def __init__(self, target, prompt="Enter value", cast_type="String"):
        self.target = target
        self.prompt = prompt
        self.cast_type = cast_type

class IRIf(IRNode):
    def __init__(self, condition, body, orelse=[]):
        self.condition = condition
        self.body = body
        self.orelse = orelse

class IRWhile(IRNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

# --- AST to IR Parser ---
class IRBuilder(ast.NodeVisitor):
    def __init__(self):
        self.ir = []

    def visit_Module(self, node):
        for stmt in node.body:
            ir_node = self.visit(stmt)
            if isinstance(ir_node, list):
                self.ir.extend(ir_node)
            elif ir_node:
                self.ir.append(ir_node)

    def visit_Assign(self, node):
        if isinstance(node.value, ast.Call):
            func = getattr(node.value.func, 'id', '')
            if func == "int" or func == "str":
                if isinstance(node.value.args[0], ast.Call) and getattr(node.value.args[0].func, 'id', '') == "input":
                    prompt = node.value.args[0].args[0].s if node.value.args[0].args else "Enter a value"
                    target = node.targets[0].id
                    cast = "int" if func == "int" else "String"
                    return IRInput(target=target, prompt=prompt, cast_type=cast)
        target = node.targets[0].id
        value = ast.unparse(node.value)
        return IRAssignment(target, value)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and getattr(node.value.func, 'id', '') == "print":
            return IRPrint(ast.unparse(node.value.args[0]))
        return None

    def visit_If(self, node):
        condition = ast.unparse(node.test)
        body = [self.visit(stmt) for stmt in node.body if self.visit(stmt)]
        orelse = [self.visit(stmt) for stmt in node.orelse if self.visit(stmt)] if node.orelse else []
        return IRIf(condition, body, orelse)

    def visit_While(self, node):
        condition = ast.unparse(node.test)
        body = [self.visit(stmt) for stmt in node.body if self.visit(stmt)]
        return IRWhile(condition, body)

def python_to_ir(code):
    tree = ast.parse(code)
    builder = IRBuilder()
    builder.visit(tree)
    return builder.ir

# --- IR to Java Code ---
def ir_to_java(ir_nodes, indent="        "):
    java = []
    for node in ir_nodes:
        if isinstance(node, IRInput):
            java.append(f'{indent}System.out.print("{node.prompt}: ");')
            if node.cast_type == "int":
                java.append(f'{indent}int {node.target} = scanner.nextInt();')
            else:
                java.append(f'{indent}String {node.target} = scanner.nextLine();')
        elif isinstance(node, IRAssignment):
            java.append(f"{indent}{node.target} = {node.value};")
        elif isinstance(node, IRPrint):
            java.append(f"{indent}System.out.println({node.value});")
        elif isinstance(node, IRIf):
            java.append(f"{indent}if ({node.condition}) {{")
            java += ir_to_java(node.body, indent + "    ")
            java.append(f"{indent}}}")
            if node.orelse:
                java.append(f"{indent}else {{")
                java += ir_to_java(node.orelse, indent + "    ")
                java.append(f"{indent}}}")
        elif isinstance(node, IRWhile):
            java.append(f"{indent}while ({node.condition}) {{")
            java += ir_to_java(node.body, indent + "    ")
            java.append(f"{indent}}}")
    return java

# --- GUI ---
def create_gui():
    root = tk.Tk()
    root.title("Python to Java Translator (Dynamic)")

    tk.Label(root, text="Python Code:").grid(row=0, column=0, sticky='w')
    code_input = scrolledtext.ScrolledText(root, height=8, width=70)
    code_input.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    tk.Button(root, text="Translate to Java", command=lambda: on_translate()).grid(row=2, column=0, pady=5, sticky='w')

    tk.Label(root, text="Java Output:").grid(row=3, column=0, sticky='w')
    java_output = scrolledtext.ScrolledText(root, height=15, width=70)
    java_output.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

    input_frame = tk.LabelFrame(root, text="Inputs for Simulation")
    input_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky='we')
    input_entries = {}

    tk.Label(root, text="Simulation Output:").grid(row=6, column=0, sticky='w')
    sim_output = scrolledtext.ScrolledText(root, height=5, width=70, state="disabled")
    sim_output.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

    tk.Button(root, text="Run Simulation", command=lambda: on_simulate()).grid(row=8, column=0, pady=5, sticky='w')

    ir_nodes = []

    def on_translate():
        nonlocal ir_nodes
        user_code = code_input.get("1.0", tk.END).strip()
        try:
            ir_nodes = python_to_ir(user_code)
            java_code = [
                "import java.util.Scanner;",
                "public class Main {",
                "    public static void main(String[] args) {",
                "        Scanner scanner = new Scanner(System.in);"
            ]
            java_code += ir_to_java(ir_nodes)
            java_code += ["    }", "}"]
            java_output.delete("1.0", tk.END)
            java_output.insert(tk.END, "\n".join(java_code))

            # Reset input fields
            for widget in input_frame.winfo_children():
                widget.destroy()
            input_entries.clear()

            row = 0
            for node in ir_nodes:
                if isinstance(node, IRInput):
                    tk.Label(input_frame, text=node.prompt).grid(row=row, column=0)
                    entry = tk.Entry(input_frame, width=20)
                    entry.grid(row=row, column=1)
                    input_entries[node.target] = entry
                    row += 1

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_simulate():
        inputs = {k: e.get() for k, e in input_entries.items()}
        context = {}
        output = []

        def run_ir(nodes):
            nonlocal context, output
            for node in nodes:
                if isinstance(node, IRInput):
                    val = inputs.get(node.target, "0")
                    context[node.target] = int(val) if node.cast_type == "int" else val
                elif isinstance(node, IRAssignment):
                    context[node.target] = eval(node.value, {}, context)
                elif isinstance(node, IRPrint):
                    output.append(str(eval(node.value, {}, context)))
                elif isinstance(node, IRIf):
                    if eval(node.condition, {}, context):
                        run_ir(node.body)
                    else:
                        run_ir(node.orelse)
                elif isinstance(node, IRWhile):
                    while eval(node.condition, {}, context):
                        run_ir(node.body)

        try:
            run_ir(ir_nodes)
            sim_output.config(state="normal")
            sim_output.delete("1.0", tk.END)
            sim_output.insert(tk.END, "\n".join(output))
            sim_output.config(state="disabled")
        except Exception as e:
            sim_output.config(state="normal")
            sim_output.insert(tk.END, f"\nError: {e}")
            sim_output.config(state="disabled")

    root.mainloop()

create_gui()
