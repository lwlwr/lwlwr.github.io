import json
from pathlib import Path
import tempfile
import unittest

from countdown_eval import evaluate, evaluate_file


class EvaluatorTests(unittest.TestCase):
    def test_exact_fraction(self):
        self.assertTrue(evaluate([3, 3, 8, 8], 24, '8/(3-8/3)')['correct'])

    def test_wrong_value(self):
        result = evaluate([2, 3], 6, '2+3')
        self.assertTrue(result['numbers_valid'])
        self.assertFalse(result['correct'])

    def test_multiset(self):
        self.assertFalse(evaluate([2, 2, 3], 6, '2*3')['numbers_valid'])
        self.assertFalse(evaluate([2, 3], 6, '2+2+2')['correct'])

    def test_reject_unsupported(self):
        for expression in ['__import__("os").system("true")', '2**3', '2//3',
                           'True+3', '2.0*3', '-2+3', '2<<3', '0x2*3', '2e0*3', '2#comment']:
            with self.subTest(expression=expression):
                self.assertFalse(evaluate([2, 3], 6, expression)['syntax_valid'])

    def test_division_zero(self):
        result = evaluate([2, 3, 3], 6, '2/(3-3)')
        self.assertTrue(result['syntax_valid'])
        self.assertTrue(result['numbers_valid'])
        self.assertEqual(result['reason'], 'division_by_zero')
        self.assertFalse(result['correct'])

    def test_limits(self):
        self.assertFalse(evaluate([2, 3], 6, '(' * 300)['syntax_valid'])
        self.assertFalse(evaluate([2, 3], 6, None)['correct'])
        with self.assertRaises(ValueError):
            evaluate([True, 3], 6, '2*3')

    def test_denominator_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'predictions.jsonl'
            rows = [dict(id='a', numbers=[2, 3], target=6, expression='2*3'),
                    dict(id='b', numbers=[2, 3], target=6, expression='')]
            path.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
            report = evaluate_file(path)
            self.assertEqual(report['metrics']['correct'], dict(count=1, total=2, rate=0.5))
            self.assertEqual(len(report['input_sha256']), 64)
            rows[1]['id'] = 'a'
            path.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
            with self.assertRaises(ValueError):
                evaluate_file(path)

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'empty.jsonl'
            path.write_text('', encoding='utf-8')
            with self.assertRaises(ValueError):
                evaluate_file(path)


if __name__ == '__main__':
    unittest.main()
