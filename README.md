# Gala Butik - Django E-Ticaret Projesi

Deniz Butik zarafetinden ilham alan, sıcak bej/krem (`#FAF7F2`) ve kiremit/terracotta (`#B85032`) renk paletine sahip, büyük beden (42-58) odaklı tam kapsamlı Django e-ticaret platformu.

---

## 🚀 Proje Mimarisi ve Özellikler

### 1. Django Modelleri (`store/models.py`)
- **`Category`**: Hiyerarşik alt kategori desteği (Üst Kategori > Alt Kategori), SEO slug, aktiflik ve sıra yönetimi.
- **`Product`**: SKU, fiyat, indirimli fiyat, kumaş/materyal detayı, manken ölçüleri, yıkama talimatları, çok satan/yeni sezon etiketleri.
- **`ProductImage`**: Çoklu yüksek çözünürlüklü görsel desteği, kapak fotoğrafı ve sıralama.
- **`SizeVariant`**: Büyük beden odaklı beden varyantları (`XL (42-44)`, `2XL (46-48)`, `3XL (50-52)`, `4XL (54-56)`, `5XL (58-60)`, `Standart`, `42-56`), anlık stok takibi ve barkod.
- **`Cart` & `CartItem`**: Ziyaretçi oturumu (session) ve üye sepeti entegrasyonu, 750 TL üzeri dinamik ücretsiz kargo ilerleme çubuğu.
- **`Order` & `OrderItem`**: Sipariş yaşam döngüsü, Türkiye adres formatı (İl/İlçe), kargo takip entegrasyonu.
- **`PaymentLog`**: PayTR ve İyzico sanal POS loglama simülasyonu. **Maksimum 3 Taksit Kuralı** (Tekstil ve hazır giyim mevzuatına uygun `installment_count <= 3` kısıtlaması model ve form düzeyinde zorunlu kılınmıştır).

### 2. Gelişmiş Django Yönetim Paneli (`store/admin.py`)
- **Admin Branding**: "Gala Butik Yönetim Paneli"
- **Inlines**: 
  - `ProductAdmin` içinde `ProductImageInline` (küçük resim önizlemeli) ve `SizeVariantInline` (hızlı stok girişi).
  - `OrderAdmin` içinde `OrderItemInline` ve `PaymentLogInline`.
- **Özel Görünümler & Aksiyonlar**: Renkli durum rozetleri, stok uyarıları, tek tıkla toplu sipariş durumu güncelleme (Onaylandı, Hazırlanıyor, Kargoya Verildi).

### 3. Kullanıcı Arayüzü & Şablonlar (`templates/`)
- **Aesthetic**: Deniz Butik sıcaklığında bej/krem zemin, kiremit vurguları, *Cormorant Garamond* serif başlıklar ve *Plus Jakarta Sans* gövde fontları.
- **Duyuru Çubuğu**: Ücretsiz kargo ve vade farksız 3 taksit bilgilendirmesi.
- **Sepet Çekmecesi (Offcanvas Cart Drawer)**: Sayfadan ayrılmadan açılan interaktif sepet çekmecesi ve AJAX ile sepete ekleme/çıkarma.
- **Ürün Detay**: Taksit matrisi (Bonus, World, Axess, Maximum kartlara özel 3 taksit dağılımı), manken ölçüleri ve beden tablosu modalı.
- **Tek Sayfa Ödeme (Checkout)**: Adres formu, PayTR/İyzico kart simülatörü (1-3 taksit seçimi), Havale/EFT ve Kapıda Ödeme seçenekleri.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Geliştirici Sunucusunu Başlatma
```bash
.\venv\Scripts\python.exe manage.py runserver
```
Tarayıcınızda açın: `http://127.0.0.1:8000/`

### 2. Yönetim Paneli Girişi
- **URL**: `http://127.0.0.1:8000/admin/`
- **Kullanıcı Adı**: `admin`
- **Şifre**: `admin123`

### 3. Örnek Verileri Yeniden Yükleme
```bash
.\venv\Scripts\python.exe manage.py seed_data
```

### 4. Otomatik Testleri Çalıştırma
```bash
.\venv\Scripts\python.exe manage.py test
```