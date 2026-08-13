"""
Modul Tes untuk BroLang
========================

Menyediakan framework testing built-in.

Contoh:
    impor tes

    tes.describe("Kalkulator"):
        tes.it("menjumlahkan dengan benar"):
            tes.harusnya(2 + 2 == 4)
        tes.it("mengurangi dengan benar"):
            tes.harusnya(5 - 3 == 2)

    tes.jalankan()
"""

from types import SimpleNamespace
import time
import traceback


class TestResult:
    """Hasil dari satu test."""

    def __init__(self, nama, passed=True, error=None, durasi=0):
        self.nama = nama
        self.passed = passed
        self.error = error
        self.durasi = durasi


class DescribeBlock:
    """Block describe dalam test."""

    def __init__(self, nama):
        self.nama = nama
        self.tests = []
        this = self

        this.before_each = None
        this.after_each = None
        this.before_all = None
        this.after_all = None


class TestRunner:
    """Runner untuk menjalankan test."""

    def __init__(self):
        self._blocks = []
        self._current_block = None
        this = self

        this.results = []
        this.total = 0
        this.passed = 0
        this.failed = 0
        this.errors = []
        this.verbose = True

    def describe(self, nama, callback=None):
        """Describe block untuk mengelompokkan test."""
        block = DescribeBlock(nama)
        self._blocks.append(block)
        self._current_block = block

        if callback:
            callback()

        self._current_block = None
        return block

    def it(self, nama, callback=None):
        """Test case."""
        test = SimpleNamespace(
            nama=nama,
            callback=callback,
            block=self._current_block,
        )

        if self._current_block:
            self._current_block.tests.append(test)
        else:
            # Create anonymous block
            block = DescribeBlock("<anonymous>")
            block.tests.append(test)
            self._blocks.append(block)

        return test

    def harusnya(self, kondisi, pesan=""):
        """Assertion: harusnya kondisi benar."""
        if not kondisi:
            error_msg = f"Assertion gagal"
            if pesan:
                error_msg += f": {pesan}"
            raise AssertionError(error_msg)

    def harusnya_sama(self, aktual, expected, pesan=""):
        """Assertion: harusnya sama."""
        if aktual != expected:
            error_msg = f"Diharapkan {repr(expected)}, tapi mendapatkan {repr(aktual)}"
            if pesan:
                error_msg += f" ({pesan})"
            raise AssertionError(error_msg)

    def harusnya_berbeda(self, aktual, expected, pesan=""):
        """Assertion: harusnya berbeda."""
        if aktual == expected:
            error_msg = f"Harusnya berbeda dari {repr(expected)}"
            if pesan:
                error_msg += f" ({pesan})"
            raise AssertionError(error_msg)

    def harusnya_true(self, value, pesan=""):
        """Assertion: harusnya True."""
        if not value:
            error_msg = f"Harusnya True, tapi mendapatkan {repr(value)}"
            if pesan:
                error_msg += f" ({pesan})"
            raise AssertionError(error_msg)

    def harusnya_false(self, value, pesan=""):
        """Assertion: harusnya False."""
        if value:
            error_msg = f"Harusnya False, tapi mendapatkan {repr(value)}"
            if pesan:
                error_msg += f" ({pesan})"
            raise AssertionError(error_msg)

    def harusnya_error(self, callback, error_type=None):
        """Assertion: harusnya error."""
        try:
            callback()
            raise AssertionError("Seharusnya error tapi tidak error")
        except error_type:
            pass  # Expected error
        except AssertionError:
            raise
        except Exception as e:
            if error_type and not isinstance(e, error_type):
                raise AssertionError(f"Error type salah: {type(e).__name__} bukan {error_type.__name__}")

    def jalankan(self):
        """Menjalankan semua test."""
        self.results = []
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

        print(f"\n{'='*60}")
        print("Menjalankan tes...")
        print(f"{'='*60}")

        start_time = time.time()

        for block in self._blocks:
            print(f"\n  {block.nama}:")

            if block.before_all:
                block.before_all()

            for test in block.tests:
                self.total += 1
                test_start = time.time()

                if block.before_each:
                    block.before_each()

                try:
                    if test.callback:
                        test.callback()
                    result = TestResult(test.nama, passed=True, durasi=time.time() - test_start)
                    self.passed += 1
                    print(f"    ✓ {test.nama} ({(time.time() - test_start)*1000:.1f}ms)")
                except Exception as e:
                    result = TestResult(test.nama, passed=False, error=e, durasi=time.time() - test_start)
                    self.failed += 1
                    self.errors.append((test.nama, e))
                    print(f"    ✗ {test.nama}")
                    print(f"      Error: {e}")

                self.results.append(result)

                if block.after_each:
                    block.after_each()

            if block.after_all:
                block.after_all()

        total_time = time.time() - start_time

        print(f"\n{'='*60}")
        print(f"Hasil: {self.passed}/{self.total} lulus ({self.failed} gagal)")
        print(f"Waktu: {total_time*1000:.1f}ms")
        print(f"{'='*60}\n")

        return self.failed == 0

    def laporan(self):
        """Menampilkan laporan detail."""
        print(f"\n{'='*60}")
        print("Laporan Detail")
        print(f"{'='*60}")

        for r in self.results:
            status = "✓" if r.passed else "✗"
            print(f"  {status} {r.nama} ({r.durasi*1000:.1f}ms)")
            if r.error:
                print(f"    Error: {r.error}")

        print(f"\nTotal: {self.total}")
        print(f"Lulus: {self.passed}")
        print(f"Gagal: {self.failed}")
        print(f"{'='*60}\n")

    def reset(self):
        """Reset runner."""
        self._blocks.clear()
        self.results.clear()
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors.clear()


