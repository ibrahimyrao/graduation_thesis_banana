# 🍌 Muz Olgunluk Takip Sistemi (Banana Ripeness Tracker)

Bu proje, bir bitirme tezi kapsamında geliştirilmiş IoT tabanlı bir tarımsal izleme sistemidir. Sistem, seralarda yetiştirilen muzların olgunluk durumunu gerçek zamanlı olarak izlemek ve hasat zamanını tahmin etmek amacıyla tasarlanmıştır. Görüntü işleme teknikleri ve kablosuz haberleşme altyapısı kullanılarak, üreticilere veriye dayalı karar verme imkanı sunar.

## 📋 Proje Özeti

Muz Olgunluk Takip Sistemi, ESP32-CAM modülü kullanarak belirli aralıklarla muz hedeflerinden görüntü alır. Alınan görüntüler Wi-Fi üzerinden merkezi bir sunucuya (Python/Flask tabanlı) iletilir. Sunucu tarafında çalışan OpenCV destekli algoritma, görüntüleri işleyerek muzların renk değişimini (HSV renk uzayı) analiz eder. Elde edilen veriler kaydedilir ve olgunlaşma süreci matematiksel olarak modellenerek tahmini hasat zamanı hesaplanır. Kullanıcılar, web arayüzü üzerinden anlık durumu ve tahmini hasat zamanını takip edebilirler.

## ✨ Temel Özellikler

*   **Otomatik Görüntüleme:** ESP32-CAM modülü, kullanıcı müdahalesi olmadan periyodik olarak (varsayılan: her 6 saatte bir) yüksek çözünürlüklü fotoğraflar çeker.
*   **Kablosuz Veri Aktarımı:** Çekilen görüntüler, yerel ağ üzerinden HTTP POST isteği ile sunucuya iletilir.
*   **Görüntü İşleme ve Analiz:**
    *   OpenCV kütüphanesi ile çekilen görüntüler üzerinde renk analizi yapılır.
    *   RGB yerine HSV (Hue, Saturation, Value) renk uzayı kullanılarak ışık değişimlerinden daha az etkilenen, daha kararlı bir olgunluk tespiti sağlanır.
    *   Muz renginin değişim trendi takip edilerek "Olgunlaştı" veya "Olgunlaşmadı" kararı verilir.
*   **Veri Kaydı ve Loglama:** Her analiz sonucu, tarih ve renk değerleriyle birlikte CSV formatında (`hsv_log.csv`) saklanır.
*   **Tahmini Hasat Zamanı:** Geçmiş 24 saatlik veri ile mevcut durum karşılaştırılarak olgunlaşma hızı hesaplanır ve tahmini hasat saati öngörülür.
*   **Kullanıcı Arayüzü:** Basit ve anlaşılır bir web arayüzü ile son çekilen fotoğraf, güncel durum ve tahmini süre görüntülenir.

## 🛠️ Kullanılan Teknolojiler ve Donanımlar

### Donanım
*   **ESP32-CAM:** Wi-Fi ve Bluetooth özellikli, kamera modüllü mikrodenetleyici kartı. (AI-Thinker Modeli)
*   **FTDI Programlayıcı:** ESP32-CAM modülüne kod yüklemek için.
*   **Muz Numunesi:** Test ve kalibrasyon için.

### Yazılım ve Kütüphaneler
**Gömülü Yazılım (Embedded):**
*   Arduino IDE (C++)
*   `esp_camera.h`: Kamera sürücü kütüphanesi.
*   `WiFi.h`: Kablosuz ağ bağlantısı için.
*   `HTTPClient.h`: Sunucu ile iletişim için HTTP istemcisi.

**Sunucu Tarafı (Backend):**
*   Python 3.x
*   **Flask:** Hafif web sunucusu ve API yönetimi.
*   **OpenCV (`cv2`):** Görüntü işleme ve bilgisayarlı görü algoritmaları.
*   **CSV:** Veri saklama ve okuma.
*   **HTML/CSS:** Web arayüzü tasarımı (Template Engine).

## 📊 Algoritma Mantığı

Sistem, muzun olgunlaşma sürecini temel olarak renk değişimi üzerinden takip eder. Yeşil muzlar olgunlaştıkça sarıya döner. Bu değişim, HSV renk uzayında **Hue (H)** değeri ile temsil edilir.

1.  **Görüntü Alımı:** Kameradan alınan görüntüde analiz edilecek bölge (ROI - Region of Interest) belirlenir.
2.  **Renk Dönüşümü:** RGB formatındaki görüntü HSV formatına çevrilir.
3.  **H Eşiği Kontrolü:** Ortalama H değeri 15 ile 45 arasındaysa (sarı tonları), muz "Olgunlaştı" olarak işaretlenir. Aksi takdirde (yeşil tonları) "Olgunlaşmadı" kabul edilir.
4.  **Zaman Tahmini:** Son 24 saatteki renk değişimi hızı (Delta H) hesaplanır. Hedeflenen olgunluk rengine kalan mesafe bu hıza bölünerek tahmini süre (saat) bulunur.

## 📂 Proje Yapısı

```
graduation_thesis_banana-main/
│
├── esp32_cam/             # ESP32-CAM kaynak kodları
│   └── esp32_cam.ino      # Kamera ve WiFi işlem kodu
│
├── muz_serasi/            # Backend ve Web Arayüzü kodları
│   ├── app.py             # Flask uygulaması ve Görüntü İşleme mantığı
│   ├── hsv_log.csv        # Veri kayıt dosyası
│   ├── uploads/           # Kameradan gelen fotoğrafların kaydedildiği klasör
│   └── ...
│
└── README.md              # Proje dokümantasyonu
```

## 📝 Lisans ve İletişim

Bu proje, akademik bir çalışma (bitirme tezi) kapsamında açık kaynak olarak paylaşılmıştır. Eğitim ve araştırma amaçlı kullanılabilir.

---