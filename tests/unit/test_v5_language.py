"""
Unit tests untuk BroLang v5.0 Features
=====================================

Tests untuk:
- Type System (tipe data dengan anotasi)
- Interfaces/Antarmuka
- Abstract Classes (kelas abstrak)
- Higher-Order Functions (peta, saring, kurangi)
- Result/Option Types (penanganan error)
- Macros (metaprogramming)
- Module System (ruang nama)
- Access Modifiers (publik, privat, terlindungi)
- Null Coalescing (??)
- Chained Comparisons (0 < x < 10)
- For Each with Index
- Generators (hasilkan)
- Iterator Protocol (__iter__/__next__)
- Properties (getter/setter)
- Static Methods (statis)
- Type Checking (cek_tipe/pastikan)
- String Interpolation ($variable / f-string)
- Class Inheritance Syntax
"""

import pytest
from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.exceptions import RuntimeError_


def run_code(code):
    """Helper untuk menjalankan kode BroLang."""
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.interpret(ast)
    return interp.output


class TestTypeSystem:
    """Tests untuk Type System v5.0."""

    def test_type_alias(self):
        code = '''
tipe AngkaPositif = angka
buat x = 10
tulis x
'''
        output = run_code(code)
        assert "10" in output[0]

    def test_function_basic(self):
        code = '''
fungsi tambah(a, b)
    kembali a + b
selesai
tulis tambah(2, 3)
'''
        output = run_code(code)
        assert "5" in output[0]


class TestHigherOrderFunctions:
    """Tests untuk Higher-Order Functions v5.0."""

    def test_map_basic(self):
        code = '''
buat angka = [1, 2, 3, 4, 5]
buat hasil = peta(angka, lalu(x) x * 2)
tulis hasil
'''
        output = run_code(code)
        assert "[2, 4, 6, 8, 10]" in output[0]

    def test_filter_basic(self):
        code = '''
buat angka = [1, 2, 3, 4, 5]
buat hasil = saring(angka, lalu(x) x > 3)
tulis hasil
'''
        output = run_code(code)
        assert "[4, 5]" in output[0]

    def test_reduce_basic(self):
        code = '''
buat angka = [1, 2, 3, 4, 5]
buat hasil = kurangi(angka, lalu(a, b) a + b, 0)
tulis hasil
'''
        output = run_code(code)
        assert "15" in output[0]


class TestResultOptionTypes:
    """Tests untuk Result/Option Types v5.0."""

    def test_result_success(self):
        code = '''
buat hasil = Benar(42)
tulis hasil
'''
        output = run_code(code)
        assert "42" in output[0]

    def test_result_failure(self):
        code = '''
buat hasil = Salah("error message")
tulis hasil
'''
        output = run_code(code)
        assert "error message" in output[0]

    def test_option_some(self):
        code = '''
buat nilai = Ada(100)
tulis nilai
'''
        output = run_code(code)
        assert "100" in output[0]


class TestMacros:
    """Tests untuk Macros v5.0."""

    def test_macro_definition(self):
        code = '''
makro Sapa(nama)
    tulis "Halo, " + nama
selesai
Sapa("Budi")
'''
        output = run_code(code)
        assert "Halo, Budi" in output[0]

    def test_macro_no_params(self):
        code = '''
makro Logger()
    tulis "[LOG] Program dimulai"
selesai
Logger()
'''
        output = run_code(code)
        assert "[LOG] Program dimulai" in output[0]


class TestModuleSystem:
    """Tests untuk Module System v5.0."""

    def test_namespace(self):
        code = '''
ruang nama Matematika
    fungsi tambah(a, b)
        kembali a + b
    selesai
selesai
pakai Matematika
tulis Matematika.tambah(2, 3)
'''
        output = run_code(code)
        assert "5" in output[0]


class TestNullCoalescing:
    """Tests untuk Null Coalescing v5.0."""

    def test_null_coalescing_with_value(self):
        code = '''
buat x = 10
buat hasil = x ?? 0
tulis hasil
'''
        output = run_code(code)
        assert "10" in output[0]

    def test_null_coalescing_with_null(self):
        code = '''
buat x = kosong
buat hasil = x ?? 0
tulis hasil
'''
        output = run_code(code)
        assert "0" in output[0]


