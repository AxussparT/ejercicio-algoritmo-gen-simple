"""
Evaluador seguro de funciones matemáticas univariadas f(x).
Analiza expresiones matemáticas mediante AST restringido para garantizar seguridad.
"""
import ast
import math
import numpy as np
from typing import Callable, Union

ALLOWED_NAMES = {
    'sin': np.sin,
    'cos': np.cos,
    'tan': np.tan,
    'exp': np.exp,
    'log': np.log,
    'log10': np.log10,
    'sqrt': np.sqrt,
    'abs': np.abs,
    'sinh': np.sinh,
    'cosh': np.cosh,
    'tanh': np.tanh,
    'asin': np.arcsin,
    'acos': np.arccos,
    'atan': np.arctan,
    'pi': np.pi,
    'e': np.e
}

ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Constant,
    ast.Load,
    # Operadores permitidos
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.USub, ast.UAdd
)

class SafeEvaluator:
    """
    Parser y evaluador seguro para funciones univariadas de la forma f(x).
    """
    def __init__(self, expression_str: str):
        self.expression_str = expression_str.strip()
        # Normalizar notación común como ^ a **
        normalized = self.expression_str.replace('^', '**')
        self._compiled_code = self._validate_and_compile(normalized)

    def _validate_and_compile(self, expr: str):
        try:
            tree = ast.parse(expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Error de sintaxis en la expresión: {e.msg}")

        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_NODES):
                raise ValueError(f"Elemento no permitido en la expresión matemática: {type(node).__name__}")
            if isinstance(node, ast.Name):
                if node.id != 'x' and node.id not in ALLOWED_NAMES:
                    raise ValueError(f"Variable o función no reconocida: '{node.id}'. Use 'x' y funciones estándar como sin, cos, exp, etc.")
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_NAMES:
                    raise ValueError("Llamada a función no permitida o no reconocida.")

        return compile(tree, filename="<math_expression>", mode="eval")

    def evaluate(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Evalúa la función f(x) para un escalar o un array de numpy."""
        local_scope = {'x': x, **ALLOWED_NAMES}
        try:
            result = eval(self._compiled_code, {"__builtins__": {}}, local_scope)
            if isinstance(result, (int, float)):
                if math.isnan(result) or math.isinf(result):
                    return 1e12 # Penalización en caso de indeterminación
                return float(result)
            elif isinstance(result, np.ndarray):
                result = np.nan_to_num(result, nan=1e12, posinf=1e12, neginf=-1e12)
                return result
            return float(result)
        except ZeroDivisionError:
            return 1e12
        except Exception as e:
            raise RuntimeError(f"Error al evaluar f(x): {str(e)}")

    def __call__(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        return self.evaluate(x)
