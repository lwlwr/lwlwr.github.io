"""Independent expression evaluator added 2026-10-23, not historical reward code."""

import argparse
import ast
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re


def evaluate(numbers, target, expression):
    """Require each positive input integer exactly once; allow +, -, *, / only.

    Unary operators, floats, booleans, calls, names and powers are rejected.
    Intermediate fractions and negative values are permitted. No eval/exec.
    """
    if (not isinstance(numbers, list) or not 1 <= len(numbers) <= 10
            or any(type(n) is not int or not 1 <= n <= 10**6 for n in numbers)
            or type(target) is not int or abs(target) > 10**12):
        raise ValueError('numbers: 1-10 positive integers <= 1e6; target: integer <= 1e12 in magnitude')
    result = dict(syntax_valid=False, numbers_valid=False, correct=False, reason='syntax')
    if (not isinstance(expression, str) or not 1 <= len(expression) <= 256
            or re.fullmatch(r'[0-9+*/()\s-]+', expression) is None):
        return result
    try:
        tree = ast.parse(expression.strip(), mode='eval')
        if sum(1 for _ in ast.walk(tree)) > 100:
            return result
        def visit(node):
            if isinstance(node, ast.Constant) and type(node.value) is int:
                if not 1 <= node.value <= 10**6:
                    raise ValueError('literal out of range')
                return Fraction(node.value)
            if isinstance(node, ast.BinOp) and type(node.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                return left / right
            raise ValueError('unsupported syntax')

        # Validate the entire syntax before evaluating: division by zero must
        # not hide a later invalid literal or cause an incomplete number count.
        for node in ast.walk(tree):
            if type(node) not in (ast.Expression, ast.BinOp, ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div):
                return result
            if isinstance(node, ast.Constant) and (type(node.value) is not int or not 1 <= node.value <= 10**6):
                return result
        result['syntax_valid'] = True
        literals = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)]
        result['numbers_valid'] = Counter(literals) == Counter(numbers)
        value = visit(tree.body)
        result['value'] = str(value)
        result['correct'] = result['numbers_valid'] and value == target
        result['reason'] = ('numbers' if not result['numbers_valid'] else
                            'ok' if result['correct'] else 'wrong_value')
    except ZeroDivisionError:
        result['reason'] = 'division_by_zero'
    except (SyntaxError, ValueError, RecursionError):
        result.update(syntax_valid=False, numbers_valid=False, reason='syntax')
    return result


def evaluate_file(path):
    """One pre-extracted expression per task; malformed rows fail loudly."""
    raw = Path(path).read_bytes()
    rows, seen = [], set()
    for line_no, line in enumerate(raw.decode('utf-8').splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        task_id = row['id']
        if not isinstance(task_id, str) or not task_id or task_id in seen:
            raise ValueError(f'line {line_no}: id must be a unique nonempty string')
        seen.add(task_id)
        rows.append(dict(id=task_id, **evaluate(row['numbers'], row['target'], row['expression'])))
    if not rows:
        raise ValueError('empty evaluation file')
    n = len(rows)
    metrics = {}
    for key in ('syntax_valid', 'numbers_valid', 'correct'):
        count = sum(row[key] for row in rows)
        metrics[key] = dict(count=count, total=n, rate=count / n)
    return dict(protocol='countdown-expression-v1', input_sha256=hashlib.sha256(raw).hexdigest(),
                metrics=metrics, samples=rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('predictions', help='JSONL with id, numbers, target, expression')
    args = parser.parse_args()
    print(json.dumps(evaluate_file(args.predictions), ensure_ascii=False, indent=2))
