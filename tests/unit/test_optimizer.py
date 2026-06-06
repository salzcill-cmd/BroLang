"""
Unit tests untuk Optimizer BroLang.
"""

import pytest
from brolang.ast.nodes import (
    NumberNode, DecimalNode, StringNode, BooleanNode,
    BinaryOpNode, UnaryOpNode,
)
from brolang.optimizer import Optimizer


class TestConstantFolding:
    """Test constant folding optimization."""

    def setup_method(self):
        self.optimizer = Optimizer()

    def test_add_numbers(self):
        node = BinaryOpNode(
            left=NumberNode(value=2),
            operator="+",
            right=NumberNode(value=3),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, NumberNode)
        assert result.value == 5

    def test_subtract_numbers(self):
        node = BinaryOpNode(
            left=NumberNode(value=10),
            operator="-",
            right=NumberNode(value=3),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, NumberNode)
        assert result.value == 7

    def test_multiply_numbers(self):
        node = BinaryOpNode(
            left=NumberNode(value=4),
            operator="*",
            right=NumberNode(value=3),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, NumberNode)
        assert result.value == 12

    def test_string_concat(self):
        node = BinaryOpNode(
            left=StringNode(value="Halo "),
            operator="+",
            right=StringNode(value="Dunia"),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, StringNode)
        assert result.value == "Halo Dunia"

    def test_comparison_equal(self):
        node = BinaryOpNode(
            left=NumberNode(value=5),
            operator="==",
            right=NumberNode(value=5),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, BooleanNode)
        assert result.value is True

    def test_comparison_not_equal(self):
        node = BinaryOpNode(
            left=NumberNode(value=5),
            operator="!=",
            right=NumberNode(value=3),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, BooleanNode)
        assert result.value is True

    def test_logical_and(self):
        node = BinaryOpNode(
            left=BooleanNode(value=True),
            operator="dan",
            right=BooleanNode(value=True),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, BooleanNode)
        assert result.value is True

    def test_logical_or(self):
        node = BinaryOpNode(
            left=BooleanNode(value=False),
            operator="atau",
            right=BooleanNode(value=True),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, BooleanNode)
        assert result.value is True

    def test_unary_minus(self):
        node = UnaryOpNode(operator="-", operand=NumberNode(value=5))
        result = self.optimizer.visit(node)
        assert isinstance(result, NumberNode)
        assert result.value == -5

    def test_unary_not(self):
        node = UnaryOpNode(operator="bukan", operand=BooleanNode(value=True))
        result = self.optimizer.visit(node)
        assert isinstance(result, BooleanNode)
        assert result.value is False


class TestAlgebraicSimplification:
    """Test algebraic simplification."""

    def setup_method(self):
        self.optimizer = Optimizer()

    def test_add_zero(self):
        node = BinaryOpNode(
            left=NumberNode(value=5),
            operator="+",
            right=NumberNode(value=0),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, NumberNode)
        assert result.value == 5

    def test_multiply_by_one(self):
        node = BinaryOpNode(
            left=NumberNode(value=5),
            operator="*",
            right=NumberNode(value=1),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, NumberNode)
        assert result.value == 5

    def test_multiply_by_zero(self):
        node = BinaryOpNode(
            left=NumberNode(value=5),
            operator="*",
            right=NumberNode(value=0),
        )
        result = self.optimizer.visit(node)
        assert isinstance(result, NumberNode)
        assert result.value == 0
