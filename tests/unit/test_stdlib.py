"""
Unit tests untuk Standard Library BroLang.
"""

import pytest
from brolang.stdlib import get_stdlib_module


class TestStdlibMatematika:
    """Test modul matematika."""

    def setup_method(self):
        self.mat = get_stdlib_module("matematika")

    def test_akar(self):
        assert self.mat.akar(25) == 5.0

    def test_sin(self):
        assert abs(self.mat.sin(0)) < 0.0001

    def test_cos(self):
        assert abs(self.mat.cos(0) - 1) < 0.0001

    def test_pi(self):
        assert abs(self.mat.pi() - 3.14159) < 0.001

    def test_absolut(self):
        assert self.mat.absolut(-5) == 5

    def test_faktorial(self):
        assert self.mat.faktorial(5) == 120


class TestStdlibTeks:
    """Test modul teks."""

    def setup_method(self):
        self.t = get_stdlib_module("teks")

    def test_upper(self):
        assert self.t.upper("halo") == "HALO"

    def test_lower(self):
        assert self.t.lower("HALO") == "halo"

    def test_kapital(self):
        assert self.t.kapital("halo dunia") == "Halo dunia"

    def test_potong(self):
        assert self.t.potong("a,b,c", ",") == ["a", "b", "c"]

    def test_gabung(self):
        assert self.t.gabung(["a", "b"], ",") == "a,b"

    def test_panjang(self):
        assert self.t.panjang("halo") == 4


class TestStdlibAcak:
    """Test modul acak."""

    def setup_method(self):
        self.acak = get_stdlib_module("acak")

    def test_bulat(self):
        result = self.acak.bulat(1, 10)
        assert 1 <= result <= 10

    def test_pilih(self):
        items = [1, 2, 3]
        result = self.acak.pilih(items)
        assert result in items
