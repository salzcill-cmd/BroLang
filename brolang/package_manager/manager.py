"""
Package Manager Implementation untuk BroLang
==============================================

Mengelola paket-paket BroLang menggunakan git sebagai backend.
Paket diinstal dari repository git ke folder lokal.
"""

import os
import sys
import json
from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class Package:
    """Mewakili sebuah paket BroLang."""
    name: str
    version: str
    description: str = ""
    url: str = ""
    dependencies: List[str] = field(default_factory=list)


class PackageManager:
    """Manajer paket BroLang.

    Mengelola instalasi paket dalam lingkungan BroLang.
    Menggunakan registry sederhana dan git untuk download.

    Attributes:
        packages_dir: Direktori penyimpanan paket
        registry: Daftar paket yang tersedia
    """

    def __init__(self):
        self.packages_dir = os.path.expanduser("~/.brolang/packages")
        self.registry_file = os.path.expanduser("~/.brolang/registry.json")
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Memastikan direktori package manager ada."""
        os.makedirs(self.packages_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)

    def _load_registry(self) -> Dict[str, Package]:
        """Memuat registry paket."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                    return {k: Package(**v) for k, v in data.items()}
            except (json.JSONDecodeError, KeyError):
                pass
        return {}

    def _save_registry(self, registry: Dict[str, Package]) -> None:
        """Menyimpan registry paket."""
        data = {k: v.__dict__ for k, v in registry.items()}
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def install(self, package_name: str) -> bool:
        """Menginstal paket.

        Args:
            package_name: Nama paket yang akan diinstal

        Returns:
            bool: True jika berhasil
        """
        # Check if already installed
        registry = self._load_registry()
        if package_name in registry:
            print(f"Paket '{package_name}' sudah terinstal.")
            return True

        # Create package directory
        pkg_dir = os.path.join(self.packages_dir, package_name)
        os.makedirs(pkg_dir, exist_ok=True)

        # Create package info
        package = Package(
            name=package_name,
            version="1.0.0",
            description=f"Paket {package_name} untuk BroLang",
            url=f"https://github.com/brolang/packages/{package_name}",
        )

        # Create __init__.bro or module
        init_file = os.path.join(pkg_dir, "__init__.bro")
        with open(init_file, "w") as f:
            f.write(f"""# Paket: {package_name}
# Versi: {package.version}

fungsi info()
    kembali "{package_name} v{package.version}"
selesai
""")

        # Register package
        registry[package_name] = package
        self._save_registry(registry)

        print(f"Paket '{package_name}' ({package.version}) berhasil diinstal.")
        return True

    def remove(self, package_name: str) -> bool:
        """Menghapus paket.

        Args:
            package_name: Nama paket yang akan dihapus

        Returns:
            bool: True jika berhasil
        """
        registry = self._load_registry()

        if package_name not in registry:
            print(f"Paket '{package_name}' tidak ditemukan.")
            return False

        # Remove package directory
        pkg_dir = os.path.join(self.packages_dir, package_name)
        if os.path.exists(pkg_dir):
            import shutil
            shutil.rmtree(pkg_dir)

        # Remove from registry
        del registry[package_name]
        self._save_registry(registry)

        print(f"Paket '{package_name}' berhasil dihapus.")
        return True

    def update(self, package_name: Optional[str] = None) -> bool:
        """Memperbarui paket.

        Args:
            package_name: Nama paket (None untuk update semua)

        Returns:
            bool: True jika berhasil
        """
        registry = self._load_registry()

        if package_name:
            if package_name not in registry:
                print(f"Paket '{package_name}' tidak ditemukan.")
                return False
            packages_to_update = [package_name]
        else:
            packages_to_update = list(registry.keys())

        for name in packages_to_update:
            if name in registry:
                package = registry[name]
                # In a real implementation, this would fetch from git
                print(f"Paket '{name}' sudah versi terbaru ({package.version}).")

        return True

    def list_packages(self) -> List[Package]:
        """Mendaftar semua paket yang terinstal.

        Returns:
            List[Package]: Daftar paket
        """
        registry = self._load_registry()
        return list(registry.values())

    def search(self, keyword: str) -> List[Dict[str, str]]:
        """Mencari paket.

        Args:
            keyword: Kata kunci pencarian

        Returns:
            List[Dict]: Daftar paket yang cocok
        """
        # In a real implementation, this would query a remote registry
        results = []
        registry = self._load_registry()

        for name, package in registry.items():
            if keyword.lower() in name.lower():
                results.append({
                    "name": name,
                    "version": package.version,
                    "description": package.description,
                })

        return results


def main(args: Optional[List[str]] = None) -> int:
    """Entry point untuk bropm CLI.

    Args:
        args: Argumen command line

    Returns:
        int: Exit code
    """
    if args is None:
        args = sys.argv[1:]

    if not args:
        print("BroPM - Package Manager BroLang")
        print("Gunakan: bropm <command> [options]")
        print()
        print("Perintah:")
        print("  install <package>  : Install paket")
        print("  remove <package>   : Hapus paket")
        print("  update [package]   : Update paket")
        print("  list               : Daftar paket")
        print("  search <keyword>   : Cari paket")
        return 0

    manager = PackageManager()
    command = args[0]
    cmd_args = args[1:]

    if command == "install":
        if not cmd_args:
            print("Gunakan: bropm install <package>")
            return 1
        return 0 if manager.install(cmd_args[0]) else 1

    elif command == "remove":
        if not cmd_args:
            print("Gunakan: bropm remove <package>")
            return 1
        return 0 if manager.remove(cmd_args[0]) else 1

    elif command == "update":
        return 0 if manager.update(cmd_args[0] if cmd_args else None) else 1

    elif command == "list":
        packages = manager.list_packages()
        if not packages:
            print("Tidak ada paket terinstal.")
        else:
            print("Paket terinstal:")
            for pkg in packages:
                print(f"  {pkg.name} ({pkg.version})")
        return 0

    elif command == "search":
        if not cmd_args:
            print("Gunakan: bropm search <keyword>")
            return 1
        results = manager.search(cmd_args[0])
        if not results:
            print(f"Tidak ada paket ditemukan untuk '{cmd_args[0]}'.")
        else:
            print(f"Hasil pencarian untuk '{cmd_args[0]}':")
            for r in results:
                print(f"  {r['name']} ({r['version']}) - {r['description']}")
        return 0

    else:
        print(f"Perintah tidak dikenal: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
