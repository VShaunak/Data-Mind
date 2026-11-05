import ast
from typing import List, Dict, Any, Tuple, Set

ALLOWED_ROOT_MODULES: Set[str] = {
    "pandas",
    "numpy",
    "scipy",
    "statsmodels",
    "sklearn",
    "plotly",
    "matplotlib",
    "seaborn",
    "PIL",
    "math",
    "random",
    "statistics",
    "datetime",
    "collections",
    "itertools",
    "re",
    "json",
    "io",
    "typing",
    "pathlib",
    "sys",  # for sys.argv or sys.stdout/stderr only
}

FORBIDDEN_CALLS: Set[str] = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "open_code",
}

FORBIDDEN_ATTRIBUTES: Set[str] = {
    "system",
    "popen",
    "spawn",
    "subprocess",
    "fork",
    "kill",
    "rmtree",
    "remove",
    "unlink",
    "rmdir",
    "environ",
    "getenv",
    "putenv",
}

class SecurityGuardrailVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.imports: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            root_mod = alias.name.split(".")[0]
            self.imports.append(alias.name)
            if root_mod not in ALLOWED_ROOT_MODULES:
                self.errors.append(f"Disallowed import: '{alias.name}'. Only approved data science libraries are permitted.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            root_mod = node.module.split(".")[0]
            self.imports.append(node.module)
            if root_mod not in ALLOWED_ROOT_MODULES:
                self.errors.append(f"Disallowed import from: '{node.module}'.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Check direct calls like eval(...) or exec(...)
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.errors.append(f"Forbidden function call: '{node.func.id}()'.")
        # Check attribute calls like os.system(...)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_ATTRIBUTES:
                self.errors.append(f"Forbidden method call: '.{node.func.attr}()'.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # Prevent access to __builtins__, __globals__, os.environ, etc.
        if node.attr in ("__builtins__", "__globals__", "__subclasses__", "__bases__"):
            self.errors.append(f"Forbidden introspection attribute: '{node.attr}'.")
        elif node.attr in ("environ", "getenv"):
            self.errors.append(f"Forbidden environment access attribute: '{node.attr}'.")
        self.generic_visit(node)

def validate_python_code(code: str) -> Tuple[bool, List[str], List[str], List[str]]:
    """
    Validates Python code against AST syntax, import allowlists, and execution security guardrails.
    Returns: (is_valid, errors, warnings, detected_imports)
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not code or not code.strip():
        return False, ["Code is empty."], [], []

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"SyntaxError on line {e.lineno}: {e.msg}"], [], []
    except Exception as e:
        return False, [f"Failed to parse AST: {str(e)}"], [], []

    visitor = SecurityGuardrailVisitor()
    visitor.visit(tree)

    errors.extend(visitor.errors)
    warnings.extend(visitor.warnings)

    is_valid = len(errors) == 0
    return is_valid, errors, warnings, visitor.imports

