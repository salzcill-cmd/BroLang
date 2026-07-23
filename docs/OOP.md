# Class & OOP

> **OOP di BroLang itu keren abis.** Inheritensi, polymorphism, property, metaclass — ada semua.

## Class Dasar

```
kelas Mahasiswa
    fungsi __init__(nama, nim)
        self.nama = nama
        self.nim = nim
    selesai

    fungsi sapa()
        tulis("Halo, nama saya " + self.nama + "!")
    selesai
selesai

buat mhs = Mahasiswa("Budi", "12345")
mhs.sapa()    # Halo, nama saya Budi!
```

## Return dari Constructor

```
kelas Pecahan
    fungsi __init__(pembilang, penyebut)
        self.pembilang = pembilang
        self.penyebut = penyebut
        kembali self
    selesai

    fungsi desimal()
        kembali self.pembilang / self.penyebut
    selesai
selesai

buat p = Pecahan(1, 3)
tulis(p.desimal())    # 0.333...
```

## Inheritensi

```
kelas Hewan
    fungsi __init__(nama)
        self.nama = nama
    selesai

    fungsi suara()
        tulis("...")
    selesai
selesai

kelas Kucing(Hewan)
    fungsi __init__(nama, warna)
        super().__init__(nama)
        self.warna = warna
    selesai

    fungsi suara()
        tulis("Meong!")
    selesai

    fungsi info()
        tulis("Kucing " + self.nama + " warnanya " + self.warna)
    selesai
selesai

buat kucing = Kucing("Kitty", "Putih")
kucing.suara()    # Meong!
kucing.info()     # Kucing Kitty warnanya Putih
```

## Dataclasses

> **Ga perlu nulis `__init__` manual.** Dataclass auto generate constructor buat kamu.

```
@dataclass
kelas Mahasiswa
    nama
    nim
    jurusan = "Informatika"
selesai

buat mhs = Mahasiswa("Budi", "12345")
tulis(mhs.nama)
tulis(mhs.nim)
tulis(mhs.jurusan)
```

**Auto-generate `__init__`, `repr`, `eq`** — tinggal sebut field-nya aja.

## Multiple Inheritance

```
kelas BisaTerbang
    fungsi terbang()
        tulis("Terbang tinggi!")
    selesai
selesai

kelas BisaBerenang
    fungsi berenang()
        tulis("Berenang jauh!")
    selesai
selesai

kelas Bebek(Hewan, BisaTerbang, BisaBerenang)
    fungsi __init__()
        super().__init__("Bebek")
    selesai
selesai
```

## Interfaces (v5.0)

```
antarmuka DapatJalankan {
    fungsi jalankan()
}
```

Buat kontrak, biar tau method apa aja yang wajib ada di kelas.

## Abstract Classes (v5.0)

```
abstrak kelas Hewan {
    fungsi suara()
}
```

Kelas yang ga bisa langsung dipake, harus diwarisi dulu.

## Static Methods (v5.0)

```
kelas Kalkulator
    statis fungsi tambah(a, b)
        kembali a + b
    selesai

    statis fungsi kali(a, b)
        kembali a * b
    selesai
selesai

tulis(Kalkulator.tambah(3, 4))  # 7
tulis(Kalkulator.kali(5, 6))    # 30
```

`statis` bikin method bisa dipanggil tanpa bikin instance.

## Properties (v5.0)

```
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
tulis(s.get("derajat"))     # 36
s.set("derajat", 37)
tulis(s.get("derajat"))     # 37
```

Convention: `_<nama>()` buat getter, `_<nama>_set(v)` buat setter.

## Iterator Protocol (v5.0)

```
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
untuk v dalam r lakukan
    tulis(v)
selesai
# Output: 1, 2, 3
```

Bikin objek iterable sendiri pake `__iter__`/`__next__`.

## Access Modifiers (v5.0)

```
kelas Keamanan
    privat fungsi rahasia()
        tulis("jangan liat!")
    selesai

    fungsi buka()
        self.rahasia()  # bisa dari dalam kelas
    selesai
selesai

buat k = Keamanan()
k.buka()        # bisa
k.rahasia()     # error! privat
```

`privat` beneran diproteksi, `publik` bisa diakses dari mana aja, `terlindungi` cuma bisa dari kelas turunan.

---

## Recap

| Fitur | Contoh |
|-------|--------|
| Class | `kelas Nama ... selesai` |
| Constructor | `fungsi __init__(self, ...)` |
| Instance variable | `self.nama = "Budi"` |
| Inheritensi | `kelas Anak(OrangTua)` |
| Super | `super().__init__(args)` |
| Dataclass | `@dataclass kelas X ...` |
| Interfaces | `antarmuka Nama { ... }` |
| Abstract class | `abstrak kelas Nama { ... }` |
| Static method | `statis fungsi nama()` |
| Properties | `_<nama>()` / `_<nama>_set(v)` |
| Iterator | `__iter__()` / `__next__()` |
| Access modifiers | `privat` / `publik` / `terlindungi` |
