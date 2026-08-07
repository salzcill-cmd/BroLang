"""
REPL BroLang
============

REPL (Read-Eval-Print Loop) interaktif untuk BroLang — dibuat ramah
untuk pemula Indonesia:

- Prompt `bro>` dengan pesan sambutan berisi contoh yang bisa dicoba
- Blok multi-baris (`jika ... maka`, `fungsi ...`) berfungsi dengan benar
  — selesai ditutup otomatis saat kedalaman blok kembali ke 0
- Hasil ekspresi ditampilkan: `2 + 3` -> `=> 5`
- Perintah `bantuan` (daftar fungsi + contoh) dan `tips`
- Tip acak muncul setiap beberapa input
"""

import sys
from typing import List, Optional, Any

from brolang.lexer import Lexer
from brolang.parser import Parser
from brolang.interpreter import Interpreter
from brolang.ast.nodes import (
    NumberNode, DecimalNode, StringNode, BooleanNode, KosongNode,
    IdentifierNode, BinaryOpNode, UnaryOpNode, CallNode,
    ListNode, TupleNode, SetNode, ObjectNode, IndexNode, ObjectAccessNode,
    FStringNode, LambdaNode, TernaryNode, NullCoalescingNode,
    OptionalChainingNode, ComprehensionNode, ChainedComparisonNode,
    PipelineNode,
)
from brolang import __version__

# Node yang dianggap "ekspresi" — hasilnya ditampilkan sebagai `=> nilai`
_EXPRESI_NODE = (
    NumberNode, DecimalNode, StringNode, BooleanNode, KosongNode,
    IdentifierNode, BinaryOpNode, UnaryOpNode, CallNode,
    ListNode, TupleNode, SetNode, ObjectNode, IndexNode, ObjectAccessNode,
    FStringNode, LambdaNode, TernaryNode, NullCoalescingNode,
    OptionalChainingNode, ComprehensionNode, ChainedComparisonNode,
    PipelineNode,
)

# Awalan yang membuka blok bertipe `selesai` (fungsi, kelas, coba, ...).
# Blok kurung kurawal (cocokkan/enum/struktur/antarmuka/abstrak kelas)
# ditangani lewat penanda '{' di akhir baris dan '}' di awal baris.
_PEMBUKA_BLOK = (
    "fungsi", "kelas", "kelas_error", "coba",
    "ruang", "makro", "asinkron", "dengan",
)


def delta_kedalaman(baris: str) -> int:
    """Hitung perubahan kedalaman blok untuk satu baris kode.

    Pencocokan memakai token pertama/terakhir (bukan prefix string),
    supaya nama variabel seperti `fungsiku` atau `coba2` tidak salah
    dianggap membuka blok, dan `selesai # komentar` tetap dihitung tutup.

    Blok kurung kurawal (cocokkan, enum, struktur, antarmuka, abstrak
    kelas, atau literal objek multi-baris) dihitung lewat '{' / '}'.

    Returns:
        +1 kalau baris membuka blok, -1 kalau menutup, 0 lainnya.
    """
    s = baris.strip()
    if not s:
        return 0
    # Buang komentar di akhir baris (tanda # setelah spasi putih)
    if " #" in s:
        s = s.split(" #", 1)[0].rstrip()
    if s.startswith("#"):
        return 0

    kata = s.split()
    if not kata:
        return 0

    d = 0
    if kata[0] == "selesai":
        d -= 1
    elif kata[0] in _PEMBUKA_BLOK:
        d += 1
    if kata[-1] in ("maka", "lakukan"):
        d += 1
    # Blok kurung kurawal: baris berakhir '{' membuka, baris diawali '}' menutup
    if s.rstrip().endswith("{"):
        d += 1
    if s.lstrip().startswith("}"):
        d -= 1
    return d


