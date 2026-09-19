import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Category(models.Model):
    """
    Boutique Category Model supporting multi-level hierarchical categories.
    (e.g. Büyük Beden Giyim -> Elbise, Tunik, İkili Takım)
    """
    name = models.CharField(max_length=120, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=140, unique=True, verbose_name="SEO URL (Slug)")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="Kategori Görseli")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Üst Kategori"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    is_featured_home = models.BooleanField(default=False, verbose_name="Anasayfada Öne Çıkar")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['display_order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name.replace('ı', 'i').replace('İ', 'i').replace('ğ', 'g').replace('Ğ', 'g').replace('ü', 'u').replace('Ü', 'u').replace('ş', 's').replace('Ş', 's').replace('ö', 'o').replace('Ö', 'o').replace('ç', 'c').replace('Ç', 'c'))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', kwargs={'category_slug': self.slug})

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Boutique Product Model tailored for Deniz Butik-style mature & plus-size boutique.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Kategori"
    )
    name = models.CharField(max_length=250, verbose_name="Ürün Adı")
    slug = models.SlugField(max_length=280, unique=True, verbose_name="SEO URL (Slug)")
    sku = models.CharField(max_length=60, unique=True, verbose_name="Ürün Kodu (SKU)")
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Satış Fiyatı (TL)"
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="İndirimli Fiyat (TL)"
    )
    
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Kısa Özet")
    description = models.TextField(verbose_name="Detaylı Ürün Açıklaması")
    fabric_info = models.TextField(
        blank=True,
        verbose_name="Kumaş ve Materyal Bilgisi",
        help_text="Örn: %95 Viskon, %5 Elastan. Likralı, dökümlü ve terletmeyen kumaş."
    )
    washing_instructions = models.TextField(
        blank=True,
        verbose_name="Yıkama ve Bakım Talimatı",
        default="30 derecede hassas yıkama yapınız. Ağartıcı kullanmayınız. Düşük ısıda tersten ütüleyiniz."
    )
    model_measurements = models.TextField(
        blank=True,
        verbose_name="Manken & Kalıp Bilgileri",
        help_text="Örn: Manken Ölçüleri: Boy: 1.74m, Göğüs: 104cm, Bel: 86cm, Basen: 112cm. Giydiği Beden: 44/XL. Kalıp: Rahat / Tam Kalıp."
    )
    
    # Merchandising flags
    is_bestseller = models.BooleanField(default=False, verbose_name="Çok Satan")
    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkan")
    is_new = models.BooleanField(default=True, verbose_name="Yeni Sezon")
    is_active = models.BooleanField(default=True, verbose_name="Satışta / Aktif")
    
    view_count = models.PositiveIntegerField(default=0, verbose_name="Görüntülenme Sayısı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Eklenme Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name.replace('ı', 'i').replace('İ', 'i').replace('ğ', 'g').replace('Ğ', 'g').replace('ü', 'u').replace('Ü', 'u').replace('ş', 's').replace('Ş', 's').replace('ö', 'o').replace('Ö', 'o').replace('ç', 'c').replace('Ç', 'c'))
            self.slug = f"{base_slug}-{self.sku.lower()}" if self.sku else base_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def has_discount(self):
        return bool(self.discount_price and self.discount_price < self.price)

    @property
    def discount_percent(self):
        if self.has_discount:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return int(round(discount))
        return 0

    @property
    def total_stock(self):
        return sum(variant.stock for variant in self.size_variants.filter(is_active=True))

    @property
    def is_in_stock(self):
        return self.total_stock > 0

    @property
    def primary_image(self):
        feature_img = self.images.filter(is_feature=True).first()
        if feature_img:
            return feature_img
        first_img = self.images.first()
        return first_img

    @property
    def installment_3x(self):
        """Enforces Turkish max 3 installments rule calculation."""
        price = self.current_price
        return round(price / Decimal('3.00'), 2)


class ProductImage(models.Model):
    """
    High-resolution images for boutique gallery with feature cover flag and order.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Ürün"
    )
    image = models.ImageField(upload_to="products/%Y/%m/", verbose_name="Görsel")
    image_url_fallback = models.URLField(max_length=500, blank=True, verbose_name="Harici Görsel Linki (Opsiyonel)")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Görsel Açıklaması (Alt Tag)")
    is_feature = models.BooleanField(default=False, verbose_name="Kapak Görseli mi?")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")

    class Meta:
        verbose_name = "Ürün Görseli"
        verbose_name_plural = "Ürün Görselleri"
        ordering = ['-is_feature', 'display_order', 'id']

    def __str__(self):
        return f"{self.product.name} - Görsel {self.id}"

    @property
    def url(self):
        if self.image:
            return self.image.url
        if self.image_url_fallback:
            return self.image_url_fallback
        return "/static/images/placeholder.jpg"


class SizeVariant(models.Model):
    """
    Size Variants with focus on Büyük Beden (Plus Size) ranges.
    Options include standard boutique sizing and numeric Turkish apparel sizes (42 to 58).
    """
    SIZE_CHOICES = [
        ('Standart', 'Standart Beden (38-44 Uyumlu)'),
        ('M (38-40)', 'M (38-40)'),
        ('L (40-42)', 'L (40-42)'),
        ('XL (42-44)', 'XL (42-44) - Büyük Beden'),
        ('2XL (46-48)', '2XL (46-48) - Büyük Beden'),
        ('3XL (50-52)', '3XL (50-52) - Büyük Beden'),
        ('4XL (54-56)', '4XL (54-56) - Büyük Beden'),
        ('5XL (58-60)', '5XL (58-60) - Büyük Beden'),
        ('42', '42 Beden'),
        ('44', '44 Beden'),
        ('46', '46 Beden'),
        ('48', '48 Beden'),
        ('50', '50 Beden'),
        ('52', '52 Beden'),
        ('54', '54 Beden'),
        ('56', '56 Beden'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="size_variants",
        verbose_name="Ürün"
    )
    size = models.CharField(max_length=30, choices=SIZE_CHOICES, verbose_name="Beden / Boyut")
    stock = models.PositiveIntegerField(default=10, verbose_name="Stok Miktarı")
    sku = models.CharField(max_length=80, blank=True, verbose_name="Beden Barkodu / Özel SKU")
    is_active = models.BooleanField(default=True, verbose_name="Satışa Açık")

    class Meta:
        verbose_name = "Beden Varyantı"
        verbose_name_plural = "Beden Varyantları"
        unique_together = ('product', 'size')
        ordering = ['size']

    def __str__(self):
        return f"{self.product.name} - {self.get_size_display()} ({self.stock} Adet)"

    @property
    def is_in_stock(self):
        return self.is_active and self.stock > 0


class Cart(models.Model):
    """
    Cart tracking both guest shoppers (via session key) and logged-in users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
        verbose_name="Kullanıcı"
    )
    session_key = models.CharField(max_length=40, db_index=True, blank=True, verbose_name="Oturum Anahtarı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme")

    class Meta:
        verbose_name = "Alışveriş Sepeti"
        verbose_name_plural = "Alışveriş Sepetleri"

    def __str__(self):
        owner = self.user.username if self.user else f"Ziyaretçi ({self.session_key[:8]}...)"
        return f"Sepet #{self.id} - {owner}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def free_shipping_threshold(self):
        return Decimal(str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 750.00)))

    @property
    def shipping_fee(self):
        if self.subtotal >= self.free_shipping_threshold or self.total_items == 0:
            return Decimal('0.00')
        return Decimal(str(getattr(settings, 'DEFAULT_SHIPPING_FEE', 69.90)))

    @property
    def remaining_for_free_shipping(self):
        if self.subtotal < self.free_shipping_threshold:
            return self.free_shipping_threshold - self.subtotal
        return Decimal('0.00')

    @property
    def free_shipping_progress(self):
        if self.free_shipping_threshold == 0:
            return 100
        progress = (self.subtotal / self.free_shipping_threshold) * 100
        return min(int(progress), 100)

    @property
    def total_amount(self):
        return self.subtotal + self.shipping_fee