class TestChainedComparisons:
    """Tests untuk Chained Comparisons v5.0."""

    def test_chained_comparison_true(self):
        code = '''
buat x = 5
jika 0 < x < 10 maka
    tulis "dalam range"
selesai
'''
        output = run_code(code)
        assert "dalam range" in output[0]


class TestForEachWithIndex:
    """Tests untuk For Each with Index v5.0."""

    def test_for_each_basic(self):
        code = '''
buat buah = ["apel", "mangga", "jeruk"]
untuk setiap item dalam buah lakukan
    tulis item
selesai
'''
        output = run_code(code)
        assert "apel" in output[0]
        assert "mangga" in output[1]
        assert "jeruk" in output[2]


class TestAccessModifiers:
    """Tests untuk Access Modifiers v5.0."""

    def test_public_function(self):
        code = '''
publik fungsi sapa()
    tulis "Halo!"
selesai
sapa()
'''
        output = run_code(code)
        assert "Halo!" in output[0]

    def test_private_function(self):
        code = '''
privat fungsi internal()
    tulis "internal"
selesai
tulis "public"
'''
        output = run_code(code)
        assert "public" in output[0]


class TestInterfaces:
    """Tests untuk Interfaces v5.0."""

    def test_interface_declaration(self):
        code = '''
antarmuka DapatJalankan {
    fungsi jalankan()
}
tulis "interface declared"
'''
        output = run_code(code)
        assert "interface declared" in output[0]


class TestAbstractClasses:
    """Tests untuk Abstract Classes v5.0."""

    def test_abstract_class_declaration(self):
        code = '''
abstrak kelas Hewan {
    fungsi suara()
}
tulis "abstract class declared"
'''
        output = run_code(code)
        assert "abstract class declared" in output[0]

    def test_abstract_class_cannot_instantiate(self):
        code = '''
abstrak kelas Hewan {
    fungsi suara()
}
buat hewan = Hewan()
'''
        from brolang.exceptions import RuntimeError_
        with pytest.raises(RuntimeError_):
            run_code(code)

    def test_abstract_class_inherit_works(self):
        code = '''
abstrak kelas Hewan {
    fungsi suara()
}
kelas Kucing(Hewan)
    fungsi suara()
        tulis "Meong!"
    selesai
selesai
buat k = Kucing()
k.suara()
'''
        output = run_code(code)
        assert "Meong!" in output[0]


class TestAccessModifierEnforcement:
    """Tests untuk access modifier enforcement v5.0."""

    def test_private_method_blocked(self):
        code = '''
kelas Rahasia
    privat fungsi tersembunyi()
        tulis "rahasia"
    selesai

    fungsi buka()
        tulis "publik"
    selesai
selesai
buat r = Rahasia()
r.tersembunyi()
'''
        from brolang.exceptions import RuntimeError_
        with pytest.raises(RuntimeError_):
            run_code(code)

    def test_private_method_accessible_inside(self):
        code = '''
kelas Rahasia
    privat fungsi tersembunyi()
        tulis "dari dalam"
    selesai

    fungsi buka()
        self.tersembunyi()
    selesai
selesai
buat r = Rahasia()
r.buka()
'''
        output = run_code(code)
        assert "dari dalam" in output[0]

    def test_public_method_accessible(self):
        code = '''
kelas Terbuka
    publik fungsi sapa()
        tulis "Halo!"
    selesai
selesai
buat t = Terbuka()
t.sapa()
'''
        output = run_code(code)
        assert "Halo!" in output[0]


class TestInterfaceEnforcement:
    """Tests untuk interface enforcement v5.0."""

    def test_interface_stores_methods(self):
        code = '''
antarmuka DapatJalankan {
    fungsi jalankan()
}
tulis "ok"
'''
        output = run_code(code)
        assert "ok" in output[0]


# ============= Generators =============


class TestGenerators:
    """Tests untuk Generator (hasilkan) v5.0."""

    def test_generator_basic(self):
        code = '''
fungsi gen_sampai(n)
    buat i = 0
    selama i < n lakukan
        hasilkan i
        i = i + 1
    selesai
selesai

untuk angka dalam gen_sampai(5) lakukan
    tulis(angka)
selesai
'''
        output = run_code(code)
        assert output == ["0", "1", "2", "3", "4"]

    def test_generator_collect_all(self):
        code = '''
fungsi gen_ganjil(n)
    buat i = 1
    selama i <= n lakukan
        hasilkan i
        i = i + 2
    selesai
selesai

buat hasil = []
untuk x dalam gen_ganjil(9) lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 3, 5, 7, 9]" in output[0]

    def test_generator_with_for_loop_inside(self):
        code = '''
