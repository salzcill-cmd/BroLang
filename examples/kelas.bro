# ============================================================
#  BroLang v9.0 — Kelas & OOP
#  Jalankan: bro examples/kelas.bro
# ============================================================

tulis "============================================="
tulis "  BroLang v9.0 — Kelas & OOP"
tulis "============================================="
tulis ""

# ============ 1. Kelas Dasar ============
tulis "=== Kelas Dasar ==="

kelas Manusia
    fungsi __init__(nama, umur)
        buat self.nama = nama
        buat self.umur = umur
    selesai

    fungsi sapa()
        kembali "Halo, nama saya " + self.nama
    selesai

    fungsi info()
        kembali self.nama + " (" + teks(self.umur) + " tahun)"
    selesai

    fungsi birthday()
        self.umur = self.umur + 1
    selesai
selesai

buat budi = Manusia("Budi", 17)
tulis budi.sapa()
tulis budi.info()
budi.birthday()
tulis "Setelah ulang tahun:", budi.info()
tulis ""

# ============ 2. Inheritance (Pewarisan) ============
tulis "=== Inheritance ==="

kelas Mahasiswa : Manusia
    fungsi __init__(nama, umur, jurusan)
        buat self.nama = nama
        buat self.umur = umur
        buat self.jurusan = jurusan
    selesai

    fungsi info()
        kembali self.nama + " (" + teks(self.umur) + " tahun) - " + self.jurusan
    selesai

    fungsi belajar(mata_kuliah)
        kembali self.nama + " sedang belajar " + mata_kuliah
    selesai
selesai

buat ani = Mahasiswa("Ani", 20, "Informatika")
tulis ani.sapa()
tulis ani.info()
tulis ani.belajar("Pemrograman")
tulis ""

# ============ 3. Encapsulation ============
tulis "=== Encapsulation ==="

kelas RekeningBank
    fungsi __init__(nama, saldo)
        buat self.__nama = nama
        buat self.__saldo = saldo
    selesai

    fungsi get_nama()
        kembali self.__nama
    selesai

    fungsi get_saldo()
        kembali self.__saldo
    selesai

    fungsi setor(jumlah)
        jika jumlah > 0 maka
            self.__saldo = self.__saldo + jumlah
            kembali "Setor " + teks(jumlah) + " berhasil"
        selesai
        kembali "Jumlah tidak valid"
    selesai

    fungsi tarik(jumlah)
        jika jumlah > 0 maka
            jika jumlah <= self.__saldo maka
                self.__saldo = self.__saldo - jumlah
                kembali "Tarik " + teks(jumlah) + " berhasil"
            selesai
        selesai
        kembali "Saldo tidak cukup"
    selesai
selesai

buat rekening = RekeningBank("Budi", 1000000)
tulis "Nama:", rekening.get_nama()
tulis "Saldo:", rekening.get_saldo()
tulis rekening.setor(500000)
tulis "Saldo:", rekening.get_saldo()
tulis rekening.tarik(200000)
tulis "Saldo:", rekening.get_saldo()
tulis ""

# ============ 4. Metode Tambahan ============
tulis "=== Metode Tambahan ==="

kelas Vektor
    fungsi __init__(x, y)
        buat self.x = x
        buat self.y = y
    selesai

    fungsi tambah(other)
        kembali Vektor(self.x + other.x, self.y + other.y)
    selesai

    fungsi kurang(other)
        kembali Vektor(self.x - other.x, self.y - other.y)
    selesai

    fungsi kali(scalar)
        kembali Vektor(self.x * scalar, self.y * scalar)
    selesai

    fungsi __str__()
        kembali "Vektor(" + teks(self.x) + ", " + teks(self.y) + ")"
    selesai

    fungsi magnitude()
        kembali (self.x * self.x + self.y * self.y) ** 0.5
    selesai
selesai

buat v1 = Vektor(3, 4)
buat v2 = Vektor(1, 2)
buat v3 = v1.tambah(v2)
buat v4 = v1.kurang(v2)
buat v5 = v1.kali(2)

tulis "v1:", v1
tulis "v2:", v2
tulis "v1.tambah(v2):", v3
tulis "v1.kurang(v2):", v4
tulis "v1.kali(2):", v5
tulis "|v1|:", v1.magnitude()
tulis ""

# ============ 5. Properti ============
tulis "=== Properti ==="

kelas Suhu
    fungsi __init__(celsius)
        buat self._celsius = celsius
    selesai

    fungsi get_celsius()
        kembali self._celsius
    selesai

    fungsi get_fahrenheit()
        kembali self._celsius * 9 / 5 + 32
    selesai

    fungsi get_kelvin()
        kembali self._celsius + 273.15
    selesai
selesai

buat suhu = Suhu(100)
tulis "Celsius:", suhu.get_celsius()
tulis "Fahrenheit:", suhu.get_fahrenheit()
tulis "Kelvin:", suhu.get_kelvin()
tulis ""

tulis "Selesai! 🎉"