class CartItem(models.Model):
    """
    Individual item in the cart with selected size variant.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Sepet")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    size_variant = models.ForeignKey(
        SizeVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Seçilen Beden"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Adet")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Eklenme Tarihi")

    class Meta:
        verbose_name = "Sepet Öğesi"
        verbose_name_plural = "Sepet Öğeleri"

    def __str__(self):
        size_str = self.size_variant.get_size_display() if self.size_variant else "Standart"
        return f"{self.product.name} ({size_str}) x {self.quantity}"

    @property
    def unit_price(self):
        return self.product.current_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Order(models.Model):
    """
    Customer Order Model with full lifecycle tracking, shipping details and Turkish addressing.
    """
    STATUS_CHOICES = [
        ('pending', 'Ödeme Bekleniyor'),
        ('confirmed', 'Sipariş Onaylandı'),
        ('preparing', 'Hazırlanıyor'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
        ('refunded', 'İade Edildi'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Kredi / Banka Kartı (PayTR / İyzico - Max 3 Taksit)'),
        ('bank_transfer', 'Havale / EFT (Ön Onaylı)'),
        ('cash_on_delivery', 'Kapıda Nakit / Kart ile Ödeme (+19.90 TL Hizmet Bedeli)'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ödeme Bekleniyor'),
        ('paid', 'Ödendi / Başarılı'),
        ('failed', 'Ödeme Başarısız'),
    ]

    order_number = models.CharField(max_length=32, unique=True, editable=False, verbose_name="Sipariş No")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Müşteri Hesabı"
    )
    
    # Customer Details
    first_name = models.CharField(max_length=60, verbose_name="Ad")
    last_name = models.CharField(max_length=60, verbose_name="Soyad")
    email = models.EmailField(verbose_name="E-Posta")
    phone = models.CharField(max_length=20, verbose_name="Telefon Numarası")
    
    # Shipping & Billing Address
    address_title = models.CharField(max_length=40, default="Ev Adresim", verbose_name="Adres Başlığı")
    address_line1 = models.CharField(max_length=255, verbose_name="Açık Adres (Cadde, Sokak, No, Daire)")
    address_line2 = models.CharField(max_length=100, blank=True, verbose_name="Bina / Kat / Ek Bilgi")
    district = models.CharField(max_length=60, verbose_name="İlçe")
    city = models.CharField(max_length=60, verbose_name="İl / Şehir")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="Posta Kodu")
    order_notes = models.TextField(blank=True, verbose_name="Sipariş / Kurye Notu")
    
    # Financials
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ara Toplam (TL)")
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Kargo Ücreti (TL)")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Genel Toplam (TL)")
    
    # Status & Payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Sipariş Durumu")
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='credit_card', verbose_name="Ödeme Yöntemi")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Ödeme Durumu")
    installments = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name="Taksit Sayısı (Maksimum 3)"
    )
    
    # Logistics
    cargo_company = models.CharField(max_length=50, default="Yurtiçi Kargo", verbose_name="Kargo Firması")
    tracking_number = models.CharField(max_length=80, blank=True, verbose_name="Kargo Takip No")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.order_number} - {self.first_name} {self.last_name} ({self.total_amount} TL)"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"GLA-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        lines = [self.address_line1]
        if self.address_line2:
            lines.append(self.address_line2)
        lines.append(f"{self.district} / {self.city}")
        if self.postal_code:
            lines.append(self.postal_code)
        return ", ".join(lines)


class OrderItem(models.Model):
    """
    Snapshotted product records tied to an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Sipariş")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ürün")
    product_name = models.CharField(max_length=250, verbose_name="Ürün Adı")
    size_title = models.CharField(max_length=80, verbose_name="Beden Seçimi")
    sku = models.CharField(max_length=60, blank=True, verbose_name="SKU")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat (TL)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Adet")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Fiyat (TL)")
    product_image_url = models.CharField(max_length=500, blank=True, verbose_name="Ürün Görsel URL")

    class Meta:
        verbose_name = "Sipariş Kalemi"
        verbose_name_plural = "Sipariş Kalemleri"

    def __str__(self):
        return f"{self.product_name} ({self.size_title}) x {self.quantity}"