fungsi gen_duplikat(arr)
    untuk item dalam arr lakukan
        hasilkan item
        hasilkan item
    selesai
selesai

buat hasil = []
untuk x dalam gen_duplikat([1, 2]) lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 1, 2, 2]" in output[0]

    def test_generator_empty(self):
        code = '''
fungsi gen_kosong()
    buat i = 0
    selama i < 0 lakukan
        hasilkan i
    selesai
selesai

buat hasil = []
untuk x dalam gen_kosong() lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[]" in output[0]

    def test_generator_with_condition(self):
        code = '''
fungsi gen_genap(n)
    buat i = 0
    selama i < n lakukan
        jika i % 2 == 0 maka
            hasilkan i
        selesai
        i = i + 1
    selesai
selesai

buat hasil = []
untuk x dalam gen_genap(6) lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[0, 2, 4]" in output[0]

    def test_generator_multiple_calls(self):
        code = '''
fungsi gen_angka()
    hasilkan 1
    hasilkan 2
    hasilkan 3
selesai

buat hasil1 = []
untuk x dalam gen_angka() lakukan
    hasil1.append(x)
selesai
tulis(hasil1)

buat hasil2 = []
untuk x dalam gen_angka() lakukan
    hasil2.append(x)
selesai
tulis(hasil2)
'''
        output = run_code(code)
        assert "[1, 2, 3]" in output[0]
        assert "[1, 2, 3]" in output[1]

    # ============= hasilkandari (yield from) — fix v6.9 =============

    def test_generator_yield_from_list(self):
        """hasilkandari [1, 2, 3] menghasilkan SEMUA item."""
        code = '''
fungsi gen()
    hasilkandari [1, 2, 3]
selesai

buat hasil = []
untuk x dalam gen() lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 2, 3]" in output[0]

    def test_generator_yield_from_generator(self):
        """hasilkandari dari fungsi generator lain menghasilkan semua nilainya."""
        code = '''
fungsi sumber()
    hasilkan 1
    hasilkan 2
selesai

fungsi gen()
    hasilkandari sumber()
selesai

buat hasil = []
untuk x dalam gen() lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 2]" in output[0]

    def test_generator_yield_from_guard(self):
        """Regresi v6.9: guard `hasilkandari ... jika c` menghasilkan semua item
        (sebelumnya hanya elemen pertama — raise pertama menghentikan loop)."""
        code = '''
fungsi gen()
    hasilkandari [1, 2, 3] jika benar
    hasilkandari [9, 8] jika salah
selesai

buat hasil = []
untuk x dalam gen() lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 2, 3]" in output[0]

    def test_generator_yield_from_di_blok_jika(self):
        """hasilkandari di dalam blok jika + statement lanjutan setelahnya."""
        code = '''
fungsi gen(x)
    jika x > 0 maka
        hasilkandari [1, 2]
    selesai
    hasilkan 9
selesai

buat hasil = []
untuk x dalam gen(5) lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 2, 9]" in output[0]

    def test_generator_yield_di_blok_jika_tidak_memotong(self):
        """Regresi v6.9: yield di dalam blok jika tidak lagi menghentikan
        eksekusi statement setelahnya di blok yang sama."""
        code = '''
fungsi gen()
    jika benar maka
        hasilkan 1
        hasilkan 2
    selesai
    hasilkan 3
selesai

buat hasil = []
untuk x dalam gen() lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 2, 3]" in output[0]

    def test_generator_yield_from_else(self):
        """hasilkandari di cabang lainnya (else) tetap dikoleksi."""
        code = '''
fungsi gen(x)
    jika x > 0 maka
        hasilkan 1
    lainnya
        hasilkandari [2, 3]
    selesai
selesai

buat hasil = []
untuk x dalam gen(-1) lakukan
    hasil.append(x)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[2, 3]" in output[0]


# ============= Iterator Protocol =============


