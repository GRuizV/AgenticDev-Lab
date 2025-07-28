# builtin imports
import os
import ast
from datetime import datetime




# constants setting
IGNORED_DIRS = {"__pycache__", ".vscode", ".git", "pba_venv"}
DIRS_IGNORE_FILES = {
    "input_pdfs",
    "Amazon Textract",
    "Test PDFs",
    "Manual Extraction",
    "experiments",
    "test #0",
    "test #1",
    "test #2"    
    }  # configurable: map folders only
IGNORED_FILES = {"__init__.py"} # specific files to ignore



def format_arg(arg):
    """Format argument with its type annotation if present."""
    if arg.annotation:
        return f"{arg.arg}: {ast.unparse(arg.annotation)}"
    return arg.arg

def extract_functions_and_methods(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    functions = []
    classes = {}

    for node in tree.body:
        # Top-level functions
        if isinstance(node, ast.FunctionDef):
            args = [format_arg(a) for a in node.args.args]
            returns = ast.unparse(node.returns) if node.returns else "None"
            docstring = ast.get_docstring(node)
            docstring = (f"  # {docstring.splitlines()[0]}" if docstring else "")
            functions.append(f"{node.name}({', '.join(args)}) -> {returns}{docstring}")

        # Classes and methods
        elif isinstance(node, ast.ClassDef):
            methods = []
            for sub_node in node.body:
                if isinstance(sub_node, ast.FunctionDef):
                    args = [format_arg(a) for a in sub_node.args.args]
                    returns = ast.unparse(sub_node.returns) if sub_node.returns else "None"
                    docstring = ast.get_docstring(sub_node)
                    docstring = (f"  # {docstring.splitlines()[0]}" if docstring else "")
                    methods.append(f"{sub_node.name}({', '.join(args)}) -> {returns}{docstring}")
            classes[node.name] = methods

    return functions, classes

def generate_markdown_tree(start_path, output_dir):
    
    modules_index = {}

    def walk_dir(path, prefix=""):
        entries = sorted(os.listdir(path))
        entries = [e for e in entries if not e.startswith(".") and e not in IGNORED_DIRS]
        result = []
        for index, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            connector = "└──" if index == len(entries) - 1 else "├──"

            if os.path.isdir(full_path):
                result.append(f"{prefix}{connector} 📁 {entry}")
                extension = "    " if index == len(entries) - 1 else "│   "
                result += walk_dir(full_path, prefix + extension)
            else:
                # Skip files in special directories
                if any(skip in path for skip in DIRS_IGNORE_FILES):
                    continue
                # Skip explicitly ignored files
                if entry in IGNORED_FILES:
                    continue

                result.append(f"{prefix}{connector} 📄 {entry}")
                if entry.endswith(".py"):
                    functions, classes = extract_functions_and_methods(full_path)
                    modules_index[entry] = {"functions": functions, "classes": classes}
        return result

    # Build tree
    tree_lines = ["# Project Directory\n"]
    tree_lines.append(f"📁 {os.path.basename(start_path) or start_path}/")
    tree_lines += walk_dir(start_path)

    # Append modules index
    tree_lines.append("\n## Modules Index\n")
    for module, content in modules_index.items():
        tree_lines.append(f"- {module}:")
        for fn in content["functions"]:
            tree_lines.append(f"    * {fn}")
        for cls, methods in content["classes"].items():
            tree_lines.append(f"    * class {cls}:")
            for method in methods:
                tree_lines.append(f"        - {method}")
        tree_lines.append("")  # spacing

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"project_map_{timestamp}.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tree_lines))

    print(f"✅ Markdown document map saved to: {output_file}")



st_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA"
out_dir = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\docs\context_maintenance\\"

# ---- Example usage ----
generate_markdown_tree(start_path=st_path, output_dir=out_dir)







