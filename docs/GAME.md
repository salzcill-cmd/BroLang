# 🎮 Game Development

> **Bikin game pake BroLang? Bisa banget!** Lewat module `grafis` dan `game`.

## 🚀 Mulai Bikin Game

### Window Dasar

```
muat grafis

grafis.buat_layar(800, 600)
grafis.set_judul("Game Pertamaku")

selama benar lakukan
    grafis.mulai_frame()

    # Isi background warna abu-abu
    grafis.isi_layar(100, 100, 100)

    grafis.selesai_frame()
selesai
```

### Input Handling

```
muat grafis
muat game

grafis.buat_layar(800, 600)

buat player_x = 400
buat player_y = 300
buat kecepatan = 5

selama benar lakukan
    grafis.mulai_frame()
    grafis.isi_layar(50, 50, 50)

    # Gerakin player pake WASD
    jika game.input_ditekan("d") maka
        player_x = player_x + kecepatan
    selesai
    jika game.input_ditekan("a") maka
        player_x = player_x - kecepatan
    selesai
    jika game.input_ditekan("s") maka
        player_y = player_y + kecepatan
    selesai
    if game.input_ditekan("w") maka
        player_y = player_y - kecepatan
    selesai

    # Gambar player (kotak biru)
    grafis.gambar_kotak(player_x, player_y, 50, 50, 0, 100, 255)

    grafis.selesai_frame()
selesai
```

### Collision Detection

```
buat collision = game.cek_tabrakan(
    player_x, player_y, 50, 50,
    musuh_x, musuh_y, 50, 50
)

jika collision maka
    tulis "Kena musuh!"
selesai
```

---

## 📖 Recap

| Fitur | Fungsi |
|-------|--------|
| Buat layar | `grafis.buat_layar(w, h)` |
| Background | `grafis.isi_layar(r, g, b)` |
| Input | `game.input_ditekan("tombol")` |
| Tabrakan | `game.cek_tabrakan(x1,y1,w1,h1, x2,y2,w2,h2)` |
| Suara | `audio.mainkan("file.mp3")` |
