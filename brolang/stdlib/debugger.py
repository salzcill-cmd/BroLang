"""
Modul Debugger untuk BroLang
=============================

Menyediakan fitur debugging untuk program BroLang.

Contoh:
    impor debugger

    debugger.set_breakpoint("main.bro", 10)
    debugger.mulai()
"""

from types import SimpleNamespace
import sys


class Breakpoint:
    """Breakpoint untuk debugging."""

    def __init__(self, file, baris, kondisi=None):
        self.file = file
        self.baris = baris
        self.kondisi = kondisi
        this = self
        this.aktif = True
        this.hit_count = 0

    def cek(self, current_file, current_line):
        """Mengecek apakah breakpoint tercapai."""
        if not self.aktif:
            return False
        if self.file != current_file:
            return False
        if self.baris != current_line:
            return False
        self.hit_count += 1
        return True


class Debugger:
    """Debugger untuk BroLang."""

    def __init__(self):
        self.breakpoints = []
        this = self

        this.aktif = False
        this.paused = False
        this.step_mode = False
        this.verbose = False

        # Variable tracking
        this.variabel_snapshots = []
        this.call_stack = []
        this.watch_list = []

    def set_breakpoint(self, file, baris, kondisi=None):
        """Set breakpoint."""
        bp = Breakpoint(file, baris, kondisi)
        self.breakpoints.append(bp)
        return bp

    def hapus_breakpoint(self, file, baris):
        """Menghapus breakpoint."""
        self.breakpoints = [
            bp for bp in self.breakpoints
            if not (bp.file == file and bp.baris == baris)
        ]

    def hapus_semua_breakpoint(self):
        """Menghapus semua breakpoint."""
        self.breakpoints.clear()

    def mulai(self):
        """Memulai debugging."""
        self.aktif = True
        self.paused = False
        self.step_mode = False
        if self.verbose:
            print("[Debugger] Dimulai")

    def berhenti(self):
        """Menghentikan debugging."""
        self.aktif = False
        if self.verbose:
            print("[Debugger] Dihentikan")

    def pause(self):
        """Pause debugger."""
        self.paused = True

    def resume(self):
        """Lanjutkan dari pause."""
        self.paused = False
        self.step_mode = False

    def step(self):
        """Step satu baris."""
        self.step_mode = True
        self.paused = False

    def cek_breakpoint(self, file, baris, env=None):
        """Mengecek apakah ada breakpoint di baris ini."""
        if not self.aktif:
            return False

        for bp in self.breakpoints:
            if bp.cek(file, baris):
                if bp.kondisi and env:
                    # Evaluate condition
                    try:
                        from brolang.lexer import Lexer
                        from brolang.parser import Parser
                        from brolang.interpreter import Interpreter
                        lexer = Lexer(bp.kondisi)
                        tokens = lexer.tokenize()
                        parser = Parser(tokens)
                        ast = parser.parse()
                        interp = Interpreter()
                        interp.current_env = env
                        result = interp.interpret(ast)
                        if not result:
                            continue
                    except Exception:
                        continue

                self.paused = True
                print(f"\n{'='*50}")
                print(f"[Breakpoint] {file}:{baris}")
                print(f"{'='*50}")
                if env:
                    self.tampilkan_variabel(env)
                return True

        if self.step_mode:
            self.paused = True
            print(f"\n[Step] {file}:{baris}")
            if env:
                self.tampilkan_variabel(env)
            return True

        return False

    def tampilkan_variabel(self, env):
        """Menampilkan variabel dalam scope."""
        print("\nVariabel:")
        for name, value in env.variables.items():
            print(f"  {name} = {repr(value)}")

    def tambah_watch(self, nama):
        """Menambahkan variabel ke watch list."""
        self.watch_list.append(nama)

    def hapus_watch(self, nama):
        """Menghapus dari watch list."""
        if nama in self.watch_list:
            self.watch_list.remove(nama)

    def tampilkan_watch(self, env):
        """Menampilkan nilai watch list."""
        print("\nWatch List:")
        for name in self.watch_list:
            try:
                value = env.get_variable(name)
                print(f"  {name} = {repr(value)}")
            except Exception:
                print(f"  {name} = <tidak ditemukan>")

    def tampilkan_call_stack(self):
        """Menampilkan call stack."""
        print("\nCall Stack:")
        for i, frame in enumerate(reversed(self.call_stack)):
            print(f"  {i}: {frame}")

    def push_frame(self, frame_info):
        """Push frame ke call stack."""
        self.call_stack.append(frame_info)

    def pop_frame(self):
        """Pop frame dari call stack."""
        if self.call_stack:
            self.call_stack.pop()

    def info(self):
        """Menampilkan info debugger."""
        print(f"\n{'='*50}")
        print("[Debugger Info]")
        print(f"  Aktif: {self.aktif}")
        print(f"  Paused: {self.paused}")
        print(f"  Step Mode: {self.step_mode}")
        print(f"  Breakpoints: {len(self.breakpoints)}")
        for bp in self.breakpoints:
            status = "aktif" if bp.aktif else "nonaktif"
            print(f"    {bp.file}:{bp.baris} [{status}] (hit: {bp.hit_count})")
        print(f"  Watch: {len(self.watch_list)}")
        print(f"  Call Stack: {len(self.call_stack)}")
        print(f"{'='*50}")


# Global debugger instance
_debugger = Debugger()


def set_breakpoint(file, baris, kondisi=None):
    """Set breakpoint."""
    return _debugger.set_breakpoint(file, baris, kondisi)


def hapus_breakpoint(file, baris):
    """Menghapus breakpoint."""
    _debugger.hapus_breakpoint(file, baris)


def mulai():
    """Memulai debugging."""
    _debugger.mulai()


def berhenti():
    """Menghentikan debugging."""
    _debugger.berhenti()


def pause():
    """Pause debugger."""
    _debugger.pause()


def resume():
    """Lanjutkan."""
    _debugger.resume()


def step():
    """Step satu baris."""
    _debugger.step()


def info():
    """Info debugger."""
    _debugger.info()


def tambah_watch(nama):
    """Tambah watch."""
    _debugger.tambah_watch(nama)


module = SimpleNamespace(
    Debugger=Debugger,
    Breakpoint=Breakpoint,
    set_breakpoint=set_breakpoint,
    hapus_breakpoint=hapus_breakpoint,
    mulai=mulai,
    berhenti=berhenti,
    pause=pause,
    resume=resume,
    step=step,
    info=info,
    tambah_watch=tambah_watch,
    _debugger=_debugger,
)