class PaymentLog(models.Model):
    """
    Payment transaction logs for PayTR, İyzico, and alternative gateways.
    Strictly enforces maximum 3 installments rule per Turkish apparel trade laws.
    """
    PROVIDER_CHOICES = [
        ('paytr', 'PayTR Sanal POS'),
        ('iyzico', 'İyzico Checkout API'),
        ('bank_transfer', 'Havale / EFT Bildirimi'),
        ('cash_on_delivery', 'Kapıda Ödeme Tahsilatı'),
    ]

    STATUS_CHOICES = [
        ('success', 'Başarılı (Tahsil Edildi)'),
        ('failed', 'Başarısız (Hata Alındı)'),
        ('pending', 'İşlem Sürüyor'),
        ('refunded', 'İade Edildi'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment_logs", verbose_name="İlişkili Sipariş")
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES, default='paytr', verbose_name="Ödeme Sağlayıcı")
    transaction_id = models.CharField(max_length=120, blank=True, verbose_name="İşlem / Dekont No")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="İşlem Durumu")
    
    # INSTALLMENT RULE: Max 3 installments for textile/clothing industry in Turkey
    installment_count = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(3, message="Tekstil ve giyim mevzuatı gereği taksit sayısı en fazla 3 olabilir.")
        ],
        verbose_name="Taksit Sayısı (Maks. 3 Taksit Kuralı)"
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ödenen Tutar (TL)")
    card_family = models.CharField(max_length=50, blank=True, verbose_name="Kart Programı (Bonus, World, Axess, vb.)")
    card_last_four = models.CharField(max_length=4, blank=True, verbose_name="Kart Son 4 Hane")
    raw_response = models.TextField(blank=True, verbose_name="API Ham Yanıt (JSON/XML)")
    error_message = models.TextField(blank=True, verbose_name="Hata Detayı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tarih")

    class Meta:
        verbose_name = "Ödeme Kaydı (Payment Log)"
        verbose_name_plural = "Ödeme Kayıtları (Payment Logs)"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_provider_display()} ({self.amount} TL) [{self.get_status_display()}]"

    def clean(self):
        if self.installment_count > 3:
            raise ValidationError({'installment_count': "Tekstil ve giyim kategorisinde BDDK kuralları gereği en fazla 3 taksit seçilebilir."})
        super().clean()