_TIPS: List[str] = [
    "Buat komentar dengan # supaya kode lebih jelas:  # ini komentar",
    "Variabel bisa diubah:  buat x = 5  lalu  x = 10",
    "tulis bisa menerima beberapa nilai:  tulis 1, 2, 3",
    "String digabung dengan +:  tulis \"Halo \" + nama",
    "f-string menyisipkan variabel:  tulis f\"Halo {nama}\"",
    "List mulai dari index 0:  list[0] adalah elemen pertama",
    "range(n) menghasilkan angka 0 sampai n-1",
    "Jangan lupa tutup blok dengan 'selesai'",
    "Angka desimal pakai titik: 3.14 (bukan koma)",
    "Coba bandingkan dengan == (dua tanda sama), bukan =",
    "Ketik 'bantuan' untuk daftar fungsi dan contoh",
    "Ketik 'keluar' atau Ctrl+C untuk berhenti",
]


class BroLangREPL:
    """REPL interaktif BroLang (ramah pemula)."""

    def __init__(self):
        # Satu interpreter persisten — state (variabel/fungsi) bertahan
        # antar input, seperti REPL Python.
        self.interpreter = Interpreter()
        self.history: List[str] = []
        self.multiline: bool = False
        self.buffer: List[str] = []
        self._kedalaman: int = 0
        self._input_count: int = 0

    def start(self) -> None:
        """Memulai REPL."""
        self._print_welcome()
        self._run_loop()

    def _print_welcome(self) -> None:
        """Pesan sambutan ramah pemula dengan contoh yang bisa dicoba."""
        print()
        print(f"  🐍  BroLang {__version__} — bahasa pemrograman Bahasa Indonesia")
        print("=" * 58)
        print("  Ketik kode langsung di sini. Coba beberapa contoh ini:")
        print()
        print('    tulis "Halo Dunia!"')
        print("    2 + 3 * 4")
        print('    buat nama = "Budi"')
        print("    untuk i dalam range(3) lakukan")
        print()
        print("  Perintah: bantuan | tips | contoh | bersih | keluar")
        print("  (Ctrl+C untuk keluar)")
        print("=" * 58)
        print()

    def _tampilkan_tip(self) -> None:
        import random
        print(f"💡 Tip: {random.choice(_TIPS)}")

    def _perintah(self, perintah: str) -> bool:
        """Tangani perintah REPL. Return True kalau diproses sebagai perintah."""
        p = perintah.strip().lower()
        if p in ("exit", "quit", "keluar", "q"):
            print("Sampai jumpa! Tetap semangat belajar ya 💪")
            return True  # sinyal keluar
        if p in ("bantuan", "help", "?"):
            self._tampilkan_bantuan()
            return True
        if p in ("tips", "tip"):
            self._tampilkan_tip()
            return True
        if p in ("contoh", "examples"):
            self._tampilkan_contoh()
            return True
        if p in ("bersih", "clear"):
            print("\n" * 3)
            return True
        if p in ("riwayat", "history"):
            for i, h in enumerate(self.history[-20:], 1):
                print(f"  {i:>3}  {h}")
            return True
        return False

    def _tampilkan_bantuan(self) -> None:
        print()
        print("  📖 BANTUAN CEPAT")
        print("  " + "-" * 54)
        print("  Mencetak hasil:")
        print('    tulis "Halo"')
        print("  Variabel:")
        print('    buat umur = 17      tulis umur')
        print("  Percabangan:")
        print("    jika umur >= 17 maka")
        print("        tulis \"Dewasa\"")
        print("    selesai")
        print("  Perulangan:")
        print("    untuk i dalam range(5) lakukan")
        print("        tulis i")
        print("    selesai")
        print("  Fungsi:")
        print("    fungsi kali2(x)")
        print("        kembali x * 2")
        print("    selesai")
        print("    tulis kali2(21)")
        print("  " + "-" * 54)
        print("  Fungsi bawaan: tulis, buat, panjang(), teks(), angka(),")
        print("  desimal(), rentang/range(), masukkan/input(), tipe()")
        print("  Perintah: bantuan | tips | contoh | riwayat | bersih | keluar")
        print()

    def _tampilkan_contoh(self) -> None:
        print()
        print("  🎁 CONTOH PROGRAM PENDEK")
        print("  " + "-" * 54)
        print('  1) tulis "Halo Dunia!"')
        print("  2) buat a = 10")
        print("     buat b = 5")
        print("     tulis a + b")
        print("  3) untuk i dalam range(3) lakukan")
        print("        tulis \"Baris \" + teks(i + 1)")
        print("     selesai")
        print("  4) fungsi luas(p, l)")
        print("        kembali p * l")
        print("     selesai")
        print("     tulis luas(5, 4)")
        print("  " + "-" * 54)
        print()

    def _run_loop(self) -> None:
        """Loop utama REPL."""
        while True:
            try:
                prompt = "... " if self.multiline else "bro> "
                line = input(prompt)

                # Keluar dari REPL
                if not self.multiline and self._perintah(line):
                    if line.strip().lower() in ("exit", "quit", "keluar", "q"):
                        break
                    continue

                # Di tengah blok multi-baris: perintah keluar/batal = batalkan
                if self.multiline and line.strip().lower() in (
                    "exit", "quit", "keluar", "q", "batal", "cancel"):
                    print("(blok dibatalkan)")
                    self.buffer = []
                    self.multiline = False
                    self._kedalaman = 0
                    continue

                # Baris kosong: di mode multiline = kirim jawaban
                if line.strip() == "":
                    if self.multiline:
                        if self.buffer:
                            self._execute("\n".join(self.buffer))
                            self.buffer = []
                            self.multiline = False
                            self._kedalaman = 0
                    continue

                delta = delta_kedalaman(line)
                if not self.multiline and delta > 0:
                    # Mulai mode multiline
                    self.multiline = True
                    self._kedalaman = delta
                    self.buffer = [line]
                    continue

                if self.multiline:
                    self.buffer.append(line)
                    self._kedalaman += delta
                    if self._kedalaman <= 0:
                        self._execute("\n".join(self.buffer))
                        self.buffer = []
                        self.multiline = False
                        self._kedalaman = 0
                    continue

                # Baris tunggal
                self._execute(line)

            except KeyboardInterrupt:
                if self.multiline:
                    print("\n(blok dibatalkan)")
                    self.buffer = []
                    self.multiline = False
                    self._kedalaman = 0
                else:
                    print("\nSampai jumpa! Tetap semangat belajar ya 💪")
                    break
            except EOFError:
                print("\nSampai jumpa!")
                break

    def _execute(self, source: str) -> None:
        """Mengeksekusi satu blok kode."""
        if not source.strip():
            return

        self.history.append(source)
        self._input_count += 1
        if self._input_count % 5 == 0:
            self._tampilkan_tip()

        try:
            tokens = Lexer(source).tokenize()
            ast = Parser(tokens).parse()

            if not ast.statements:
                return

            # Jalankan via interpreter (state persisten antar input)
            hasil = self.interpreter.interpret(ast)

            # Tampilkan hasil kalau input terakhir berupa ekspresi murni
            stmt_terakhir = ast.statements[-1]
            if isinstance(stmt_terakhir, _EXPRESI_NODE) and hasil is not None:
                print(f"=> {hasil}")

        except Exception as e:
            print(str(e))

    def _execute_multiline(self) -> None:
        """(Dipertahankan untuk kompatibilitas) — jalankan buffer multiline."""
        source = "\n".join(self.buffer)
        self.buffer = []
        self.multiline = False
        self._kedalaman = 0
        if source.strip():
            self._execute(source)


def start_repl() -> None:
    """Convenience function untuk memulai REPL."""
    repl = BroLangREPL()
    repl.start()


if __name__ == "__main__":
    start_repl()