class TestIteratorProtocol:
    """Tests untuk Iterator Protocol (__iter__/__next__) v5.0."""

    def test_basic_iterator(self):
        code = '''
kelas Rentang
    fungsi __init__(mulai, akhir)
        self.mulai = mulai
        self.akhir = akhir
    selesai

    fungsi __iter__()
        self._current = self.mulai
        kembali self
    selesai

    fungsi __next__()
        jika self._current >= self.akhir maka
            hentikan_iterasi()
        selesai
        buat val = self._current
        self._current = self._current + 1
        kembali val
    selesai
selesai

buat r = Rentang(1, 4)
buat hasil = []
untuk v dalam r lakukan
    hasil.append(v)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[1, 2, 3]" in output[0]

    def test_iterator_with_step(self):
        code = '''
kelas Langkah
    fungsi __init__(mulai, akhir, langkah)
        self.mulai = mulai
        self.akhir = akhir
        self.langkah = langkah
    selesai

    fungsi __iter__()
        self._current = self.mulai
        kembali self
    selesai

    fungsi __next__()
        jika self._current >= self.akhir maka
            hentikan_iterasi()
        selesai
        buat val = self._current
        self._current = self._current + self.langkah
        kembali val
    selesai
selesai

buat hasil = []
untuk v dalam Langkah(0, 10, 3) lakukan
    hasil.append(v)
selesai
tulis(hasil)
'''
        output = run_code(code)
        assert "[0, 3, 6, 9]" in output[0]


# ============= Properties =============


class TestProperties:
    """Tests untuk Properties (getter/setter) v5.0."""

    def test_property_getter(self):
        code = '''
kelas Suhu
    fungsi __init__(derajat)
        self._derajat = derajat
    selesai

    fungsi _derajat()
        kembali self._derajat
    selesai
selesai

buat s = Suhu(36)
tulis(s.get("derajat"))
'''
        output = run_code(code)
        assert "36" in output[0]

    def test_property_setter(self):
        code = '''
kelas Suhu
    fungsi __init__(derajat)
        self._derajat = derajat
    selesai

    fungsi _derajat()
        kembali self._derajat
    selesai

    fungsi _derajat_set(nilai)
        self._derajat = nilai
    selesai
selesai

buat s = Suhu(36)
s.set("derajat", 37)
tulis(s.get("derajat"))
'''
        output = run_code(code)
        assert "37" in output[0]

    def test_property_roundtrip(self):
        code = '''
kelas Counter
    fungsi __init__(nilai)
        self._nilai = nilai
    selesai

    fungsi _nilai()
        kembali self._nilai
    selesai

    fungsi _nilai_set(v)
        self._nilai = v
    selesai
selesai

buat c = Counter(0)
tulis(c.get("nilai"))
c.set("nilai", 10)
tulis(c.get("nilai"))
c.set("nilai", c.get("nilai") + 5)
tulis(c.get("nilai"))
'''
        output = run_code(code)
        assert output == ["0", "10", "15"]


# ============= Static Methods =============


class TestStaticMethods:
    """Tests untuk Static Methods (statis) v5.0."""

    def test_static_method_basic(self):
        code = '''
kelas Kalkulator
    statis fungsi tambah(a, b)
        kembali a + b
    selesai
selesai

tulis(Kalkulator.tambah(3, 4))
'''
        output = run_code(code)
        assert "7" in output[0]

    def test_static_method_multiple(self):
        code = '''
kelas Matematika
    statis fungsi kuadrat(x)
        kembali x * x
    selesai

    statis fungsi kubik(x)
        kembali x * x * x
    selesai
selesai

tulis(Matematika.kuadrat(5))
tulis(Matematika.kubik(3))
'''
        output = run_code(code)
        assert output == ["25", "27"]

    def test_static_method_on_instance(self):
        code = '''
kelas Util
    statis fungsi sapa()
        kembali "Halo"
    selesai
selesai

buat u = Util()
tulis(u.sapa())
'''
        output = run_code(code)
        assert "Halo" in output[0]

    def test_static_method_mixed_with_instance(self):
        code = '''
kelas Foo
    statis fungsi dari_nilai(x)
        kembali x * 2
    selesai

    fungsi tambah(self, y)
        kembali self.nilai + y
    selesai
selesai

tulis(Foo.dari_nilai(5))
'''
        output = run_code(code)
        assert "10" in output[0]


# ============= Type Checking =============


class TestTypeChecking:
    """Tests untuk Type Checking (cek_tipe/pastikan) v5.0."""

    def test_cektipe_basic(self):
        code = '''
tulis(cek_tipe(42))
tulis(cek_tipe("halo"))
tulis(cek_tipe([1, 2]))
tulis(cek_tipe(benar))
'''
        output = run_code(code)
        assert output[0] != ""
        assert output[1] != ""

    def test_cektipe_with_type_name(self):
        code = '''
