from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    Category,
    Product,
    ProductImage,
    SizeVariant,
    Cart,
    CartItem,
    Order,
    OrderItem,
    PaymentLog,
)

# Customizing Admin Branding for Gala Butik
admin.site.site_header = "Gala Butik Yönetim Paneli"
admin.site.site_title = "Gala Butik Admin"
admin.site.index_title = "E-Ticaret ve Mağaza Yönetimi"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'product_count_badge', 'is_featured_home', 'is_active', 'display_order')
    list_editable = ('is_featured_home', 'is_active', 'display_order')
    list_filter = ('is_active', 'is_featured_home', 'parent')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def product_count_badge(self, obj):
        count = obj.products.count()
        return format_html(
            '<span style="background-color: #F3EDE2; color: #B85032; font-weight: bold; padding: 3px 8px; border-radius: 12px;">{} Ürün</span>',
            count
        )
    product_count_badge.short_description = "Toplam Ürün"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ('image', 'image_url_fallback', 'alt_text', 'is_feature', 'display_order', 'preview_image')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj and obj.url:
            return format_html('<img src="{}" style="height: 60px; width: 60px; object-fit: cover; border-radius: 6px; border: 1px solid #ddd;" />', obj.url)
        return "-"
    preview_image.short_description = "Önizleme"


class SizeVariantInline(admin.TabularInline):
    model = SizeVariant
    extra = 4
    fields = ('size', 'stock', 'sku', 'is_active')
    ordering = ('size',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail_preview',
        'name',
        'sku',
        'category',
        'formatted_price',
        'formatted_discount_price',
        'total_stock_badge',
        'is_new',
        'is_bestseller',
        'is_featured',
        'is_active',
        'created_at'
    )
    list_editable = ('is_new', 'is_bestseller', 'is_featured', 'is_active')
    list_filter = ('category', 'is_active', 'is_bestseller', 'is_new', 'is_featured', 'created_at')
    search_fields = ('name', 'sku', 'short_description', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, SizeVariantInline]
    
    fieldsets = (
        ('Genel Ürün Bilgileri', {
            'fields': (
                ('name', 'slug'),
                ('category', 'sku'),
                'short_description',
                'description',
            )
        }),
        ('Fiyatlandırma & Kampanya', {
            'fields': (
                ('price', 'discount_price'),
            )
        }),
        ('Kumaş, Manken & Yıkama Detayları', {
            'classes': ('collapse',),
            'fields': (
                'fabric_info',
                'model_measurements',
                'washing_instructions',
            )
        }),
        ('Vitrin & Durum Ayarları', {
            'fields': (
                ('is_active', 'is_new', 'is_bestseller', 'is_featured'),
            )
        }),
    )

    def thumbnail_preview(self, obj):
        img = obj.primary_image
        if img:
            return format_html('<img src="{}" style="height: 50px; width: 50px; object-fit: cover; border-radius: 6px; border: 1px solid #EAE3D9;" />', img.url)
        return format_html('<span style="color:#999; font-size: 11px;">Görsel Yok</span>')
    thumbnail_preview.short_description = "Görsel"

    def formatted_price(self, obj):
        return f"{obj.price:,.2f} ₺"
    formatted_price.short_description = "Liste Fiyatı"

    def formatted_discount_price(self, obj):
        if obj.discount_price:
            return format_html('<span style="color: #B85032; font-weight: bold;">{:,.2f} ₺</span>', obj.discount_price)
        return "-"
    formatted_discount_price.short_description = "İndirimli"

    def total_stock_badge(self, obj):
        stock = obj.total_stock
        color = "#16a34a" if stock > 5 else ("#d97706" if stock > 0 else "#dc2626")
        bg_color = "#dcfce7" if stock > 5 else ("#fef3c7" if stock > 0 else "#fee2e2")
        return format_html(
            '<span style="background-color: {}; color: {}; font-weight: bold; padding: 2px 8px; border-radius: 10px;">{} Adet</span>',
            bg_color, color, stock
        )
    total_stock_badge.short_description = "Toplam Stok"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'size_title', 'price', 'quantity', 'total_price', 'item_preview')
    can_delete = False

    def item_preview(self, obj):
        if obj and obj.product_image_url:
            return format_html('<img src="{}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 4px;" />', obj.product_image_url)
        return "-"
    item_preview.short_description = "Ürün"


