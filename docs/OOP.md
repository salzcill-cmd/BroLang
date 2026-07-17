# 🏗️ Class & OOP

> **OOP di BroLang itu keren abis.** Inheritensi, polymorphism, property, metaclass — ada semua.

## 📝 Class Dasar

```
class Mahasiswa
    fungsi init(nama, nim)
        ini.nama = nama
        ini.nim = nim
    selesai

    fungsi sapa()
        tulis "Halo, nama saya " + ini.nama + "!"
    selesai
selesai

buat mhs = Mahasiswa("Budi", "12345")
mhs.sapa()    # Halo, nama saya Budi!
```

## 🔙 Return dari Constructor

```
class Pecahan
    fungsi init(pembilang, penyebut)
        ini.pembilang = pembilang
        ini.penyebut = penyebut
        kembali ini
    selesai

    fungsi desimal()
        kembali ini.pembilang / ini.penyebut
    selesai
selesai

buat p = Pecahan(1, 3)
tulis p.desimal()    # 0.333...
```

## 🔗 Inheritensi

```
class Hewan
    fungsi init(nama)
        ini.nama = nama
    selesai

    fungsi suara()
        tulis "..."
    selesai
selesai

class Kucing(Hewan)
    fungsi init(nama, warna)
        super.init(nama)
        ini.warna = warna
    selesai

    fungsi suara()
        tulis "Meong!"
    selesai

    fungsi info()
        tulis "Kucing " + ini.nama + " warnanya " + ini.warna
    selesai
selesai

buat kucing = Kucing("Kitty", "Putih")
kucing.suara()    # Meong!
kucing.info()     # Kucing Kitty warnanya Putih
```

## 📦 Dataclasses

> **Ga perlu nulis `init` manual.** Dataclass自动 generate constructor untuk kamu.

```
@dataclass
class Mahasiswa
    nama
    nim
    jurusan = "Informatika"
selesai

buat mhs = Mahasiswa("Budi", "12345")
tulis mhs.nama
tulis mhs.nim
tulis mhs.jurusan
```

**Auto-generate `init`, `repr`, `eq`** — tinggal sebut field-nya aja.

## 🧬 Multiple Inheritance

```
class BisaTerbang
    fungsi terbang()
        tulis "Terbang tinggi!"
    selesai
selesai

class BisaBerenang
    fungsi berenang()
        tulis "Berenang jauh!"
    selesai
selesai

class Bebek(Hewan, BisaTerbang, BisaBerenang)
    fungsi init()
        super.init("Bebek")
    selesai
selesai
```

---

## 📖 Recap

| Fitur | Contoh |
|-------|--------|
| Class | `class Nama ... selesai` |
| Constructor | `fungsi init(self, ...)` |
| Instance variable | `ini.nama = "Budi"` |
| Inheritensi | `class Anak(OrangTua)` |
| Super | `super.init(args)` |
| Dataclass | `@dataclass class X ...` |