# Global test runner
_runner = TestRunner()


def describe(nama, callback=None):
    """Describe block."""
    return _runner.describe(nama, callback)


def it(nama, callback=None):
    """Test case."""
    return _runner.it(nama, callback)


def harusnya(kondisi, pesan=""):
    """Assertion."""
    _runner.harusnya(kondisi, pesan)


# v7.1: alias aman-keyword (`harusnya` adalah keyword bahasa) — level modul
# agar berfungsi di interpreter DAN VM.
harus = harusnya


def harusnya_sama(aktual, expected, pesan=""):
    """Assertion: equality."""
    _runner.harusnya_sama(aktual, expected, pesan)


def harusnya_berbeda(aktual, expected, pesan=""):
    """Assertion: inequality."""
    _runner.harusnya_berbeda(aktual, expected, pesan)


def harusnya_true(value, pesan=""):
    """Assertion: true."""
    _runner.harusnya_true(value, pesan)


def harusnya_false(value, pesan=""):
    """Assertion: false."""
    _runner.harusnya_false(value, pesan)


def harusnya_error(callback, error_type=None):
    """Assertion: error."""
    _runner.harusnya_error(callback, error_type)


def jalankan():
    """Menjalankan semua test."""
    return _runner.jalankan()


def laporan():
    """Menampilkan laporan."""
    _runner.laporan()


def reset():
    """Reset runner."""
    _runner.reset()


module = SimpleNamespace(
    TestRunner=TestRunner,
    TestResult=TestResult,
    DescribeBlock=DescribeBlock,
    describe=describe,
    it=it,
    harusnya=harusnya,
    harus=harusnya,  # v7.1: alias aman-keyword (`harusnya` adalah keyword)
    harusnya_sama=harusnya_sama,
    harusnya_berbeda=harusnya_berbeda,
    harusnya_true=harusnya_true,
    harusnya_false=harusnya_false,
    harusnya_error=harusnya_error,
    jalankan=jalankan,
    laporan=laporan,
    reset=reset,
    _runner=_runner,
)
