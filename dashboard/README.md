# CyberLab Command Center

CyberLab laboratuvarlarını Termux üzerinde izlemek için yerel ve bağımlılıksız kontrol paneli.

## Gösterdikleri

- keşfedilen LAB klasörleri
- tamamlanan / devam eden laboratuvarlar
- `observations.md` içindeki `VERIFIED` bulgu sayısı
- 10 aşamalı yol haritası
- Git branch ve clean/dirty durumu
- son commitler
- Red Team / Victim / Blue Team çalışma modeli

Dashboard salt okunurdur; tarama yapmaz, laboratuvar çalıştırmaz ve dosya değiştirmez.

## Termux'ta çalıştırma

Repo kökünden:

```bash
python dashboard/serve.py
```

Tablet tarayıcısında:

```text
http://127.0.0.1:8765
```

Durdurmak için `Ctrl+C`.

## Güvenlik

Sunucu yalnızca `127.0.0.1` adresine bind olur; Wi-Fi/LAN arayüzüne açılmaz. `/api/status` yalnızca yerel repo metadatasını ve laboratuvar dokümanlarını okur. Python standart kütüphanesi ve yerel `git` komutları dışında bağımlılık yoktur.

Bir lab, `README.md` ve `observations.md` mevcutsa ve observations içinde en az bir `VERIFIED` işareti varsa tamamlanmış kabul edilir. İleride bu heuristiği `lab.json` manifest sistemine yükseltebiliriz.
