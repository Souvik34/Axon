
import ast
import operator


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression: str) -> float | int:
    if not expression or len(expression) > 200:
        raise ValueError("Invalid or oversized expression.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("Invalid mathematical expression.") from exc

    if isinstance(result, float) and not __import__("math").isfinite(result):
        raise ValueError("Calculation produced a non-finite result.")

    if isinstance(result, (int, float)) and abs(result) > 1e100:
        raise ValueError("Calculation result is too large.")

    return result


def _evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large.")

        return OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.operand))

    raise ValueError("Unsupported mathematical expression.")
