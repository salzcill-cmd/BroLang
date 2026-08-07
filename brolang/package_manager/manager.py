"""
Package Manager BroLang (BroPM)
================================

Mengelola paket-paket BroLang:

- `bro pkg init`        : Buat project/package baru dengan brolang.json
- `bro pkg install`     : Install paket dari git URL atau folder lokal
- `bro pkg remove`      : Hapus paket terinstall
- `bro pkg list`        : Daftar paket terinstall
- `bro pkg search`      : Cari paket di registry lokal
- `bro pkg update`      : Update paket
- `bro pkg publish`     : Publish paket ke registry lokal
- `bro pkg info`        : Info paket (installed)

Paket disimpan di ~/.brolang/packages/<nama>/ dan bisa di-import
dengan `impor <nama>` dari bahasa BroLang.
"""

import os
import sys
import json
import shutil
import subprocess
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

MANIFEST_NAME = "brolang.json"


@dataclass
class Package:
    """Mewakili sebuah paket BroLang."""
    name: str
    version: str
    description: str = ""
    url: str = ""
    dependencies: List[str] = field(default_factory=list)
    source: str = "lokal"  # lokal, git, registry
    main: str = "__init__.bro"


class PackageManager:
    """Manajer paket BroLang.

    Attributes:
        packages_dir: Direktori penyimpanan paket
        registry_file: File registry paket
        registry_url: URL registry publik (default: local registry)
    """

    def __init__(self, packages_dir: Optional[str] = None, registry_url: str = ""):
        self.packages_dir = (
            packages_dir
            or os.environ.get("BROLANG_PACKAGES_DIR")
            or os.path.expanduser("~/.brolang/packages")
        )
        self.registry_file = os.path.expanduser("~/.brolang/registry.json")
        self.registry_url = (
            registry_url
            or os.environ.get("BROLANG_REGISTRY_DIR")
            or os.path.expanduser("~/.brolang/registry")
        )
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Memastikan direktori package manager ada."""
        os.makedirs(self.packages_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        os.makedirs(self.registry_url, exist_ok=True)

    # ============= Registry =============

    def _load_registry(self) -> Dict[str, Package]:
        """Memuat registry paket (lokal + registry bersama)."""
        registry: Dict[str, Package] = {}

        # Baca file registry user
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        registry[k] = Package(**v)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        # Baca registry bersama (hasil publish)
        shared_file = os.path.join(self.registry_url, "registry.json")
        if os.path.exists(shared_file):
            try:
                with open(shared_file, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if k not in registry:
                            registry[k] = Package(**v)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

        return registry

    def _save_registry(self, registry: Dict[str, Package]) -> None:
        """Menyimpan registry paket user."""
        data = {k: v.__dict__ for k, v in registry.items()}
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)

    # ============= Manifest (brolang.json) =============

    @staticmethod
    def create_manifest(name: str, version: str = "1.0.0",
                        description: str = "", main: str = "main.bro",
                        dependencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """Membuat isi manifest brolang.json."""
        return {
            "nama": name,
            "versi": version,
            "deskripsi": description,
            "main": main,
            "dependencies": dependencies or [],
            "brolang": ">=5.0.0",
        }

    def init_project(self, name: Optional[str] = None) -> bool:
        """Membuat project BroLang baru dengan brolang.json.

        Args:
            name: Nama project (default: nama folder saat ini)
        """
        project_dir = os.getcwd()
        project_name = name or os.path.basename(project_dir)
        manifest_path = os.path.join(project_dir, MANIFEST_NAME)

        if os.path.exists(manifest_path):
            print(f"Manifest '{MANIFEST_NAME}' sudah ada di {project_dir}.")
            return True

        manifest = self.create_manifest(project_name)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Buat main.bro jika belum ada
        main_file = os.path.join(project_dir, manifest["main"])
        if not os.path.exists(main_file):
            with open(main_file, "w", encoding="utf-8") as f:
                f.write(f"# {project_name}\n# ============\n\nfungsi info()\n    kembali \"{project_name} v{manifest['versi']}\"\nselesai\n")

        print(f"Project '{project_name}' berhasil diinisialisasi:")
        print(f"  {MANIFEST_NAME}  <- manifest package")
        print(f"  {manifest['main']}   <- file utama")
        print()
        print("Perintah selanjutnya:")
        print("  bro pkg publish   <- publish ke registry lokal")
        print("  bro pkg install   <- install package lain")
        return True

    def read_manifest(self, path: str = None) -> Optional[Dict[str, Any]]:
        """Membaca manifest brolang.json dari folder."""
        path = path or os.path.join(os.getcwd(), MANIFEST_NAME)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    # ============= Install =============

    def install(self, target: str) -> bool:
        """Menginstal paket.

        Mendukung:
        - Nama paket dari registry lokal (sudah dipublish)
        - Path folder lokal berisi brolang.json
        - URL git (https://...git, git@..., atau path ke repo git)
        """
        # Jika target adalah path lokal
        if os.path.isdir(target):
            return self._install_from_dir(target)
        if target.startswith(("https://", "http://", "git@", "git://", "ssh://")):
            return self._install_from_git(target)
        return self._install_from_registry(target)

    def _install_from_dir(self, source_dir: str) -> bool:
        """Install paket dari folder lokal yang punya brolang.json."""
        manifest = self.read_manifest(os.path.join(source_dir, MANIFEST_NAME))
        if manifest is None:
            print(f"Error: '{source_dir}' tidak memiliki {MANIFEST_NAME}.")
            print("Jalankan 'bro pkg init' di folder tersebut dulu.")
            return False

        name = manifest.get("nama", os.path.basename(source_dir))
        version = manifest.get("versi", "1.0.0")
        pkg_dir = os.path.join(self.packages_dir, name)

        # Bersihkan dulu jika sudah ada
        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)
        os.makedirs(pkg_dir, exist_ok=True)

        # Salin file .bro dan manifest
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".bro") or file == MANIFEST_NAME:
                    src = os.path.join(root, file)
                    rel = os.path.relpath(src, source_dir)
                    dst = os.path.join(pkg_dir, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)

        package = Package(
            name=name,
            version=version,
            description=manifest.get("deskripsi", ""),
            url=os.path.abspath(source_dir),
            dependencies=manifest.get("dependencies", []),
            source="lokal",
            main=manifest.get("main", "__init__.bro"),
        )

        registry = self._load_registry()
        registry[name] = package
        self._save_registry(registry)

        print(f"Paket '{name}' ({version}) berhasil diinstal dari {source_dir}.")
        self._print_dependencies(package)
        return True

    def _install_from_git(self, url: str) -> bool:
        """Install paket dari repository git (mirip pip install git+...)."""
        # Ekstrak nama repo dari URL
        repo_name = url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        tmp_dir = os.path.join(self.packages_dir, f".tmp_{repo_name}")
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        print(f"Meng-clone {url} ...")
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", url, tmp_dir],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                print(f"Error clone: {result.stderr.strip()}")
                return False
        except FileNotFoundError:
            print("Error: 'git' tidak terinstall di sistem.")
            return False
        except subprocess.TimeoutExpired:
            print("Error: timeout saat clone repository.")
            return False

        ok = self._install_from_dir(tmp_dir)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return ok

    def _install_from_registry(self, package_name: str) -> bool:
        """Install paket dari registry (paket yang sudah dipublish)."""
        registry = self._load_registry()
        if package_name in registry:
            pkg = registry[package_name]
            # Cari folder package di registry bersama
            shared_dir = os.path.join(self.registry_url, package_name)
            if os.path.isdir(shared_dir):
                return self._install_from_dir(shared_dir)

            # Package sudah terdaftar tapi folder hilang
            if os.path.isdir(os.path.join(self.packages_dir, package_name)):
                print(f"Paket '{package_name}' ({pkg.version}) sudah terinstal.")
                return True
            return self._install_from_dir(shared_dir) if os.path.isdir(shared_dir) else False

        print(f"Paket '{package_name}' tidak ditemukan di registry.")
        print("Coba: bro pkg search <keyword>")
        return False

    def _print_dependencies(self, package: Package) -> None:
        """Menampilkan dependency package."""
        if package.dependencies:
            print(f"Dependencies: {', '.join(package.dependencies)}")
            for dep in package.dependencies:
                self.install(dep)
        else:
            print("Tidak ada dependencies.")

    # ============= Remove =============

    def remove(self, package_name: str) -> bool:
        """Menghapus paket terinstall."""
        registry = self._load_registry()
        if package_name not in registry:
            print(f"Paket '{package_name}' tidak ditemukan.")
            return False

        pkg_dir = os.path.join(self.packages_dir, package_name)
        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)

        del registry[package_name]
        self._save_registry(registry)
        print(f"Paket '{package_name}' berhasil dihapus.")
        return True

    # ============= Update =============

    def update(self, package_name: Optional[str] = None) -> bool:
        """Memperbarui paket (dari source aslinya)."""
        registry = self._load_registry()

        if package_name:
            if package_name not in registry:
                print(f"Paket '{package_name}' tidak ditemukan.")
                return False
            packages = [package_name]
        else:
            packages = list(registry.keys())

        for name in packages:
            pkg = registry[name]
            if pkg.url and os.path.isdir(pkg.url):
                self._install_from_dir(pkg.url)
            elif pkg.url and pkg.url.startswith(("https://", "git@")):
                self._install_from_git(pkg.url)
            else:
                print(f"Paket '{name}' sudah versi terbaru ({pkg.version}).")

        return True

    # ============= Publish =============

    def publish(self) -> bool:
        """Mempublish paket dari folder saat ini ke registry lokal."""
        manifest = self.read_manifest()
        if manifest is None:
            print(f"Error: tidak ada {MANIFEST_NAME} di folder ini.")
            print("Jalankan 'bro pkg init' dulu.")
            return False

        name = manifest.get("nama", os.path.basename(os.getcwd()))
        version = manifest.get("versi", "1.0.0")

        # Salin ke registry bersama
        shared_dir = os.path.join(self.registry_url, name)
        if os.path.exists(shared_dir):
            shutil.rmtree(shared_dir)
        os.makedirs(shared_dir, exist_ok=True)

        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith(".bro") or file == MANIFEST_NAME:
                    src = os.path.join(root, file)
                    rel = os.path.relpath(src, os.getcwd())
                    dst = os.path.join(shared_dir, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)

        # Update registry bersama
        shared_file = os.path.join(self.registry_url, "registry.json")
        shared_registry: Dict[str, Any] = {}
        if os.path.exists(shared_file):
            try:
                with open(shared_file, "r") as f:
                    shared_registry = json.load(f)
            except json.JSONDecodeError:
                pass

        shared_registry[name] = {
            "name": name,
            "version": version,
            "description": manifest.get("deskripsi", ""),
            "url": f"file://{shared_dir}",
            "dependencies": manifest.get("dependencies", []),
            "source": "registry",
            "main": manifest.get("main", "__init__.bro"),
        }
        with open(shared_file, "w") as f:
            json.dump(shared_registry, f, indent=2)

        print(f"Paket '{name}' ({version}) berhasil dipublish ke registry lokal.")
        print(f"  Registry: {self.registry_url}")
        print(f"Install di project lain: bro pkg install {name}")
        return True

    # ============= List / Search / Info =============

    def list_packages(self) -> List[Package]:
        """Mendaftar semua paket yang terinstal."""
        registry = self._load_registry()
        return list(registry.values())

    def search(self, keyword: str) -> List[Dict[str, str]]:
        """Mencari paket di registry."""
        results = []
        registry = self._load_registry()

        for name, package in registry.items():
            if (keyword.lower() in name.lower()
                    or keyword.lower() in (package.description or "").lower()):
                results.append({
                    "name": name,
                    "version": package.version,
                    "description": package.description,
                })

        # Juga cari folder di registry bersama
        shared_registry_file = os.path.join(self.registry_url, "registry.json")
        if os.path.exists(shared_registry_file):
            try:
                with open(shared_registry_file, "r") as f:
                    data = json.load(f)
                for name, pkg in data.items():
                    if (keyword.lower() in name.lower()
                            or keyword.lower() in (pkg.get("description") or "").lower()):
                        if not any(r["name"] == name for r in results):
                            results.append({
                                "name": name,
                                "version": pkg.get("version", "?"),
                                "description": pkg.get("description", ""),
                            })
            except json.JSONDecodeError:
                pass

        return results

    def info(self, package_name: str) -> Optional[Package]:
        """Menampilkan info paket."""
        registry = self._load_registry()
        pkg = registry.get(package_name)
        if pkg is None:
            print(f"Paket '{package_name}' tidak ditemukan.")
            return None

        print(f"Nama        : {pkg.name}")
        print(f"Versi       : {pkg.version}")
        print(f"Deskripsi   : {pkg.description}")
        print(f"Source      : {pkg.url or pkg.source}")
        print(f"Dependencies: {', '.join(pkg.dependencies) if pkg.dependencies else '-'}")
        return pkg

    # ============= Import Support =============

    def find_package(self, package_name: str) -> Optional[str]:
        """Mencari folder package terinstall untuk keperluan import.

        Returns:
            Path ke folder package, atau None jika tidak ditemukan.
        """
        pkg_dir = os.path.join(self.packages_dir, package_name)
        if os.path.isdir(pkg_dir):
            # Verifikasi ada file main
            manifest = self.read_manifest(os.path.join(pkg_dir, MANIFEST_NAME))
            if manifest:
                return pkg_dir
            if os.path.exists(os.path.join(pkg_dir, "__init__.bro")):
                return pkg_dir
        return None


def main(args: Optional[List[str]] = None) -> int:
    """Entry point untuk BroPM CLI (dipanggil dari 'bro pkg ...')."""
    if args is None:
        args = sys.argv[1:]

    if not args:
        print("BroPM - Package Manager BroLang")
        print("Gunakan: bro pkg <command> [options]")
        print()
        print("Perintah:")
        print("  init [nama]        : Buat project/package baru (brolang.json)")
        print("  install <paket>    : Install paket (nama, folder, atau git URL)")
        print("  remove <paket>     : Hapus paket")
        print("  update [paket]     : Update paket")
        print("  list               : Daftar paket terinstall")
        print("  search <kata>      : Cari paket di registry")
        print("  publish            : Publish paket dari folder saat ini")
        print("  info <paket>       : Info paket")
        return 0

    manager = PackageManager()
    command = args[0]
    cmd_args = args[1:]

    if command == "init":
        return 0 if manager.init_project(cmd_args[0] if cmd_args else None) else 1

    elif command == "install":
        if not cmd_args:
            print("Gunakan: bro pkg install <paket>")
            print("Contoh:  bro pkg install matematika-ku")
            print("         bro pkg install /path/ke/folder")
            print("         bro pkg install https://github.com/user/repo.git")
            return 1
        return 0 if manager.install(cmd_args[0]) else 1

    elif command == "remove":
        if not cmd_args:
            print("Gunakan: bro pkg remove <paket>")
            return 1
        return 0 if manager.remove(cmd_args[0]) else 1

    elif command == "update":
        return 0 if manager.update(cmd_args[0] if cmd_args else None) else 1

    elif command == "list":
        packages = manager.list_packages()
        if not packages:
            print("Tidak ada paket terinstal.")
            print("Gunakan 'bro pkg install <paket>' atau 'bro pkg publish' untuk mulai.")
        else:
            print("Paket terinstal:")
            print(f"{'Nama':<20} {'Versi':<10} {'Source':<12} Deskripsi")
            print("-" * 70)
            for pkg in packages:
                src = pkg.source if not pkg.url else (pkg.url[:24] + "..." if len(pkg.url) > 24 else pkg.url)
                print(f"{pkg.name:<20} {pkg.version:<10} {src:<12} {pkg.description}")
        return 0

    elif command == "search":
        if not cmd_args:
            print("Gunakan: bro pkg search <kata_kunci>")
            return 1
        results = manager.search(cmd_args[0])
        if not results:
            print(f"Tidak ada paket ditemukan untuk '{cmd_args[0]}'.")
        else:
            print(f"Hasil pencarian untuk '{cmd_args[0]}':")
            for r in results:
                print(f"  {r['name']} ({r['version']}) - {r['description']}")
        return 0

    elif command == "publish":
        return 0 if manager.publish() else 1

    elif command == "info":
        if not cmd_args:
            print("Gunakan: bro pkg info <paket>")
            return 1
        return 0 if manager.info(cmd_args[0]) is not None else 1

    else:
        print(f"Perintah tidak dikenal: {command}")
        print("Gunakan 'bro pkg' tanpa argumen untuk bantuan.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