class PaymentLogInline(admin.StackedInline):
    model = PaymentLog
    extra = 0
    readonly_fields = ('provider', 'transaction_id', 'status', 'installment_count', 'amount', 'card_family', 'card_last_four', 'created_at', 'raw_response', 'error_message')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'phone',
        'city',
        'total_amount_formatted',
        'payment_badge',
        'status_badge',
        'installments_info',
        'cargo_company',
        'tracking_number',
        'created_at'
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'cargo_company', 'created_at')
    search_fields = ('order_number', 'first_name', 'last_name', 'email', 'phone', 'tracking_number', 'city')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, PaymentLogInline]
    actions = ['mark_as_confirmed', 'mark_as_preparing', 'mark_as_shipped', 'mark_as_delivered']

    fieldsets = (
        ('Sipariş Bilgileri', {
            'fields': (
                ('order_number', 'created_at'),
                ('status', 'payment_status', 'payment_method', 'installments'),
            )
        }),
        ('Müşteri ve İletişim', {
            'fields': (
                ('first_name', 'last_name'),
                ('email', 'phone'),
            )
        }),
        ('Teslimat Adresi', {
            'fields': (
                'address_title',
                'address_line1',
                'address_line2',
                ('district', 'city', 'postal_code'),
                'order_notes',
            )
        }),
        ('Kargo ve Takip', {
            'fields': (
                ('cargo_company', 'tracking_number'),
            )
        }),
        ('Ödeme ve Tutar', {
            'fields': (
                ('subtotal', 'shipping_fee', 'total_amount'),
            )
        }),
    )
    readonly_fields = ('order_number', 'created_at')

    def total_amount_formatted(self, obj):
        return format_html('<span style="font-weight: bold; color: #2B2623;">{:,.2f} ₺</span>', obj.total_amount)
    total_amount_formatted.short_description = "Tutar"

    def status_badge(self, obj):
        colors = {
            'pending': ('#fef3c7', '#d97706'),
            'confirmed': ('#e0f2fe', '#0284c7'),
            'preparing': ('#fef08a', '#854d0e'),
            'shipped': ('#dbeafe', '#2563eb'),
            'delivered': ('#dcfce7', '#16a34a'),
            'cancelled': ('#fee2e2', '#dc2626'),
            'refunded': ('#f3e8ff', '#9333ea'),
        }
        bg, fg = colors.get(obj.status, ('#f3f4f6', '#4b5563'))
        return format_html(
            '<span style="background-color: {}; color: {}; font-weight: bold; padding: 3px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = "Sipariş Durumu"

    def payment_badge(self, obj):
        if obj.payment_status == 'paid':
            return format_html('<span style="background-color: #dcfce7; color: #16a34a; font-weight: bold; padding: 2px 6px; border-radius: 8px;">✓ Ödendi</span>')
        elif obj.payment_status == 'pending':
            return format_html('<span style="background-color: #fef3c7; color: #d97706; font-weight: bold; padding: 2px 6px; border-radius: 8px;">⏳ Bekliyor</span>')
        return format_html('<span style="background-color: #fee2e2; color: #dc2626; font-weight: bold; padding: 2px 6px; border-radius: 8px;">✗ Başarısız</span>')
    payment_badge.short_description = "Ödeme Durumu"

    def installments_info(self, obj):
        if obj.installments > 1:
            return format_html('<span style="color: #B85032; font-weight: 600;">{} Taksit (Maks 3)</span>', obj.installments)
        return "Tek Çekim"
    installments_info.short_description = "Taksit"

    # Admin actions
    @admin.action(description="Seçili siparişleri 'Onaylandı' olarak işaretle")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description="Seçili siparişleri 'Hazırlanıyor' olarak işaretle")
    def mark_as_preparing(self, request, queryset):
        queryset.update(status='preparing')

    @admin.action(description="Seçili siparişleri 'Kargoya Verildi' olarak işaretle")
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description="Seçili siparişleri 'Teslim Edildi' olarak işaretle")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'provider', 'installment_count_badge', 'amount_formatted', 'status_badge', 'card_family', 'card_last_four', 'created_at')
    list_filter = ('provider', 'status', 'installment_count', 'created_at')
    search_fields = ('order__order_number', 'transaction_id', 'card_family')
    readonly_fields = ('order', 'provider', 'transaction_id', 'status', 'installment_count', 'amount', 'card_family', 'card_last_four', 'raw_response', 'error_message', 'created_at')

    def order_link(self, obj):
        return format_html('<a href="/admin/store/order/{}/change/">#{}</a>', obj.order.id, obj.order.order_number)
    order_link.short_description = "Sipariş"

    def installment_count_badge(self, obj):
        if obj.installment_count == 1:
            return "Tek Çekim (Peşin)"
        return format_html('<span style="color:#B85032; font-weight:bold;">{} Taksit (Maks 3)</span>', obj.installment_count)
    installment_count_badge.short_description = "Taksit"

    def amount_formatted(self, obj):
        return f"{obj.amount:,.2f} ₺"
    amount_formatted.short_description = "Ödenen Tutar"

    def status_badge(self, obj):
        if obj.status == 'success':
            return format_html('<span style="color: #16a34a; font-weight: bold;">Başarılı</span>')
        elif obj.status == 'failed':
            return format_html('<span style="color: #dc2626; font-weight: bold;">Başarısız</span>')
        return obj.get_status_display()
    status_badge.short_description = "Durum"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'total_items', 'subtotal_formatted', 'created_at')
    readonly_fields = ('session_key', 'created_at', 'updated_at')

    def subtotal_formatted(self, obj):
        return f"{obj.subtotal:,.2f} ₺"
    subtotal_formatted.short_description = "Sepet Tutarı"
