"""
Evaluador seguro de funciones matemáticas para dimensiones arbitrarias (1D, 2D, ... nD).
Analiza expresiones matemáticas mediante AST restringido para garantizar seguridad
e incluye detección automática del número de dimensiones.
"""
import ast
import re
import math
import numpy as np
from typing import Callable, Union, List, Any

ALLOWED_FUNCTIONS = {
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
    'e': np.e,
    # Funciones vectoriales / agregación
    'sum': np.sum,
    'prod': np.prod,
    'mean': np.mean,
    'len': len,
    'min': np.min,
    'max': np.max
}

ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Constant,
    ast.Load,
    ast.Subscript,
    ast.Slice,
    # Operadores aritméticos
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.USub, ast.UAdd
)

def detect_dimensions(expression_str: str) -> int:
    """
    Detecta automáticamente el número de dimensiones implícito en una expresión matemática:
    - Variables x1, x2, ..., xN -> N
    - Variables x[0], x[1], ..., x[N-1] -> N
    - Variables x, y -> 2; x, y, z -> 3; x, y, z, w -> 4
    - Por defecto retorna 1 si solo se encuentra 'x' univariada.
    """
    expr = expression_str.strip()
    if not expr:
        return 1

    detected = 1

    # 1. Patrón x1, x2, x3... o x_1, x_2...
    matches_num = re.findall(r'\bx_?(\d+)\b', expr, re.IGNORECASE)
    if matches_num:
        max_idx = max(int(m) for m in matches_num)
        detected = max(detected, max_idx)

    # 2. Patrón x[0], x[1]...
    matches_sub = re.findall(r'\bx\[\s*(\d+)\s*\]', expr, re.IGNORECASE)
    if matches_sub:
        max_sub = max(int(m) for m in matches_sub) + 1
        detected = max(detected, max_sub)

    # 3. Patrón de variables espaciales x, y, z, w
    lower_expr = expr.lower()
    has_w = bool(re.search(r'\bw\b', lower_expr))
    has_z = bool(re.search(r'\bz\b', lower_expr))
    has_y = bool(re.search(r'\by\b', lower_expr))

    if has_w:
        detected = max(detected, 4)
    elif has_z:
        detected = max(detected, 3)
    elif has_y:
        detected = max(detected, 2)

    return max(1, detected)

class SafeEvaluator:
    """
    Parser y evaluador seguro para funciones de n dimensiones.
    """
    def __init__(self, expression_str: str, dimensions: int = 1):
        self.expression_str = expression_str.strip()
        self.dimensions = max(1, int(dimensions))
        normalized = self.expression_str.replace('^', '**')
        self._compiled_code = self._validate_and_compile(normalized)
        
        # Determinar si la expresión utiliza 'y', 'z' o 'w'
        lower = normalized.lower()
        self.uses_spatial_vars = bool(re.search(r'\b[yzw]\b', lower))
        self.uses_indexed_vars = bool(re.search(r'\bx_?\d+\b', lower))

    def _validate_and_compile(self, expr: str):
        try:
            tree = ast.parse(expr, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Error de sintaxis en la expresión: {e.msg}")

        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_NODES):
                raise ValueError(f"Elemento no permitido en la expresión matemática: {type(node).__name__}")
            if isinstance(node, ast.Name):
                name = node.id
                # Nombres válidos: funciones, variables numéricas x, y, z, w, x1, x2, etc.
                is_math_func = name in ALLOWED_FUNCTIONS
                is_valid_var = (
                    name in ('x', 'y', 'z', 'w') or
                    re.match(r'^x_?\d+$', name) is not None
                )
                if not (is_math_func or is_valid_var):
                    raise ValueError(f"Variable o función no reconocida: '{name}'.")
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in ALLOWED_FUNCTIONS:
                        raise ValueError(f"Llamada a función no permitida: '{node.func.id}'.")

        return compile(tree, filename="<math_expression>", mode="eval")

    def evaluate(self, x_input: Union[float, np.ndarray, list]) -> float:
        """
        Evalúa f(x) para un punto escalar o un vector de n dimensiones.
        """
        vec = np.atleast_1d(np.asarray(x_input, dtype=float))
        
        local_scope = dict(ALLOWED_FUNCTIONS)
        
        # Mapeo de variables según la formulación
        if self.uses_spatial_vars:
            # x, y, z, w como coordenadas individuales
            local_scope['x'] = float(vec[0]) if len(vec) > 0 else 0.0
            if len(vec) > 1: local_scope['y'] = float(vec[1])
            if len(vec) > 2: local_scope['z'] = float(vec[2])
            if len(vec) > 3: local_scope['w'] = float(vec[3])
        else:
            if self.dimensions == 1 and not self.uses_indexed_vars:
                # 1D escalar
                local_scope['x'] = float(vec[0]) if len(vec) > 0 else 0.0
            else:
                # nD: 'x' representa el array completo para sum(x**2), x[0], etc.
                local_scope['x'] = vec

        # Siempre exponer x1, x2, ... y x_1, x_2, ...
        for i in range(len(vec)):
            val = float(vec[i])
            local_scope[f'x{i+1}'] = val
            local_scope[f'x_{i+1}'] = val

        try:
            result = eval(self._compiled_code, {"__builtins__": {}}, local_scope)
            if isinstance(result, (int, float, np.floating, np.integer)):
                val = float(result)
                if math.isnan(val) or math.isinf(val):
                    return 1e12
                return val
            elif isinstance(result, np.ndarray):
                arr = np.nan_to_num(result, nan=1e12, posinf=1e12, neginf=-1e12)
                return float(np.sum(arr))
            return float(result)
        except ZeroDivisionError:
            return 1e12
        except Exception as e:
            raise RuntimeError(f"Error al evaluar f(x): {str(e)}")

    def __call__(self, x_input: Union[float, np.ndarray, list]) -> float:
        return self.evaluate(x_input)
