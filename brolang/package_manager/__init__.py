"""
Package Manager BroLang (bropm)
================================

Manajer paket untuk ekosistem BroLang.
Mengelola instalasi, penghapusan, dan update paket.

Perintah:
    bropm install <package>  : Install paket
    bropm remove <package>   : Hapus paket
    bropm update <package>   : Update paket
    bropm list               : Daftar paket terinstal
    bropm search <keyword>   : Cari paket

Contoh:
    bropm install web
    bropm remove web
    bropm update
"""

from brolang.package_manager.manager import PackageManager, main as bropm_main