tulis(cek_tipe(42, "angka"))
tulis(cek_tipe("halo", "teks"))
'''
        output = run_code(code)
        assert output[0] == "True"
        assert output[1] == "True"

    def test_cektipe_wrong_type(self):
        code = '''
tulis(cek_tipe("halo", "angka"))
'''
        output = run_code(code)
        assert "False" in output[0]

    def test_pastikan_success(self):
        code = '''
pastikan(42 == 42, "Harus sama!")
tulis("passed")
'''
        output = run_code(code)
        assert "passed" in output[0]

    def test_pastikan_failure(self):
        code = '''
pastikan(42 == 99, "Harus sama!")
'''
        with pytest.raises(RuntimeError_):
            run_code(code)

    def test_pastikan_no_message(self):
        code = '''
pastikan(benar)
tulis("ok")
'''
        output = run_code(code)
        assert "ok" in output[0]


# ============= String Interpolation =============


class TestStringInterpolation:
    """Tests untuk String Interpolation ($variable & f-string) v5.0."""

    def test_dollar_variable(self):
        code = '''
buat nama = "Bro"
tulis("Halo $nama!")
'''
        output = run_code(code)
        assert "Halo Bro!" in output[0]

    def test_dollar_multiple_vars(self):
        code = '''
buat nama = "Bro"
buat umur = 5
tulis("Nama: $nama, Umur: $umur")
'''
        output = run_code(code)
        assert "Nama: Bro, Umur: 5" in output[0]

    def test_dollar_expression(self):
        code = '''
tulis("2 + 3 = ${2 + 3}")
'''
        output = run_code(code)
        assert "2 + 3 = 5" in output[0]

    def test_dollar_function_call(self):
        code = '''
buat data = [1, 2, 3]
tulis("Panjang: ${panjang(data)}")
'''
        output = run_code(code)
        assert "Panjang: 3" in output[0]

    def test_fstring_basic(self):
        code = '''
buat nama = "Bro"
tulis(f"Halo {nama}!")
'''
        output = run_code(code)
        assert "Halo Bro!" in output[0]

    def test_fstring_expression(self):
        code = '''
tulis(f"{2 + 3}")
'''
        output = run_code(code)
        assert "5" in output[0]

    def test_fstring_method_call(self):
        code = '''
buat nama = "bro"
tulis(f"{nama.upper()}")
'''
        output = run_code(code)
        assert "BRO" in output[0]

    def test_dollar_escape(self):
        code = '''
tulis("Harga: \\$100")
'''
        output = run_code(code)
        assert "$100" in output[0]

    def test_plain_string_unaffected(self):
        code = '''
tulis("Tanpa interpolation")
'''
        output = run_code(code)
        assert "Tanpa interpolation" in output[0]

    def test_mixed_interpolation(self):
        code = '''
buat x = 10
tulis("Nilai $x dan ${x * 2}")
'''
        output = run_code(code)
        assert "Nilai 10 dan 20" in output[0]


# ============= Class Inheritance Syntax =============


class TestClassInheritanceSyntax:
    """Tests untuk Class Inheritance Syntax v5.0."""

    def test_paren_inheritance(self):
        code = '''
kelas Animal
    fungsi suara()
        tulis "?"
    selesai
selesai

kelas Dog(Animal)
    fungsi suara()
        tulis "Guk guk!"
    selesai
selesai

buat d = Dog()
d.suara()
'''
        output = run_code(code)
        assert "Guk guk!" in output[0]

    def test_deep_inheritance(self):
        code = '''
kelas A
    fungsi prefix()
        kembali "A"
    selesai
selesai

kelas B(A)
    fungsi prefix()
        kembali "B"
    selesai
selesai

kelas C(B)
    fungsi prefix()
        kembali "C"
    selesai
selesai

buat c = C()
tulis(c.prefix())
'''
        output = run_code(code)
        assert "C" in output[0]

    def test_inherited_method(self):
        code = '''
kelas Base
    fungsi greet()
        kembali "Hello"
    selesai
selesai

kelas Child(Base)
    fungsi child_only()
        kembali "child"
    selesai
selesai

buat c = Child()
tulis(c.greet())
tulis(c.child_only())
'''
        output = run_code(code)
        assert output == ["Hello", "child"]
